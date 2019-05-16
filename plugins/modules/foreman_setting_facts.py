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
                    'status': ['deprecated'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: foreman_setting_facts
deprecated:
  removed_in: "2.8"
  why: This has been replaced with another module.
  alternative: Use M(foreman_search_facts) instead.
short_description: Gather facts about Foreman Settings
description:
  - "Gather facts about Foreman Settings"
author:
  - "Matthias M Dellweg (@mdellweg) ATIX AG"
requirements:
  - "nailgun >= 0.30.2"
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
      - Name of the Setting to fetch
      - If not given, fetch all settings
    required: false
'''

EXAMPLES = '''
- name: "Read a Setting"
  foreman_setting_facts:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "http_proxy"
  register: result
- debug:
    var: result.settings[0].value

- name: "Read all Settings"
  foreman_setting_facts:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
  register: result
- debug:
    var: item.name
  with_items: result.settings
'''

RETURN = '''
settings:
  description: List of settings
'''

try:
    from ansible.module_utils.ansible_nailgun_cement import (
        create_server,
        ping_server,
        find_entities,
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
    'description': 'description',
    'value': 'value',
    'default': 'default',
    'type': 'settings_type',
    'created_at': 'created_at',
    'updated_at': 'updated_at',
}


def main():
    module = AnsibleModule(
        argument_spec=dict(
            server_url=dict(required=True),
            username=dict(required=True),
            password=dict(required=True, no_log=True),
            verify_ssl=dict(type='bool', default=True),
            name=dict(),
        ),
        supports_check_mode=True,
    )

    if has_import_error:
        module.fail_json(msg=import_error_msg)

    params_dict = dict(
        [(k, v) for (k, v) in module.params.items() if v is not None])

    server_url = params_dict.pop('server_url')
    username = params_dict.pop('username')
    password = params_dict.pop('password')
    verify_ssl = params_dict.pop('verify_ssl')

    try:
        create_server(server_url, (username, password), verify_ssl)
    except Exception as e:
        module.fail_json(msg="Failed to connect to Foreman server: %s " % e)

    ping_server(module)

    search_params = {k: v for (k, v) in params_dict.items() if k == 'name'}
    entities = find_entities(Setting, **search_params)
    settings = [{key: getattr(entity, value) for (key, value) in name_map.items()}
                for entity in entities]

    module.exit_json(changed=False, settings=settings)


if __name__ == '__main__':
    main()
