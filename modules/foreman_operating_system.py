#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2017 Matthias M Dellweg (ATIX AG)
# (c) 2017 Bernhard Hopfenmüller (ATIX AG)
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: foreman_operating_system
short_description: Manage Foreman Operating Systems
description:
  - "Manage Foreman Operating System Entities"
  - "Uses https://github.com/SatelliteQE/nailgun"
version_added: "2.4"
author:
  - "Matthias M Dellweg (@mdellweg) ATIX AG"
  - "Bernhard Hopfenmüller (@Fobhep) ATIX AG"
requirements:
  - "nailgun >= 0.29.0"
  - "ansible >= 2.3"
options:
  server_url:
    description:
      - URL of Foreman server
    required: true
  username:
    description:
      - Username on Foreman server
    required: true
  password:
    description:
      - Password for user accessing Foreman server
    required: true
  verify_ssl:
    description:
      - Verify SSL of the Foreman server
    required: false
    default: true
    type: bool
  name:
    description:
      - Name of the Operating System
    required: true
  release_name:
    description:
      - Release name of the operating system (recommended for debian)
  description:
    description:
      - Description of the Operating System
    required: false
  family:
    description:
      - distribution family of the Operating System
    required: true
  major:
    description:
      - major version of the Operating System
    required: true
  minor:
    description:
      - minor version of the Operating System
    required: false
  architectures:
    description:
      - architectures, the operating system can be installed on
    required: false
    type: list
  media:
    description:
      - list of installation media
    required: false
    type: list
  ptables:
    description:
      - list of partitioning tables
    required: false
    type: list
  provisioning_templates:
    description:
      - list of provisioning templates
    required: false
    type: list
  password_hash:
    description:
      - hashing algorithm for passwd
    required: false
    choices:
      - MD5
      - SHA256
      - SHA512
  state:
    description:
      - State of the Operating System
    default: present
    choices:
      - present
      - present_with_defaults
      - absent
'''

EXAMPLES = '''
- name: "Create an Operating System"
  foreman_operating_system:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: Debian 9
    release_name: stretch
    family: Debian
    major: 9
    state: present

- name: "Ensure existence of an Operating System (provide default values)"
  foreman_operating_system:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: Centos 7
    family: Red Hat
    major: 7
    password_hash: SHA256
    state: present_with_defaults

- name: "Delete an Operating System"
  foreman_operating_system:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: Debian 9
    family: Debian
    major: 9
    state: absent
'''

RETURN = ''' # '''

try:
    from ansible.module_utils.ansible_nailgun_cement import (
        find_entities,
        find_entities_by_name,
        find_operating_system_by_title,
        naildown_entity_state,
        sanitize_entity_dict,
    )

    from nailgun.entities import (
        OperatingSystem,
        Architecture,
        Media,
        PartitionTable,
        ProvisioningTemplate,
    )
except ImportError:
    pass

from ansible.module_utils.foreman_helper import ForemanEntityAnsibleModule

# This is the only true source for names (and conversions thereof)
name_map = {
    'name': 'name',
    'description': 'description',
    'family': 'family',
    'major': 'major',
    'minor': 'minor',
    'release_name': 'release_name',
    'architectures': 'architecture',
    'media': 'medium',
    'ptables': 'ptable',
    'provisioning_templates': 'provisioning_template',
    'password_hash': 'password_hash',
}


def main():
    module = ForemanEntityAnsibleModule(
        argument_spec=dict(
            name=dict(required=True),
            release_name=dict(),
            description=dict(),
            family=dict(required=True),
            major=dict(required=True),
            minor=dict(),
            architectures=dict(type='list'),
            media=dict(type='list'),
            ptables=dict(type='list'),
            provisioning_templates=dict(type='list'),
            password_hash=dict(choices=['MD5', 'SHA256', 'SHA512']),
            state=dict(default='present', choices=['present', 'present_with_defaults', 'absent']),
        ),
        supports_check_mode=True,
    )

    (operating_system_dict, state) = module.parse_params()

    module.connect()

    try:
        # Try to find the Operating System to work on
        # name is however not unique, but description is, as well as "<name> <major>[.<minor>]"
        entity = None
        # If we have a description, search for it
        if 'description' in operating_system_dict and operating_system_dict['description'] != '':
            entity = find_operating_system_by_title(module, title=operating_system_dict['description'], failsafe=True)
        # If we did not yet find a unique OS, search by name & version
        if entity is None:
            search_dict = {'name': operating_system_dict['name']}
            if 'major' in operating_system_dict:
                search_dict['major'] = operating_system_dict['major']
            if 'minor' in operating_system_dict:
                search_dict['minor'] = operating_system_dict['minor']
            entities = find_entities(OperatingSystem, **search_dict)
            if len(entities) == 1:
                entity = entities[0]
    except Exception as e:
        module.fail_json(msg='Failed to find entity: %s ' % e)

    if not entity and (state == 'present' or state == 'present_with_defaults'):
        # we actually attempt to create a new one...
        for param_name in ['major', 'family', 'password_hash']:
            if param_name not in operating_system_dict.keys():
                module.fail_json(msg='{} is a required parameter to create a new operating system.'.format(param_name))

    # Set Architectures of Operating System
    if 'architectures' in operating_system_dict:
        operating_system_dict['architectures'] = find_entities_by_name(
            Architecture, operating_system_dict['architectures'], module)

    # Set Installation Media of Operating System
    if 'media' in operating_system_dict:
        operating_system_dict['media'] = find_entities_by_name(
            Media, operating_system_dict['media'], module)

    # Set Partition Tables of Operating System
    if 'ptables' in operating_system_dict:
        operating_system_dict['ptables'] = find_entities_by_name(
            PartitionTable, operating_system_dict['ptables'], module)

    # Set Provisioning Templates of Operating System
    if 'provisioning_templates' in operating_system_dict:
        operating_system_dict['provisioning_templates'] = find_entities_by_name(
            ProvisioningTemplate, operating_system_dict['provisioning_templates'], module)

    operating_system_dict = sanitize_entity_dict(operating_system_dict, name_map)

    changed = naildown_entity_state(OperatingSystem, operating_system_dict, entity, state, module)

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()
