#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2018 Markus Bucher (ATIX AG)
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
module: foreman_domain
short_description: Manage Foreman Domains using Foreman API
description:
  - Create and Delete Foreman Domains using Foreman API
author:
  - "Markus Bucher (@m-bucher) ATIX AG"
options:
  name:
    description: The full DNS domain name
    required: true
    type: str
  updated_name:
    description: New domain name. When this parameter is set, the module will not be idempotent.
    type: str
  dns_proxy:
    aliases:
      - dns
    description: DNS proxy to use within this domain for managing A records
    required: false
    type: str
  description:
    aliases:
      - fullname
    description: Full name describing the domain
    required: false
    type: str
  parameters:
    description:
      - Domain specific host parameters
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.entity_state
  - theforeman.foreman.foreman.taxonomy
  - theforeman.foreman.foreman.nested_parameters
'''

EXAMPLES = '''
- name: domain
  foreman_domain:
    name: "example.org"
    description: "Example Domain"
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

from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import ForemanTaxonomicEntityAnsibleModule, parameter_entity_spec


class ForemanDomainModule(ForemanTaxonomicEntityAnsibleModule):
    pass


def main():
    module = ForemanDomainModule(
        argument_spec=dict(
            updated_name=dict(),
        ),
        entity_spec=dict(
            name=dict(required=True),
            description=dict(aliases=['fullname'], flat_name='fullname'),
            dns_proxy=dict(type='entity', flat_name='dns_id', aliases=['dns'], resource_type='smart_proxies'),
            parameters=dict(type='nested_list', entity_spec=parameter_entity_spec),
        ),
    )

    with module.api_connection():
        module.run()


if __name__ == '__main__':
    main()
