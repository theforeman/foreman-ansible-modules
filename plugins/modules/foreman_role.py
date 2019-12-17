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

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: foreman_role
short_description: Manage Foreman Roles using Foreman API
description:
  - Create and Delete Foreman Roles using Foreman API
author:
  - "Christoffer Reijer (@ephracis) Basalt AB"
options:
  name:
    description: The name of the role
    required: true
    type: str
  description:
    description: Description of the role
    required: false
    type: str
  filters:
    description: Filters with permissions for this role
    required: false
    type: list
    elements: dict
    suboptions:
      permissions:
        description: List of permissions
        required: true
        type: list
      search:
        description: Filter condition for the resources
        required: false
        type: str
extends_documentation_fragment:
  - foreman
  - foreman.entity_state
  - foreman.taxonomy
'''

EXAMPLES = '''
- name: role
  foreman_role:
    name: "Provisioner"
    description: "Only provision on libvirt"
    locations:
      - "Uppsala"
    organizations:
      - "Basalt"
    filters:
      - permissions:
          - view_hosts
        search: "owner_type = Usergroup and owner_id = 4"
    server_url: "https://foreman.example.com"
    username: "admin"
    password: "secret"
    state: present
'''

RETURN = ''' # '''

import copy

from ansible.module_utils.foreman_helper import ForemanTaxonomicEntityAnsibleModule


filter_entity_spec = dict(
    permissions=dict(type='entity_list', flat_name='permission_ids', required=True),
    search=dict(),
)


def main():
    module = ForemanTaxonomicEntityAnsibleModule(
        entity_spec=dict(
            name=dict(required=True),
            description=dict(),
            filters=dict(type='nested_list', entity_spec=filter_entity_spec),
        ),
    )

    entity_dict = module.clean_params()

    module.connect()

    entity = module.find_resource_by_name('roles', name=entity_dict['name'], failsafe=True)

    entity_dict = module.handle_taxonomy_params(entity_dict)

    filters = entity_dict.pop("filters", None)

    new_entity = module.ensure_entity('roles', entity_dict, entity)

    if not module.desired_absent and filters is not None:
        scope = {'role_id': new_entity['id']}

        if entity:
            current_filters = [module.show_resource('filters', filter['id']) for filter in entity['filters']]
        else:
            current_filters = []
        desired_filters = copy.deepcopy(filters)

        for desired_filter in desired_filters:
            # search for an existing filter
            for current_filter in current_filters:
                if desired_filter['search'] == current_filter['search']:
                    if set(desired_filter['permissions']) == set(perm['name'] for perm in current_filter['permissions']):
                        current_filters.remove(current_filter)
                        break
            else:
                desired_filter['permissions'] = module.find_resources_by_name('permissions', desired_filter['permissions'], thin=True)
                module.ensure_entity('filters', desired_filter, None, params=scope, state='present', entity_spec=filter_entity_spec)
        for current_filter in current_filters:
            module.ensure_entity('filters', None, {'id': current_filter['id']}, params=scope, state='absent', entity_spec=filter_entity_spec)

    module.exit_json()


if __name__ == '__main__':
    main()
