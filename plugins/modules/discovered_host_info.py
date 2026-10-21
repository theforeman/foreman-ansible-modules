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
module: discovered_host_info
version_added: 5.13.0
short_description: Fetch information about discovered hosts
description:
  - Fetch information about hosts found by the Foreman Discovery plugin.
author:
  - "Jakub Duch (@jakduch)"
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.infomodule
'''

EXAMPLES = '''
- name: Show a discovered host
  theforeman.foreman.discovered_host_info:
    username: admin
    password: changeme
    server_url: https://foreman.example.com
    name: discovered.example.com

- name: Show all discovered hosts in a subnet
  theforeman.foreman.discovered_host_info:
    username: admin
    password: changeme
    server_url: https://foreman.example.com
    search: subnet = Provisioning
'''

RETURN = '''
discovered_host:
  description: Details about the found discovered host.
  returned: success and I(name) was passed
  type: dict
discovered_hosts:
  description: List of found discovered hosts and their details.
  returned: success and I(search) was passed
  type: list
  elements: dict
'''

from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import (
    ForemanInfoAnsibleModule,
)


class ForemanDiscoveredHostInfo(ForemanInfoAnsibleModule):
    pass


def main():
    module = ForemanDiscoveredHostInfo(
        required_plugins=[('discovery', ['*'])],
    )

    with module.api_connection():
        module.run()


if __name__ == '__main__':
    main()
