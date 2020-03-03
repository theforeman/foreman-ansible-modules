#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2017, Andrew Kofink <ajkofink@gmail.com>
# (c) 2019, Baptiste Agasse <baptiste.agasse@gmail.com>
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
module: katello_lifecycle_environment
short_description: Create and Manage Katello lifecycle environments
description:
    - Create and Manage Katello lifecycle environments
author:
  - "Andrew Kofink (@akofink)"
  - "Baptiste Agasse (@bagasse)"
options:
  name:
    description:
      - Name of the lifecycle environment
    required: true
    type: str
  label:
    description:
      - Label of the lifecycle environment. This field cannot be updated.
    type: str
  description:
    description:
      - Description of the lifecycle environment
    type: str
  prior:
    description:
      - Name of the parent lifecycle environment
    type: str
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.entity_state
  - theforeman.foreman.foreman.organization
'''

EXAMPLES = '''
- name: "Add a production lifecycle environment"
  katello_lifecycle_environment:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "Production"
    label: "production"
    organization: "Default Organization"
    prior: "Library"
    description: "The production environment"
    state: "present"
'''

RETURN = '''# '''

from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import KatelloEntityAnsibleModule


def main():
    module = KatelloEntityAnsibleModule(
        entity_spec=dict(
            name=dict(required=True),
            label=dict(),
            description=dict(),
            prior=dict(type='entity'),
        ),
    )

    entity_dict = module.clean_params()

    with module.api_connection():
        entity_dict, scope = module.handle_organization_param(entity_dict)

        entity = module.find_resource_by_name('lifecycle_environments', name=entity_dict['name'], params=scope, failsafe=True)
        if not module.desired_absent:
            if 'prior' in entity_dict:
                entity_dict['prior'] = module.find_resource_by_name('lifecycle_environments', entity_dict['prior'], params=scope, thin=True)
            # Default to 'Library' for new env with no 'prior' provided
            elif not entity:
                entity_dict['prior'] = module.find_resource_by_name('lifecycle_environments', 'Library', params=scope, thin=True)

        if entity:
            if 'label' in entity_dict and entity_dict['label'] and entity['label'] != entity_dict['label']:
                module.fail_json(msg="Label cannot be updated on a lifecycle environment.")

            if 'prior' in entity_dict and entity['prior']['id'] != entity_dict['prior']['id']:
                module.fail_json(msg="Prior cannot be updated on a lifecycle environment.")

        module.ensure_entity('lifecycle_environments', entity_dict, entity, params=scope)


if __name__ == '__main__':
    main()
