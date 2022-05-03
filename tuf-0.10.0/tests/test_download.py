#!/usr/bin/env python

"""
<Program>
  test_download.py
  
<Author>
  Konstantin Andrianov.
  
<Started>
  March 26, 2012.
  
<Copyright>
  See LICENSE for licensing information.

<Purpose>
  Unit test for 'download.py'.

  NOTE: Make sure test_download.py is ran in 'tuf/tests/' directory.
  Otherwise, module that launches simple server would not be found.  
"""

# Help with Python 3 compatibility, where the print statement is a function, an
# implicit relative import is invalid, and the '/' operator performs true
# division.  Example:  print 'hello world' raises a 'SyntaxError' exception.
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import hashlib
import logging
import os
import random
import subprocess
import time
import unittest

import tuf
import tuf.conf
import tuf.download as download
import tuf.log
import tuf.unittest_toolbox as unittest_toolbox

import six

logger = logging.getLogger('tuf.test_download')


class TestDownload(unittest_toolbox.Modified_TestCase):
  def setUp(self):
    """ 
    Create a temporary file and launch a simple server in the
    current working directory.
    """

    unittest_toolbox.Modified_TestCase.setUp(self)

    # Making a temporary file.
    current_dir = os.getcwd()
    target_filepath = self.make_temp_data_file(directory=current_dir)
    self.target_fileobj = open(target_filepath, 'r')
    self.target_data = self.target_fileobj.read()
    self.target_data_length = len(self.target_data)

    # Launch a SimpleHTTPServer (serves files in the current dir).
    self.PORT = random.randint(30000, 45000)
    command = ['python', 'simple_server.py', str(self.PORT)]
    self.server_proc = subprocess.Popen(command, stderr=subprocess.PIPE)
    logger.info('\n\tServer process started.')
    logger.info('\tServer process id: '+str(self.server_proc.pid))
    logger.info('\tServing on port: '+str(self.PORT))
    junk, rel_target_filepath = os.path.split(target_filepath)
    self.url = 'http://localhost:'+str(self.PORT)+'/'+rel_target_filepath

    # NOTE: Following error is raised if delay is not applied:
    #    <urlopen error [Errno 111] Connection refused>
    time.sleep(1)

    # Computing hash of target file data.
    m = hashlib.md5()
    m.update(self.target_data.encode('utf-8'))
    digest = m.hexdigest()
    self.target_hash = {'md5':digest}  


  # Stop server process and perform clean up.
  def tearDown(self):
    unittest_toolbox.Modified_TestCase.tearDown(self)
    if self.server_proc.returncode is None:
      logger.info('\tServer process '+str(self.server_proc.pid)+' terminated.')
      self.server_proc.kill()
    self.target_fileobj.close()


  # Test: Normal case.
  def test_download_url_to_tempfileobj(self):

    download_file = download.safe_download

    temp_fileobj = download_file(self.url, self.target_data_length)
    self.assertEqual(self.target_data, temp_fileobj.read().decode('utf-8'))
    self.assertEqual(self.target_data_length, len(temp_fileobj.read()))
    temp_fileobj.close_temp_file()


  # Test: Incorrect lengths.
  def test_download_url_to_tempfileobj_and_lengths(self):
    # We do *not* catch 'tuf.DownloadLengthMismatchError' in the following two
    # calls because the file at 'self.url' contains enough bytes to satisfy the
    # smaller number of required bytes requested. safe_download() and
    # unsafe_download() will only log a warning when the the server-reported
    # length of the file does not match the required_length.  'updater.py'
    # *does* verify the hashes of downloaded content.
    download.safe_download(self.url, self.target_data_length - 4)
    download.unsafe_download(self.url, self.target_data_length - 4)

    # We catch 'tuf.DownloadLengthMismatchError' here because safe_download()
    # will not download more bytes than requested.
    self.assertRaises(tuf.DownloadLengthMismatchError, download.safe_download,
                      self.url, self.target_data_length + 1)

    # However, we do *not* catch 'tuf.DownloadLengthMismatchError' in the next
    # test condition because unsafe_download() does not enforce the required
    # length argument.  The length reported and the length downloaded are still
    # logged.
    temp_fileobj = \
      download.unsafe_download(self.url, self.target_data_length + 1)
    self.assertEqual(self.target_data, temp_fileobj.read().decode('utf-8'))
    self.assertEqual(self.target_data_length, len(temp_fileobj.read()))
    temp_fileobj.close_temp_file()



  def test_download_url_to_tempfileobj_and_performance(self):

    """
    # Measuring performance of 'auto_flush = False' vs. 'auto_flush = True'
    # in download._download_file() during write. No change was observed.
    star_cpu = time.clock()
    star_real = time.time()

    temp_fileobj = download_file(self.url, 
                                 self.target_data_length)

    end_cpu = time.clock()
    end_real = time.time()  
 
    self.assertEqual(self.target_data, temp_fileobj.read())
    self.assertEqual(self.target_data_length, len(temp_fileobj.read()))
    temp_fileobj.close_temp_file()

    print "Performance cpu time: "+str(end_cpu - star_cpu)
    print "Performance real time: "+str(end_real - star_real)

    # TODO: [Not urgent] Show the difference by setting write(auto_flush=False)
    """


  # Test: Incorrect/Unreachable URLs.
  def test_download_url_to_tempfileobj_and_urls(self):

    download_file = download.safe_download
    unsafe_download_file = download.unsafe_download

    self.assertRaises(tuf.FormatError,
                      download_file, None, self.target_data_length)

    self.assertRaises(tuf.FormatError,
                      download_file,
                      self.random_string(), self.target_data_length)

    self.assertRaises(six.moves.urllib.error.HTTPError,
                      download_file,
                      'http://localhost:' + str(self.PORT) + '/' + self.random_string(), 
                      self.target_data_length)

    self.assertRaises(six.moves.urllib.error.URLError,
                      download_file,
                      'http://localhost:' + str(self.PORT+1) + '/' + self.random_string(), 
                      self.target_data_length)

    # Specify an unsupported URI scheme.
    url_with_unsupported_uri = self.url.replace('http', 'file')
    self.assertRaises(tuf.FormatError, download_file, url_with_unsupported_uri,
                      self.target_data_length)
    self.assertRaises(tuf.FormatError, unsafe_download_file,
                      url_with_unsupported_uri, self.target_data_length)

 

  def test__get_opener(self):
    # Test normal case.
    # A simple https server should be used to test the rest of the optional
    # ssl-related functions of 'tuf.download.py'.
    fake_cacert = self.make_temp_data_file()
    
    with open(fake_cacert, 'wt') as file_object:
      file_object.write('fake cacert')
    
    tuf.conf.ssl_certificates = fake_cacert
    tuf.download._get_opener('https')
    tuf.conf.ssl_certificates = None




  def test_https_connection(self):
    # Make a temporary file to be served to the client.
    current_directory = os.getcwd()
    target_filepath = self.make_temp_data_file(directory=current_directory)
    target_data = None  
    target_data_length = 0
    
    with open(target_filepath, 'r') as target_file_object:
      target_data = target_file_object.read()
      target_data_length = len(target_data)
    
    # Launch an https server (serves files in the current dir).
    port = random.randint(30000, 45000)
    command = ['python', 'simple_https_server.py', str(port)]
    https_server_process = subprocess.Popen(command, stderr=subprocess.PIPE)
    
    # NOTE: Following error is raised if delay is not applied:
    #    <urlopen error [Errno 111] Connection refused>
    time.sleep(1)
    
    junk, relative_target_filepath = os.path.split(target_filepath)
    https_url = 'https://localhost:' + str(port) + '/' + relative_target_filepath
   
    # Download the target file using an https connection.
    tuf.conf.ssl_certificates = 'https_client.pem'
    message = 'Downloading target file from https server: ' + https_url  
    logger.info(message)
    try: 
      download.safe_download(https_url, target_data_length)
      download.unsafe_download(https_url, target_data_length)
    
    finally:
      https_server_process 
      if https_server_process.returncode is None:
        message = \
          'Server process ' + str(https_server_process.pid) + ' terminated.'
        logger.info(message)
        self.server_proc.kill()



  def test__get_content_length(self):
    content_length = \
      tuf.download._get_content_length({'bad_connection_object': 8})
    self.assertEqual(content_length, None)


# Run unit test.
if __name__ == '__main__':
  unittest.main()
