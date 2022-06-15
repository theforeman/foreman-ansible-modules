#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2022, Jeffrey van Pelt <jeff@vanpelt.one>
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
module: discovery_rule
version_added: x.x.x
short_description: Manage Host Discovery Rules
description:
  - Manage Host Discovery Rules
author:
  - "Jeffrey van Pelt (@Thulium-Drake)"
options:
  name:
    description:
      - Name of the Discovery Rule
    required: true
    type: str
  parent:
    description:
      - Title of a parent Location for nesting
    type: str
  organizations:
    description:
      - List of organizations the location should be assigned to
    type: list
    elements: str
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.entity_state
  - theforeman.foreman.foreman.nested_parameters
'''

EXAMPLES = '''
- name: 'Ensure Discovery Rule'
    theforeman.foreman.discovery_rule:
      username: 'admin'
      password: 'secret_password'
      server_url: 'https://foreman.example.com'
      name: 'my-first-disco'
      search: 'mac = bb:bb:bb:bb:bb:bb'
      hostgroup: 'RedHat7-Base'
      hostname: 'servera'
      max_count: 1
      organizations:
        - 'MyOrg'
      locations:
        - 'DC1'

- name: 'Remove Discovery Rule'
  theforeman.foreman.discovery_rule:
    username: 'admin'
    password: 'secret_password'
    server_url: 'https://foreman.example.com'
    name: 'my-first-disco'
    state: 'absent'
'''

RETURN = '''
entity:
  description: Final state of the affected entities grouped by their type.
  returned: success
  type: dict
  contains:
    discovery_rules:
      description: List of discovery rules.
      type: list
      elements: dict
'''

from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import ForemanEntityAnsibleModule, NestedParametersMixin


class ForemanDiscoveryRuleModule(NestedParametersMixin, ForemanEntityAnsibleModule):
    pass


def main():
    module = ForemanDiscoveryRuleModule(
        foreman_spec=dict(
            name=dict(required=True),
            search=dict(),
            hostgroup=dict(type='entity'),
            hostname=dict(),
            max_count=dict(type='int'),
            priority=dict(type='int'),
            enabled=dict(type='bool'),
            organizations=dict(type='entity_list'),
            locations=dict(type='entity_list'),
        ),
        required_if=[
            ['state', 'present', ['hostgroup', 'search']],
        ],
    )

    with module.api_connection():
        module.run()


if __name__ == '__main__':
    main()
