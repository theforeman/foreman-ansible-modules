#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2017, Lester R Claudio <claudiol@redhat.com>
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
module: foreman_realm
short_description: Manage Foreman Realms
description:
  - Manage Foreman Realms
author:
  - "Lester R Claudio (@claudiol1)"
requirements:
  - "nailgun >= 0.30.2"
  - "python >= 2.6"
  - "ansible >= 2.3"
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
      - Name of the Foreman realm
    required: true
  realm_proxy:
    description:
      - Id of Proxy to use for this realm
    type: int
    required: true
  realm_type:
    description:
      - Realm type, e.g. FreeIPA or Active Directory or Red Hat Identity Management
    required: true
  state:
    description:
      - State of the Realm
    default: present
    choices:
      - present
      - absent
'''
EXAMPLES = '''
- name: "Create EXAMPLE.LOCAL Realm"
  foreman_realm:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "EXAMPLE.COM"
    realm_proxy: 1
    realm_type: "Red Hat Identity Management"
    state: present
'''

RETURN = '''# '''

try:
    from ansible.module_utils.ansible_nailgun_cement import (
        create_server,
        ping_server,
        entity_mixins,
        find_entities,
        naildown_entity_state,
    )
    from nailgun.entities import Realm

    has_import_error = False
except ImportError as e:
    has_import_error = True
    import_error_msg = str(e)


from ansible.module_utils.basic import AnsibleModule


def sanitize_realm_dict(realm_dict):
    # This is the only true source for names (and conversions thereof)
    name_map = {
        'name': 'name',
        'realm_proxy': 'realm_proxy',
        'realm_type': 'realm_type',
    }
    result = {}
    for key, value in name_map.items():
        if key in realm_dict:
            result[value] = realm_dict[key]
    return result


def main():

    module = AnsibleModule(
        argument_spec=dict(
            server_url=dict(required=True),
            username=dict(required=True, no_log=True),
            password=dict(required=True, no_log=True),
            verify_ssl=dict(type='bool', default=True),
            name=dict(required=True),
            realm_proxy=dict(type='int', required=True),
            realm_type=dict(required=True, choices=['Red Hat Identity Management', 'FreeIPA', 'Active Directory']),
            state=dict(default='present', choices=['present', 'absent']),
        ),
        supports_check_mode=True,
    )

    if has_import_error:
        module.fail_json(msg=import_error_msg)

    realm_dict = dict(
        [(k, v) for (k, v) in module.params.items() if v is not None])

    server_url = realm_dict.pop('server_url')
    username = realm_dict.pop('username')
    password = realm_dict.pop('password')
    verify_ssl = realm_dict.pop('verify_ssl')
    state = realm_dict.pop('state')

    try:
        create_server(server_url, (username, password), verify_ssl)
    except Exception as e:
        module.fail_json(msg="Failed to connect to Foreman server: %s " % e)

    ping_server(module)
    try:
        entities = find_entities(Realm, name=realm_dict['name'])
        if len(entities) > 0:
            entity = entities[0]
        else:
            entity = None
    except Exception as e:
        module.fail_json(msg='Failed to find entity: %s ' % e)

    realm_dict = sanitize_realm_dict(realm_dict)

    changed = naildown_entity_state(Realm, realm_dict, entity, state, module)

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()
