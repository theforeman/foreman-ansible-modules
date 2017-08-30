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
        required: true
        choices:
        - present
        - lastest
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
    state: present

- name: "Update a Global Parameter"
  foreman_global_parameter:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "TheAnswer"
    value: "43"
    state: latest

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
    from ansible.module_utils.ansible_nailgun_cement import (
        CommonParameter,
        Organization,
        Location,
        create_server,
        ping_server,
        handle_no_nailgun,
        find_entities,
        naildown_entity_state,
    )

    HAS_NAILGUN_PACKAGE = True
except:
    HAS_NAILGUN_PACKAGE = False

from ansible.module_utils.basic import AnsibleModule


def sanitize_global_parameter_dict(global_parameter_dict):
    # This is the only true source for names (and conversions thereof)
    name_map = {
        'name': 'name',
        'value': 'value',
    }
    result = {}
    for key, value in name_map.iteritems():
        if key in global_parameter_dict:
            result[value] = global_parameter_dict[key]
    return result


def main():
    module = AnsibleModule(
        argument_spec=dict(
            server_url=dict(required=True),
            username=dict(required=True),
            password=dict(required=True, no_log=True),
            verify_ssl=dict(type='bool', default=True),
            name=dict(required=True),
            value=dict(),
            state=dict(required=True, choices=['present', 'latest', 'absent']),
        ),
        required_if=(
            ['state', 'present', ['value']],
            ['state', 'latest', ['value']],
        ),
        supports_check_mode=True,
    )

    handle_no_nailgun(module, HAS_NAILGUN_PACKAGE)

    global_parameter_dict = dict(
        [(k, v) for (k, v) in module.params.iteritems() if v is not None])

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

    global_parameter_dict = sanitize_global_parameter_dict(global_parameter_dict)

    changed = naildown_entity_state(CommonParameter, global_parameter_dict, entity, state, module)

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()
