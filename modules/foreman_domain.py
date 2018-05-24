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
  - nailgun >= 0.16.0
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
  verify_ssl:
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
    verify_ssl: False
    state: present
'''

RETURN = ''' # '''

try:
    from ansible.module_utils.ansible_nailgun_cement import (
        create_server,
        ping_server,
        find_domain,
        find_locations,
        find_organizations,
        find_smart_proxy,
        naildown_entity_state,
        sanitize_entity_dict,
    )

    from nailgun.entities import (
        Domain,
    )

    HAS_IMPORT_ERROR = False
except ImportError as e:
    HAS_IMPORT_ERROR = True
    IMPORT_ERROR = str(e)

from ansible.module_utils.basic import AnsibleModule


# This is the only true source for names (and conversions thereof)
name_map = {
    'name': 'name',
    'description': 'fullname',
    'dns_proxy': 'dns',
    'locations': 'location',
    'organizations': 'organization',
}


def main():
    module = AnsibleModule(
        argument_spec=dict(
            server_url=dict(required=True),
            username=dict(required=True),
            password=dict(required=True, no_log=True),
            verify_ssl=dict(type='bool', default=True),
            name=dict(required=True),
            description=dict(),
            dns_proxy=dict(),
            locations=dict(type='list'),
            organizations=dict(type='list'),
            state=dict(choices=['present', 'absent'], default='present'),
        ),
        supports_check_mode=True,
    )

    if HAS_IMPORT_ERROR:
        module.fail_json(msg=IMPORT_ERROR)

    domain_dict = dict(
        [(k, v) for (k, v) in module.params.items() if v is not None])

    server_url = domain_dict.pop('server_url')
    username = domain_dict.pop('username')
    password = domain_dict.pop('password')
    verify_ssl = domain_dict.pop('verify_ssl')
    state = domain_dict.pop('state')

    try:
        create_server(server_url, (username, password), verify_ssl)
    except Exception as e:
        module.fail_json(msg="Failed to connect to Foreman server: %s " % e)

    ping_server(module)
    try:
        # Try to find the Domain to work on
        entity = find_domain(module, name=domain_dict['name'], failsafe=True)
    except Exception as e:
        module.fail_json(msg='Failed to find entity: %s ' % e)

    if 'dns_proxy' in domain_dict:
        domain_dict['dns_proxy'] = find_smart_proxy(module, domain_dict['dns_proxy'])

    if 'locations' in domain_dict:
        domain_dict['locations'] = find_locations(module, domain_dict['locations'])

    if 'organizations' in domain_dict:
        domain_dict['organizations'] = find_organizations(module, domain_dict['organizations'])

    domain_dict = sanitize_entity_dict(domain_dict, name_map)

    changed = naildown_entity_state(Domain, domain_dict, entity, state, module)

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()

#  vim: set sts=4 ts=8 sw=4 ft=python et noro norl cin si ai :
