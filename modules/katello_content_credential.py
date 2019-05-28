#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2018, Baptiste Agasse <baptiste.agagsse@gmail.com>
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

DOCUMENTATION = '''
---
module: katello_content_credential
short_description: Create and Manage Katello content credentials
description:
  - Create and Manage Katello content credentials
author: "Baptiste Agasse (@bagasse)"
requirements:
  - "nailgun >= 0.32.0"
  - "python >= 2.6"
  - "ansible >= 2.3"
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
  name:
    description:
      - Name of the content credential
    required: true
  organization:
    description:
      - Organization name that the content credential is in
    required: true
  content_type:
    description:
    - Type of credential
    choices:
    - gpg_key
    - cert
    required: true
  content:
    description:
    - Content of the content credential
    required: true
  state:
    description:
      - State of the content credential.
    default: present
    choices:
      - present
      - absent
'''

EXAMPLES = '''
- name: "Create katello client GPG key"
  katello_content_credential:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "RPM-GPG-KEY-my-repo"
    content_type: gpg_key
    organization: "Default Organization"
    content: "{{ lookup('file', 'RPM-GPG-KEY-my-repo') }}"
'''

RETURN = ''' # '''

from ansible.module_utils.foreman_helper import KatelloEntityApypieAnsibleModule


# This is the only true source for names (and conversions thereof)
name_map = {
    'name': 'name',
    'organization': 'organization_id',
    'content_type': 'content_type',
    'content': 'content',
}


def main():
    module = KatelloEntityApypieAnsibleModule(
        argument_spec=dict(
            name=dict(required=True),
            content_type=dict(required=True, choices=['gpg_key', 'cert']),
            content=dict(required=True),
        ),
        supports_check_mode=True,
    )

    (entity_dict, state) = module.parse_params()

    module.connect()

    entity_dict['organization'] = module.find_resource_by_name('organizations', entity_dict['organization'], thin=True)
    search_params = {'organization_id': entity_dict['organization']['id']}
    entity = module.find_resource_by_name('content_credentials', name=entity_dict['name'], params=search_params, failsafe=True)

    changed = module.ensure_resource_state('content_credentials', entity_dict, entity, state, name_map)

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()
