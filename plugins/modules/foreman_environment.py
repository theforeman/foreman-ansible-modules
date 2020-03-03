#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2018 Bernhard Suttner (ATIX AG)
# (c) 2019 Christoffer Reijer (Basalt AB)
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
module: foreman_environment
short_description: Manage Foreman Environment (Puppet) using Foreman API
description:
  - Create and Delete Foreman Environment using Foreman API
author:
  - "Bernhard Suttner (@_sbernhard) ATIX AG"
  - "Christoffer Reijer (@ephracis) Basalt AB"
options:
  name:
    description: The full environment name
    required: true
    type: str
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.entity_state
  - theforeman.foreman.foreman.taxonomy
'''

EXAMPLES = '''
- name: create new environment
  foreman_environment:
    name: "testing"
    locations:
      - "Munich"
    organizations:
      - "ATIX"
    server_url: "https://foreman.example.com"
    username: "admin"
    password: "secret"
    state: present
'''

RETURN = ''' # '''

from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import (
    ForemanTaxonomicEntityAnsibleModule,
)


class ForemanEnvironmentModule(ForemanTaxonomicEntityAnsibleModule):
    pass


def main():
    module = ForemanEnvironmentModule(
        entity_spec=dict(
            name=dict(required=True),
        ),
    )

    with module.api_connection():
        module.run()


if __name__ == '__main__':
    main()
