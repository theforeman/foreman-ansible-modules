#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2022, Jeremy Lenz <jlenz@redhat.com>
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


DOCUMENTATION = '''
---
module: content_export_info
version_added: 3.5.0
short_description: List pulp3 content exports
description:
    - List information about content exports.
author:
    - "Jeremy Lenz (@jeremylenz)"
options:
  id:
    description:
      - Export history identifier.
    required: false
    type: int
  content_view_version_id:
    description:
      - Content view version identifier.
    required: false
    type: int
  content_view_id:
    description:
      - Content view identifier.
    required: false
    type: int
  destination_server:
    description:
      - Destination server name
    required: false
    type: str
  organization_id:
    description:
      - Organization identifier.
    required: false
    type: int
  type:
    description:
      - Specify complete or incremental exports.
    required: false
    type: str
    choices:
    - complete
    - incremental
  search:
    description:
      - Search string.
    required: false
    type: str
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.organization
'''

EXAMPLES = '''
- name: "List all full exports in the organization"
  content_export_info:
    organization: "Default Organization"
    type: complete
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
- name: "Get a specific export history and register the result for the next task"
  vars:
    organization_name: "Export Org"
  content_export_info:
    id: 29
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    organization: "Default Organization"
  register: result
- name: "Write metadata.json to disk using data from the previous task"
  vars:
    metadata: "{{ result['task']['results'][0]['metadata'] }}"
  ansible.builtin.copy:
    content: "{{ metadata }}"
    dest: ./metadata.json
- name: "List all exports of a specific content view version"
  content_export_info:
    content_view_version_id: 379
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    organization: "Default Organization"
- name: "List all exports marked for a specific destination server"
  content_export_info:
    destination_server: "airgapped.example.com"
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    organization: "Default Organization"
- name: "List incremental exports of a specific content view version marked for a specific destination server"
  content_export_info:
    content_view_id: 1
    destination_server: "airgapped.example.com"
    type: incremental
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    organization: "Default Organization"
- name: "List all exports of a specific content view marked for a specific destination server"
  content_export_info:
    content_view_id: 1
    destination_server: "airgapped.example.com"
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    organization: "Default Organization"

'''

from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import KatelloAnsibleModule, _flatten_entity


class KatelloContentExportInfoModule(KatelloAnsibleModule):
    pass


def main():
    module = KatelloContentExportInfoModule(
        foreman_spec=dict(
            id=dict(required=False, type='int'),
            content_view_version_id=dict(required=False, type='int'),
            content_view_id=dict(required=False, type='int'),
            destination_server=dict(required=False, type='str'),
            organization_id=dict(required=False, type='int'),
            type=dict(required=False, type='str', choices=['complete', 'incremental']),
            search=dict(required=False, type='str'),
        ),
    )

    with module.api_connection():
        module.auto_lookup_entities()

        endpoint = 'content_exports'

        payload = _flatten_entity(module.foreman_params, module.foreman_spec)
        task = module.resource_action(endpoint, 'index', payload)

        module.exit_json(task=task)


if __name__ == '__main__':
    main()
