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
version_added: "2.5"
author:
  - "Markus Bucher (@m-bucher) ATIX AG"
requirements:
  - "apypie"
options:
  name:
    description: The full DNS domain name
    required: true
  dns_proxy:
    description: DNS proxy to use within this domain for managing A records
    required: false
  description:
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
  server_url:
    description: foreman url
    required: true
  username:
    description: foreman username
    required: true
  password:
    description: foreman user password
    required: true
  validate_certs:
    aliases: [ verify_ssl ]
    description: verify ssl connection when communicating with foreman
    default: true
    type: bool
  state:
    description: domain presence
    default: present
    choices: ["present", "absent"]
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
    validate_certs: False
    state: present
'''

RETURN = ''' # '''

from ansible.module_utils.foreman_helper import ForemanEntityApypieAnsibleModule


# This is the only true source for names (and conversions thereof)
name_map = {
    'name': 'name',
    'description': 'fullname',
    'dns_proxy': 'dns_id',
    'locations': 'location_ids',
    'organizations': 'organization_ids',
}


def main():
    module = ForemanEntityApypieAnsibleModule(
        argument_spec=dict(
            name=dict(required=True),
            description=dict(),
            dns_proxy=dict(),
            locations=dict(type='list'),
            organizations=dict(type='list'),
        ),
        supports_check_mode=True,
    )

    (domain_dict, state) = module.parse_params()

    module.connect()

    # Try to find the Domain to work on
    entity = module.find_resource_by_name('domains', name=domain_dict['name'], failsafe=True)

    if 'dns_proxy' in domain_dict:
        domain_dict['dns_proxy'] = module.find_resource_by_name('smart_proxies', domain_dict['dns_proxy'], thin=True)

    if 'locations' in domain_dict:
        domain_dict['locations'] = module.find_resources('locations', domain_dict['locations'], thin=True)

    if 'organizations' in domain_dict:
        domain_dict['organizations'] = module.find_resources('organizations', domain_dict['organizations'], thin=True)

    changed = module.ensure_resource_state('domains', domain_dict, entity, state, name_map)

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()

#  vim: set sts=4 ts=8 sw=4 ft=python et noro norl cin si ai :
