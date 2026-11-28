#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2025 Marek Hulan
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
module: host_wake
version_added: 1.0.0
short_description: Send Wake-on-LAN request to host
description:
  - "Send Wake-on-LAN (WOL) request to a host"
author:
  - "Marek Hulan (@ares)"
options:
  name:
    description: Name (FQDN) of the host
    required: true
    aliases:
      - hostname
    type: str
  state:
    description: Wake-on-LAN state
    default: 'on'
    choices:
      - 'on'
    type: str
extends_documentation_fragment:
  - theforeman.foreman.foreman
'''

EXAMPLES = '''
- name: "Send Wake-on-LAN request to host"
  theforeman.foreman.host_wake:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    hostname: "test-host.domain.test"
    state: 'on'

- name: "Wake up multiple hosts"
  theforeman.foreman.host_wake:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    hostname: "{{ item }}"
    state: 'on'
  loop:
    - "host1.domain.test"
    - "host2.domain.test"
    - "host3.domain.test"
'''

RETURN = '''
wol_result:
    description: result of the Wake-on-LAN request
    returned: always
    type: dict
    sample: {"wol": true}
'''

from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import ForemanEntityAnsibleModule


def main():
    module = ForemanEntityAnsibleModule(
        foreman_spec=dict(
            name=dict(aliases=['hostname'], required=True),
        ),
        argument_spec=dict(
            state=dict(default='on', choices=['on']),
        )
    )

    module_params = module.foreman_params

    with module.api_connection():
        # Send Wake-on-LAN request using the wol endpoint
        params = {'id': module_params['name']}
        wol_result = module.resource_action('hosts', 'wol', params=params)

        # Return the result
        module.exit_json(wol_result=wol_result)


if __name__ == '__main__':
    main()
