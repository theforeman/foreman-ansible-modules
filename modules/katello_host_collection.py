#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2019, Maxim Burgerhout <maxim@wzzrd.com>
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
module: katello_host_collection
short_description: Create and Manage Katello host collections
description:
    - Create and Manage Katello host collections
author:
    - "Maxim Burgerhout (@wzzrd)"
requirements:
    - "nailgun >= 0.32.0"
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
    default: true
    type: bool
  description:
    description:
      - Description of the Katello host collection
    required: false
  organization:
    description:
      - Organization that the Product is in
    required: true
  name:
    description:
      - Name of the Katello host collection
    required: true
  state:
    description:
      - State of the host collection
    default: present
    choices:
      - present
      - absent
      - present_with_defaults
'''

EXAMPLES = '''
- name: "Create Foo host collection"
  katello_host_collection:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "Foo"
    description: "Foo host collection for Foo servers"
    organization: "My Cool new Organization"
    state: present
'''

RETURN = '''# '''

try:
    from nailgun.entities import (
        HostCollection,
    )

    from ansible.module_utils.ansible_nailgun_cement import (
        create_server,
        ping_server,
        find_host_collection,
        find_organization,
        naildown_entity_state,
        sanitize_entity_dict,
    )
    has_import_error = False
except ImportError as e:
    has_import_error = True
    import_error_msg = str(e)

from ansible.module_utils.basic import AnsibleModule


# This is the only true source for names (and conversions thereof)
name_map = {
    'name': 'name',
    'organization': 'organization',
    'description': 'description',
}


def main():
    module = AnsibleModule(
        argument_spec=dict(
            server_url=dict(required=True),
            username=dict(required=True, no_log=True),
            password=dict(required=True, no_log=True),
            verify_ssl=dict(type='bool', default=True),
            name=dict(required=True),
            organization=dict(required=True),
            description=dict(),
            state=dict(default='present', choices=['present_with_defaults', 'present', 'absent']),
        ),
        supports_check_mode=True,
    )

    if has_import_error:
        module.fail_json(msg=import_error_msg)

    entity_dict = dict(
        [(k, v) for (k, v) in module.params.items() if v is not None])

    server_url = entity_dict.pop('server_url')
    username = entity_dict.pop('username')
    password = entity_dict.pop('password')
    verify_ssl = entity_dict.pop('verify_ssl')
    state = entity_dict.pop('state')

    try:
        create_server(server_url, (username, password), verify_ssl)
    except Exception as e:
        module.fail_json(msg="Failed to connect to Foreman server: %s " % e)

    ping_server(module)

    entity_dict['organization'] = find_organization(module, name=entity_dict['organization'])

    entity = find_host_collection(module, name=entity_dict['name'], organization=entity_dict['organization'], failsafe=True)

    entity_dict = sanitize_entity_dict(entity_dict, name_map)

    changed = naildown_entity_state(HostCollection, entity_dict, entity, state, module)

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()
