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
module: foreman_architecture
short_description: Manage Foreman Architectures using Foreman API
description:
  - Create, Update and Delete Foreman Architectures using Foreman API
author:
  - "Manisha Singhal (@Manisha15) ATIX AG"
requirements:
  - "apypie"
options:
  name:
    description: Name of architecture
    required: true
  operatingsystems:
    description: List of operating systems the architecture should be assigned to
    required: false
    default: None
  state:
    description: Architecture presence
    default: present
    choices: ["present", "absent"]
extends_documentation_fragment: foreman
'''

EXAMPLES = '''
- name: "Create an Architecture"
  foreman_architecture:
    name: "i386"
    operatingsystems:
      - "TestOS1"
      - "TestOS2"
    server_url: "https://foreman.example.com"
    username: "admin"
    password: "secret"
    state: present

- name: "Update an Architecture"
  foreman_architecture:
    name: "i386"
    operatingsystems:
      - "TestOS3"
      - "TestOS4"
    server_url: "https://foreman.example.com"
    username: "admin"
    password: "secret"
    state: present

- name: "Delete an Architecture"
  foreman_architecture:
    name: "i386"
    server_url: "https://foreman.example.com"
    username: "admin"
    password: "secret"
    state: absent
'''

RETURN = ''' # '''

from ansible.module_utils.foreman_helper import ForemanEntityApypieAnsibleModule


def main():
    module = ForemanEntityApypieAnsibleModule(
        entity_spec=dict(
            name=dict(required=True),
            operatingsystems=dict(type='entity_list', flat_name='operatingsystem_ids'),
        ),
    )

    entity_dict = module.clean_params()

    module.connect()

    if not module.desired_absent:
        if 'operatingsystems' in entity_dict:
            entity_dict['operatingsystems'] = module.find_operatingsystems(entity_dict['operatingsystems'], thin=True)

    entity = module.find_resource_by_name('architectures', name=entity_dict['name'], failsafe=True)

    changed = module.ensure_entity_state('architectures', entity_dict, entity)

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()
