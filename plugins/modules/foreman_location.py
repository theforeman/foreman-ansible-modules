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
  - "apypie >= 0.0.2"
options:
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
extends_documentation_fragment: foreman
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

from ansible.module_utils.foreman_helper import (
    build_fqn,
    ForemanEntityApypieAnsibleModule,
    split_fqn,
)


# This is the only true source for names (and conversions thereof)
name_map = {
    'name': 'name',
    'parent': 'parent_id',
    'organizations': 'organization_ids',
}


def main():
    module = ForemanEntityApypieAnsibleModule(
        argument_spec=dict(
            name=dict(required=True),
            parent=dict(),
            organizations=dict(type='list'),
        ),
        supports_check_mode=True,
    )

    entity_dict = module.clean_params()

    module.connect()

    # Get short name and parent from provided name
    name, parent = split_fqn(entity_dict['name'])
    entity_dict['name'] = name

    if 'parent' in entity_dict:
        if parent:
            module.fail_json(msg="Please specify the parent either separately, or as part of the title.")
        parent = entity_dict['parent']
    if parent:
        search_string = 'title="{}"'.format(parent)
        entity_dict['parent'] = module.find_resource('locations', search=search_string, thin=True, failsafe=module.desired_absent)

        if module.desired_absent and entity_dict['parent'] is None:
            # Parent location does not exist so just exit here
            module.exit_json(changed=False)

    if not module.desired_absent:
        if 'organizations' in entity_dict:
            entity_dict['organizations'] = module.find_resources('organizations', entity_dict['organizations'], thin=True)

    entity = module.find_resource('locations', search='title="{}"'.format(build_fqn(name, parent)), failsafe=True)

    changed = module.ensure_resource_state('locations', entity_dict, entity, module.state, name_map)

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()
