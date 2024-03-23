#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2021 Martin Grundei (ATIX AG)
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

from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import ForemanEntityAnsibleModule, parameter_value_to_str
from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import _foreman_spec_helper, _flatten_entity

DOCUMENTATION = '''
---
module: ansible_variable
version_added: 2.1.0
short_description: Manage Ansible Variables
description:
  - "Manage Ansible Parameter Entities"
author:
  - "Martin Grundei (@cru90) ATIX AG"
options:
  variable:
    description:
      - Name of the Ansible variable
    aliases:
      - name
    required: true
    type: str
  default_value:
    description:
      - Default value of the Ansible variable
    type: raw
  ansible_role:
    description:
      - Ansible role the variable is assigned to
    required: true
    type: str
  parameter_type:
    description:
      - Type of default_value
    default: string
    choices:
      - string
      - boolean
      - integer
      - real
      - array
      - hash
      - yaml
      - json
  hidden_value:
    description:
      - When enabled the parameter is hidden in the UI
    choices:
      - True
      - False
      - 1
      - 0
    type: bool
  override_value_order:
    description:
      - The order in which values are resolved
      - Must be a string separated by new lines, e.g "fqdn\nhostgroup\nos\ndomain"
    type: str
  description:
    description:
      - Description of variable
    type: str
  validator_type:
    description:
      - Types of validation values
      - Valid only in combination with validator_rule
    choices:
      - regexp
      - list
  validator_rule:
    description:
      - Used to enforce certain values for the parameter values
    type:str
  merge_overrides:
    description:
      - Merge all matching values (only array/hash type)
    choices:
      - True
      - False
      - 1
      - 0
    type: bool
  merge_default:
    description:
      - Include default value when merging all matching values
    choices:
      - True
      - False
      - 1
      - 0
    type: bool
  avoid_duplicates:
    description:
      - Remove duplicate values (only array type)
    choices:
      - True
      - False
      - 1
      - 0
    type: bool
  override:
    description:
      - Whether to override variable or not
    choices:
      - True
      - False
      - 1
      - 0
    type: bool
  override_values:
    description: Value overrides
    required: false
    type: list
    elements: dict
    suboptions:
      match:
        description: Override match
        required: true
        type: string
      value:
        description: Override value, required if omit is false
        type: raw
  state:
    description: State of the entity.
    type: str
    default: present
    choices:
      - present
      - present_with_defaults
      - absent
'''

EXAMPLES = '''
- name: "Create an Ansible Variable"
  theforeman.foreman.ansible_variable:
    variable: "TheAnswer"
    ansible_role: my_role
    default_value: "I do not know"
    variable_type: "string"
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    state: present_with_defaults

- name: "Update an Ansible Variable"
  theforeman.foreman.ansible_variable:
    variable: "TheAnswer"
    ansible_role: my_role
    default_value: 42
    variable_type: "integer"
    override_values:
      - match: "domain=my_domain"
        value: "44"
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    state: present

- name: "Delete an Ansible Variable"
  theforeman.foreman.ansible_variable:
    variable: "TheAnswer"
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    state: absent
'''

RETURN = '''
entity:
  description: Final state of the affected entity grouped by their type.
  returned: success
  type: dict
  contains:
    ansible_variables:
      description: Dict of Ansible variable
      type: dict
      elements: dict
'''
override_value_spec = dict(
    id=dict(invisible=True),
    match=dict(required=True, alias=['name']),
    value=dict(type='raw', required=True),
)


