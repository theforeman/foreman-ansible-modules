#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2018, Sean O'Keeffe <seanokeeffe797@gmail.com>
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
module: foreman_search_facts
short_description: Gather facts about Foreman resources
description:
  - "Gather facts about Foreman resources"
author:
  - "Sean O'Keeffe (@sean797)"
requirements:
  - nailgun
options:
  server_url:
    description:
      - URL of Foreman server
    required: true
  username:
    description:
      - Username on Foreman server
    required: true
  password:
    description:
      - Password for user accessing Foreman server
    required: true
  validate_certs:
    aliases: [ verify_ssl ]
    description:
      - Verify SSL of the Foreman server
    default: true
    type: bool
  resource:
    description:
      - Resource to search
      - Set to an invalid choice like I(foo) see all available options.
  search:
    description:
      - Search query to use
      - If None, all resources are returned
'''

EXAMPLES = '''
- name: "Read a Setting"
  foreman_search_facts:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    resource: settings
    search: name = http_proxy
  register: result
- debug:
    var: result.resources[0].value

- name: "Read all Registries"
  foreman_search_facts:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    resource: registries
  register: result
- debug:
    var: item.name
  with_items: result.resources
'''

RETURN = '''
resources:
  description: Search results from Foreman
  returned: always
  type: list
'''

from ansible.module_utils.foreman_helper import ForemanApypieAnsibleModule


def main():

    module = ForemanApypieAnsibleModule(
        argument_spec=dict(
            resource=dict(type='str', required=True),
            search=dict(default=""),
        ),
        supports_check_mode=True,
    )

    module_params = module.parse_params()
    entity = module_params['resource']
    search = module_params['search']

    module.connect()

    response = module.list_resource(entity, search)

    module.exit_json(changed=False, resources=response)


if __name__ == '__main__':
    main()
