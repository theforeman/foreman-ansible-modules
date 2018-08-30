#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2018 Matthias M Dellweg (ATIX AG)
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
module: foreman_setting
short_description: Manage Foreman Settings
description:
  - "Manage Foreman Setting Entities"
  - "Uses https://github.com/SatelliteQE/nailgun"
version_added: "2.4"
author:
  - "Matthias M Dellweg (@mdellweg) ATIX AG"
requirements:
  - nailgun >= 0.29.0
options:
  server_url:
    description:
      - URL of Foreman server
    required: false
  username:
    description:
      - Username on Foreman server
    required: false
  password:
    description:
      - Password for user accessing Foreman server
    required: false
  verify_ssl:
    description:
      - Verify SSL of the Foreman server
    required: false
    default: true
    type: bool
  auth_block:
    description:
      - Dictionary containing the connection parameter
    required: false
    type: dict
  name:
    description:
      - Name of the Setting
    required: true
  value:
    description:
      - value to set the Setting to
      - if missing, reset to default
    required: false
'''

EXAMPLES = '''
- name: "Set a Setting"
  foreman_setting:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "http_proxy"
    value: "http://localhost:8088"

- name: "Reset a Setting"
  foreman_setting:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "http_proxy"
'''

RETURN = ''' # '''

try:
    from ansible.module_utils.ansible_nailgun_cement import (
        create_connection,
        ping_server,
        find_setting,
        naildown_entity_state,
        sanitize_entity_dict,
    )

    from nailgun.entities import (
        Setting,
    )

    has_import_error = False
except ImportError as e:
    has_import_error = True
    import_error_msg = str(e)
    raise

from ansible.module_utils.basic import AnsibleModule


name_map = {
    'name': 'name',
    'value': 'value',
}


def main():
    module = AnsibleModule(
        argument_spec=dict(
            server_url=dict(),
            username=dict(),
            password=dict(no_log=True),
            verify_ssl=dict(type='bool', default=True),
            auth_block=dict(type=dict, no_log=True),
            name=dict(required=True),
            value=dict(),
        ),
        supports_check_mode=True,
        mutually_exclusive=[
            ['auth_block', 'server_url'],
            ['auth_block', 'username'],
            ['auth_block', 'password'],
            ['auth_block', 'verify_ssl'],
        ],
        required_one_of=[
            ['auth_block', 'server_url'],
            ['auth_block', 'username'],
            ['auth_block', 'password'],
        ],
    )

    if has_import_error:
        module.fail_json(msg=import_error_msg)

    entity_dict = dict(
        [(k, v) for (k, v) in module.params.items() if v is not None])

    auth_block = entity_dict.pop('auth_block', None) or {  # Searching for a better name
        'server_url': entity_dict.pop('server_url'),
        'username': entity_dict.pop('username'),
        'password': entity_dict.pop('password'),
        'verify_ssl': entity_dict.pop('verify_ssl', True),
    }

    create_connection(auth_block, module)

    ping_server(module)

    entity = find_setting(
        module,
        name=entity_dict['name'],
        failsafe=False,
    )

    if 'value' not in entity_dict:
        entity_dict['value'] = entity.default or ""

    entity_dict = sanitize_entity_dict(entity_dict, name_map)

    changed = naildown_entity_state(Setting, entity_dict, entity, 'present', module)

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()
