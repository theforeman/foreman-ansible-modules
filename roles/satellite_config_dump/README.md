Role Name
=========

This role dumps a Satellite configuration to a set of YAML files
easily consumed by the Foreman Ansible modules so that the original
Satellite can be easily duplicated to another Satellite

Requirements
------------


Role Variables
--------------

satellite_config_dump_path:
    The path where the dump directory will be created. Must 
    have a trailing slash ('/'), must already exist.

satellite_config_dump_folder:
    The folder that will be created for the dump files. Will be
    created inside the satellite_config_dump_path folder.

Dependencies
------------

N/A

Example Playbook
----------------

    - hosts: localhost
      roles:
         - satellite_config_dump

License
-------

GPL 3.0 and later

