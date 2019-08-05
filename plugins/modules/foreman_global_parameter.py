#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2017 Matthias Dellweg & Bernhard Hopfenmüller (ATIX AG)
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
module: foreman_global_parameter
short_description: Manage Foreman Global Parameters
description:
  - "Manage Foreman Global Parameter Entities"
  - "Uses https://github.com/SatelliteQE/nailgun"
author:
  - "Bernhard Hopfenmueller (@Fobhep) ATIX AG"
  - "Matthias Dellweg (@mdellweg) ATIX AG"
  - "Manisha Singhal (@manisha15) ATIX AG"
requirements:
  - "apypie"
options:
  name:
    description:
      - Name of the Global Parameter
    required: true
  value:
    description:
      - Value of the Global Parameter
    required: false
  parameter_type:
    description:
      - Type of value
    default: string
    choices:
      - string
      - boolean
      - integer
      - real
      - array
      - hash
      - yaml
      - json
    note: This parameter has an effect only on foreman >= 1.22
  state:
    description:
      - State of the Global Parameter
    default: present
    choices:
      - present
      - present_with_defaults
      - absent
extends_documentation_fragment: foreman
'''

EXAMPLES = '''
- name: "Create a Global Parameter"
  foreman_global_parameter:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "TheAnswer"
    value: "42"
    state: present_with_defaults

- name: "Update a Global Parameter"
  foreman_global_parameter:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "TheAnswer"
    value: "43"
    state: present

- name: "Delete a Global Parameter"
  foreman_global_parameter:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "TheAnswer"
    state: absent
'''

RETURN = ''' # '''


from ansible.module_utils.foreman_helper import ForemanEntityApypieAnsibleModule, parameter_value_to_str


def main():
    module = ForemanEntityApypieAnsibleModule(
        entity_spec=dict(
            name=dict(required=True),
            value=dict(type='raw'),
            parameter_type=dict(default='string', choices=['string', 'boolean', 'integer', 'real', 'array', 'hash', 'yaml', 'json']),
        ),
        argument_spec=dict(
            state=dict(default='present', choices=['present_with_defaults', 'present', 'absent']),
        ),
        required_if=(
            ['state', 'present_with_defaults', ['value']],
            ['state', 'present', ['value']],
        ),
    )

    entity_dict = module.clean_params()

    module.connect()

    entity = module.find_resource_by_name('common_parameters', name=entity_dict['name'], failsafe=True)

    if not module.desired_absent:
        # Convert values according to their corresponding parameter_type
        if entity and 'parameter_type' not in entity:
            entity['parameter_type'] = 'string'
        entity_dict['value'] = parameter_value_to_str(entity_dict['value'], entity_dict['parameter_type'])
        if entity and 'value' in entity:
            entity['value'] = parameter_value_to_str(entity['value'], entity.get('parameter_type', 'string'))

    changed = module.ensure_entity_state('common_parameters', entity_dict, entity)

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()
