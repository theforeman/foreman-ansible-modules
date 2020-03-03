#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2017, Matthias M Dellweg <dellweg@atix.de> (ATIX AG)
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
module: foreman_location
short_description: Manage Foreman Location
description:
  - Manage Foreman Location
author:
  - "Matthias M Dellweg (@mdellweg) ATIX AG"
options:
  name:
    description:
      - Name or Title of the Foreman Location
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
'''

EXAMPLES = '''
# Create a simple location
- name: "Create CI Location"
  foreman_location:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "My Cool New Location"
    organizations:
      - "Default Organization"
    state: present

# Create a nested location
- name: "Create Nested CI Location"
  foreman_location:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "My Nested location"
    parent: "My Cool New Location"
    state: present

# Create a new nested location with parent included in name
- name: "Create New Nested Location"
  foreman_location:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "My Cool New Location/New nested location"
    state: present

# Move a nested location to another parent
- name: "Create Nested CI Location"
  foreman_location:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "My Cool New Location/New nested location"
    parent: "My Cool New Location/My Nested location"
    state: present
'''

RETURN = ''' # '''

from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import ForemanEntityAnsibleModule


class ForemanLocationModule(ForemanEntityAnsibleModule):
    pass


def main():
    module = ForemanLocationModule(
        entity_spec=dict(
            name=dict(required=True),
            parent=dict(type='entity'),
            organizations=dict(type='entity_list'),
        ),
    )

    with module.api_connection():
        module.run()


if __name__ == '__main__':
    main()
