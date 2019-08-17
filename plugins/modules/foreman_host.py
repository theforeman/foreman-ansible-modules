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
      - Name of host (without the related domain!)
    required: true
  hostgroup:
    description:
      - Name of related hostgroup
    required: true
  location:
    description:
      - Name of related location
    required: false
  organization:
    description:
      - Name of related organization
    required: false
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

- name: "Delete a host"
  foreman_host:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "new_host"
    state: absent
'''

RETURN = ''' # '''

from ansible.module_utils.foreman_helper import (
    ForemanEntityAnsibleModule,
    parameter_entity_spec
)


def main():
    module = ForemanEntityAnsibleModule(
        entity_spec=dict(
            name=dict(required=True),
            hostgroup=dict(type='entity', required=True, flat_name='hostgroup_id'),
            location=dict(type='entity', flat_name='location_id'),
            organization=dict(type='entity', flat_name='organization_id'),
            enabled=dict(default='true', type='bool'),
            build=dict(default='false', type='bool'),
        )
    )

    entity_dict = module.clean_params()

    module.connect()

    hostgroup = module.find_resource_by_name('hostgroups', entity_dict['hostgroup'], thin=False)
    entity_dict['hostgroup'] = {'id': hostgroup['id']}
    entity_dict['name'] = "{name}.{domain}".format(name=entity_dict['name'],
                                                   domain=hostgroup['domain_name'])
  
    entity = module.find_resource_by_name('hosts', name=entity_dict['name'], failsafe=True)
  
    if not module.desired_absent:
        if 'location' in entity_dict:
            entity_dict['location'] = module.find_resources_by_title('locations', [entity_dict['location']], thin=True)[0]

        if 'organization' in entity_dict:
            entity_dict['organization'] = module.find_resources_by_name('organizations', [entity_dict['organization']], thin=True)[0]

    changed, host = module.ensure_entity('hosts', entity_dict, entity)
    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()
