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

DOCUMENTATION = '''
---
module: foreman_domain
short_description: Manage Foreman Domains using Foreman API
description:
  - Create and Delete Foreman Domains using Foreman API
author:
  - "Markus Bucher (@m-bucher) ATIX AG"
requirements:
  - "apypie"
options:
  name:
    description: The full DNS domain name
    required: true
  dns_proxy:
    aliases:
      - dns
    description: DNS proxy to use within this domain for managing A records
    required: false
  fullname:
    aliases:
      - description
    description: Full name describing the domain
    required: false
  locations:
    description: List of locations the domain should be assigned to
    required: false
    default: None
    type: list
  organizations:
    description: List of organizations the domain should be assigned to
    required: false
    default: None
    type: list
  state:
    description: domain presence
    default: present
    choices: ["present", "absent"]
extends_documentation_fragment: foreman
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

from ansible.module_utils.foreman_helper import ForemanEntityApypieAnsibleModule


def main():
    module = ForemanEntityApypieAnsibleModule(
        entity_spec=dict(
            name=dict(required=True),
            fullname=dict(aliases=['description']),
            dns_proxy=dict(type='entity', flat_name='dns_id', aliases=['dns']),
            locations=dict(type='entity_list', flat_name='location_ids'),
            organizations=dict(type='entity_list', flat_name='organization_ids'),
        ),
    )

    entity_dict = module.clean_params()

    module.connect()

    # Try to find the Domain to work on
    entity = module.find_resource_by_name('domains', name=entity_dict['name'], failsafe=True)

    if not module.desired_absent:
        if 'dns_proxy' in entity_dict:
            entity_dict['dns_proxy'] = module.find_resource_by_name('smart_proxies', entity_dict['dns_proxy'], thin=True)

        if 'locations' in entity_dict:
            entity_dict['locations'] = module.find_resources_by_title('locations', entity_dict['locations'], thin=True)

        if 'organizations' in entity_dict:
            entity_dict['organizations'] = module.find_resources_by_name('organizations', entity_dict['organizations'], thin=True)

    changed = module.ensure_entity_state('domains', entity_dict, entity)

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()

#  vim: set sts=4 ts=8 sw=4 ft=python et noro norl cin si ai :
