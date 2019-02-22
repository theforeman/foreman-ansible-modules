#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2017, Matthias M Dellweg <dellweg@atix.de> (ATIX AG)
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
module: foreman_location
short_description: Manage Foreman Location
description:
  - Manage Foreman Location
author:
  - "Matthias M Dellweg (@mdellweg) ATIX AG"
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
  name:
    description:
      - Name or Title of the Foreman Location
    required: true
  parent:
    description:
      - Title of a parent Location for nesting
  organizations:
    description:
      - List of organizations the location should be assigned to
    type: list
  state:
    description:
      - State of the Location
    default: present
    choices:
      - present
      - absent
'''

EXAMPLES = '''
# Create a simple location
- name: "Create CI Location"
  foreman_location:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "My Cool New Location"
    organizations:
      - "Default Organization"
    state: present

# Create a nested location
- name: "Create Nested CI Location"
  foreman_location:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "My Nested location"
    parent: "My Cool New Location"
    state: present

# Create a new nested location with parent included in name
- name: "Create New Nested Location"
  foreman_location:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "My Cool New Location/New nested location"
    state: present

# Move a nested location to another parent
- name: "Create Nested CI Location"
  foreman_location:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "My Cool New Location/New nested location"
    parent: "My Cool New Location/My Nested location"
    state: present
'''

RETURN = ''' # '''

try:
    from ansible.module_utils.ansible_nailgun_cement import (
        find_entities,
        find_location,
        find_organizations,
        naildown_entity_state,
        sanitize_entity_dict,
    )
    from ansible.module_utils.foreman_helper import (
        split_fqn,
        build_fqn,
    )
    from nailgun.entities import Location
except ImportError:
    pass


from ansible.module_utils.foreman_helper import ForemanEntityAnsibleModule


# This is the only true source for names (and conversions thereof)
name_map = {
    'name': 'name',
    'parent': 'parent',
    'organizations': 'organization',
}


def main():
    module = ForemanEntityAnsibleModule(
        argument_spec=dict(
            name=dict(required=True),
            parent=dict(),
            organizations=dict(type='list'),
        ),
        supports_check_mode=True,
    )

    (entity_dict, state) = module.parse_params()

    module.connect()

    name_or_title = entity_dict.pop('name')
    parent = entity_dict.pop('parent', None)

    # Get short name and parent from provided name
    parent_from_title, name = split_fqn(name_or_title)

    entity_dict['name'] = name
    if parent:
        entity_dict['parent'] = find_location(module, parent)
    elif parent_from_title:
        entity_dict['parent'] = find_location(module, parent_from_title)

    if 'organizations' in entity_dict:
        entity_dict['organizations'] = find_organizations(module, entity_dict['organizations'])

    entity = find_location(module, title=build_fqn(name_or_title, parent), failsafe=True)
    entity_dict = sanitize_entity_dict(entity_dict, name_map)

    changed = naildown_entity_state(Location, entity_dict, entity, state, module)

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()
