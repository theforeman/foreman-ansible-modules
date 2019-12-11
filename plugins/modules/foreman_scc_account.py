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
    description: Name of the scc_account
    required: true
    type: str
  login:
    description: Login id of scc_account
    required: false
    type: str
  scc_account_password:
    description: Password of scc_account
    required: false
    type: str
  base_url:
    description: URL of SUSE for scc_account
    required: false
    type: str
  interval:
    description: Interval for syncing scc_account
    required: false
    type: str
    choices: ["never", "daily", "weekly", "monthly"]
  sync_date:
    description: Last Sync time of scc_account
    required: false
    type: str
  organization:
    description: Name of related organization
    type: str
    required: true
  test_connection:
    description: Test scc_account credentials that connects to the server
    required: false
    default: false
    type: bool
  updated_name:
    description: Name to be updated of scc_account
    type: str
  state:
    description: State of the scc_account
    default: present
    choices: ["present", "absent", "synced"]
    type: str
extends_documentation_fragment:
  - foreman
  - foreman.organization
'''

EXAMPLES = '''
- name: "Create an scc_account"
  foreman_scc_account:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "Test"
    login: "abcde"
    scc_account_password: "12345"
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
            interval=dict(choices=['never', 'daily', 'weekly', 'monthly']),
            state=dict(default='present', choices=['present', 'absent', 'synced']),
        ),
        argument_spec=dict(
            test_connection=dict(type='bool', default=False),
        ),
    )

    entity_dict = module.clean_params()

    module.connect()

    entity_dict, scope = module.handle_organization_param(entity_dict)

    entity = module.find_resource_by_name('scc_accounts', name=entity_dict['name'], params=scope, failsafe=True)

    if not module.desired_absent:
        if not entity:
            if 'login' not in entity_dict:
                module.fail_json(msg="scc account login not provided")
            if 'scc_account_password' not in entity_dict:
                module.fail_json(msg="Scc account password not provided")

        if entity_dict['test_connection']:
            scc_account_credentials = {}
            if entity:
                scc_account_credentials['id'] = entity['id']
            if 'login' in entity_dict:
                scc_account_credentials['login'] = entity_dict['login']
            if 'scc_account_password' in entity_dict:
                scc_account_credentials['password'] = entity_dict['scc_account_password']
            if 'base_url' in entity_dict:
                scc_account_credentials['base_url'] = entity_dict['base_url']
            module.resource_action('scc_accounts', 'test_connection', scc_account_credentials, ignore_check_mode=True)

    if 'updated_name' in entity_dict:
        entity_dict['name'] = entity_dict['updated_name']

    if module.state == 'synced':
        module.resource_action('scc_accounts', 'sync', {'id': entity['id']})
    else:
        module.ensure_entity('scc_accounts', entity_dict, entity, params=scope)

    module.exit_json()


if __name__ == '__main__':
    main()
