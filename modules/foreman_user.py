#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2018, Ondřej Gajdušek ogajduse@redhat.com>
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
module: foreman_user
short_description: Manage Foreman User
description:
    - Manage Foreman User
author:
    - "Ondřej Gajdušek (@ogajduse)"
requirements:
    - "nailgun >= 0.28.0"
    - "python >= 2.6"
    - "ansible >= 2.3"
options:
  server_url:
    description:
      - URL of Foreman server
    required: true
  username:
    description:
      - Username on Foreman server
    required: true
  password:
    description:
      - Password for user accessing Foreman server
    required: true
  verify_ssl:
    description:
      - Verify SSL of the Foreman server
    required: false
    default: true
    type: bool
  login:
    description:
      - Login of the Foreman user
    required: true
  user_password:
    description:
      - Password for the given Foreman login
    required: true
  first_name:
    description:
      - First name of the user
    required: false
  last_name:
    description:
      - Last name of the user
    required: false
  admin:
    description:
      - Give admin rights to the user
    required: false
    default: false
    type: bool
  default_location:
    description:
      - Name of the default location the user is in
    required: false
  default_organization:
    description:
      - Name of the default organization the user is in
    required: false
  auth_source:
    description:
      - Authentication source the user is authorized by
    default: INTERNAL
    required: true
  locations:
    description:
      - Locations that the user is in
    required: false
    default: None
    type: list
  organizations:
    description:
      - Organizations that the user is in
    required: false
    default: None
    type: list
  roles:
    description:
      - Roles to be assigned to the user
    required: false
    default: None
    type: list
  mail:
    description:
      - Mail of the user
    required: false
'''

EXAMPLES = '''
- name: "Create a new User"
  foreman_user:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    login: "exampleuser"
    user_password: "secret"
    first_name: "Example"
    last_name: "User"
    admin: false
    default_location: "Default Location"
    default_organization: "Default Organization"
    auth_source: "INTERNAL"
    locations:
      - "Default Location"
      - "My Cool New Location"
    organizations:
      - "Default Location"
    mail: "exampleuser@example.com"
    state: present
'''

RETURN = '''# '''

try:
    from ansible.module_utils.ansible_nailgun_cement import (
        create_server,
        ping_server,
        find_user,
        naildown_entity_state,
        sanitize_entity_dict,
        find_auth_source_ldap,
        find_organizations,
        find_organization,
        find_roles,
        find_locations,
        find_location,
    )
    from nailgun.entities import User

    has_import_error = False
except ImportError as e:
    has_import_error = True
    import_error_msg = str(e)


from ansible.module_utils.basic import AnsibleModule


# This is the only true source for names (and conversions thereof)
name_map = {
    'login': 'login',
    'first_name': 'firstname',
    'last_name': 'lastname',
    'mail': 'mail',
    'admin': 'admin',
    'user_password': 'password',
    'default_location': 'default_location',
    'default_organization': 'default_organization',
    'auth_source': 'auth_source',
    'locations': 'location',
    'organizations': 'organization',
    'roles': 'role',
}


def main():
    module = AnsibleModule(
        argument_spec=dict(
            server_url=dict(required=True),
            username=dict(required=True, no_log=True),
            password=dict(required=True, no_log=True),
            verify_ssl=dict(type='bool', default=True),
            login=dict(required=True),
            first_name=dict(),
            last_name=dict(),
            mail=dict(),
            admin=dict(type='bool', default=False),
            user_password=dict(required=True, no_log=True),
            default_location=dict(),
            default_organization=dict(),
            auth_source=dict(default='INTERNAL'),
            locations=dict(type='list'),
            organizations=dict(type='list'),
            roles=dict(type='list'),
            state=dict(default='present', choices=['present', 'absent']),
        ),
        supports_check_mode=True,
    )

    if has_import_error:
        module.fail_json(msg=import_error_msg)

    entity_dict = dict(
        [(k, v) for (k, v) in module.params.items() if v is not None])

    server_url = entity_dict.pop('server_url')
    username = entity_dict.pop('username')
    password = entity_dict.pop('password')
    verify_ssl = entity_dict.pop('verify_ssl')
    state = entity_dict.pop('state')

    try:
        create_server(server_url, (username, password), verify_ssl)
    except Exception as e:
        module.fail_json(msg="Failed to connect to Foreman server: %s " % e)

    ping_server(module)

    if entity_dict['auth_source'] == 'INTERNAL':
        entity_dict['auth_source'] = 1
    else:
        entity_dict['auth_source'] = find_auth_source_ldap(module, name=entity_dict['auth_source'])

    if 'default_organization' in entity_dict:
        entity_dict['default_organization'] = find_organization(module, name=entity_dict['default_organization'])

    if 'default_location' in entity_dict:
        entity_dict['default_location'] = find_location(module, name=entity_dict['default_location'])

    if 'organizations' in entity_dict:
        entity_dict['organizations'] = find_organizations(module, entity_dict['organizations'])

    if 'locations' in entity_dict:
        entity_dict['locations'] = find_locations(module, entity_dict['locations'])

    if 'roles' in entity_dict:
        entity_dict['roles'] = find_roles(module, entity_dict['roles'])

    entity = find_user(module, login=entity_dict['login'], failsafe=True)

    entity_dict = sanitize_entity_dict(entity_dict, name_map)

    changed = naildown_entity_state(User, entity_dict, entity, state, module)

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()
