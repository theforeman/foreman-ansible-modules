#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2026 Jakub Duchek
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
module: host_power_info
version_added: 5.13.0
short_description: Fetch the power state of a host
description:
  - Fetch the current power state of a host.
author:
  - "Jakub Duchek (@jakduch)"
options:
  name:
    description: Name (FQDN) of the host.
    required: true
    aliases:
      - hostname
    type: str
extends_documentation_fragment:
  - theforeman.foreman.foreman
'''

EXAMPLES = '''
- name: Query host power state
  theforeman.foreman.host_power_info:
    username: admin
    password: changeme
    server_url: https://foreman.example.com
    hostname: test-host.domain.test
  register: result

- name: Show host power state
  ansible.builtin.debug:
    msg: "Host power state is {{ result.power_state }}"
'''

RETURN = '''
power_state:
  description: Current power state of the host.
  returned: always
  type: str
  sample: "off"
'''

from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import ForemanAnsibleModule
from ansible_collections.theforeman.foreman.plugins.module_utils.host_power import get_host_power_state


def main():
    module = ForemanAnsibleModule(
        foreman_spec=dict(
            name=dict(aliases=['hostname'], required=True),
        ),
    )

    with module.api_connection():
        power_state = get_host_power_state(module, module.foreman_params['name'])
        module.exit_json(power_state=power_state)


if __name__ == '__main__':
    main()
