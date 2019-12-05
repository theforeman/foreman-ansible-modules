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
  - foreman
  - foreman.state
  - foreman.taxonomy
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

from ansible.module_utils.foreman_helper import (
    ForemanTaxonomicEntityAnsibleModule,
)


def main():
    module = ForemanTaxonomicEntityAnsibleModule(
        entity_spec=dict(
            name=dict(required=True),
        ),
    )

    entity_dict = module.clean_params()

    module.connect()

    entity = module.find_resource_by_name('environments', name=entity_dict['name'], failsafe=True)

    entity_dict = module.handle_taxonomy_params(entity_dict)

    module.ensure_entity('environments', entity_dict, entity)

    module.exit_json()


if __name__ == '__main__':
    main()
