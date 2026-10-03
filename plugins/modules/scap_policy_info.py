#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2026 Dennis Lamm (@expeditioneer)
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
module: scap_policy_info
version_added: 5.12.0
short_description: Fetch information about SCAP policies
description:
  - Fetch information about OpenSCAP compliance policies.
author:
  - "Dennis Lamm (@expeditioneer)"
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.infomodule
'''

EXAMPLES = '''
- name: "Show a SCAP policy"
  theforeman.foreman.scap_policy_info:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "AlmaLinux 10 CIS"

- name: "Show all CIS SCAP policies"
  theforeman.foreman.scap_policy_info:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    search: "name ~ CIS"
'''

RETURN = '''
policy:
  description: Details about the found SCAP policy
  returned: success and I(name) was passed
  type: dict
policies:
  description: List of all found SCAP policies and their details
  returned: success and I(search) was passed
  type: list
  elements: dict
'''

from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import (
    ForemanInfoAnsibleModule,
)


class ForemanScapPolicyInfo(ForemanInfoAnsibleModule):
    pass


def main():
    module = ForemanScapPolicyInfo(
        entity_name='policy',
        required_plugins=[('openscap', ['*'])],
    )

    with module.api_connection():
        module.run()


if __name__ == '__main__':
    main()
