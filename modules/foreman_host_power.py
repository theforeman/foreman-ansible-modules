#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2019 Bernhard Hopfenmüller (ATIX AG)
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

from ansible.module_utils.foreman_helper import ForemanEntityAnsibleModule
ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: foreman_host_power
short_description: Manage Foreman hosts power state
description:
  - "Manage power state of Foreman host"
  - "This beta version can start and stop an existing foreman host and question the current power state."
version_added: "2.7"
author:
  - "Bernhard Hopfenmueller (@Fobhep) ATIX AG"
requirements:
  - "nailgun >= 0.29.0"
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
  hostname:
    description:
      - fqdn of host
    required: true
  power_state:
    description: Desired power state
    type: list
    choices:
      - on
      - off
      - state
'''

EXAMPLES = '''
- name: "Switch a host on"
  foreman_host_power:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    hostname: "test-host.domain.test"
    state: on

- name: "Switch a host off"
  foreman_host_power:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    hostname: "test-host.domain.test"
    state: off

- name: "Query host power state"
  foreman_host_power:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    hostname: "test-host.domain.test"
    state: state
    register: result
- debug:
    msg: "Host power state is {{ result.power_state }}"


'''

RETURN = '''
power_state:
    description: current power state of host
    returned: always
    type: string
    sample: "off"
 '''

try:
    from nailgun.entities import (
        Host,
    )

    from ansible.module_utils.ansible_nailgun_cement import (
        find_host,
        naildown_power_state,
        query_power_state,
    )
except ImportError:
    pass


def main():
    module = ForemanEntityAnsibleModule(
        argument_spec=dict(
            hostname=dict(required=True),
            state=dict(default='present', choices=['on', 'off', 'state']),
        ),
        supports_check_mode=True,
    )

    (host_dict, state) = module.parse_params()

    module.connect()

    entity = find_host(module, host_dict['hostname'], failsafe=True)

    if state == 'state':
        power_state = query_power_state(module, entity)
        module.exit_json(changed=False, power_state=power_state)

    else:
        changed = naildown_power_state(module, entity, state)
        module.exit_json(changed=changed)


if __name__ == '__main__':
    main()
