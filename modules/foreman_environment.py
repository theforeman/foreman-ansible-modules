#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2018 Bernhard Suttner (ATIX AG)
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

DOCUMENTATION = '''
---
module: foreman_environment
short_description: Manage Foreman Environment (Puppet) using Foreman API
description:
  - Create and Delete Foreman Environment using Foreman API
version_added: "2.5"
author:
  - "Bernhard Suttner(@_sbernhard) ATIX AG"
requirements:
  - "nailgun >= 0.30.0"
  - "ansible >= 2.3"
options:
  name:
    description: The full environment name
    required: true
  locations:
    description: List of locations the environent should be assigned to
    required: false
    type: list
  organizations:
    description: List of organizations the environment should be assigned to
    required: false
    type: list
  server_url:
    description: foreman url
    required: true
  username:
    description: foreman username
    required: true
  password:
    description: foreman user password
    required: true
  verify_ssl:
    description: verify ssl connection when communicating with foreman
    default: true
    type: bool
  state:
    description: environment presence
    default: present
    choices: ["present", "absent"]
'''

EXAMPLES = '''
- name: create new environment
  foreman_environment:
    name: "testing"
    locations:
      - "Munich"
    organizations:
      - "ATIX"
    server_url: "https://foreman.example.com"
    username: "admin"
    password: "secret"
    verify_ssl: False
    state: present
'''

RETURN = ''' # '''

try:
    from ansible.module_utils.ansible_nailgun_cement import (
        find_environment,
        find_locations,
        find_organizations,
        naildown_entity_state,
        sanitize_entity_dict,
    )

    from nailgun.entities import (
        Environment,
        Location,
        Organization,
    )
except ImportError:
    pass

from ansible.module_utils.foreman_helper import ForemanEntityAnsibleModule


# This is the only true source for names (and conversions thereof)
name_map = {
    'locations': 'location',
    'name': 'name',
    'organizations': 'organization',
}


def main():
    module = ForemanEntityAnsibleModule(
        argument_spec=dict(
            name=dict(required=True),
            locations=dict(type='list'),
            organizations=dict(type='list'),
        ),
        supports_check_mode=True,
    )

    (entity_dict, state) = module.parse_params()

    module.connect()

    try:
        entity = find_environment(module, name=entity_dict['name'], failsafe=True)
    except Exception as e:
        module.fail_json(msg='Failed to find entity: %s ' % e)

    # Set Locations of partition table
    if 'locations' in entity_dict:
        entity_dict['locations'] = find_locations(module, entity_dict['locations'])

    # Set Organizations of partition table
    if 'organizations' in entity_dict:
        entity_dict['organizations'] = find_organizations(module, entity_dict['organizations'])

    entity_dict = sanitize_entity_dict(entity_dict, name_map)

    changed = naildown_entity_state(Environment, entity_dict, entity, state, module)

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()

#  vim: set sts=4 ts=8 sw=4 ft=python et noro norl cin si ai :
