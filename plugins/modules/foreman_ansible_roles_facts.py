#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2020, Brant Evans (bevans@redhat.com)
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
module: foreman_ansible_roles_facts
short_description: Gather Ansible Roles facts
description:
  - Gather facts about Foreman Ansible Roles
author:
  - "Brant Evans (@branic)
options:
  action:
    description:
      - Method to use for gathering facts
    default: list
    choices:
      - list
      - show
      - fetch
    required: false
    type: str
  proxy:
    description:
      - The Smart Porxy name to use for fetching Ansible Roles
    required: false
    type: str
    alias: smart_proxy
  search:
    description:
      - Search query to use
      - If None, all resources are returned
    type: str
  full_details:
    description:
      - If C(True) all details about the found resources are returned
    type: bool
    default: false
    aliases: [ info ]
  organization:
    description:
      - Organization that the role is in
    required: false
    type: str
  location:
    description:
      - Location that the role is in
    required: false
    type: str
extends_documentation_fragment:
  - foreman
'''


EXAMPLES = '''
- name: Get Ansible Roles available to import on a proxy
  foreman_ansible_roles:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    state: "fetch"
    proxy: "foreman.example.com"
  register: result
- debug:
    var: result

- name: Get all imported Ansible Roles
  foreman_ansible_roles:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    organization: "
    state: "list"
  register: result
- debug:
    var: result

- name: Find the imported Ansible Role named example_role
  foreman_ansible_roles:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    organization: "
    state: "list"
    search: "name=example_role"
  register: result
- debug:
    var: result
'''

RETURN = '''
ansible_roles:
  description: Roles that are able to be imported on the proxy
  returned: state = fetched
  type: list
'''

from ansible.module_utils.foreman_helper import ForemanEntityAnsibleModule


class ForemanAnsibleRolesFactsModule(ForemanEntityAnsibleModule):
    pass


def main():

    module = ForemanAnsibleRolesFactsModule(
        foreman_spec = dict(
            action = dict(default='fetch', choices=['fetch', 'list', 'show']),
            proxy = dict(type='entity', flat_name='proxy_id', aliases=['smart_proxy'], resource_type='smart_proxies'),
            search=dict(default=""),
            full_details=dict(type='bool', aliases=['info'], default='false'),
            organization=dict(type='entity', flat_name='organization_id', resource_type='organizations'),
            location=dict(type='entity', flat_name='location_id', resource_type='locations'),
        ),

        required_if = [
            ['action', 'fetch', ['proxy']]
        ],
    )

    module_params = module.clean_params()
    resource = 'ansible_roles'
    search = module_params['search']
    params = {}

    if module_params['action'] == 'show':
        module_params['action'] = 'list'
        module_params['full_details'] = True

    with module.api_connection():
        _entity, module_params = module.resolve_entities(module_params, 'ansible_roles')

        if 'proxy' in module_params:
            params['proxy_id'] = module_params['proxy']['id']

        if 'organization' in module_params:
            params['organization_id'] = module_params['organization']['id']

        if 'location' in module_params:
            params['location_id'] = module_params['location']['id']

        if module_params['action'] == 'fetch':
            resources = module.fetch_resource('ansible_roles', params)
            module.exit_json(ansible_roles=resources['results']['ansible_roles'])
            # module.exit_json(mod_parms=module_params, my_parms=params)

        if module_params['action'] == 'list':
            if 'organization' in module_params:
                params['organization_id'] = module.find_resource_by_name('organizations', module_params['organization'], thin=True)['id']

            response = module.list_resource(resource, search, params)

            if module_params['full_details']:
                resources = []
                for found_resource in response:
                    resources.append(module.show_resource(resource, found_resource['id'], params))
            else:
                resources = response

            module.exit_json(ansible_roles=resources)

if __name__ == '__main__':
    main()