class AnsibleAnsibleVariableModule(ForemanEntityAnsibleModule):
    def ensure_override_values(self, entity, expected_override_values):
        if not self.desired_absent:
            if expected_override_values is not None:
                parameter_type = entity.get('variable_type', 'string')
                scope = {'ansible_variable_id': entity['id']}
                current_override_values = {override_value['match']: override_value for override_value in entity.get('override_values', [])}
                desired_override_values = {override_value['match']: override_value for override_value in expected_override_values}
                for match in desired_override_values:
                    desired_override_value = desired_override_values[match]
                    if 'value' in desired_override_value:
                        desired_override_value['value'] = parameter_value_to_str(desired_override_value['value'], parameter_type)
                    current_override_value = current_override_values.pop(match, None)
                    if current_override_value:
                        current_override_value['value'] = parameter_value_to_str(current_override_value['value'], parameter_type)

                    if self.state == "present_with_defaults":
                        self.ensure_entity(
                            'ansible_override_values', desired_override_value, current_override_value,
                            state="present_with_defaults", foreman_spec=override_value_spec, params=scope)

                    if self.state == "present":
                        self.ensure_override_values_present(
                            'ansible_override_values', desired_override_value, current_override_value,
                            state="present", foreman_spec=override_value_spec, params=scope)

                for current_override_value in current_override_values.values():
                    self.ensure_entity(
                        'ansible_override_values', None, current_override_value, state="absent", foreman_spec=override_value_spec, params=scope)
        else:
            if entity:
                for override_value in entity.get('override_values', []):
                    self.ensure_entity('ansible_override_values', None, override_value, state="absent", foreman_spec=override_value_spec)

    def ensure_override_values_present(self, resource, desired_entity, current_entity, params=None, state=None, foreman_spec=None):
        """ Fix for ensure present state for override values, as the
            update option is not available for this resource

            Parameters:
                resource (string): Plural name of the api resource to manipulate
                desired_entity (dict): Desired properties of the entity
                current_entity (dict, None): Current properties of the entity or None if nonexistent
                params (dict): Lookup parameters (i.e. parent_id for nested entities) (optional)
                state (dict): Desired state of the entity (optionally taken from the module)
                foreman_spec (dict): Description of the entity structure (optionally taken from module)
            Return value:
                The new current state of the entity
        """
        if state is None:
            state = self.state
        if foreman_spec is None:
            foreman_spec = self.foreman_spec
        else:
            foreman_spec, _dummy = _foreman_spec_helper(foreman_spec)

        updated_entity = None

        self.record_before(resource, _flatten_entity(current_entity, foreman_spec))

        if state == 'present':
            if current_entity is None:
                updated_entity = self._create_entity(resource, desired_entity, params, foreman_spec)
            else:
                if not (current_entity['match'] == desired_entity['match']
                        and current_entity['value'] == desired_entity['value']):
                    updated_entity = self._delete_entity(resource, current_entity, params)
                    updated_entity = self._create_entity(resource, desired_entity, params, foreman_spec)
                else:
                    updated_entity = current_entity
        else:
            self.fail_json(msg='Not a valid state: {0}'.format(state))

        self.record_after(resource, _flatten_entity(updated_entity, foreman_spec))
        self.record_after_full(resource, updated_entity)

        return updated_entity


def main():
    module = AnsibleAnsibleVariableModule(
        entity_key='variable',
        foreman_spec=dict(
            variable=dict(required=True, aliases=['name']),
            default_value=dict(type='raw'),
            ansible_role=dict(required=True, type='entity', flat_name='ansible_role_id', aliases=['role'], resource_type='ansible_roles'),
            variable_type=dict(default='string', aliases=['parameter_type'], choices=['string', 'boolean', 'integer', 'real', 'array', 'hash', 'yaml', 'json']),
            # If set this will cause the module to loose its idempotency
            hidden_value=dict(type=bool, choices=[True, False, 1, 0]),

            # At the moment this must be a string of the type: fqdn\nhostgroup\nos\ndomain
            override_value_order=dict(type='str'),

            description=dict(type='str'),

            # Only in combination, no enforce option available
            validator_type=dict(choices=['regexp', 'list']),
            validator_rule=dict(type='str'),

            merge_overrides=dict(type=bool, choices=[True, False, 1, 0]),
            merge_default=dict(type=bool, choices=[True, False, 1, 0]),
            avoid_duplicates=dict(type=bool, choices=[True, False, 1, 0]),

            override=dict(type=bool, choices=[True, False, 1, 0]),

            override_values=dict(type='nested_list', foreman_spec=override_value_spec),
        ),

        argument_spec=dict(
            state=dict(default='present', choices=['present_with_defaults', 'present', 'absent']),
            updated_name=dict(),
        ),
    )

    with module.api_connection():
        # Ansible API returns ansible role already flattened
        # Therefore switch to the flattened ansible_role_id
        for key, value in module.foreman_spec.items():
            if key == "ansible_role":
                entity = module.lookup_entity(key)
                if not module.foreman_spec.get('ansible_role_id'):
                    module.foreman_spec['ansible_role_id'] = dict(type=int)
                    del module.foreman_spec['ansible_role']
                if not module.foreman_params.get('ansible_role_id'):
                    module.foreman_params['ansible_role_id'] = entity['id']
                    del module.foreman_params['ansible_role']

        entity = module.lookup_entity('entity')
        if not module.desired_absent:
            # Convert values according to their corresponding variable_type
            if entity and 'variable_type' not in entity:
                entity['variable_type'] = 'string'
            module.foreman_params['default_value'] = parameter_value_to_str(module.foreman_params['default_value'], module.foreman_params['variable_type'])
            if entity and 'default_value' in entity:
                entity['default_value'] = parameter_value_to_str(entity['default_value'], entity.get('variable_type', 'string'))

        desired_override_values = module.foreman_params.pop('override_values', None)

        current_override_values = None
        if entity:
            current_override_values = entity.pop('override_values', None)

            # Foreman API returns 'hidden_value?' instead of 'hidden_value'
            # Same bug as for smartclass parameters
            if 'hidden_value?' in entity:
                entity['hidden_value'] = entity.pop('hidden_value?')

        entity = module.run()

        if current_override_values and entity:
            entity['override_values'] = current_override_values
        # override_values handling
        module.ensure_override_values(entity, desired_override_values)


if __name__ == '__main__':
    main()
