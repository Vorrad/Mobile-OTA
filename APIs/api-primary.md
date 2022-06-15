# Primary 类定义

uptane/client/primary.py 中对Primary类的定义：

```
  <Purpose>
    This class contains the necessary code to perform Uptane validation of
    images and metadata, and core functionality supporting distribution of
    metadata and images to Secondary ECUs, combining ECU Manifests into a
    Vehicle Manifest and signing it, combining tokens for a Timeserver request,
    validating the response, etc.

  <Fields>

    self.vin
      A unique identifier for the vehicle that contains this Secondary ECU.
      In this reference implementation, this conforms to
      uptane.formats.VIN_SCHEMA. There is no need to use the vehicle's VIN in
      particular; we simply need a unique identifier for the vehicle, known
      to the Director.

    self.ecu_serial
      A unique identifier for this Primary ECU. In this reference
      implementation, this conforms to uptane.formats.ECU_SERIAL_SCHEMA.
      (In other implementations, the important point is that this should be
      unique.) The Director should be aware of this identifier.

    self.primary_key
      The signing key for this Primary ECU. This key will be used to sign
      Vehicle Manifests that will then be sent to the Director). The Director
      should be aware of the corresponding public key, so that it can validate
      these Vehicle Manifests. Conforms to tuf.formats.ANYKEY_SCHEMA.

    self.updater
      A tuf.client.updater.Updater object used to retrieve metadata and
      target files from the Director and Supplier repositories.

    self.full_client_dir
      The full path of the directory where all client data is stored for this
      Primary. This includes verified and unverified metadata and images and
      any temp files. Conforms to tuf.formats.PATH_SCHEMA.

    self.director_repo_name
      The name of the Director repository (e.g. 'director'), as listed in the
      map (or pinning) file (pinned.json). This value must appear in that file.
      Used to distinguish between the Image Repository and the Director
      Repository. Conforms to tuf.formats.REPOSITORY_NAME_SCHEMA.

    self.timeserver_public_key:
      The public key matching the private key that we expect the timeserver to
      use when signing attestations. Validation is against this key.

    self.ecu_manifests
      A dictionary containing the manifests provided by all ECUs. Will include
      all manifests sent by all ECUs. The Primary does not verify signatures on
      ECU manifests according to the Implementation Specification.
      Compromised ECUs may send bogus ECU manifests, so we simply send all
      manifests to the Director, who will sort through and discern what is
      going on.
      This is emptied every time the Primary produces a Vehicle Manifest
      (which will have included all of them). An implementer may wish to
      consider keeping these around until there is some likelihood that the
      Director has received them, as doing otherwise could deprive the
      Director of some historical and error/attack data. (Future ECU Manifests
      will provide current information, but useful diagnostic information may
      be lost.)

    self.my_secondaries:
      This is a list of all ECU Serials belonging to Secondaries of this
      Primary.

    self.assigned_targets:
      A dict mapping ECU Serial to the target file info that the Director has
      instructed that ECU to install.

    self.nonces_to_send:
      The list of nonces sent to us from Secondaries and not yet sent to the
      Timeserver.

    self.nonces_sent:
      The list of nonces sent to the Timeserver by our Secondaries, which we
      have already sent to the Timeserver. Will be checked against the
      Timeserver's response.

    # TODO: Rename these two variables, valid -> verified, along with the
    #       verification functions.  Do likewise in Secondary.
    self.all_valid_timeserver_attestations:
      A list of all attestations received from Timeservers that have been
      verified by update_time().
      Items are appended to the end.

    self.all_valid_timeserver_times:
      A list of all times extracted from all Timeserver attestations that have
      been verified by update_time().
      Items are appended to the end.

    self.distributable_full_metadata_archive_fname:
      The filename at which the full metadata archive is stored after each
      update cycle. Path is relative to uptane.WORKING_DIR. This is atomically
      moved into place (renamed) after it has been fully written, to avoid
      race conditions.

    self.distributable_partial_metadata_fname:
      The filename at which the Director's targets metadata file is stored after
      each update cycle, once it is safe to use. This is atomically moved into
      place (renamed) after it has been fully written, to avoid race conditions.


  Methods organized by purpose: ("self" arguments excluded)

    High-level Methods for OEM/Supplier Primary code to use:
      __init__()
      primary_update_cycle()
      generate_signed_vehicle_manifest()
      get_nonces_to_send_and_rotate()
      save_distributable_metadata_files()
      update_time(timeserver_attestation)

    Lower-level methods called by primary_update_cycle() to perform retrieval
    and validation of metadata and data from central services:
      refresh_toplevel_metadata()
      get_target_list_from_director()
      get_validated_target_info()

    Components of the interface available to a Secondary client:
      register_ecu_manifest(vin, ecu_serial, nonce, signed_ecu_manifest)
      get_last_timeserver_attestation()
      update_exists_for_ecu(ecu_serial)
      get_image_fname_for_ecu(ecu_serial)
      get_full_metadata_archive_fname()
      get_partial_metadata_fname()
      register_new_secondary(ecu_serial)

    Private methods:
      _check_ecu_serial(ecu_serial)


  Use:
    import uptane.clients.primary as primary
    p = primary.Primary(
        full_client_dir='/Users/s/w/uptane/temp_primarymetadata',
        vin='vin11111',
        ecu_serial='ecu00000',
        timeserver_public_key=<some key>)

    p.register_ecu_manifest(vin, ecu_serial, nonce, <a signed ECU manifest>)
    p.register_ecu_manifest(...)
    ...

    nonces = p.get_nonces_to_send_and_rotate()

    <submit the nonces to the Timeserver and save the returned time attestation>

    p.update_time(<the returned time attestation>)

    <metadata> = p.get_metadata_for_ecu(ecu_serial)
    <secondary firmware> = p.get_image_for_ecu(ecu_serial)
    <metadata> = p.get_metadata_for_ecu(<some other ecu serial>)
    ...

    And so on, with ECUs requesting images and metadata and registering ECU
    manifests (and providing nonces thereby).
```