#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2026 Jakub Duchek
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


DOCUMENTATION = '''
---
module: template_combination
version_added: 5.13.0
short_description: Manage provisioning template and host group associations
description:
  - Create and remove associations between provisioning templates and host groups.
author:
  - "Jakub Duchek (@jakduch)"
options:
  provisioning_template:
    description:
      - Name of the provisioning template.
    required: true
    type: str
  hostgroup:
    description:
      - Title of the host group.
    required: true
    type: str
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.entity_state
'''

EXAMPLES = '''
- name: Associate a provisioning template with a host group
  theforeman.foreman.template_combination:
    username: admin
    password: changeme
    server_url: https://foreman.example.com
    provisioning_template: Kickstart default
    hostgroup: Base/Production
    state: present

- name: Remove a provisioning template association from a host group
  theforeman.foreman.template_combination:
    username: admin
    password: changeme
    server_url: https://foreman.example.com
    provisioning_template: Kickstart default
    hostgroup: Base/Production
    state: absent
'''

RETURN = '''
entity:
  description: Final state of the affected entities grouped by their type.
  returned: success
  type: dict
  contains:
    template_combinations:
      description: List of provisioning template and host group associations.
      type: list
      elements: dict
'''


from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import ForemanEntityAnsibleModule


class ForemanTemplateCombinationModule(ForemanEntityAnsibleModule):
    def _create_entity(self, resource, desired_entity, params, foreman_spec):
        payload = {
            'provisioning_template_id': params['provisioning_template_id'],
            'template_combination': {
                'hostgroup_id': desired_entity['hostgroup']['id'],
            },
        }
        if self.check_mode:
            self.set_changed()
            fake_entity = desired_entity.copy()
            fake_entity['id'] = -1
            return fake_entity
        return self.resource_action(resource, 'create', payload)


def main():
    module = ForemanTemplateCombinationModule(
        foreman_spec=dict(
            provisioning_template=dict(required=True, type='entity', ensure=False),
            hostgroup=dict(required=True, type='entity'),
        ),
        entity_opts=dict(resolve=False),
    )

    with module.api_connection():
        provisioning_template = module.lookup_entity('provisioning_template')
        hostgroup = module.lookup_entity('hostgroup')
        scope = {'provisioning_template_id': provisioning_template['id']}

        combinations = module.list_resource('template_combinations', params=scope)
        entity = next((item for item in combinations if item['hostgroup_id'] == hostgroup['id']), None)
        module.set_entity('entity', entity)

        module.run(params=scope)


if __name__ == '__main__':
    main()
