#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2017, Andrew Kofink <ajkofink@gmail.com>
# (c) 2019, Baptiste Agasse <baptiste.agasse@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
  - foreman
  - foreman.entity_state
  - foreman.organization
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

RETURN = ''' # '''

from ansible.module_utils.foreman_helper import KatelloEntityAnsibleModule


class KatelloLifecycleEnvironmentModule(KatelloEntityAnsibleModule):
    pass


def main():
    module = KatelloLifecycleEnvironmentModule(
        entity_opts=dict(
            failsafe=True,
        ),
        foreman_spec=dict(
            name=dict(required=True),
            label=dict(),
            description=dict(),
            prior=dict(type='entity', resource_type='lifecycle_environments', scope='organization'),
        ),
    )

<<<<<<< HEAD
    with module.api_connection():
        entity, entity_dict = module.resolve_entities()
        scope = {'organization_id': entity_dict['organization']['id']}

        if not module.desired_absent:
            # Default to 'Library' for new env with no 'prior' provided
            if 'prior' not in entity_dict and not entity:
                entity_dict['prior'] = module.find_resource_by_name('lifecycle_environments', 'Library', params=scope, thin=True)
=======
    module_params = module.clean_params()

    with module.api_connection():
        module_params, scope = module.handle_organization_param(module_params)

        entity = module.find_resource_by_name('lifecycle_environments', name=module_params['name'], params=scope, failsafe=True)
        if not module.desired_absent:
            if 'prior' in module_params:
                module_params['prior'] = module.find_resource_by_name('lifecycle_environments', module_params['prior'], params=scope, thin=True)
            # Default to 'Library' for new env with no 'prior' provided
            elif not entity:
                module_params['prior'] = module.find_resource_by_name('lifecycle_environments', 'Library', params=scope, thin=True)
>>>>>>> Rename entity_dict to module_params

        if entity:
            if 'label' in module_params and module_params['label'] and entity['label'] != module_params['label']:
                module.fail_json(msg="Label cannot be updated on a lifecycle environment.")

            if 'prior' in module_params and entity['prior']['id'] != module_params['prior']['id']:
                module.fail_json(msg="Prior cannot be updated on a lifecycle environment.")

        module.ensure_entity('lifecycle_environments', module_params, entity, params=scope)


if __name__ == '__main__':
    main()
