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

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: foreman_role
short_description: Manage Foreman Roles using Foreman API
description:
  - Create and Delete Foreman Roles using Foreman API
author:
  - "Christoffer Reijer (@ephracis) Basalt AB"
requirements:
  - "apypie"
options:
  name:
    description: The name of the role
    required: true
    type: str
  description:
    description: Description of the role
    required: false
    type: str
  locations:
    description: List of locations the role should be assigned to
    required: false
    type: list
  organizations:
    description: List of organizations the role should be assigned to
    required: false
    type: list
  state:
    description: role presence
    default: present
    choices: ["present", "absent"]
    type: str
extends_documentation_fragment: foreman
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
    state: present
'''

RETURN = ''' # '''

from ansible.module_utils.foreman_helper import ForemanEntityAnsibleModule


def main():
    module = ForemanEntityAnsibleModule(
        entity_spec=dict(
            name=dict(required=True),
            description=dict(),
            locations=dict(type='entity_list', flat_name='location_ids'),
            organizations=dict(type='entity_list', flat_name='organization_ids'),
        ),
    )

    entity_dict = module.clean_params()

    module.connect()

    entity = module.find_resource_by_name('roles', name=entity_dict['name'], failsafe=True)

    if not module.desired_absent:
        if 'locations' in entity_dict:
            entity_dict['locations'] = module.find_resources_by_title('locations', entity_dict['locations'], thin=True)

        if 'organizations' in entity_dict:
            entity_dict['organizations'] = module.find_resources_by_name('organizations', entity_dict['organizations'], thin=True)

    changed = module.ensure_entity_state('roles', entity_dict, entity)

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()

#  vim: set sts=4 ts=8 sw=4 ft=python et noro norl cin si ai :
