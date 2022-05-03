#!/usr/bin/env python

"""
<Program Name>
  generate.py

<Author>
  Vladimir Diaz <vladimir.v.diaz@gmail.com>

<Started>
  February 26, 2014.

<Copyright>
  See LICENSE for licensing information.

<Purpose>
  Provide a set of pre-generated key files and a basic repository that unit
  tests can use in their test cases.  The pre-generated files created by this
  script should be copied by the unit tests as needed.  The original versions
  should be preserved.  'tuf/tests/unit/repository_files/' will store the files
  generated.  'generate.py' should not require re-execution if the pre-generated
  repository files have already been created, unless they need to change in some
  way.
"""

import shutil
import datetime
import optparse
import stat

from tuf.repository_tool import *
import tuf.util


parser = optparse.OptionParser()
parser.add_option("-k","--keys", action='store_true',  dest="should_generate_keys",
    help="Generate a new set of keys", default=False)
parser.add_option("-d","--dry-run", action='store_true', dest="dry_run",
    help="Do not write the files, just run", default=False)
(options, args) = parser.parse_args()


repository = create_new_repository('repository')

root_key_file = 'keystore/root_key'
targets_key_file = 'keystore/targets_key' 
snapshot_key_file = 'keystore/snapshot_key'
timestamp_key_file = 'keystore/timestamp_key'
delegation_key_file = 'keystore/delegation_key'


if options.should_generate_keys and not options.dry_run:
  # Generate and save the top-level role keys, including the delegated roles.
  # The unit tests should only have to import the keys they need from these
  # pre-generated key files.
  # Generate public and private key files for the top-level roles, and two
  # delegated roles (these number of keys should be sufficient for most of the
  # unit tests).  Unit tests may generate additional keys, if needed.
  generate_and_write_rsa_keypair(root_key_file, bits=2048, password='password')
  generate_and_write_rsa_keypair(targets_key_file, bits=2048,
      password='password')
  generate_and_write_rsa_keypair(snapshot_key_file, bits=2048,
      password='password')
  generate_and_write_rsa_keypair(timestamp_key_file, bits=2048,
      password='password')
  generate_and_write_rsa_keypair(delegation_key_file, bits=2048,
      password='password')

# Import the public keys.  These keys are needed so that metadata roles are
# assigned verification keys, which clients use to verify the signatures created
# by the corresponding private keys.
root_public = import_rsa_publickey_from_file(root_key_file+'.pub')
targets_public = import_rsa_publickey_from_file(targets_key_file+'.pub')
snapshot_public = import_rsa_publickey_from_file(snapshot_key_file+'.pub')
timestamp_public = import_rsa_publickey_from_file(timestamp_key_file+'.pub')
delegation_public = import_rsa_publickey_from_file(delegation_key_file+'.pub')

# Import the private keys.  These private keys are needed to generate the
# signatures included in metadata.
root_private = import_rsa_privatekey_from_file(root_key_file, 'password')
targets_private = import_rsa_privatekey_from_file(targets_key_file, 'password')
snapshot_private = import_rsa_privatekey_from_file(snapshot_key_file, 'password')
timestamp_private = import_rsa_privatekey_from_file(timestamp_key_file, 'password')
delegation_private = import_rsa_privatekey_from_file(delegation_key_file, 'password')

# Add the verification keys to the top-level roles.
repository.root.add_verification_key(root_public)
repository.targets.add_verification_key(targets_public)
repository.snapshot.add_verification_key(snapshot_public)
repository.timestamp.add_verification_key(timestamp_public)

# Load the signing keys, previously imported, for the top-level roles so that
# valid metadata can be written.  
repository.root.load_signing_key(root_private)
repository.targets.load_signing_key(targets_private)
repository.snapshot.load_signing_key(snapshot_private)
repository.timestamp.load_signing_key(timestamp_private)

# Create the target files (downloaded by clients) whose file size and digest
# are specified in the 'targets.json' file.
target1_filepath = 'repository/targets/file1.txt'
tuf.util.ensure_parent_dir(target1_filepath)
target2_filepath = 'repository/targets/file2.txt'
tuf.util.ensure_parent_dir(target2_filepath)
target3_filepath = 'repository/targets/file3.txt'
tuf.util.ensure_parent_dir(target2_filepath)

if not options.dry_run:
  with open(target1_filepath, 'wt') as file_object:
    file_object.write('This is an example target file.')

  with open(target2_filepath, 'wt') as file_object:
    file_object.write('This is an another example target file.')

  with open(target3_filepath, 'wt') as file_object:
    file_object.write('This is role1\'s target file.')

# Add target files to the top-level 'targets.json' role.  These target files
# should already exist.  'target1_filepath' contains additional information
# about the target (i.e., file permissions in octal format.)
octal_file_permissions = oct(os.stat(target1_filepath).st_mode)[4:]
file_permissions = {'file_permissions': octal_file_permissions}
repository.targets.add_target(target1_filepath, file_permissions)
repository.targets.add_target(target2_filepath)

repository.targets.delegate('role1', [delegation_public], [target3_filepath])
repository.targets('role1').load_signing_key(delegation_private)

# Set the top-level expiration times far into the future so that
# they do not expire anytime soon, or else the tests fail.  Unit tests may
# modify the expiration  datetimes (of the copied files), if they wish.
repository.root.expiration = datetime.datetime(2030, 1, 1, 0, 0)
repository.targets.expiration = datetime.datetime(2030, 1, 1, 0, 0)
repository.snapshot.expiration = datetime.datetime(2030, 1, 1, 0, 0)
repository.timestamp.expiration = datetime.datetime(2030, 1, 1, 0, 0)
repository.targets('role1').expiration = datetime.datetime(2030, 1, 1, 0, 0)

# Compress the top-level role metadata so that the unit tests have a
# pre-generated example of compressed metadata.
repository.root.compressions = ['gz']
repository.targets.compressions = ['gz']
repository.snapshot.compressions = ['gz']
repository.timestamp.compressions = ['gz']

# Create the actual metadata files, which are saved to 'metadata.staged'. 
if not options.dry_run:
  repository.write()

# Move the staged.metadata to 'metadata' and create the client folder.  The
# client folder, which includes the required directory structure and metadata
# files for clients to successfully load an 'tuf.client.updater.py' object.
staged_metadata_directory = 'repository/metadata.staged'
metadata_directory = 'repository/metadata'
if not options.dry_run:
  shutil.copytree(staged_metadata_directory, metadata_directory)

# Create the client files (required directory structure and minimal metadata)
# required by the 'tuf.interposition' and 'tuf.client.updater.py' updaters.
if not options.dry_run:
  create_tuf_client_directory('repository', 'client')
