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

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: foreman_scc_account
short_description: Manage Foreman SccAccount
description:
  - "Manage Foreman SccAccount Entities"
  - "This module requires the foreman_scc_manager plugin set up in the server"
  - "See: U(https://github.com/ATIX-AG/foreman_scc_manager)"
author:
  - "Manisha Singhal (@manisha15) ATIX AG"
options:
  name:
    description:
      - Name of the scc_account
    required: true
    type: str
  login:
    description:
      - Login id of scc_account
    required: true
    type: str
  password:
    description:
      - Password of scc_account
    required: true
    type: str
  base_url:
     description:
      - URL of SUSE for scc_account
    required: true
    type: str
  interval:
    description:
      - Interval for syncing scc_account
    required: false
    type: str
    choices:
      - never
      - daily
      - weekly
      - monthly
  sync_date:
    description:
      - Last Sync time of scc_account
    required: false
    type: str
  organization:
    description:
      - Name of related organization
    type: str
  state:
    description:
      - State of the scc_account
    default: present
    choices:
      - present
      - absent
    type: str
extends_documentation_fragment: foreman
'''

EXAMPLES = '''
- name: "Create an scc_account"
  foreman_scc_account:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "Test"
    login: "abcde"
    password: "12345"
    base_url: "https://scc.suse.com"
    state: present

- name: "Update a scc_account"
  foreman_scc_account:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "Test1"
    state: present

- name: "Delete a scc_account"
  foreman_scc_account:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "Test"
    state: absent
'''

RETURN = ''' # '''


from ansible.module_utils.foreman_helper import KatelloEntityAnsibleModule


def main():
    module = KatelloEntityAnsibleModule(
        entity_spec=dict(
            name=dict(required=True),
            updated_name=dict(),
            login=dict(),
            scc_account_password=dict(no_log=True, flat_name='password'),
            base_url=dict(),
            sync_date=dict(),
            interval=dict(default='never', choices=['never', 'daily', 'weekly', 'monthly']),
            state=dict(default='present', choices=['present', 'absent', 'sync', 'test_connection', 'bulk_subscribe']),
        ),
    )

    entity_dict = module.clean_params()

    module.connect()

    entity_dict['organization'] = module.find_resource_by_name('organizations', entity_dict['organization'], thin=True)

    scope = {'organization_id': entity_dict['organization']['id']}

    entity = module.find_resource_by_name('scc_accounts', name=entity_dict['name'], params=scope, failsafe=True)

    if 'updated_name' in entity_dict:
        entity_dict['name'] = entity_dict['updated_name']

    if module.state == 'sync':
        result = module.foremanapi.resource('scc_accounts').call('sync', {'id': entity['id']})
        if result:
            changed = True
    elif module.state == 'test_connection':
        scc_account_credentials = {'login': entity_dict['login'], 'password': entity_dict['scc_account_password']}
        result = module.foremanapi.resource('scc_accounts').call('test_connection', scc_account_credentials)
        changed = True
    else:
        changed = module.ensure_entity_state('scc_accounts', entity_dict, entity, params=scope)
    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()
