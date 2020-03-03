#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2017, Lester R Claudio <claudiol@redhat.com>
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
module: foreman_realm
short_description: Manage Foreman Realms
description:
  - Manage Foreman Realms
author:
  - "Lester R Claudio (@claudiol1)"
options:
  name:
    description:
      - Name of the Foreman realm
    required: true
    type: str
  realm_proxy:
    description:
      - Proxy to use for this realm
    required: true
    type: str
  realm_type:
    description:
      - Realm type
    choices:
      - Red Hat Identity Management
      - FreeIPA
      - Active Directory
    required: true
    type: str
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.entity_state
  - theforeman.foreman.foreman.taxonomy
'''

EXAMPLES = '''
- name: "Create EXAMPLE.LOCAL Realm"
  foreman_realm:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "EXAMPLE.COM"
    realm_proxy: "foreman.example.com"
    realm_type: "Red Hat Identity Management"
    state: present
'''

RETURN = ''' # '''

from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import ForemanTaxonomicEntityAnsibleModule


class ForemanRealmModule(ForemanTaxonomicEntityAnsibleModule):
    pass


def main():
    module = ForemanRealmModule(
        entity_spec=dict(
            name=dict(required=True),
            realm_proxy=dict(type='entity', required=True, resource_type='smart_proxies'),
            realm_type=dict(required=True, choices=['Red Hat Identity Management', 'FreeIPA', 'Active Directory']),
        ),
    )

    with module.api_connection():
        module.run()


if __name__ == '__main__':
    main()
