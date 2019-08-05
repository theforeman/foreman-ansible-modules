#!/usr/bin/python
# -*- coding: utf-8 -*-
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

DOCUMENTATION = '''
---
module: foreman_auth_source_ldap
short_description: Manage Foreman LDAP authentication sources using Foreman API
description:
  - Create and Delete Foreman LDAP authentication sources using Foreman API
version_added: "2.9"
author:
  - "Christoffer Reijer (@ephracis) Basalt AB"
requirements:
  - "apypie"
options:
  name:
    description: The name of the LDAP authentication source
    required: true
  host:
    description: The hostname of the LDAP server
    required: true
  port:
    description: The port number of the LDAP server
    required: false
    type: int
    default: 389
  account:
    description: Account name to use when accessing the LDAP server.
    required: false
  account_password:
    description: Account password to use when accessing the LDAP server. Required when using `onthefly_register`
    required: false
  base_dn:
    description: The base DN to use when searching.
    required: false
  attr_login:
    description: Attribute containing login ID. Required when using `onthefly_register`
    required: false
  attr_firstname:
    description: Attribute containing first name. Required when using `onthefly_register`
    required: false
  attr_lastname:
    description: Attribute containing last name. Required when using `onthefly_register`
    required: false
  attr_mail:
    description: Attribute containing email address. Required when using `onthefly_register`
    required: false
  attr_photo:
    description: Attribute containing user photo
    required: false
  onthefly_register:
    description: Whether or not to register users on the fly.
    required: false
    type: bool
  usergroup_sync:
    description: Whether or not to sync external user groups on login
    required: false
    type: bool
  tls:
    description: Whether or not to use TLS when contacting the LDAP server.
    required: false
    type: bool
  groups_base:
    description: Base DN where groups reside.
    required: false
    type: bool
  server_type:
    description: Type of the LDAP server
    required: false
    default: posix
    choices: ["free_ipa", "active_directory", "posix"]
  ldap_filter:
    description: Filter to apply to LDAP searches
    required: false
  organizations:
    description: List of organizations the authentication source should be assigned to
    type: list
  locations:
    description: List of locations the authentication source should be assigned to
    type: list
  state:
    description: State ot the LDAP authentication source
    default: present
    choices: ["present", "absent"]
extends_documentation_fragment: foreman
'''

EXAMPLES = '''
- name: LDAP Authentication source
  foreman_auth_source_ldap:
    name: "Example LDAP"
    host: "ldap.example.org"
    server_url: "https://foreman.example.com"
    locations:
      - "Uppsala"
    organizations:
      - "Sweden"
    username: "admin"
    password: "secret"
    state: present

- name: LDAP Authentication with automatic registration
  foreman_auth_source_ldap:
    name: "Example LDAP"
    host: "ldap.example.org"
    onthefly_register: True
    account: uid=ansible,cn=sysaccounts,cn=etc,dc=example,dc=com
    account_password: secret
    base_dn: dc=example,dc=com
    groups_base: cn=groups,cn=accounts, dc=example,dc=com
    server_type: free_ipa
    attr_login: uid
    attr_firstname: givenName
    attr_lastname: sn
    attr_mail: mail
    attr_photo: jpegPhoto
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
            host=dict(required=True),
            port=dict(type='int', default=389),
            account=dict(),
            account_password=dict(no_log=True),
            base_dn=dict(),
            attr_login=dict(),
            attr_firstname=dict(),
            attr_lastname=dict(),
            attr_mail=dict(),
            attr_photo=dict(),
            onthefly_register=dict(type='bool'),
            usergroup_sync=dict(type='bool'),
            tls=dict(type='bool'),
            groups_base=dict(),
            server_type=dict(choices=["free_ipa", "active_directory", "posix"]),
            ldap_filter=dict(),
            locations=dict(type='entity_list', flat_name='location_ids'),
            organizations=dict(type='entity_list', flat_name='organization_ids'),
        ),
    )

    entity_dict = module.clean_params()

    module.connect()

    entity = module.find_resource_by_name('auth_source_ldaps', name=entity_dict['name'], failsafe=True)

    if not module.desired_absent:
        if 'locations' in entity_dict:
            entity_dict['locations'] = module.find_resources_by_title('locations', entity_dict['locations'], thin=True)

        if 'organizations' in entity_dict:
            entity_dict['organizations'] = module.find_resources_by_name('organizations', entity_dict['organizations'], thin=True)

    changed = module.ensure_entity_state('auth_source_ldaps', entity_dict, entity)

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()

#  vim: set sts=4 ts=8 sw=4 ft=python et noro norl cin si ai :
