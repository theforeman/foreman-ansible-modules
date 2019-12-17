#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2018 Manuel Bonk (ATIX AG)
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
module: foreman_installation_medium
short_description: Manage Foreman Installation Medium using Foreman API
description:
  - Create and Delete Foreman Installation Medium using Foreman API
author:
  - "Manuel Bonk(@manuelbonk) ATIX AG"
options:
  name:
    description:
      - |
        The full installation medium name.
        The special name "*" (only possible as parameter) is used to perform bulk actions (modify, delete) on all existing partition tables.
    required: true
    type: str
  updated_name:
    description: New full installation medium name. When this parameter is set, the module will not be idempotent.
    type: str
  operatingsystems:
    description: List of operating systems the installation medium should be assigned to
    required: false
    type: list
  os_family:
    description:
      - The OS family the template shall be assigned with.
      - If no os_family is set but a operatingsystem, the value will be derived from it.
  path:
    description: Path to the installation medium
    type: str
extends_documentation_fragment:
  - foreman
  - foreman.entity_state_with_defaults
  - foreman.taxonomy
  - foreman.os_family
'''

EXAMPLES = '''
- name: create new debian medium
  foreman_installation_medium:
    name: "wheezy"
    locations:
      - "Munich"
    organizations:
      - "ATIX"
    operatingsystems:
      - "Debian"
    path: "http://debian.org/mirror/"
    server_url: "https://foreman.example.com"
    username: "admin"
    password: "secret"
    state: present
'''

RETURN = ''' # '''

from ansible.module_utils.foreman_helper import ForemanTaxonomicEntityAnsibleModule, OS_LIST


def main():
    module = ForemanTaxonomicEntityAnsibleModule(
        argument_spec=dict(
            updated_name=dict(),
            state=dict(default='present', choices=['present', 'present_with_defaults', 'absent']),
        ),
        entity_spec=dict(
            name=dict(required=True),
            operatingsystems=dict(type='entity_list', flat_name='operatingsystem_ids'),
            os_family=dict(choices=OS_LIST),
            path=dict(),
        ),
    )

    entity_dict = module.clean_params()

    module.connect()
    name = entity_dict['name']

    affects_multiple = name == '*'
    # sanitize user input, filter unuseful configuration combinations with 'name: *'
    if affects_multiple:
        if module.state == 'present_with_defaults':
            module.fail_json(msg="'state: present_with_defaults' and 'name: *' cannot be used together")
        if module.params['updated_name']:
            module.fail_json(msg="updated_name not allowed if 'name: *'!")
        if module.desired_absent:
            if list(entity_dict.keys()) != ['name']:
                entity_dict.pop('name', None)
                module.fail_json(msg='When deleting all installation media, there is no need to specify further parameters: %s ' % entity_dict.keys())

    if affects_multiple:
        entities = module.list_resource('media')
        if not module.desired_absent:  # not 'thin'
            entities = [module.show_resource('media', entity['id']) for entity in entities]
        if not entities:
            # Nothing to do shortcut to exit
            module.exit_json()
    else:
        entity = module.find_resource_by_name('media', name=entity_dict['name'], failsafe=True)

    entity_dict = module.handle_taxonomy_params(entity_dict)

    if not module.desired_absent:
        if not affects_multiple and entity and 'updated_name' in entity_dict:
            entity_dict['name'] = entity_dict.pop('updated_name')
        if 'operatingsystems' in entity_dict:
            entity_dict['operatingsystems'] = module.find_operatingsystems(entity_dict['operatingsystems'], thin=True)
            if not affects_multiple and len(entity_dict['operatingsystems']) == 1 and 'os_family' not in entity_dict and entity is None:
                entity_dict['os_family'] = module.show_resource('operatingsystems', entity_dict['operatingsystems'][0]['id'])['family']

    if not affects_multiple:
        module.ensure_entity('media', entity_dict, entity)
    else:
        entity_dict.pop('name')
        for entity in entities:
            module.ensure_entity('media', entity_dict, entity)

    module.exit_json()


if __name__ == '__main__':
    main()
