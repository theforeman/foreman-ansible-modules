#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2019 Christoffer Reijer (Basalt AB)
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
module: foreman_role
short_description: Manage Foreman Roles using Foreman API
description:
  - Create and Delete Foreman Roles using Foreman API
version_added: "2.9"
author:
  - "Christoffer Reijer (@ephracis) Basalt AB"
requirements:
  - "apypie"
options:
  name:
    description: The name of the role
    required: true
  description:
    description: Description of the role
    required: false
  locations:
    description: List of locations the role should be assigned to
    required: false
    default: None
    type: list
  organizations:
    description: List of organizations the role should be assigned to
    required: false
    default: None
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
  validate_certs:
    aliases: [ verify_ssl ]
    description: verify ssl connection when communicating with foreman
    default: true
    type: bool
  state:
    description: role presence
    default: present
    choices: ["present", "absent"]
'''

EXAMPLES = '''
- name: role
  foreman_role:
    name: "Provisioner"
    description: "Only provision on libvirt"
    locations:
      - "Uppsala"
    organizations:
      - "Basalt"
    server_url: "https://foreman.example.com"
    username: "admin"
    password: "secret"
    validate_certs: False
    state: present
'''

RETURN = ''' # '''

from ansible.module_utils.foreman_helper import ForemanEntityApypieAnsibleModule


# This is the only true source for names (and conversions thereof)
name_map = {
    'name': 'name',
    'description': 'description',
    'locations': 'location_ids',
    'organizations': 'organization_ids',
}


def main():
    module = ForemanEntityApypieAnsibleModule(
        argument_spec=dict(
            name=dict(required=True),
            description=dict(),
            locations=dict(type='list'),
            organizations=dict(type='list'),
        ),
        supports_check_mode=True,
    )

    (entity_dict, state) = module.parse_params()

    module.connect()

    entity = module.find_resource_by_name('roles', name=entity_dict['name'], failsafe=True)

    if 'locations' in entity_dict:
        entity_dict['locations'] = module.find_resources('locations', entity_dict['locations'], thin=True)

    if 'organizations' in entity_dict:
        entity_dict['organizations'] = module.find_resources('organizations', entity_dict['organizations'], thin=True)

    changed = module.ensure_resource_state('roles', entity_dict, entity, state, name_map)

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()

#  vim: set sts=4 ts=8 sw=4 ft=python et noro norl cin si ai :
