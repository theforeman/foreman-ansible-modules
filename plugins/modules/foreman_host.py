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

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
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
options:
  name:
    description:
      - Fully Qualified Domain Name of host
    required: true
    type: str
  hostgroup:
    description:
      - Name of related hostgroup.
      - Required if I(state=present) and (I(managed=true) or I(build=true))
    required: false
    type: str
  location:
    description:
      - Name of related location
    required: false
    type: str
  organization:
    description:
      - Name of related organization
    required: false
    type: str
  build:
    description:
      - Whether or not to setup build context for the host
    type: bool
    required: false
  enabled:
    description:
      - Include this host within Foreman reporting
    type: bool
    required: false
  managed:
    description:
      - Whether a host is managed or unmanaged.
      - Forced to true when I(build=true)
    type: bool
    required: false
  ip:
    description:
      - IP address of the primary interface of the host.
    type: str
    required: false
  mac:
    description:
      - MAC address of the primary interface of the host.
      - Please include leading zeros and separate nibbles by colons, otherwise the execution will not be idempotent.
      - Example EE:BB:01:02:03:04
    type: str
    required: false
  comment:
    description:
      - Comment about the host.
    type: str
    required: false
  owner:
    description:
      - Owner (user) of the host.
      - Mutually exclusive with I(owner_group).
    type: str
    required: false
  owner_group:
    description:
      - Owner (user group) of the host.
      - Mutually excluside with I(owner).
    type: str
    required: false
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.entity_state
  - theforeman.foreman.foreman.host_options
  - theforeman.foreman.foreman.nested_parameters
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

from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import ForemanEntityAnsibleModule, HostMixin


class ForemanHostModule(HostMixin, ForemanEntityAnsibleModule):
    pass


def main():
    module = ForemanHostModule(
        entity_spec=dict(
            name=dict(required=True),
            hostgroup=dict(type='entity'),
            location=dict(type='entity'),
            organization=dict(type='entity'),
            enabled=dict(type='bool'),
            managed=dict(type='bool'),
            build=dict(type='bool'),
            ip=dict(),
            mac=dict(),
            comment=dict(),
            owner=dict(type='entity', resource_type='users', flat_name='owner_id'),
            owner_group=dict(type='entity', resource_type='usergroups', flat_name='owner_id'),
            owner_type=dict(type='invisible'),
        ),
        required_if=(
            ['managed', True, ['hostgroup']],
            ['build', True, ['hostgroup']],
        ),
        mutually_exclusive=[
            ['owner', 'owner_group']
        ],
    )

    entity_dict = module.clean_params()

    # additional param validation
    if '.' not in entity_dict['name']:
        module.fail_json(msg="The hostname must be FQDN")

    if not module.desired_absent:
        if 'hostgroup' not in entity_dict and entity_dict.get('managed', True):
            module.fail_json(msg='Hostgroup can be omitted only with managed=False')

        if 'build' in entity_dict and entity_dict['build']:
            # When 'build'=True, 'managed' has to be True. Assuming that user's priority is to build.
            if 'managed' in entity_dict and not entity_dict['managed']:
                module.warn("when 'build'=True, 'managed' is ignored and forced to True")
            entity_dict['managed'] = True
        elif 'build' not in entity_dict and 'managed' in entity_dict and not entity_dict['managed']:
            # When 'build' is not given and 'managed'=False, have to clear 'build' context that might exist on the server.
            entity_dict['build'] = False

        if 'mac' in entity_dict:
            entity_dict['mac'] = entity_dict['mac'].lower()

        if 'owner' in entity_dict:
            entity_dict['owner_type'] = 'User'
        elif 'owner_group' in entity_dict:
            entity_dict['owner_type'] = 'Usergroup'

    with module.api_connection():
        module.run(entity_dict=entity_dict)


if __name__ == '__main__':
    main()
