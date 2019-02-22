#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2018 Manuel Bonk (ATIX AG)
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
module: foreman_installation_medium
short_description: Manage Foreman Installation Medium using Foreman API
description:
  - Create and Delete Foreman Installation Medium using Foreman API
version_added: "2.5"
author:
  - "Manuel Bonk(@manuelbonk) ATIX AG"
requirements:
  - "nailgun >= 0.16.0"
  - "ansible >= 2.3"
options:
  name:
    description:
      - |
        The full installation medium name.
        The special name "*" (only possible as parameter) is used to perform bulk actions (modify, delete) on all existing partition tables.
    required: true
  locations:
    description: List of locations the installation medium should be assigned to
    required: false
    type: list
  operatingsystems:
    description: List of operating systems the installation medium should be assigned to
    required: false
    type: list
  organizations:
    description: List of organizations the installation medium should be assigned to
    required: false
    type: list
  os_family:
    description: The OS family the template shall be assigned with. If no os_family is set but a operatingsystem, the value will be derived from it.
    required: false
    choices:
      - AIX
      - Altlinux
      - Archlinux
      - Debian
      - Freebsd
      - Gentoo
      - Junos
      - Redhat
      - Solaris
      - Suse
      - Windows
  path:
    description: Path to the installation medium
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
    description: installation medium presence
    default: present
    choices: ["present", "absent"]
'''

EXAMPLES = '''
- name: create new debian medium
  foreman_installation_medium:
    name: "wheezy"
    locations:
      - "Munich"
    organizations:
      - "ATIX"
    operatingsystems:
      - "Debian"
    path: "http://debian.org/mirror/"
    server_url: "https://foreman.example.com"
    username: "admin"
    password: "secret"
    verify_ssl: False
    state: present
'''

RETURN = ''' # '''

try:
    from ansible.module_utils.ansible_nailgun_cement import (
        find_entities,
        find_installation_medium,
        find_locations,
        find_organizations,
        find_operating_systems_by_title,
        naildown_entity_state,
        sanitize_entity_dict,
    )

    from nailgun.entities import (
        Media,
    )
except ImportError:
    pass

from ansible.module_utils.foreman_helper import ForemanEntityAnsibleModule


# This is the only true source for names (and conversions thereof)
name_map = {
    'locations': 'location',
    'name': 'name',
    'operatingsystems': 'operatingsystem',
    'organizations': 'organization',
    'os_family': 'os_family',
    'path': 'path_',
}


def main():
    module = ForemanEntityAnsibleModule(
        argument_spec=dict(
            name=dict(required=True),
            locations=dict(type='list'),
            organizations=dict(type='list'),
            operatingsystems=dict(type='list'),
            os_family=dict(),
            path=dict(),
        ),
        supports_check_mode=True,
    )

    (medium_dict, state) = module.parse_params()

    module.connect()
    name = medium_dict['name']

    affects_multiple = name == '*'
    # sanitize user input, filter unuseful configuration combinations with 'name: *'
    if affects_multiple:
        if state == 'present_with_defaults':
            module.fail_json(msg="'state: present_with_defaults' and 'name: *' cannot be used together")
        if state == 'absent':
            if list(medium_dict.keys()) != ['name']:
                module.fail_json(msg='When deleting all installation media, there is no need to specify further parameters %s ' % medium_dict.keys())

    try:
        if affects_multiple:
            entities = find_entities(Media)
        else:
            entities = find_installation_medium(module, name=medium_dict['name'], failsafe=True)
    except Exception as e:
        module.fail_json(msg='Failed to find entity: %s ' % e)

    if 'operatingsystems' in medium_dict:
        medium_dict['operatingsystems'] = find_operating_systems_by_title(module, medium_dict['operatingsystems'])
        if len(medium_dict['operatingsystems']) == 1 and 'os_family' not in medium_dict and entities is None:
            medium_dict['os_family'] = medium_dict['operatingsystems'][0].family

    if 'locations' in medium_dict:
        medium_dict['locations'] = find_locations(module, medium_dict['locations'])

    if 'organizations' in medium_dict:
        medium_dict['organizations'] = find_organizations(module, medium_dict['organizations'])

    medium_dict = sanitize_entity_dict(medium_dict, name_map)

    changed = False
    if not affects_multiple:
        changed = naildown_entity_state(
            Media, medium_dict, entities, state, module)
    else:
        medium_dict.pop('name')
        for entity in entities:
            changed |= naildown_entity_state(
                Media, medium_dict, entity, state, module)

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()

#  vim: set sts=4 ts=8 sw=4 ft=python et noro norl cin si ai :
