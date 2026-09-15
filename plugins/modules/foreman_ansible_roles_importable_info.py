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
short_description: Gather names of Ansible Roles that can be imported
description:
  - Gather names of Ansible Roles that can be imported
author:
  - "Brant Evans (@branic)"
options:
  proxy:
    description:
      - The Smart Proxy name to use for fetching Ansible Roles
    required: false
    type: str
    aliases: 
      - smart_proxy
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
  foreman_ansible_roles_importable_info:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    proxy: "foreman.example.com"
  register: result
- debug:
    var: result
'''

RETURN = '''
ansible_roles:
  description: Roles that are able to be imported on the proxy
  returned: always
  type: list
'''

from ansible.module_utils.foreman_helper import ForemanAnsibleModule, _flatten_entity


class ForemanAnsibleRolesImportableInfoModule(ForemanAnsibleModule):
    pass


def main():

    module = ForemanAnsibleRolesImportableInfoModule(
        foreman_spec=dict(
            proxy=dict(type='entity', flat_name='proxy_id', aliases=['smart_proxy'], resource_type='smart_proxies', required=True),
            organization=dict(type='entity'),
            location=dict(type='entity'),
        ),
    )

    resource = 'ansible_roles'

    with module.api_connection():
        module.auto_lookup_entities()
        params = _flatten_entity(module.foreman_params, module.foreman_spec)

        resources = module.fetch_resource(resource, params)
        resources = resources['results']['ansible_roles']

        module.exit_json(ansible_roles=resources)


if __name__ == '__main__':
    main()
