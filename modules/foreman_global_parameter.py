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
version_added: "2.4"
author:
- "Bernhard Hopfenmueller (@Fobhep) ATIX AG"
- "Matthias Dellweg (@mdellweg) ATIX AG"
requirements:
    - nailgun >= 0.29.0
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
        - Name of the Global Parameter
        required: true
    value:
        description:
        - Value of the Global Parameter
        required: false
    state:
        description:
        - State of the Global Parameter
        default: present
        choices:
        - present
        - present_with_defaults
        - absent
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

try:
    from nailgun.entities import (
        CommonParameter,
    )

    from ansible.module_utils.ansible_nailgun_cement import (
        create_server,
        ping_server,
        find_entities,
        naildown_entity_state,
        sanitize_entity_dict,
    )

    HAS_IMPORT_ERROR = False
except ImportError as e:
    HAS_IMPORT_ERROR = True
    IMPORT_ERROR = str(e)

from ansible.module_utils.basic import AnsibleModule


# This is the only true source for names (and conversions thereof)
name_map = {
    'name': 'name',
    'value': 'value',
}


def main():
    module = AnsibleModule(
        argument_spec=dict(
            server_url=dict(required=True),
            username=dict(required=True),
            password=dict(required=True, no_log=True),
            verify_ssl=dict(type='bool', default=True),
            name=dict(required=True),
            value=dict(),
            state=dict(default='present', choices=['present_with_defaults', 'present', 'absent']),
        ),
        required_if=(
            ['state', 'present_with_defaults', ['value']],
            ['state', 'present', ['value']],
        ),
        supports_check_mode=True,
    )

    if HAS_IMPORT_ERROR:
        module.fail_json(msg=IMPORT_ERROR)

    global_parameter_dict = dict(
        [(k, v) for (k, v) in module.params.items() if v is not None])

    server_url = global_parameter_dict.pop('server_url')
    username = global_parameter_dict.pop('username')
    password = global_parameter_dict.pop('password')
    verify_ssl = global_parameter_dict.pop('verify_ssl')
    state = global_parameter_dict.pop('state')

    try:
        create_server(server_url, (username, password), verify_ssl)
    except Exception as e:
        module.fail_json(msg="Failed to connect to Foreman server: %s " % e)

    ping_server(module)
    try:
        entities = find_entities(CommonParameter, name=global_parameter_dict['name'])
        if len(entities) > 0:
            entity = entities[0]
        else:
            entity = None
    except Exception as e:
        module.fail_json(msg='Failed to find entity: %s ' % e)

    global_parameter_dict = sanitize_entity_dict(global_parameter_dict, name_map)

    changed = naildown_entity_state(CommonParameter, global_parameter_dict, entity, state, module)

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()
