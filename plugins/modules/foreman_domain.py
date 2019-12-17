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
  - foreman
  - foreman.entity_state
  - foreman.taxonomy
  - foreman.nested_parameters
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

from ansible.module_utils.foreman_helper import ForemanTaxonomicEntityAnsibleModule, parameter_entity_spec


def main():
    module = ForemanTaxonomicEntityAnsibleModule(
        argument_spec=dict(
            updated_name=dict(),
        ),
        entity_spec=dict(
            name=dict(required=True),
            description=dict(aliases=['fullname'], flat_name='fullname'),
            dns_proxy=dict(type='entity', flat_name='dns_id', aliases=['dns']),
            parameters=dict(type='nested_list', entity_spec=parameter_entity_spec),
        ),
    )

    entity_dict = module.clean_params()

    module.connect()

    # Try to find the Domain to work on
    entity = module.find_resource_by_name('domains', name=entity_dict['name'], failsafe=True)

    entity_dict = module.handle_taxonomy_params(entity_dict)

    if not module.desired_absent:
        if entity and 'updated_name' in entity_dict:
            entity_dict['name'] = entity_dict.pop('updated_name')
        if 'dns_proxy' in entity_dict:
            entity_dict['dns_proxy'] = module.find_resource_by_name('smart_proxies', entity_dict['dns_proxy'], thin=True)

    parameters = entity_dict.get('parameters')

    domain = module.ensure_entity('domains', entity_dict, entity)

    if domain:
        scope = {'domain_id': domain['id']}
        module.ensure_scoped_parameters(scope, entity, parameters)

    module.exit_json()


if __name__ == '__main__':
    main()
