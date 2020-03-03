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
module: foreman_bookmark
short_description: Manage Foreman Bookmarks
description:
  - "Manage Foreman Bookmark Entities"
author:
  - "Bernhard Hopfenmueller (@Fobhep) ATIX AG"
  - "Christoffer Reijer (@ephracis) Basalt AB"
options:
  name:
    description:
      - Name of the bookmark
    required: true
    type: str
  controller:
    description:
      - Controller for the bookmark
    required: true
    type: str
  public:
    description:
      - Make bookmark available for all users
    required: false
    default: true
    type: bool
  query:
    description:
      - Query of the bookmark
    type: str
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.entity_state_with_defaults
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

from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import ForemanEntityAnsibleModule


class ForemanBookmarkModule(ForemanEntityAnsibleModule):
    pass


def main():
    module = ForemanBookmarkModule(
        entity_spec=dict(
            name=dict(required=True),
            controller=dict(required=True),
            public=dict(default='true', type='bool'),
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

    with module.api_connection():
        module.run(search='name="{0}",controller="{1}"'.format(entity_dict['name'], entity_dict['controller']))


if __name__ == '__main__':
    main()
