#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2026 Jakub Duch
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
module: discovered_host
version_added: 5.13.0
short_description: Manage discovered hosts
description:
  - Perform actions on hosts found by the Foreman Discovery plugin.
  - Provisioning executes the first matching discovery rule.
author:
  - "Jakub Duch (@jakduch)"
options:
  name:
    description:
      - Name of the discovered host.
    required: true
    aliases:
      - hostname
    type: str
  action:
    description:
      - Action to perform on the discovered host.
      - C(provision) executes the first matching discovery rule.
      - Deleting a host that does not exist is idempotent.
    required: true
    choices:
      - delete
      - provision
      - reboot
      - refresh
    type: str
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
extends_documentation_fragment:
  - theforeman.foreman.foreman
'''

EXAMPLES = '''
- name: Refresh facts of a discovered host
  theforeman.foreman.discovered_host:
    username: admin
    password: changeme
    server_url: https://foreman.example.com
    name: discovered.example.com
    action: refresh

- name: Provision a discovered host using discovery rules
  theforeman.foreman.discovered_host:
    username: admin
    password: changeme
    server_url: https://foreman.example.com
    name: discovered.example.com
    action: provision

- name: Reboot a discovered host
  theforeman.foreman.discovered_host:
    username: admin
    password: changeme
    server_url: https://foreman.example.com
    name: discovered.example.com
    action: reboot

- name: Delete a discovered host
  theforeman.foreman.discovered_host:
    username: admin
    password: changeme
    server_url: https://foreman.example.com
    name: discovered.example.com
    action: delete
'''

RETURN = '''
result:
  description: Result returned by the Discovery API.
  returned: success and the host exists
  type: dict
'''

from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import (
    ForemanStatelessEntityAnsibleModule,
)


ACTIONS = {
    'delete': 'destroy',
    'provision': 'auto_provision',
    'reboot': 'reboot',
    'refresh': 'refresh_facts',
}


class ForemanDiscoveredHostModule(ForemanStatelessEntityAnsibleModule):
    pass


def main():
    module = ForemanDiscoveredHostModule(
        foreman_spec=dict(
            name=dict(required=True, aliases=['hostname']),
        ),
        argument_spec=dict(
            action=dict(required=True, choices=sorted(ACTIONS)),
        ),
        required_plugins=[('discovery', ['*'])],
    )

    with module.api_connection():
        discovered_host = module.lookup_entity('entity')
        action = module.params['action']

        if discovered_host is None:
            if action == 'delete':
                module.exit_json()
            module.fail_json(msg="Could not find discovered host '{0}'.".format(module.params['name']))

        result = module.resource_action(
            'discovered_hosts',
            ACTIONS[action],
            {'id': discovered_host['id']},
        )
        module.exit_json(result=result)


if __name__ == '__main__':
    main()
