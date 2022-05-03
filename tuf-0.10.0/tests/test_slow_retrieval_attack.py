#!/usr/bin/env python

"""
<Program Name>
  test_slow_retrieval_attack.py

<Author>
  Konstantin Andrianov.

<Started>
  March 13, 2012.

  April 5, 2014.
    Refactored to use the 'unittest' module (test conditions in code, rather
    than verifying text output), use pre-generated repository files, and
    discontinue use of the old repository tools. Expanded comments and modified
    previous setup. -vladimir.v.diaz

<Copyright>
  See LICENSE for licensing information.

<Purpose>
  Simulate a slow retrieval attack, where an attacker is able to prevent clients
  from receiving updates by responding to client requests so slowly that updates
  never complete.  Test cases included for two types of slow retrievals: data
  that slowly trickles in, and data that is only returned after a long time
  delay.  TUF prevents slow retrieval attacks by ensuring the download rate
  does not fall below a required rate (tuf.conf.MIN_AVERAGE_DOWNLOAD_SPEED).

  Note: There is no difference between 'updates' and 'target' files.
"""

# Help with Python 3 compatibility, where the print statement is a function, an
# implicit relative import is invalid, and the '/' operator performs true
# division.  Example:  print 'hello world' raises a 'SyntaxError' exception.
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import os
import sys
import tempfile
import random
import time
import shutil
import json
import subprocess
import logging
import sys

# 'unittest2' required for testing under Python < 2.7.
if sys.version_info >= (2, 7):
  import unittest

else:
  import unittest2 as unittest 

import tuf.formats
import tuf.util
import tuf.log
import tuf.client.updater as updater
import tuf.unittest_toolbox as unittest_toolbox
import tuf.repository_tool as repo_tool

import six

logger = logging.getLogger('tuf.test_slow_retrieval_attack')
repo_tool.disable_console_log_messages()


