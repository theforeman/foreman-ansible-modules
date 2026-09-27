#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2019 Bernhard Hopfenmüller (ATIX AG)
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
module: host_power
version_added: 1.0.0
short_description: Manage the power state of a host
description:
  - Manage the power state of a host.
  - Use M(theforeman.foreman.host_power_info) to query the current power state.
  - The C(state) and C(status) states are kept for backwards compatibility.
author:
  - "Bernhard Hopfenmueller (@Fobhep) ATIX AG"
  - "Baptiste Agasse (@bagasse)"
options:
  name:
    description: Name (FQDN) of the host.
    required: true
    aliases:
      - hostname
    type: str
  state:
    description: Desired power state.
    default: state
    choices:
      - 'on'
      - 'start'
      - 'off'
      - 'stop'
      - 'soft'
      - 'reboot'
      - 'cycle'
      - 'reset'
      - 'state'
      - 'status'
    type: str
extends_documentation_fragment:
  - theforeman.foreman.foreman
'''

EXAMPLES = '''
- name: "Switch a host on"
  theforeman.foreman.host_power:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    hostname: "test-host.domain.test"
    state: 'on'

- name: "Switch a host off"
  theforeman.foreman.host_power:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    hostname: "test-host.domain.test"
    state: 'off'

- name: "Query host power state"
  theforeman.foreman.host_power_info:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    hostname: "test-host.domain.test"
  register: result

- ansible.builtin.debug:
    msg: "Host power state is {{ result.power_state }}"
'''

RETURN = '''
power_state:
    description: current power state of host
    returned: always
    type: str
    sample: "off"
 '''

from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import ForemanEntityAnsibleModule
from ansible_collections.theforeman.foreman.plugins.module_utils.host_power import get_host_power_state


def main():
    module = ForemanEntityAnsibleModule(
        foreman_spec=dict(
            name=dict(aliases=['hostname'], required=True),
        ),
        argument_spec=dict(
            state=dict(default='state', choices=['on', 'start', 'off', 'stop', 'soft', 'reboot', 'cycle', 'reset', 'state', 'status']),
        )
    )

    module_params = module.foreman_params

    with module.api_connection():
        power_state = get_host_power_state(module, module_params['name'])
        params = {'id': module_params['name']}

        if module.state in ['state', 'status']:
            module.exit_json(power_state=power_state)
        elif ((module.state in ['on', 'start'] and power_state == 'on')
              or (module.state in ['off', 'stop'] and power_state == 'off')):
            module.exit_json()
        else:
            params['power_action'] = module.state
            module.resource_action('hosts', 'power', params=params)


if __name__ == '__main__':
    main()
