#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2019 Manisha Singhal (ATIX AG)
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
module: compute_attribute
short_description: Manage Compute Attributes
description:
  - "Manage Compute Attributes"
  - "This beta version can create, and update compute attributes"
author:
  - "Manisha Singhal (@Manisha15) ATIX AG"
options:
  compute_resource:
    description:
      - Name of compute resource
    required: true
    type: str
  compute_profile:
    description:
      - Name of compute profile
    required: true
    type: str
  vm_attrs:
    description:
      - Hash containing the data of vm_attrs
    required: false
    aliases:
      - vm_attributes
    type: dict
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.entity_state
'''

EXAMPLES = '''
- name: "Create compute attribute"
  compute_attribute:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    compute_profile: "Test Compute Profile"
    compute_resource: "Test Compute Resource"
    vm_attrs:
      memory_mb: '2048'
      cpu: '2'
    state: present

- name: "Update compute attribute"
  compute_attribute:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    compute_profile: "Test Compute Profile"
    compute_resource: "Test Compute Resource"
    vm_attrs:
      memory_mb: '1024'
      cpu: '1'
    state: present
'''

RETURN = ''' # '''

from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import ForemanEntityAnsibleModule


class ForemanComputeAttributeModule(ForemanEntityAnsibleModule):
    pass


def main():
    module = ForemanComputeAttributeModule(
        foreman_spec=dict(
            compute_profile=dict(required=True, type='entity'),
            compute_resource=dict(required=True, type='entity', thin=False),
            vm_attrs=dict(type='dict', aliases=['vm_attributes']),
        ),
        entity_opts=dict(resolve=False),
        entity_resolve=False,
    )

    with module.api_connection():
        compute_attributes = module.lookup_entity('compute_resource').get('compute_attributes')
        compute_profile_id = module.lookup_entity('compute_profile').get('id')
        entity = next((item for item in compute_attributes if item.get('compute_profile_id') == compute_profile_id), None)
        module.set_entity('entity', entity)
        module.run()


if __name__ == '__main__':
    main()