class TestSlowRetrievalAttack(unittest_toolbox.Modified_TestCase):

  @classmethod
  def setUpClass(cls):
    # setUpClass() is called before any of the test cases are executed.
    
    # Create a temporary directory to store the repository, metadata, and target
    # files.  'temporary_directory' must be deleted in TearDownModule() so that
    # temporary files are always removed, even when exceptions occur. 
    cls.temporary_directory = tempfile.mkdtemp(dir=os.getcwd())
    cls.SERVER_PORT = random.randint(30000, 45000)



  @classmethod 
  def tearDownClass(cls):
    # tearDownModule() is called after all the test cases have run.
    # http://docs.python.org/2/library/unittest.html#class-and-module-fixtures
   
    # Remove the temporary repository directory, which should contain all the
    # metadata, targets, and key files generated of all the test cases.
    shutil.rmtree(cls.temporary_directory)



  def _start_slow_server(self, mode):
    # Launch a SimpleHTTPServer (serves files in the current directory).
    # Test cases will request metadata and target files that have been
    # pre-generated in 'tuf/tests/repository_data', which will be served by the
    # SimpleHTTPServer launched here.  The test cases of this unit test assume 
    # the pre-generated metadata files have a specific structure, such
    # as a delegated role 'targets/role1', three target files, five key files,
    # etc.
    command = ['python', 'slow_retrieval_server.py', str(self.SERVER_PORT), mode]
    server_process = subprocess.Popen(command, stderr=subprocess.PIPE)
    logger.info('Slow Retrieval Server process started.')
    logger.info('Server process id: '+str(server_process.pid))
    logger.info('Serving on port: '+str(self.SERVER_PORT))
    url = 'http://localhost:'+str(self.SERVER_PORT) + os.path.sep

    # NOTE: Following error is raised if a delay is not applied:
    # <urlopen error [Errno 111] Connection refused>
    time.sleep(1)

    return server_process
   


  def _stop_slow_server(self, server_process):
    # Kill the SimpleHTTPServer process.
    if server_process.returncode is None:
      logger.info('Server process '+str(server_process.pid)+' terminated.')
      server_process.kill()
    


  def setUp(self):
    # We are inheriting from custom class.
    unittest_toolbox.Modified_TestCase.setUp(self)
  
    # Copy the original repository files provided in the test folder so that
    # any modifications made to repository files are restricted to the copies.
    # The 'repository_data' directory is expected to exist in 'tuf/tests/'.
    original_repository_files = os.path.join(os.getcwd(), 'repository_data') 
    temporary_repository_root = \
      self.make_temp_directory(directory=self.temporary_directory)
  
    # The original repository, keystore, and client directories will be copied
    # for each test case. 
    original_repository = os.path.join(original_repository_files, 'repository')
    original_client = os.path.join(original_repository_files, 'client')
    original_keystore = os.path.join(original_repository_files, 'keystore')
    
    # Save references to the often-needed client repository directories.
    # Test cases need these references to access metadata and target files. 
    self.repository_directory = \
      os.path.join(temporary_repository_root, 'repository')
    self.client_directory = os.path.join(temporary_repository_root, 'client')
    self.keystore_directory = os.path.join(temporary_repository_root, 'keystore')
    
    # Copy the original 'repository', 'client', and 'keystore' directories
    # to the temporary repository the test cases can use.
    shutil.copytree(original_repository, self.repository_directory)
    shutil.copytree(original_client, self.client_directory)
    shutil.copytree(original_keystore, self.keystore_directory)
    
    # The slow retrieval server, in mode 2 (1 byte per second), will only
    # sleep for a  total of (target file size) seconds.  Add a target file
    # that contains sufficient number of bytes to trigger a slow retrieval
    # error.  "sufficient number of bytes" assumed to be
    # >> 'tuf.conf.SLOW_START_GRACE_PERIOD' bytes.
    extra_bytes = 8
    total_bytes = tuf.conf.SLOW_START_GRACE_PERIOD + extra_bytes 

    repository = repo_tool.load_repository(self.repository_directory)
    file1_filepath = os.path.join(self.repository_directory, 'targets',
                                  'file1.txt')
    with open(file1_filepath, 'wb') as file_object:
      data = 'a' * total_bytes
      file_object.write(data.encode('utf-8'))

    key_file = os.path.join(self.keystore_directory, 'timestamp_key') 
    timestamp_private = repo_tool.import_rsa_privatekey_from_file(key_file,
                                                                  'password')
    key_file = os.path.join(self.keystore_directory, 'snapshot_key') 
    snapshot_private = repo_tool.import_rsa_privatekey_from_file(key_file,
                                                                  'password')
    key_file = os.path.join(self.keystore_directory, 'targets_key') 
    targets_private = repo_tool.import_rsa_privatekey_from_file(key_file,
                                                                  'password')

    repository.targets.load_signing_key(targets_private)
    repository.snapshot.load_signing_key(snapshot_private)
    repository.timestamp.load_signing_key(timestamp_private)
    
    repository.write()
    
    # Move the staged metadata to the "live" metadata.
    shutil.rmtree(os.path.join(self.repository_directory, 'metadata'))
    shutil.copytree(os.path.join(self.repository_directory, 'metadata.staged'),
                    os.path.join(self.repository_directory, 'metadata'))
    
    # Set the url prefix required by the 'tuf/client/updater.py' updater.
    # 'path/to/tmp/repository' -> 'localhost:8001/tmp/repository'. 
    repository_basepath = self.repository_directory[len(os.getcwd()):]
    url_prefix = \
      'http://localhost:' + str(self.SERVER_PORT) + repository_basepath 
    
    # Setting 'tuf.conf.repository_directory' with the temporary client
    # directory copied from the original repository files.
    tuf.conf.repository_directory = self.client_directory 
    self.repository_mirrors = {'mirror1': {'url_prefix': url_prefix,
                                           'metadata_path': 'metadata',
                                           'targets_path': 'targets',
                                           'confined_target_dirs': ['']}}

    # Create the repository instance.  The test cases will use this client
    # updater to refresh metadata, fetch target files, etc.
    self.repository_updater = updater.Updater('test_repository',
                                              self.repository_mirrors)
    


  def tearDown(self):
    # Modified_TestCase.tearDown() automatically deletes temporary files and
    # directories that may have been created during each test case.
    unittest_toolbox.Modified_TestCase.tearDown(self)



  def test_with_tuf_mode_1(self):
    # Simulate a slow retrieval attack.
    # 'mode_1': When download begins,the server blocks the download for a long
    # time by doing nothing before it sends the first byte of data.

    server_process = self._start_slow_server('mode_1')
   
    # Verify that the TUF client detects replayed metadata and refuses to
    # continue the update process.
    client_filepath = os.path.join(self.client_directory, 'file1.txt')
    try:
      file1_target = self.repository_updater.target('file1.txt')
      self.repository_updater.download_target(file1_target, self.client_directory)
     
    # Verify that the specific 'tuf.SlowRetrievalError' exception is raised by
    # each mirror.
    except tuf.NoWorkingMirrorError as exception:
      for mirror_url, mirror_error in six.iteritems(exception.mirror_errors):
        url_prefix = self.repository_mirrors['mirror1']['url_prefix']
        url_file = os.path.join(url_prefix, 'targets', 'file1.txt')
       
        # Verify that 'file1.txt' is the culprit.
        self.assertEqual(url_file, mirror_url)
        self.assertTrue(isinstance(mirror_error, tuf.DownloadLengthMismatchError))
    
    else:
      self.fail('TUF did not prevent a slow retrieval attack.')

    finally:
      self._stop_slow_server(server_process)



  def test_with_tuf_mode_2(self):
    # Simulate a slow retrieval attack.
    # 'mode_2': During the download process, the server blocks the download 
    # by sending just several characters every few seconds.

    server_process = self._start_slow_server('mode_2')
    client_filepath = os.path.join(self.client_directory, 'file1.txt')
    original_average_download_speed = tuf.conf.MIN_AVERAGE_DOWNLOAD_SPEED 
    tuf.conf.MIN_AVERAGE_DOWNLOAD_SPEED = 1

    try:
      file1_target = self.repository_updater.target('file1.txt')
      self.repository_updater.download_target(file1_target, self.client_directory)

    # Verify that the specific 'tuf.SlowRetrievalError' exception is raised by
    # each mirror.  'file1.txt' should be large enough to trigger a slow
    # retrieval attack, otherwise the expected exception may not be
    # consistently raised.
    except tuf.NoWorkingMirrorError as exception:
      for mirror_url, mirror_error in six.iteritems(exception.mirror_errors):
        url_prefix = self.repository_mirrors['mirror1']['url_prefix']
        url_file = os.path.join(url_prefix, 'targets', 'file1.txt')
       
        # Verify that 'file1.txt' is the culprit.
        self.assertEqual(url_file, mirror_url)
        self.assertTrue(isinstance(mirror_error, tuf.DownloadLengthMismatchError))
    
    else:
      # Another possibility is to check for a successfully downloaded
      # 'file1.txt' at this point.
      self.fail('TUF did not prevent a slow retrieval attack.')

    finally:
      self._stop_slow_server(server_process)
      tuf.conf.MIN_AVERAGE_DOWNLOAD_SPEED = original_average_download_speed 


if __name__ == '__main__':
  unittest.main()
