#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2024, Partha Aji
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
module: content_import_version
version_added: 4.0.0
short_description: Manage content view version content imports
description:
    - Import a content view version to a foreman.
author:
    - "Partha Aji (@parthaa)"
options:
  path:
    description:
      - Directory containing the exported content view version archive.
    required: true
    type: str
  metadata:
    description:
      - Contents of the metadata.json file. This is not required if the metadata_file location is provided.
  metadata_file:
    description:
      - Location of the metadata.json file. Not required if the metadata has been already provided via the other parameter
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.organization
  - theforeman.foreman.foreman.katelloimport
'''

EXAMPLES = '''
- name: "Import content view version from metadata"
  theforeman.foreman.content_import_version:
    path: "/var/lib/pulp/imports/example-content"
    metadata: "{{ lookup('file', '/tmp/metadata.json') | from_json }}"
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    organization: "Default Organization"

- name: "Import content view version with specific metadata json"
  theforeman.foreman.content_import_version:
    path: "/var/lib/pulp/imports/example-content"
    metadata_file: "/tmp/metadata.json"
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    organization: "Default Organization"
'''

from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import KatelloContentImportBaseModule


class KatelloContentImportModule(KatelloContentImportBaseModule):
    pass

def main():
    module = KatelloContentImportModule(
      import_action='version',
    )

    with module.api_connection():
        module.run()

if __name__ == '__main__':
    main()
