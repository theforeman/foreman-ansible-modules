#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2019 Bernhard Hopfenmüller (ATIX AG)
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
module: foreman_host
short_description: Manage Foreman hosts
description:
  - "Manage Foreman host Entities"
  - "This beta version can create and delete hosts from preexisting host groups"
author:
  - "Bernhard Hopfenmueller (@Fobhep) ATIX AG"
requirements:
  - "apypie"
options:
  name:
    description:
      - Fully Qualified Name of host
    required: true
  hostgroup:
    description:
      - Name of related hostgroup.
      - Required if I(state=present) and (I(managed=true) or I(build=true))
    required: true
  location:
    description:
      - Name of related location
    required: false
  organization:
    description:
      - Name of related organization
    required: false
  build:
    description:
      - Whether or not to setup build context for the host
    type: bool
    required: false
    default: None
  enabled:
    description:
      - Include this host within Foreman reporting
    type: bool
    required: false
    default: true
  managed:
    description:
      - Whether a host is managed or unmanaged
    type: bool
    required: false
    default: None
  state:
    description: host presence
    default: present
    choices: ["present", "absent"]
extends_documentation_fragment: foreman
'''

EXAMPLES = '''
- name: "Create a host"
  foreman_host:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "new_host"
    hostgroup: my_hostgroup
    state: present

- name: "Create a host with build context"
  foreman_host:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "new_host"
    hostgroup: my_hostgroup
    build: true
    state: present

- name: "Create an unmanaged host"
  foreman_host:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "new_host"
    managed: false
    state: present

- name: "Delete a host"
  foreman_host:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "new_host"
    state: absent
'''

RETURN = ''' # '''

from ansible.module_utils.foreman_helper import ForemanEntityAnsibleModule


def main():
    module = ForemanEntityAnsibleModule(
        entity_spec=dict(
            name=dict(required=True),
            hostgroup=dict(type='entity', flat_name='hostgroup_id'),
            location=dict(type='entity', flat_name='location_id'),
            organization=dict(type='entity', flat_name='organization_id'),
            enabled=dict(default='true', type='bool'),
            managed=dict(type='bool'),
            build=dict(type='bool'),
        ),
        required_if=(
            ['managed', True, ['hostgroup']],
            ['build', True, ['hostgroup']],
        ),
    )

    entity_dict = module.clean_params()

    # additional param validation
    if 'managed' in entity_dict and 'build' in entity_dict:
        if not entity_dict['managed'] and entity_dict['build']:
            module.fail_json(msg="If 'build' is True, 'managed' has to be either True or omitted")

    module.connect()

    entity = module.find_resource_by_name('hosts', name=entity_dict['name'], failsafe=True)

    if not module.desired_absent:
        if 'hostgroup' in entity_dict:
            entity_dict['hostgroup'] = module.find_resource_by_name('hostgroups', entity_dict['hostgroup'], thin=True)

        if 'location' in entity_dict:
            entity_dict['location'] = module.find_resource_by_title('locations', entity_dict['location'], thin=True)

        if 'organization' in entity_dict:
            entity_dict['organization'] = module.find_resource_by_name('organizations', entity_dict['organization'], thin=True)

    changed, host = module.ensure_entity('hosts', entity_dict, entity)
    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()
