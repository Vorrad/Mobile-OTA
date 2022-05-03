#!/usr/bin/env python

"""
<Program Name>
  test_repository_tool.py

<Author> 
  Vladimir Diaz <vladimir.v.diaz@gmail.com>

<Started>
  April 7, 2014. 

<Copyright>
  See LICENSE for licensing information.

<Purpose>
  Unit test for 'repository_tool.py'.
"""

# Help with Python 3 compatibility, where the print statement is a function, an
# implicit relative import is invalid, and the '/' operator performs true
# division.  Example:  print 'hello world' raises a 'SyntaxError' exception.
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import os
import time
import datetime
import unittest
import logging
import tempfile
import shutil
import sys

# 'unittest2' required for testing under Python < 2.7.
if sys.version_info >= (2, 7):
  import unittest

else:
  import unittest2 as unittest 

import tuf
import tuf.log
import tuf.formats
import tuf.roledb
import tuf.keydb
import tuf.hash
import tuf.repository_tool as repo_tool

import six

logger = logging.getLogger('tuf.test_repository_tool')

repo_tool.disable_console_log_messages()


class TestRepository(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    
    # setUpClass() is called before tests in an individual class are executed.
    
    # Create a temporary directory to store the repository, metadata, and target
    # files.  'temporary_directory' must be deleted in TearDownClass() so that
    # temporary files are always removed, even when exceptions occur. 
    cls.temporary_directory = tempfile.mkdtemp(dir=os.getcwd())
    


  @classmethod 
  def tearDownClass(cls):
    
    # tearDownModule() is called after all the tests have run.
    # http://docs.python.org/2/library/unittest.html#class-and-module-fixtures
   
    # Remove the temporary repository directory, which should contain all the
    # metadata, targets, and key files generated for the test cases.
    shutil.rmtree(cls.temporary_directory)
  
  
  
  def setUp(self):
    pass



  def tearDown(self):
    tuf.roledb.clear_roledb() 
    tuf.keydb.clear_keydb()


  def test_init(self):
    
    # Test normal case.
    repository = repo_tool.Repository('repository_directory/',
                                      'metadata_directory/',
                                      'targets_directory/')
    self.assertTrue(isinstance(repository.root, repo_tool.Root))
    self.assertTrue(isinstance(repository.snapshot, repo_tool.Snapshot))
    self.assertTrue(isinstance(repository.timestamp, repo_tool.Timestamp))
    self.assertTrue(isinstance(repository.targets, repo_tool.Targets))

    # Test improperly formatted arguments.
    self.assertRaises(tuf.FormatError, repo_tool.Repository, 3,
                      'metadata_directory/', 'targets_directory')
    self.assertRaises(tuf.FormatError, repo_tool.Repository,
                      'repository_directory', 3, 'targets_directory')
    self.assertRaises(tuf.FormatError, repo_tool.Repository,
                      'repository_directory', 'metadata_directory', 3)

  

  def test_write_and_write_partial(self):
    # Test creation of a TUF repository.
    # 
    # 1. Import public and private keys.
    # 2. Add verification keys.
    # 3. Load signing keys.
    # 4. Add target files.
    # 5. Perform delegation.
    # 5. write()
    # 
    # Copy the target files from 'tuf/tests/repository_data' so that write()
    # has target fileinfo to include in metadata.
    temporary_directory = tempfile.mkdtemp(dir=self.temporary_directory)
    targets_directory = os.path.join(temporary_directory, 'repository',
                                     repo_tool.TARGETS_DIRECTORY_NAME)
    original_targets_directory = os.path.join('repository_data',
                                              'repository', 'targets')
    shutil.copytree(original_targets_directory, targets_directory)

    # In this case, create_new_repository() creates the 'repository/'
    # sub-directory in 'temporary_directory' if it does not exist.
    repository_directory = os.path.join(temporary_directory, 'repository')
    metadata_directory = os.path.join(repository_directory,
                                      repo_tool.METADATA_STAGED_DIRECTORY_NAME)
    repository = repo_tool.create_new_repository(repository_directory)

    
    # (1) Load the public and private keys of the top-level roles, and one
    # delegated role.
    keystore_directory = os.path.join('repository_data', 'keystore')
   
    # Load the public keys.
    root_pubkey_path = os.path.join(keystore_directory, 'root_key.pub')
    targets_pubkey_path = os.path.join(keystore_directory, 'targets_key.pub')
    snapshot_pubkey_path = os.path.join(keystore_directory, 'snapshot_key.pub')
    timestamp_pubkey_path = os.path.join(keystore_directory, 'timestamp_key.pub')
    role1_pubkey_path = os.path.join(keystore_directory, 'delegation_key.pub')
    
    root_pubkey = repo_tool.import_rsa_publickey_from_file(root_pubkey_path)
    targets_pubkey = \
      repo_tool.import_rsa_publickey_from_file(targets_pubkey_path)
    snapshot_pubkey = \
      repo_tool.import_rsa_publickey_from_file(snapshot_pubkey_path)
    timestamp_pubkey = \
      repo_tool.import_rsa_publickey_from_file(timestamp_pubkey_path)
    role1_pubkey = repo_tool.import_rsa_publickey_from_file(role1_pubkey_path)
    
    # Load the private keys.
    root_privkey_path = os.path.join(keystore_directory, 'root_key')
    targets_privkey_path = os.path.join(keystore_directory, 'targets_key')
    snapshot_privkey_path = os.path.join(keystore_directory, 'snapshot_key')
    timestamp_privkey_path = os.path.join(keystore_directory, 'timestamp_key')
    role1_privkey_path = os.path.join(keystore_directory, 'delegation_key')
    
    root_privkey = \
      repo_tool.import_rsa_privatekey_from_file(root_privkey_path, 'password')
    targets_privkey = \
      repo_tool.import_rsa_privatekey_from_file(targets_privkey_path,
                                                'password')
    snapshot_privkey = \
      repo_tool.import_rsa_privatekey_from_file(snapshot_privkey_path,
                                                'password')
    timestamp_privkey = \
      repo_tool.import_rsa_privatekey_from_file(timestamp_privkey_path,
                                                'password')
    role1_privkey = \
      repo_tool.import_rsa_privatekey_from_file(role1_privkey_path,
                                                'password')


    # (2) Add top-level verification keys.
    repository.root.add_verification_key(root_pubkey)
    repository.targets.add_verification_key(targets_pubkey)
    repository.snapshot.add_verification_key(snapshot_pubkey)

    # Verify that repository.write() fails for insufficient threshold
    # of signatures (default threshold = 1).
    self.assertRaises(tuf.UnsignedMetadataError, repository.write) 
    
    repository.timestamp.add_verification_key(timestamp_pubkey)
    
    
    # (3) Load top-level signing keys.
    repository.root.load_signing_key(root_privkey)
    repository.targets.load_signing_key(targets_privkey)
    repository.snapshot.load_signing_key(snapshot_privkey)
   
    # Verify that repository.write() fails for insufficient threshold
    # of signatures (default threshold = 1).
    self.assertRaises(tuf.UnsignedMetadataError, repository.write) 
    
    repository.timestamp.load_signing_key(timestamp_privkey)
   
    
    # (4) Add target files.
    target1 = os.path.join(targets_directory, 'file1.txt')
    target2 = os.path.join(targets_directory, 'file2.txt')
    target3 = os.path.join(targets_directory, 'file3.txt')
    repository.targets.add_target(target1)
    repository.targets.add_target(target2)

    # (5) Perform delegation.
    repository.targets.delegate('role1', [role1_pubkey], [target3]) 
    repository.targets('role1').load_signing_key(role1_privkey)
    
    # (6) Write repository.
    repository.targets.compressions = ['gz']
    repository.write()

    
    # Verify that the expected metadata is written.
    for role in ['root.json', 'targets.json', 'snapshot.json', 'timestamp.json']:
      role_filepath = os.path.join(metadata_directory, role)
      role_signable = tuf.util.load_json_file(role_filepath)
      
      # Raise 'tuf.FormatError' if 'role_signable' is an invalid signable.
      tuf.formats.check_signable_object_format(role_signable)

      if role == 'targets.json':
        compressed_filepath = role_filepath + '.gz'
        self.assertTrue(os.path.exists(compressed_filepath))
       
    # Verify the 'role1.json' delegation is also written.
    role1_filepath = os.path.join(metadata_directory, 'targets', 'role1.json')
    role1_signable = tuf.util.load_json_file(role1_filepath)
    tuf.formats.check_signable_object_format(role1_signable)

    # Verify that an exception is *not* raised for multiple repository.write().
    repository.write()

    # Verify the status() does not raise an exception.
    repository.status()
    
    # Verify status() does not raise 'tuf.InsufficientKeysError' if a top-level
    # role does and 'targets/role1' do not contain a threshold of keys.
    root_roleinfo = tuf.roledb.get_roleinfo('root')
    old_threshold = root_roleinfo['threshold']
    root_roleinfo['threshold'] = 10
    role1_roleinfo = tuf.roledb.get_roleinfo('targets/role1')
    old_role1_threshold = role1_roleinfo['threshold']
    role1_roleinfo['threshold'] = 10
    tuf.roledb.update_roleinfo('root', root_roleinfo)
    tuf.roledb.update_roleinfo('targets/role1', role1_roleinfo)
    repository.status()
   
    # Restore the original threshold values.
    root_roleinfo['threshold'] = old_threshold
    tuf.roledb.update_roleinfo('root', root_roleinfo)
    role1_roleinfo['threshold'] = old_role1_threshold
    tuf.roledb.update_roleinfo('targets/role1', role1_roleinfo)


    # Verify status() does not raise 'tuf.UnsignedMetadataError' if any of the
    # the top-level roles and 'targets/role1' are improperly signed.
    repository.root.unload_signing_key(root_privkey)
    repository.root.load_signing_key(targets_privkey)
    repository.targets('role1').unload_signing_key(role1_privkey)
    repository.targets('role1').load_signing_key(targets_privkey)
    repository.status()

    # Reset Root and 'targets/role1', and verify Targets.
    repository.root.unload_signing_key(targets_privkey)
    repository.root.load_signing_key(root_privkey)
    repository.targets('role1').unload_signing_key(targets_privkey)
    repository.targets('role1').load_signing_key(role1_privkey)
    repository.targets.unload_signing_key(targets_privkey)
    repository.targets.load_signing_key(snapshot_privkey)
    repository.status()

    # Reset Targets and verify Snapshot.
    repository.targets.unload_signing_key(snapshot_privkey)
    repository.targets.load_signing_key(targets_privkey)
    repository.snapshot.unload_signing_key(snapshot_privkey)
    repository.snapshot.load_signing_key(timestamp_privkey)
    repository.status()
   
    # Reset Snapshot and verify timestamp. 
    repository.snapshot.unload_signing_key(timestamp_privkey)
    repository.snapshot.load_signing_key(snapshot_privkey)
    repository.timestamp.unload_signing_key(timestamp_privkey)
    repository.timestamp.load_signing_key(root_privkey)
    repository.status()

    # Reset Timestamp
    repository.timestamp.unload_signing_key(root_privkey)
    repository.timestamp.load_signing_key(timestamp_privkey)

    # Verify that a write() fails if a repository is loaded and a change
    # is made to a role.
    repo_tool.load_repository(repository_directory)
    
    repository.timestamp.expiration = datetime.datetime(2030, 1, 1, 12, 0)
    self.assertRaises(tuf.UnsignedMetadataError, repository.write)

    # Verify that a write_partial() is allowed. 
    repository.write_partial()

    # Next, perform a non-partial write() with consistent snapshots enabled.
    # Since the timestamp was modified, load its private key.
    repository.timestamp.load_signing_key(timestamp_privkey)

    # Test creation of a consistent snapshot repository.  Writing a consistent
    # snapshot modifies the Root metadata, which specifies whether a repository
    # supports consistent snapshots.  Verify that an exception is raised due to
    # the missing signatures of Root and Snapshot.
    self.assertRaises(tuf.UnsignedMetadataError, repository.write,
                      False, True)
    
    # Load the private keys of Root and Snapshot (new version required since
    # Root has changed.)
    repository.root.load_signing_key(root_privkey)
    repository.snapshot.load_signing_key(snapshot_privkey)
   
    # Verify that consistent snapshot can be written and loaded. 
    repository.write(consistent_snapshot=True) 
    repo_tool.load_repository(repository_directory)

    # Test improperly formatted arguments.
    self.assertRaises(tuf.FormatError, repository.write, 3, False)
    self.assertRaises(tuf.FormatError, repository.write, False, 3)



  def test_get_filepaths_in_directory(self):
    # Test normal case.
    # Use the pre-generated metadata directory for testing.
    # Set 'repo' reference to improve readability.
    repo = repo_tool.Repository
    metadata_directory = os.path.join('repository_data',
                                      'repository', 'metadata')
    # Verify the expected filenames.  get_filepaths_in_directory() returns
    # a list of absolute paths.
    metadata_files = repo.get_filepaths_in_directory(metadata_directory) 
    expected_files = ['root.json', 'root.json.gz', 'targets.json',
                      'targets.json.gz', 'snapshot.json', 'snapshot.json.gz',
                      'timestamp.json', 'timestamp.json.gz']
    basenames = [] 
    for filepath in metadata_files:
      basenames.append(os.path.basename(filepath))
    self.assertEqual(sorted(expected_files), sorted(basenames))

    # Test improperly formatted arguments.
    self.assertRaises(tuf.FormatError, repo.get_filepaths_in_directory,
                      3, recursive_walk=False, followlinks=False)
    self.assertRaises(tuf.FormatError, repo.get_filepaths_in_directory,
                      metadata_directory, 3, followlinks=False)
    self.assertRaises(tuf.FormatError, repo.get_filepaths_in_directory,
                      metadata_directory, recursive_walk=False, followlinks=3)

    # Test invalid directory argument.
    # A non-directory.
    self.assertRaises(tuf.Error, repo.get_filepaths_in_directory,
                      os.path.join(metadata_directory, 'root.json'))
    temporary_directory = tempfile.mkdtemp(dir=self.temporary_directory)
    nonexistent_directory = os.path.join(temporary_directory, 'nonexistent/')
    self.assertRaises(tuf.Error, repo.get_filepaths_in_directory,
                      nonexistent_directory, recursive_walk=False,
                      followlinks=False)





class TestMetadata(unittest.TestCase):
  def setUp(self):
    # Inherit from the repo_tool.Metadata() base class.  All of the methods
    # to be tested in TestMetadata require at least 1 role, so create it here
    # and set its roleinfo.
    class MetadataRole(repo_tool.Metadata):
      
      def __init__(self):
        super(MetadataRole, self).__init__() 
        
        self._rolename = 'metadata_role'
        
        # Expire in 86400 seconds (1 day).
        expiration = \
          tuf.formats.unix_timestamp_to_datetime(int(time.time() + 86400))
        expiration = expiration.isoformat() + 'Z' 
        roleinfo = {'keyids': [], 'signing_keyids': [], 'threshold': 1, 
                    'signatures': [], 'version': 0,
                    'consistent_snapshot': False,
                    'compressions': [''], 'expires': expiration,
                    'partial_loaded': False}
        
        tuf.roledb.add_role(self._rolename, roleinfo)
    
    self.metadata = MetadataRole() 



  def tearDown(self):
    tuf.roledb.clear_roledb()
    tuf.keydb.clear_keydb()
    self.metadata = None 

  

  def test_rolename(self):
    base_metadata = repo_tool.Metadata()
    
    self.assertEqual(base_metadata.rolename, None)
    
    # Test the sub-classed MetadataRole().
    self.assertEqual(self.metadata.rolename, 'metadata_role')



  def test_version(self):
    # Test version getter, and the default version number.
    self.assertEqual(self.metadata.version, 0)

    # Test version setter, and verify updated version number.
    self.metadata.version = 8
    self.assertEqual(self.metadata.version, 8)



  def test_threshold(self):
    # Test threshold getter, and the default threshold number.
    self.assertEqual(self.metadata.threshold, 1)

    # Test threshold setter, and verify updated threshold number.
    self.metadata.threshold = 3
    self.assertEqual(self.metadata.threshold, 3)



  def test_expiration(self):
    # Test expiration getter.
    expiration = self.metadata.expiration
    self.assertTrue(isinstance(expiration, datetime.datetime))

    # Test expiration setter. 
    self.metadata.expiration = datetime.datetime(2030, 1, 1, 12, 0)
    expiration = self.metadata.expiration
    self.assertTrue(isinstance(expiration, datetime.datetime))

    # test a setter with microseconds, we are forcing the microseconds value 
    expiration = datetime.datetime.today() + datetime.timedelta(weeks = 1)
    # we force the microseconds value if we are unlucky enough to get a 0
    if expiration.microsecond == 0:
      expiration = expiration.replace(microsecond = 1)    

    new_expiration = self.metadata.expiration
    self.assertTrue(isinstance(new_expiration, datetime.datetime))

    # check that the expiration value is truncated
    self.assertTrue(new_expiration.microsecond == 0)

    # Test improperly formatted datetime.
    try: 
      self.metadata.expiration = '3' 
    
    except tuf.FormatError:
      pass
    
    else:
      self.fail('Setter failed to detect improperly formatted datetime.')


    # Test invalid argument (i.e., expiration has already expired.)
    expired_datetime = tuf.formats.unix_timestamp_to_datetime(int(time.time() - 1))
    try: 
      self.metadata.expiration = expired_datetime 
    
    except tuf.Error:
      pass
    
    else:
      self.fail('Setter failed to detect an expired datetime.')



  def test_keys(self):
    # Test default case, where a verification key has not been added. 
    self.assertEqual(self.metadata.keys, [])


    # Test keys() getter after a verification key has been loaded.
    key_path = os.path.join('repository_data',
                            'keystore', 'root_key.pub')
    key_object = repo_tool.import_rsa_publickey_from_file(key_path)
    self.metadata.add_verification_key(key_object)
    
    keyid = key_object['keyid']
    self.assertEqual([keyid], self.metadata.keys)



  def test_signing_keys(self):
    # Test default case, where a signing key has not been added. 
    self.assertEqual(self.metadata.signing_keys, [])


    # Test signing_keys() getter after a signing key has been loaded.
    key_path = os.path.join('repository_data',
                            'keystore', 'root_key')
    key_object = repo_tool.import_rsa_privatekey_from_file(key_path, 'password')
    self.metadata.load_signing_key(key_object)
    
    keyid = key_object['keyid']
    self.assertEqual([keyid], self.metadata.signing_keys)



  def test_compressions(self):
    # Test default case, where only uncompressed metadata is supported.
    self.assertEqual(self.metadata.compressions, [''])

    # Test compressions getter after a compressions algorithm is added.
    self.metadata.compressions = ['gz']

    self.assertEqual(self.metadata.compressions, ['', 'gz'])


    # Test improperly formatted argument.
    try:
      self.metadata.compressions = 3
    except tuf.FormatError:
      pass
    else:
      self.fail('Setter failed to detect improperly formatted compressions')



  def test_add_verification_key(self):
    # Add verification key and verify with keys() that it was added. 
    key_path = os.path.join('repository_data',
                            'keystore', 'root_key.pub')
    key_object = repo_tool.import_rsa_publickey_from_file(key_path)
    self.metadata.add_verification_key(key_object)
    
    keyid = key_object['keyid']
    self.assertEqual([keyid], self.metadata.keys)


    # Test improperly formatted key argument.
    self.assertRaises(tuf.FormatError, self.metadata.add_verification_key, 3)



  def test_remove_verification_key(self):
    # Add verification key so that remove_verifiation_key() can be tested.
    key_path = os.path.join('repository_data',
                            'keystore', 'root_key.pub')
    key_object = repo_tool.import_rsa_publickey_from_file(key_path)
    self.metadata.add_verification_key(key_object)
    
    keyid = key_object['keyid']
    self.assertEqual([keyid], self.metadata.keys)


    # Test successful removal of verification key added above.
    self.metadata.remove_verification_key(key_object)
    self.assertEqual(self.metadata.keys, [])
    

    # Test improperly formatted argument
    self.assertRaises(tuf.FormatError, self.metadata.remove_verification_key, 3)


    # Test non-existent public key argument.
    key_path = os.path.join('repository_data',
                            'keystore', 'targets_key.pub')
    unused_key_object = repo_tool.import_rsa_publickey_from_file(key_path)
    
    self.assertRaises(tuf.Error, self.metadata.remove_verification_key,
                      unused_key_object)



  def test_load_signing_key(self):
    # Test normal case. 
    key_path = os.path.join('repository_data',
                            'keystore', 'root_key')
    key_object = repo_tool.import_rsa_privatekey_from_file(key_path, 'password')
    self.metadata.load_signing_key(key_object)
    
    keyid = key_object['keyid']
    self.assertEqual([keyid], self.metadata.signing_keys)


    # Test improperly formatted arguments.
    self.assertRaises(tuf.FormatError, self.metadata.load_signing_key, 3)

    
    # Test non-private key.
    key_path = os.path.join('repository_data',
                            'keystore', 'root_key.pub')
    key_object = repo_tool.import_rsa_publickey_from_file(key_path)
    self.assertRaises(tuf.Error, self.metadata.load_signing_key, key_object)



  def test_unload_signing_key(self):
    # Load a signing key so that unload_signing_key() can have a key to unload.
    key_path = os.path.join('repository_data',
                            'keystore', 'root_key')
    key_object = repo_tool.import_rsa_privatekey_from_file(key_path, 'password')
    self.metadata.load_signing_key(key_object)
    
    keyid = key_object['keyid']
    self.assertEqual([keyid], self.metadata.signing_keys)

    self.metadata.unload_signing_key(key_object)

    self.assertEqual(self.metadata.signing_keys, [])


    # Test improperly formatted arguments.
    self.assertRaises(tuf.FormatError, self.metadata.unload_signing_key, 3)


    # Test non-existent key argument.
    key_path = os.path.join('repository_data',
                            'keystore', 'targets_key')
    unused_key_object = repo_tool.import_rsa_privatekey_from_file(key_path,
                                                                  'password')
    
    self.assertRaises(tuf.Error, self.metadata.unload_signing_key,
                      unused_key_object)



  def test_add_signature(self):
    # Test normal case.
    # Load signature list from any of pre-generated metadata; needed for
    # testing.
    metadata_directory = os.path.join('repository_data',
                                      'repository', 'metadata')
    root_filepath = os.path.join(metadata_directory, 'root.json')
    root_signable = tuf.util.load_json_file(root_filepath)
    signatures = root_signable['signatures']

    # Add the first signature from the list, as only need one is needed.
    self.metadata.add_signature(signatures[0])
    self.assertEqual(signatures, self.metadata.signatures)


    # Test improperly formatted signature argument.
    self.assertRaises(tuf.FormatError, self.metadata.add_signature, 3)



  def test_remove_signature(self):
    # Test normal case.
    # Add a signature so remove_signature() has some signature to remove.
    metadata_directory = os.path.join('repository_data',
                                      'repository', 'metadata')
    root_filepath = os.path.join(metadata_directory, 'root.json')
    root_signable = tuf.util.load_json_file(root_filepath)
    signatures = root_signable['signatures']
    self.metadata.add_signature(signatures[0])

    self.metadata.remove_signature(signatures[0])
    self.assertEqual(self.metadata.signatures, [])


    # Test improperly formatted signature argument.
    self.assertRaises(tuf.FormatError, self.metadata.remove_signature, 3)


    # Test invalid signature argument (i.e., signature that has not been added.)
    # Load an unused signature to be tested.
    targets_filepath = os.path.join(metadata_directory, 'targets.json')
    targets_signable = tuf.util.load_json_file(targets_filepath)
    signatures = targets_signable['signatures']
    
    self.assertRaises(tuf.Error, self.metadata.remove_signature, signatures[0])



  def test_signatures(self):
    # Test default case, where no signatures have been added yet.
    self.assertEqual(self.metadata.signatures, [])


    # Test getter after adding an example signature.
    metadata_directory = os.path.join('repository_data',
                                      'repository', 'metadata')
    root_filepath = os.path.join(metadata_directory, 'root.json')
    root_signable = tuf.util.load_json_file(root_filepath)
    signatures = root_signable['signatures']

    # Add the first signature from the list, as only need one is needed.
    self.metadata.add_signature(signatures[0])
    self.assertEqual(signatures, self.metadata.signatures)



class TestRoot(unittest.TestCase):
  def setUp(self):
    pass



  def tearDown(self):
    tuf.roledb.clear_roledb() 
    tuf.keydb.clear_keydb()


  
  def test_init(self):
    
    # Test normal case.
    # Root() subclasses Metadata(), and creates a 'root' role in 'tuf.roledb'.
    root_object = repo_tool.Root()
    self.assertTrue(isinstance(root_object, repo_tool.Metadata))
    self.assertTrue(tuf.roledb.role_exists('root'))



class TestTimestamp(unittest.TestCase):
  def setUp(self):
    pass



  def tearDown(self):
    tuf.roledb.clear_roledb() 
    tuf.keydb.clear_keydb()
  
  
  
  def test_init(self):
    
    # Test normal case.
    # Timestamp() subclasses Metadata(), and creates a 'timestamp' role in
    # 'tuf.roledb'.
    timestamp_object = repo_tool.Timestamp()
    self.assertTrue(isinstance(timestamp_object, repo_tool.Metadata))
    self.assertTrue(tuf.roledb.role_exists('timestamp'))





class TestSnapshot(unittest.TestCase):
  def setUp(self):
    pass



  def tearDown(self):
    tuf.roledb.clear_roledb() 
    tuf.keydb.clear_keydb()
  
  
  
  def test_init(self):
    
    # Test normal case.
    # Snapshot() subclasses Metadata(), and creates a 'snapshot' role in
    # 'tuf.roledb'.
    snapshot_object = repo_tool.Snapshot()
    self.assertTrue(isinstance(snapshot_object, repo_tool.Metadata))
    self.assertTrue(tuf.roledb.role_exists('snapshot'))





class TestTargets(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    
    # setUpClass() is called before tests in an individual class are executed.
    
    # Create a temporary directory to store the repository, metadata, and target
    # files.  'temporary_directory' must be deleted in TearDownClass() so that
    # temporary files are always removed, even when exceptions occur. 
    cls.temporary_directory = tempfile.mkdtemp(dir=os.getcwd())
    


  @classmethod 
  def tearDownClass(cls):
    
    # tearDownModule() is called after all the tests have run.
    # http://docs.python.org/2/library/unittest.html#class-and-module-fixtures
   
    # Remove the temporary repository directory, which should contain all the
    # metadata, targets, and key files generated for the test cases.
    shutil.rmtree(cls.temporary_directory)
 


  def setUp(self):
    temporary_directory = tempfile.mkdtemp(dir=self.temporary_directory)
    self.targets_directory = os.path.join(temporary_directory, 'repository',
                                          'targets')
    original_targets_directory = os.path.join('repository_data',
                                              'repository', 'targets')
    shutil.copytree(original_targets_directory, self.targets_directory)
    self.targets_object = repo_tool.Targets(self.targets_directory)



  def tearDown(self):
    tuf.roledb.clear_roledb() 
    tuf.keydb.clear_keydb()
    self.targets_object = None
  
  
  
  def test_init(self):
    
    # Test normal case.
    # Snapshot() subclasses Metadata(), and creates a 'snapshot' role in
    # 'tuf.roledb'.
    targets_object = repo_tool.Targets('targets_directory/')
    self.assertTrue(isinstance(targets_object, repo_tool.Metadata))
    self.assertTrue(tuf.roledb.role_exists('targets'))

    # Custom Targets object rolename.
    targets_object = repo_tool.Targets('targets_directory/', 'project') 
    self.assertTrue(isinstance(targets_object, repo_tool.Metadata))
    self.assertTrue(tuf.roledb.role_exists('project'))

    # Custom roleinfo object (i.e., tuf.formats.ROLEDB_SCHEMA).  'keyids' and
    # 'threshold' are required, the rest are optional.
    roleinfo = {'keyids': 
          ['66c4cb5fef5e4d62b7013ef1cab4b8a827a36c14056d5603c3a970e21eb30e6f'],
                'threshold': 8}
    self.assertTrue(tuf.formats.ROLEDB_SCHEMA.matches(roleinfo))
    
    targets_object = repo_tool.Targets('targets_directory/', 'package', roleinfo)
    self.assertTrue(isinstance(targets_object, repo_tool.Metadata))
    self.assertTrue(tuf.roledb.role_exists('package'))


    # Test improperly formatted arguments.
    self.assertRaises(tuf.FormatError, repo_tool.Targets, 3)
    self.assertRaises(tuf.FormatError, repo_tool.Targets, 'targets_directory/', 3)
    self.assertRaises(tuf.FormatError, repo_tool.Targets, 'targets_directory/',
                      'targets', 3)
  


  def test_call(self):
    # Test normal case.
    # Perform a delegation so that a delegated role can be accessed and tested
    # through __call__().  Example: {targets_object}('role1').
    keystore_directory = os.path.join('repository_data', 'keystore')
    public_keypath = os.path.join(keystore_directory, 'root_key.pub')
    public_key = repo_tool.import_rsa_publickey_from_file(public_keypath)
    target1_filepath = os.path.join(self.targets_directory, 'file1.txt')
   
    # Create Targets() object to be tested.
    targets_object = repo_tool.Targets(self.targets_directory)
    targets_object.delegate('role1', [public_key], [target1_filepath])

    self.assertTrue(isinstance(targets_object('role1'), repo_tool.Targets))
   
    # Test invalid (i.e., non-delegated) rolename argument.
    self.assertRaises(tuf.UnknownRoleError, targets_object, 'unknown_role')

    # Test improperly formatted argument.
    self.assertRaises(tuf.FormatError, targets_object, 1)



  def test_get_delegated_rolenames(self):
    # Test normal case.
    # Perform two delegations so that get_delegated_rolenames() has roles to 
    # return.
    keystore_directory = os.path.join('repository_data', 'keystore')
    public_keypath = os.path.join(keystore_directory, 'root_key.pub')
    public_key = repo_tool.import_rsa_publickey_from_file(public_keypath)
    target1_filepath = os.path.join(self.targets_directory, 'file1.txt')
    target2_filepath = os.path.join(self.targets_directory, 'file2.txt')

    # Set needed arguments by delegate().
    public_keys = [public_key]
    threshold = 1

    self.targets_object.delegate('tuf', public_keys, [target1_filepath],
                                 threshold, restricted_paths=None,
                                 path_hash_prefixes=None)
    self.targets_object.delegate('warehouse', public_keys, [target2_filepath],
                                 threshold, restricted_paths=None,
                                 path_hash_prefixes=None)

    # Test that get_delegated_rolenames returns the expected delegations.
    expected_delegated_rolenames = ['targets/tuf/', 'targets/warehouse']
    for delegated_rolename in self.targets_object.get_delegated_rolenames():
      delegated_rolename in expected_delegated_rolenames  



  def test_target_files(self):
    # Test normal case.
    # Verify the targets object initially contains zero target files.
    self.assertEqual(self.targets_object.target_files, {})

    target_filepath = os.path.join(self.targets_directory, 'file1.txt')
    self.targets_object.add_target(target_filepath)

    self.assertEqual(len(self.targets_object.target_files), 1)
    self.assertTrue('/file1.txt' in self.targets_object.target_files)



  def test_delegations(self):
    # Test normal case.
    # Perform a delegation so that delegations() has a Targets() object to
    # return.
    keystore_directory = os.path.join('repository_data', 'keystore')
    public_keypath = os.path.join(keystore_directory, 'root_key.pub')
    public_key = repo_tool.import_rsa_publickey_from_file(public_keypath)
    target1_filepath = os.path.join(self.targets_directory, 'file1.txt')

    # Set needed arguments by delegate().
    public_keys = [public_key]
    rolename = 'tuf'
    list_of_targets = [target1_filepath] 
    threshold = 1

    self.targets_object.delegate(rolename, public_keys, list_of_targets,
                                 threshold, backtrack=True,
                                 restricted_paths=None,
                                 path_hash_prefixes=None)

    # Test that a valid Targets() object is returned by delegations().
    for delegated_object in self.targets_object.delegations:
      self.assertTrue(isinstance(delegated_object, repo_tool.Targets))



  def test_add_target(self):
    # Test normal case.
    # Verify the targets object initially contains zero target files.
    self.assertEqual(self.targets_object.target_files, {})

    target_filepath = os.path.join(self.targets_directory, 'file1.txt')
    self.targets_object.add_target(target_filepath)

    self.assertEqual(len(self.targets_object.target_files), 1)
    self.assertTrue('/file1.txt' in self.targets_object.target_files)
   
    # Test the 'custom' parameter of add_target(), where additional information
    # may be specified for the target.
    target2_filepath = os.path.join(self.targets_directory, 'file2.txt')

    # The file permission of the target (octal number specifying file access
    # for owner, group, others (e.g., 0755).
    octal_file_permissions = oct(os.stat(target2_filepath).st_mode)[4:]
    custom_file_permissions = {'file_permissions': octal_file_permissions}
    self.targets_object.add_target(target2_filepath, custom_file_permissions) 

    self.assertEqual(len(self.targets_object.target_files), 2)
    self.assertTrue('/file2.txt' in self.targets_object.target_files)
    self.assertEqual(self.targets_object.target_files['/file2.txt'],
                     custom_file_permissions)

    # Test improperly formatted arguments.
    self.assertRaises(tuf.FormatError, self.targets_object.add_target, 3)
    self.assertRaises(tuf.FormatError, self.targets_object.add_target, 3,
                      custom_file_permissions)
    self.assertRaises(tuf.FormatError, self.targets_object.add_target,
                      target_filepath, 3)


    # Test invalid filepath argument (i.e., non-existent or invalid file.)
    self.assertRaises(tuf.Error, self.targets_object.add_target,
                      'non-existent.txt')

    # Not under the repository's targets directory. 
    self.assertRaises(tuf.Error, self.targets_object.add_target,
                      self.temporary_directory)
    
    # Not a file (i.e., a valid path, but a directory.)
    test_directory = os.path.join(self.targets_directory, 'test_directory')
    os.mkdir(test_directory)
    self.assertRaises(tuf.Error, self.targets_object.add_target, test_directory)



  def test_add_targets(self):
    # Test normal case.
    # Verify the targets object initially contains zero target files.
    self.assertEqual(self.targets_object.target_files, {})

    target1_filepath = os.path.join(self.targets_directory, 'file1.txt')
    target2_filepath = os.path.join(self.targets_directory, 'file2.txt')
    target3_filepath = os.path.join(self.targets_directory, 'file3.txt')
   
    # Add a 'target1_filepath' duplicate for testing purposes
    # ('target1_filepath' should not be added twice.)
    target_files = \
      [target1_filepath, target2_filepath, target3_filepath, target1_filepath]
    self.targets_object.add_targets(target_files)
    
    self.assertEqual(len(self.targets_object.target_files), 3)
    self.assertEqual(self.targets_object.target_files, 
                     {'/file1.txt': {}, '/file2.txt': {}, '/file3.txt': {}})


    # Test improperly formatted arguments.
    self.assertRaises(tuf.FormatError, self.targets_object.add_targets, 3)

    # Test invalid filepath argument (i.e., non-existent or invalid file.)
    self.assertRaises(tuf.Error, self.targets_object.add_targets,
                      ['non-existent.txt'])
    self.assertRaises(tuf.Error, self.targets_object.add_targets,
                      [target1_filepath, target2_filepath, 'non-existent.txt'])
    self.assertRaises(tuf.Error, self.targets_object.add_targets,
                      [self.temporary_directory])
    temp_directory = os.path.join(self.targets_directory, 'temp')
    os.mkdir(temp_directory)
    self.assertRaises(tuf.Error, self.targets_object.add_targets,
                      [temp_directory])



  def test_remove_target(self):
    # Test normal case.
    # Verify the targets object initially contains zero target files.
    self.assertEqual(self.targets_object.target_files, {})

    # Add a target so that remove_target() has something to remove.
    target_filepath = os.path.join(self.targets_directory, 'file1.txt')
    self.targets_object.add_target(target_filepath)

    # Test remove_target()'s behavior.
    self.targets_object.remove_target(target_filepath)
    self.assertEqual(self.targets_object.target_files, {})


    # Test improperly formatted arguments.
    self.assertRaises(tuf.FormatError, self.targets_object.remove_target, 3)


    # Test invalid filepath argument (i.e., non-existent or invalid file.)
    self.assertRaises(tuf.Error, self.targets_object.remove_target,
                      '/non-existent.txt')
    # Test for filepath that hasn't been added yet.
    target5_filepath = os.path.join(self.targets_directory, 'file5.txt')
    self.assertRaises(tuf.Error, self.targets_object.remove_target,
                      target5_filepath)



  def test_clear_targets(self):
    # Test normal case.
    # Verify the targets object initially contains zero target files.
    self.assertEqual(self.targets_object.target_files, {})

    # Add targets, to be tested by clear_targets().
    target1_filepath = os.path.join(self.targets_directory, 'file1.txt')
    target2_filepath = os.path.join(self.targets_directory, 'file2.txt')
    self.targets_object.add_targets([target1_filepath, target2_filepath])

    self.targets_object.clear_targets()
    self.assertEqual(self.targets_object.target_files, {})



  def test_delegate(self):
    # Test normal case.
    # Need at least one public key and valid target paths required by
    # delegate().
    keystore_directory = os.path.join('repository_data', 'keystore')
    public_keypath = os.path.join(keystore_directory, 'root_key.pub')
    public_key = repo_tool.import_rsa_publickey_from_file(public_keypath)
    target1_filepath = os.path.join(self.targets_directory, 'file1.txt')
    target2_filepath = os.path.join(self.targets_directory, 'file2.txt')
  

    # Set needed arguments by delegate().
    public_keys = [public_key]
    rolename = 'tuf'
    list_of_targets = [target1_filepath, target2_filepath] 
    threshold = 1
    restricted_paths = [self.targets_directory]
    path_hash_prefixes = ['e3a3', '8fae', 'd543']

    self.targets_object.delegate(rolename, public_keys, list_of_targets,
                                 threshold, backtrack=True,
                                 restricted_paths=restricted_paths,
                                 path_hash_prefixes=path_hash_prefixes)

    self.assertEqual(self.targets_object.get_delegated_rolenames(),
                     ['targets/tuf'])
    
    # Try to delegate to a role that has already been delegated.
    self.assertRaises(tuf.Error, self.targets_object.delegate, rolename,
                      public_keys, list_of_targets, threshold, backtrack=True,
                      restricted_paths=restricted_paths,
                      path_hash_prefixes=path_hash_prefixes)

    # Test for targets that do not exist under the targets directory.
    self.targets_object.revoke(rolename)
    self.assertRaises(tuf.Error, self.targets_object.delegate, rolename,
                      public_keys, ['non-existent.txt'], threshold,
                      backtrack=True, restricted_paths=restricted_paths,
                      path_hash_prefixes=path_hash_prefixes)
    
    # Test for targets that do not exist under the targets directory.
    self.assertRaises(tuf.Error, self.targets_object.delegate, rolename,
                      public_keys, list_of_targets, threshold,
                      backtrack=True, restricted_paths=['non-existent.txt'],
                      path_hash_prefixes=path_hash_prefixes)


    # Test improperly formatted arguments.
    self.assertRaises(tuf.FormatError, self.targets_object.delegate,
                      3, public_keys, list_of_targets, threshold,
                      restricted_paths, path_hash_prefixes)
    self.assertRaises(tuf.FormatError, self.targets_object.delegate,
                      rolename, 3, list_of_targets, threshold,
                      restricted_paths, path_hash_prefixes)
    self.assertRaises(tuf.FormatError, self.targets_object.delegate,
                      rolename, public_keys, 3, threshold,
                      restricted_paths, path_hash_prefixes)
    self.assertRaises(tuf.FormatError, self.targets_object.delegate,
                      rolename, public_keys, list_of_targets, '3',
                      restricted_paths, path_hash_prefixes)
    self.assertRaises(tuf.FormatError, self.targets_object.delegate,
                      rolename, public_keys, list_of_targets, threshold,
                      3, path_hash_prefixes)
    self.assertRaises(tuf.FormatError, self.targets_object.delegate,
                      rolename, public_keys, list_of_targets, threshold,
                      restricted_paths, 3)


    # Test invalid arguments (e.g., already delegated 'rolename', non-existent
    # files, etc.).
    # Test duplicate 'rolename' delegation, which should have been delegated
    # in the normal case above.
    self.assertRaises(tuf.Error, self.targets_object.delegate,
                      rolename, public_keys, list_of_targets, threshold,
                      restricted_paths, path_hash_prefixes)
    
    # Test non-existent target paths.
    self.assertRaises(tuf.Error, self.targets_object.delegate,
                      rolename, public_keys, ['/non-existent'], threshold,
                      restricted_paths, path_hash_prefixes)



  def test_delegate_hashed_bins(self):
    # Test normal case.
    keystore_directory = os.path.join('repository_data', 'keystore')
    public_keypath = os.path.join(keystore_directory, 'root_key.pub')
    public_key = repo_tool.import_rsa_publickey_from_file(public_keypath)
    target1_filepath = os.path.join(self.targets_directory, 'file1.txt')

    # Set needed arguments by delegate_hashed_bins().
    public_keys = [public_key]
    list_of_targets = [target1_filepath] 

    # Test delegate_hashed_bins() and verify that 16 hashed bins have
    # been delegated in the parent's roleinfo.
    self.targets_object.delegate_hashed_bins(list_of_targets, public_keys,
                                             number_of_bins=16)

    # The expected child rolenames, since 'number_of_bins' = 16 
    delegated_rolenames = ['0', '1', '2', '3', '4', '5', '6', '7',
                           '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']

    # Prepend the parent's rolename.
    expected_delegated_rolenames = []
    for rolename in delegated_rolenames:
      rolename = self.targets_object.rolename + '/' + rolename
      expected_delegated_rolenames.append(rolename)

    self.assertEqual(sorted(self.targets_object.get_delegated_rolenames()),
                     sorted(expected_delegated_rolenames))


    # Test improperly formatted arguments.
    self.assertRaises(tuf.FormatError,
                      self.targets_object.delegate_hashed_bins, 3, public_keys,
                      number_of_bins=1)
    self.assertRaises(tuf.FormatError,
                      self.targets_object.delegate_hashed_bins,
                      list_of_targets, 3, number_of_bins=1)
    self.assertRaises(tuf.FormatError,
                      self.targets_object.delegate_hashed_bins,
                      list_of_targets, public_keys, '1')


    # Test invalid arguments.
    # Invalid number of bins, which must be a power of 2.
    self.assertRaises(tuf.Error,
                      self.targets_object.delegate_hashed_bins,
                      list_of_targets, public_keys, number_of_bins=3)
    
    # Invalid 'list_of_targets'.
    self.assertRaises(tuf.Error,
                      self.targets_object.delegate_hashed_bins,
                      ['/non-existent'], public_keys, number_of_bins=3)



  def test_add_target_to_bin(self):
    # Test normal case.
    # Delegate the hashed bins so that add_target_to_bin() can be tested.
    keystore_directory = os.path.join('repository_data', 'keystore')
    public_keypath = os.path.join(keystore_directory, 'targets_key.pub')
    public_key = repo_tool.import_rsa_publickey_from_file(public_keypath)
    target1_filepath = os.path.join(self.targets_directory, 'file1.txt')

    # Set needed arguments by delegate_hashed_bins().
    public_keys = [public_key]
    list_of_targets = [target1_filepath] 

    # Delegate to hashed bins.  The target filepath to be tested is expected 
    # to contain a hash prefix of 'e', so it should be added to the
    # 'targets/e' role.
    self.targets_object.delegate_hashed_bins(list_of_targets, public_keys,
                                             number_of_bins=16)
 
    # Ensure each hashed bin initially contains zero targets.
    for delegation in self.targets_object.delegations:
      self.assertTrue(target1_filepath not in delegation.target_files)

    # Add 'target1_filepath' and verify that the relative path of
    # 'target1_filepath' is added to the correct bin.
    self.targets_object.add_target_to_bin(target1_filepath)
    for delegation in self.targets_object.delegations:
      if delegation.rolename == 'targets/e':
        self.assertTrue('/file1.txt' in delegation.target_files)
      
      else:
        self.assertFalse('/file1.txt' in delegation.target_files)
          
    # Test for non-existent delegations and hashed bins.
    empty_targets_role = repo_tool.Targets(self.targets_directory, 'empty')
    
    self.assertRaises(tuf.Error, empty_targets_role.add_target_to_bin,
                      target1_filepath)
    
    # Non-bin delegation, although it has a correct hashed bin name.
    empty_targets_role.delegate('e', [public_key], [target1_filepath])
    self.assertRaises(tuf.Error, empty_targets_role.add_target_to_bin,
                      target1_filepath)

    # Test for a required hashed bin that does not exist.
    self.targets_object.revoke('e')
    self.assertRaises(tuf.Error, self.targets_object.add_target_to_bin,
                      target1_filepath)

    # Test improperly formatted argument.
    self.assertRaises(tuf.FormatError,
                      self.targets_object.add_target_to_bin, 3)

    # Invalid target file path argument.
    self.assertRaises(tuf.Error,
                      self.targets_object.add_target_to_bin, '/non-existent')
  
  
  
  def test_remove_target_from_bin(self):
    # Test normal case.
    # Delegate the hashed bins so that add_target_to_bin() can be tested.
    keystore_directory = os.path.join('repository_data', 'keystore')
    public_keypath = os.path.join(keystore_directory, 'targets_key.pub')
    public_key = repo_tool.import_rsa_publickey_from_file(public_keypath)
    target1_filepath = os.path.join(self.targets_directory, 'file1.txt')

    # Set needed arguments by delegate_hashed_bins().
    public_keys = [public_key]
    list_of_targets = [target1_filepath] 

    # Delegate to hashed bins.  The target filepath to be tested is expected 
    # to contain a hash prefix of 'e', so it should be added to the
    # 'targets/e' role.
    self.targets_object.delegate_hashed_bins(list_of_targets, public_keys,
                                             number_of_bins=16)
 
    # Ensure each hashed bin initially contains zero targets.
    for delegation in self.targets_object.delegations:
      self.assertTrue(target1_filepath not in delegation.target_files)

    # Add 'target1_filepath' and verify that the relative path of
    # 'target1_filepath' is added to the correct bin.
    self.targets_object.add_target_to_bin(target1_filepath)
    
    for delegation in self.targets_object.delegations:
      if delegation.rolename == 'targets/e':
        self.assertTrue('/file1.txt' in delegation.target_files)
      
      else:
        self.assertTrue('/file1.txt' not in delegation.target_files)

    # Test the remove_target_from_bin() method.  Verify that 'target1_filepath'
    # has been removed.
    self.targets_object.remove_target_from_bin(target1_filepath)
    
    for delegation in self.targets_object.delegations:
      if delegation.rolename == 'targets/e':
        self.assertTrue('/file1.txt' not in delegation.target_files)
      
      else:
        self.assertTrue('/file1.txt' not in delegation.target_files)


    # Test improperly formatted argument.
    self.assertRaises(tuf.FormatError,
                      self.targets_object.remove_target_from_bin, 3)

    # Invalid target file path argument.
    self.assertRaises(tuf.Error, self.targets_object.remove_target_from_bin,
                      '/non-existent')
    
    

  def test_add_restricted_paths(self):
    # Test normal case.
    # Perform a delegation so that add_restricted_paths() has a child role
    # to restrict.
    keystore_directory = os.path.join('repository_data', 'keystore')
    public_keypath = os.path.join(keystore_directory, 'root_key.pub')
    public_key = repo_tool.import_rsa_publickey_from_file(public_keypath)

    # Set needed arguments by delegate().
    public_keys = [public_key]
    rolename = 'tuf'
    threshold = 1

    self.targets_object.delegate(rolename, public_keys, [],
                                 threshold, restricted_paths=None,
                                 path_hash_prefixes=None)

    # Delegate an extra role for test coverage (i.e., check that restricted
    # paths are not added to a child role not requested.)
    self.targets_object.delegate('junk_role', public_keys, [])

    restricted_path = os.path.join(self.targets_directory, 'tuf_files')
    os.mkdir(restricted_path)
    restricted_paths = [restricted_path]
    self.targets_object.add_restricted_paths(restricted_paths, 'tuf')
    
    # Retrieve 'targets_object' roleinfo, and verify the roleinfo contains
    # the expected restricted paths of the delegated role.  Only
    # Repository.write() verifies that child target paths are allowed by the
    # parent.
    targets_object_roleinfo = tuf.roledb.get_roleinfo(self.targets_object.rolename)

    delegated_role = targets_object_roleinfo['delegations']['roles'][0]
    self.assertEqual(['/tuf_files/'], delegated_role['paths'])


    # Test improperly formatted arguments.
    self.assertRaises(tuf.FormatError, self.targets_object.add_restricted_paths,
                      3, 'tuf')
    self.assertRaises(tuf.FormatError, self.targets_object.add_restricted_paths,
                      restricted_paths, 3)


    # Test invalid arguments.
    # A non-delegated child role.
    self.assertRaises(tuf.Error, self.targets_object.add_restricted_paths,
                      restricted_paths, 'non_delegated_rolename')
    
    # Non-existent 'restricted_paths'.
    self.assertRaises(tuf.Error, self.targets_object.add_restricted_paths,
                      ['/non-existent'], 'tuf')
    
    # Directory not under the repository's targets directory.
    repository_directory = os.path.join('repository_data', 'repository')
    self.assertRaises(tuf.Error, self.targets_object.add_restricted_paths,
                      [repository_directory], 'tuf')



  def test_revoke(self):
    # Test normal case.
    # Perform a delegation so that revoke() has a delegation to revoke.
    keystore_directory = os.path.join('repository_data', 'keystore')
    public_keypath = os.path.join(keystore_directory, 'root_key.pub')
    public_key = repo_tool.import_rsa_publickey_from_file(public_keypath)
    target1_filepath = os.path.join(self.targets_directory, 'file1.txt')

    # Set needed arguments by delegate().
    public_keys = [public_key]
    rolename = 'tuf'
    list_of_targets = [target1_filepath] 
    threshold = 1

    self.targets_object.delegate(rolename, public_keys, list_of_targets,
                                 threshold, restricted_paths=None,
                                 path_hash_prefixes=None)

    # Test revoke()
    self.targets_object.revoke('tuf')
    self.assertEqual(self.targets_object.get_delegated_rolenames(), [])


    # Test improperly formatted rolename argument.
    self.assertRaises(tuf.FormatError, self.targets_object.revoke, 3)





class TestRepositoryToolFunctions(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    
    # setUpClass() is called before tests in an individual class are executed.
    
    # Create a temporary directory to store the repository, metadata, and target
    # files.  'temporary_directory' must be deleted in TearDownClass() so that
    # temporary files are always removed, even when exceptions occur. 
    cls.temporary_directory = tempfile.mkdtemp(dir=os.getcwd())
    


  @classmethod 
  def tearDownClass(cls):
    
    # tearDownModule() is called after all the tests have run.
    # http://docs.python.org/2/library/unittest.html#class-and-module-fixtures
   
    # Remove the temporary repository directory, which should contain all the
    # metadata, targets, and key files generated for the test cases.
    shutil.rmtree(cls.temporary_directory)



  def setUp(self):
    pass


  def tearDown(self):
    pass



  def test_create_new_repository(self):
    # Test normal case.
    # Setup the temporary repository directories needed by
    # create_new_repository().
    temporary_directory = tempfile.mkdtemp(dir=self.temporary_directory) 
    repository_directory = os.path.join(temporary_directory, 'repository')
    metadata_directory = os.path.join(repository_directory,
                                      repo_tool.METADATA_STAGED_DIRECTORY_NAME)
    targets_directory = os.path.join(repository_directory,
                                     repo_tool.TARGETS_DIRECTORY_NAME)
    
    repository = repo_tool.create_new_repository(repository_directory)
    self.assertTrue(isinstance(repository, repo_tool.Repository))
    
    # Verify that the 'repository/', 'repository/metadata', and
    # 'repository/targets' directories were created.
    self.assertTrue(os.path.exists(repository_directory))
    self.assertTrue(os.path.exists(metadata_directory))
    self.assertTrue(os.path.exists(targets_directory))


    # Test that the 'repository' directory is created (along with the other
    # sub-directories) when it does not exist yet.  The repository tool creates
    # the non-existent directory.
    shutil.rmtree(repository_directory)

    repository = repo_tool.create_new_repository(repository_directory)
    repository = repo_tool.create_new_repository(repository_directory)
    self.assertTrue(isinstance(repository, repo_tool.Repository))
    
    # Verify that the 'repository/', 'repository/metadata', and
    # 'repository/targets' directories were created.
    self.assertTrue(os.path.exists(repository_directory))
    self.assertTrue(os.path.exists(metadata_directory))
    self.assertTrue(os.path.exists(targets_directory))
     

    # Test improperly formatted arguments.
    self.assertRaises(tuf.FormatError, repo_tool.create_new_repository, 3)



  def test_load_repository(self):
    # Test normal case.
    temporary_directory = tempfile.mkdtemp(dir=self.temporary_directory) 
    original_repository_directory = os.path.join('repository_data',
                                                 'repository')
    repository_directory = os.path.join(temporary_directory, 'repository')
    shutil.copytree(original_repository_directory, repository_directory)
     
    repository = repo_tool.load_repository(repository_directory)
    self.assertTrue(isinstance(repository, repo_tool.Repository))

    # Verify the expected roles have been loaded.  See
    # 'tuf/tests/repository_data/repository/'.
    expected_roles = \
      ['root', 'targets', 'snapshot', 'timestamp', 'targets/role1']
    for role in tuf.roledb.get_rolenames():
      self.assertTrue(role in expected_roles)
    
    self.assertTrue(len(repository.root.keys))
    self.assertTrue(len(repository.targets.keys))
    self.assertTrue(len(repository.snapshot.keys))
    self.assertTrue(len(repository.timestamp.keys))
    self.assertTrue(len(repository.targets('role1').keys))

    # Assumed the targets (tuf/tests/repository_data/) role contains 'file1.txt'
    # and 'file2.txt'.
    self.assertTrue('/file1.txt' in repository.targets.target_files)
    self.assertTrue('/file2.txt' in repository.targets.target_files)
    self.assertTrue('/file3.txt' in repository.targets('role1').target_files)
    
    # Test improperly formatted arguments.
    self.assertRaises(tuf.FormatError, repo_tool.load_repository, 3)


    # Test for invalid 'repository_directory' (i.e., does not contain the
    # minimum required metadata.
    root_filepath = \
      os.path.join(repository_directory,
                   repo_tool.METADATA_STAGED_DIRECTORY_NAME, 'root.json') 
    os.remove(root_filepath)
    self.assertRaises(tuf.RepositoryError, repo_tool.load_repository,
                      repository_directory)



# Run the test cases.
if __name__ == '__main__':
  unittest.main()
