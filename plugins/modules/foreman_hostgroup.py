#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2019 Manisha Singhal (ATIX AG)
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
module: foreman_hostgroup
short_description: Manage Foreman Hostgroups using Foreman API
description:
  - Create, Update and Delete Foreman Hostgroups using Foreman API
author:
  - "Manisha Singhal (@Manisha15) ATIX AG"
requirements:
  - "apypie >= 0.0.1"
options:
  name:
    description: Name of hostgroup
    required: true
  description:
    description: Description of hostgroup
    required: false
  architecture:
    description: Architecture name
    required: False
    default: None
  medium:
    description: Medium name
    required: False
    default: None
  operatingsystem:
    description: Operatingsystem name
    required: False
    default: None
  partition_table:
    description: Partition table name
    required: False
    default: None
  root_pass:
    description: root password
    required: false
    default: None
  state:
    description: Hostgroup presence
    default: present
    choices: ["present", "absent"]
extends_documentation_fragment: foreman
'''

EXAMPLES = '''
- name: "Create a Hostgroup"
  foreman_hostgroup:
    name: "new_hostgroup"
    architecture: "architecture_name"
    operatingsystem: "operatingsystem_name"
    medium: "media_name"
    ptable: "Partition_table_name"
    server_url: "https://foreman.example.com"
    username: "admin"
    password: "secret"
    state: present

- name: "Update a Hostgroup"
  foreman_hostgroup:
    name: "new_hostgroup"
    architecture: "updated_architecture_name"
    operatingsystem: "updated_operatingsystem_name"
    medium: "updated_media_name"
    ptable: "updated_Partition_table_name"
    root_pass: "password"
    server_url: "https://foreman.example.com"
    username: "admin"
    password: "secret"
    state: present

- name: "Delete a Hostgroup"
  foreman_hostgroup:
    name: "new_hostgroup"
    server_url: "https://foreman.example.com"
    username: "admin"
    password: "secret"
    state: absent
'''

RETURN = ''' # '''

from ansible.module_utils.foreman_helper import ForemanEntityApypieAnsibleModule


# This is the only true source for names (and conversions thereof)
name_map = {
    'name': 'name',
    'description': 'description',
    'architecture': 'architecture_id',
    'operatingsystem': 'operatingsystem_id',
    'media': 'medium_id',
    'ptable': 'ptable_id',
    'root_pass': 'root_pass',
}


def main():
    module = ForemanEntityApypieAnsibleModule(
        argument_spec=dict(
            name=dict(required=True),
            description=dict(),
            architecture=dict(),
            operatingsystem=dict(),
            media=dict(),
            ptable=dict(),
            root_pass=dict(no_log=True),
        ),
    )
    entity_dict = module.clean_params()

    module.connect()

    if not module.desired_absent:
        if 'architecture' in entity_dict:
            entity_dict['architecture'] = module.find_resource_by_name('architectures', name=entity_dict['architecture'], failsafe=False, thin=True)

        if 'operatingsystem' in entity_dict:
            entity_dict['operatingsystem'] = module.find_resource_by_name('operatingsystems', name=entity_dict['operatingsystem'], failsafe=False, thin=True)

        if 'media' in entity_dict:
            entity_dict['media'] = module.find_resource_by_name('media', name=entity_dict['media'], failsafe=False, thin=True)

        if 'ptable' in entity_dict:
            entity_dict['ptable'] = module.find_resource_by_name('ptables', name=entity_dict['ptable'], failsafe=False, thin=True)

    entity = module.find_resource_by_name('hostgroups', name=entity_dict['name'], failsafe=True)
    if entity:
        entity['root_pass'] = None

    changed = module.ensure_resource_state('hostgroups', entity_dict, entity, name_map)

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()
