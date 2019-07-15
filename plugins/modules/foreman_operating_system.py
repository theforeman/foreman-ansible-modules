#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2017 Matthias M Dellweg (ATIX AG)
# (c) 2017 Bernhard Hopfenmüller (ATIX AG)
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

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: foreman_operating_system
short_description: Manage Foreman Operating Systems
description:
  - "Manage Foreman Operating System Entities"
  - "Uses https://github.com/SatelliteQE/nailgun"
author:
  - "Matthias M Dellweg (@mdellweg) ATIX AG"
  - "Bernhard Hopfenmüller (@Fobhep) ATIX AG"
requirements:
  - apypie
options:
  name:
    description:
      - Name of the Operating System
    required: true
  release_name:
    description:
      - Release name of the operating system (recommended for debian)
  description:
    description:
      - Description of the Operating System
    required: false
  family:
    description:
      - distribution family of the Operating System
    required: true
  major:
    description:
      - major version of the Operating System
    required: true
  minor:
    description:
      - minor version of the Operating System
    required: false
  architectures:
    description:
      - architectures, the operating system can be installed on
    required: false
    type: list
  media:
    description:
      - list of installation media
    required: false
    type: list
  ptables:
    description:
      - list of partitioning tables
    required: false
    type: list
  provisioning_templates:
    description:
      - list of provisioning templates
    required: false
    type: list
  password_hash:
    description:
      - hashing algorithm for passwd
    required: false
    choices:
      - MD5
      - SHA256
      - SHA512
  parameters:
    description:
      - Operating System specific host parameters
    required: false
    type: list
    elements: dict
    options:
      name:
        description:
          - Name of the parameter
        required: true
      value:
        description:
          - Value of the parameter
        required: true
        type: raw
      parameter_type:
        description:
          - Type of the parameter
        default: 'string'
        choices:
          - 'string'
          - 'boolean'
          - 'integer'
          - 'real'
          - 'array'
          - 'hash'
          - 'yaml'
          - 'json'
  state:
    description:
      - State of the Operating System
    default: present
    choices:
      - present
      - present_with_defaults
      - absent
extends_documentation_fragment: foreman
'''

EXAMPLES = '''
- name: "Create an Operating System"
  foreman_operating_system:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: Debian 9
    release_name: stretch
    family: Debian
    major: 9
    parameters:
      - name: additional-packages
        value: python vim
    state: present

- name: "Ensure existence of an Operating System (provide default values)"
  foreman_operating_system:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: Centos 7
    family: Red Hat
    major: 7
    password_hash: SHA256
    state: present_with_defaults

- name: "Delete an Operating System"
  foreman_operating_system:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: Debian 9
    family: Debian
    major: 9
    state: absent
'''

RETURN = ''' # '''


from ansible.module_utils.foreman_helper import ForemanEntityApypieAnsibleModule, parameter_value_to_str


# This is the only true source for names (and conversions thereof)
entity_spec = {
    'id': {},
    'name': {},
    'description': {},
    'family': {},
    'major': {},
    'minor': {},
    'release_name': {},
    'architectures': {'type': 'entity_list', 'flat_name': 'architecture_ids'},
    'media': {'type': 'entity_list', 'flat_name': 'medium_ids'},
    'ptables': {'type': 'entity_list', 'flat_name': 'ptable_ids'},
    'provisioning_templates': {'type': 'entity_list', 'flat_name': 'provisioning_template_ids'},
    'password_hash': {},
}


parameter_entity_spec = {
    'id': {},
    'name': {},
    'value': {},
    'parameter_type': {},
}


def main():
    module = ForemanEntityApypieAnsibleModule(
        argument_spec=dict(
            name=dict(required=True),
            release_name=dict(),
            description=dict(),
            family=dict(required=True),
            major=dict(required=True),
            minor=dict(),
            architectures=dict(type='list'),
            media=dict(type='list'),
            ptables=dict(type='list'),
            provisioning_templates=dict(type='list'),
            password_hash=dict(choices=['MD5', 'SHA256', 'SHA512']),
            parameters=dict(type='list', elements='dict', options=dict(
                name=dict(required=True),
                value=dict(type='raw', required=True),
                parameter_type=dict(default='string', choices=['string', 'boolean', 'integer', 'real', 'array', 'hash', 'yaml', 'json']),
            )),
            state=dict(default='present', choices=['present', 'present_with_defaults', 'absent']),
        ),
        entity_spec=entity_spec,
    )

    entity_dict = module.clean_params()

    module.connect()

    # Try to find the Operating System to work on
    # name is however not unique, but description is, as well as "<name> <major>[.<minor>]"
    entity = None
    # If we have a description, search for it
    if 'description' in entity_dict and entity_dict['description'] != '':
        entity = module.find_resource_by_title('operatingsystems', entity_dict['description'], failsafe=True)
    # If we did not yet find a unique OS, search by name & version
    if entity is None:
        search_string = ','.join('{}="{}"'.format(key, entity_dict[key]) for key in ('name', 'major', 'minor') if key in entity_dict)
        entity = module.find_resource('operatingsystems', search_string, failsafe=True)

    if not entity and (module.state == 'present' or module.state == 'present_with_defaults'):
        # we actually attempt to create a new one...
        for param_name in ['major', 'family', 'password_hash']:
            if param_name not in entity_dict.keys():
                module.fail_json(msg='{} is a required parameter to create a new operating system.'.format(param_name))

    if not module.desired_absent:
        if 'architectures' in entity_dict:
            entity_dict['architectures'] = module.find_resources_by_name('architectures', entity_dict['architectures'], thin=True)

        if 'media' in entity_dict:
            entity_dict['media'] = module.find_resources_by_name('media', entity_dict['media'], thin=True)

        if 'ptables' in entity_dict:
            entity_dict['ptables'] = module.find_resources_by_name('ptables', entity_dict['ptables'], thin=True)

        if 'provisioning_templates' in entity_dict:
            entity_dict['provisioning_templates'] = module.find_resources_by_name('provisioning_templates', entity_dict['provisioning_templates'], thin=True)

    parameters = entity_dict.get('parameters')

    changed, operating_system = module.ensure_entity('operatingsystems', entity_dict, entity)

    if parameters is not None:
        if module.state == 'present' or (module.state == 'present_with_defaults' and entity is None):
            search_params = {'operatingsystem_id': operating_system['id']}
            if entity:
                current_parameters = {parameter['name']: parameter for parameter in module.list_resource('parameters', params=search_params)}
            else:
                current_parameters = {}
            desired_parameters = {parameter['name']: parameter for parameter in parameters}

            for name in desired_parameters:
                desired_parameter = desired_parameters[name]
                desired_parameter['value'] = parameter_value_to_str(desired_parameter['value'], desired_parameter['parameter_type'])
                current_parameter = current_parameters.pop(name, None)
                if current_parameter:
                    if 'parameter_type' not in current_parameter:
                        current_parameter['parameter_type'] = 'string'
                    current_parameter['value'] = parameter_value_to_str(current_parameter['value'], current_parameter['parameter_type'])
                changed |= module.ensure_entity(
                    'parameters', desired_parameter, current_parameter, state="present", entity_spec=parameter_entity_spec, params=search_params)[0]
            for current_parameter in current_parameters.values():
                changed |= module.ensure_entity(
                    'parameters', None, current_parameter, state="absent", entity_spec=parameter_entity_spec, params=search_params)[0]

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()
