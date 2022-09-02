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
module: content_export_library
version_added: 3.5.0
short_description: Manage library content exports
description:
    - Export library content to a directory.
author:
    - "Jeremy Lenz (@jeremylenz)"
options:
  destination_server:
    description:
      - Destination server name; optional parameter to differentiate between exports
    required: false
    type: str
  chunk_size_gb:
    description:
      - Split the exported content into archives no greater than the specified size in gigabytes.
    required: false
    type: int
  fail_on_missing_content:
    description:
      - Fails if any of the repositories belonging to this organization are unexportable.
    required: false
    type: bool
  incremental:
    description:
      - Export only the content that has changed since the last export.
    required: false
    type: bool
  from_history_id:
    description:
      - Export history identifier used for incremental export. If not provided the most recent export history will be used.
    required: false
    type: int
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.organization
'''

EXAMPLES = '''
- name: "Export library content (full)"
  theforeman.foreman.content_export_library:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    organization: "Default Organization"
    destination_server: "airgapped.example.com"

- name: "Export library content (full) and fail if any repos are unexportable"
  theforeman.foreman.content_export_library:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    organization: "Default Organization"
    destination_server: "airgapped.example.com"
    fail_on_missing_content: true

- name: "Export library content (full) in chunks of 10 GB"
  theforeman.foreman.content_export_library:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    chunk_size_gb: 10
    organization: "Default Organization"
    destination_server: "airgapped.example.com"

- name: "Export library content (incremental) since the most recent export"
  theforeman.foreman.content_export_library:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    organization: "Default Organization"
    destination_server: "airgapped.example.com"
    incremental: true

- name: "Export library content (incremental) since a specific export"
  theforeman.foreman.content_export_library:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    organization: "Default Organization"
    destination_server: "airgapped.example.com"
    incremental: true
    from_history_id: 12345
'''

from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import KatelloAnsibleModule, _flatten_entity


class KatelloContentExportModule(KatelloAnsibleModule):
    pass


def main():
    module = KatelloContentExportModule(
        foreman_spec=dict(
            destination_server=dict(required=False, type='str'),
            chunk_size_gb=dict(required=False, type='int'),
            fail_on_missing_content=dict(required=False, type='bool'),
            from_history_id=dict(required=False, type='int'),
        ),
        argument_spec=dict(
            incremental=dict(required=False, type='bool'),
        ),
    )

    with module.api_connection():
        module.auto_lookup_entities()

        incremental = module.params['incremental']
        endpoint = 'content_export_incrementals' if incremental else 'content_exports'

        if module.params.get('from_history_id') and incremental is not True:
            module.fail_json(msg='from_history_id is only valid for incremental exports')

        payload = _flatten_entity(module.foreman_params, module.foreman_spec)
        task = module.resource_action(endpoint, 'library', payload)

        module.exit_json(task=task)


if __name__ == '__main__':
    main()
