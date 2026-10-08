#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2026, Jakub Duchek (@jakduch)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: ansible_roles_sync
version_added: 5.13.0
short_description: Sync Ansible roles from a Smart Proxy
description:
  - Sync Ansible roles and their variables from a Smart Proxy.
  - When I(roles) is omitted, all detected changes are synchronized.
author:
  - "Jakub Duchek (@jakduch)"
options:
  smart_proxy:
    description:
      - Smart Proxy to synchronize Ansible roles from.
    required: true
    type: str
  roles:
    description:
      - Names of the Ansible roles to synchronize.
      - If omitted, all roles with detected changes are synchronized.
    required: false
    type: list
    elements: str
    aliases:
      - role_names
extends_documentation_fragment:
  - theforeman.foreman.foreman
'''

EXAMPLES = '''
- name: Sync all Ansible roles from a Smart Proxy
  theforeman.foreman.ansible_roles_sync:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    smart_proxy: "foreman-proxy.example.com"

- name: Sync selected Ansible roles from a Smart Proxy
  theforeman.foreman.ansible_roles_sync:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    smart_proxy: "foreman-proxy.example.com"
    roles:
      - namespace.role
'''

RETURN = '''
roles:
  description: Ansible role changes selected for synchronization.
  returned: success
  type: list
  elements: dict
task:
  description: Foreman task which performed the synchronization.
  returned: when changes are synchronized outside check mode
  type: dict
'''

from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import ForemanAnsibleModule


def main():
    module = ForemanAnsibleModule(
        foreman_spec=dict(
            smart_proxy=dict(type='entity', required=True),
            roles=dict(type='list', elements='str', aliases=['role_names']),
        ),
        required_plugins=[('ansible', ['*'])],
    )

    module.task_timeout = 10 * 60

    with module.api_connection():
        smart_proxy = module.lookup_entity('smart_proxy')
        proxy_params = {'proxy_id': smart_proxy['id']}
        result = module.resource_action(
            'ansible_roles',
            'fetch',
            proxy_params,
            ignore_check_mode=True,
            record_change=False,
        )
        roles = result.get('results', {}).get('ansible_roles', [])

        requested_roles = module.foreman_params.get('roles')
        if requested_roles is not None:
            requested_roles = set(requested_roles)
            roles = [role for role in roles if role['name'] in requested_roles]

        task = None
        if roles:
            if module.check_mode:
                module.set_changed()
            else:
                sync_params = proxy_params.copy()
                sync_params['role_names'] = [role['name'] for role in roles]
                task = module.resource_action('ansible_roles', 'sync', sync_params, record_change=False)
                if task and task.get('id'):
                    task = module.wait_for_task(task)
                    module.set_changed()

        module.exit_json(roles=roles, task=task)


if __name__ == '__main__':
    main()
