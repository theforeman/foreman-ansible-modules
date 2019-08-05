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
module: foreman_bookmark
short_description: Manage Foreman Bookmarks
description:
  - "Manage Foreman Bookmark Entities"
author:
  - "Bernhard Hopfenmueller (@Fobhep) ATIX AG"
  - "Christoffer Reijer (@ephracis) Basalt AB"
requirements:
  - "ansible >= 2.3"
  - "apypie"
options:
  name:
    description:
      - Name of the bookmark
    required: true
  controller:
    description:
      - Controller for the bookmark
    required: true
  public:
    description:
      - Make bookmark available for all users
    required: false
    default: true
    type: bool
  query:
    description:
      - Query of the bookmark
  state:
    description:
      - State of the bookmark
    default: present
    choices:
      - present
      - present_with_defaults
      - absent
extends_documentation_fragment: foreman
'''

EXAMPLES = '''
- name: "Create a Bookmark"
  foreman_bookmark:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "recent"
    controller: "job_invocations"
    query: "started_at > '24 hours ago'"
    state: present_with_defaults

- name: "Update a Bookmark"
  foreman_bookmark:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "recent"
    controller: "job_invocations"
    query: "started_at > '12 hours ago'"
    state: present

- name: "Delete a Bookmark"
  foreman_bookmark:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "recent"
    controller: "job_invocations"
    state: absent
'''

RETURN = ''' # '''

from ansible.module_utils.foreman_helper import ForemanEntityApypieAnsibleModule


def main():
    module = ForemanEntityApypieAnsibleModule(
        entity_spec=dict(
            name=dict(required=True),
            controller=dict(required=True),
            public=dict(defaut='true', type='bool'),
            query=dict(),
        ),
        argument_spec=dict(
            state=dict(default='present', choices=[
                       'present_with_defaults', 'present', 'absent']),
        ),
        required_if=(
            ['state', 'present', ['query']],
            ['state', 'present_with_defaults', ['query']],
        ),
    )

    entity_dict = module.clean_params()

    module.connect()

    search = 'name="{}",controller="{}"'.format(entity_dict['name'], entity_dict['controller'])
    entity = module.find_resource('bookmarks', search, failsafe=True)

    changed = module.ensure_entity_state('bookmarks', entity_dict, entity)

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()
