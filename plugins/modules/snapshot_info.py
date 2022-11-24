#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2022 Manisha Singhal (ATIX AG)
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
module: snapshot_info
version_added: 3.8.0
short_description: Fetch information about Foreman Snapshots
description:
  - Fetch information about Foreman Snapshots
author:
  - "Manisha Singhal (@Manisha15) ATIX AG"
options:
  host:
    description:
      - Name of related Host
    required: true
    type: str
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.infomodule
'''

EXAMPLES = '''
- name: "Show all snapshots for a host"
  theforeman.foreman.snapshot_info:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    host: "server.example.com"

- name: "Show a snapshot"
  theforeman.foreman.snapshot_info:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    host: "server.example.com"
    search: "name=ansible"
'''

RETURN = '''
snapshots:
  description: List of all snapshots and their details for a host
  returned: success and I(search) was passed
  type: list
  elements: dict
snapshot:
  description: Details about the first found snapshot with searched name
  returned: success and I(name) was passed
  type: list
  elements: dict
'''

from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import (
    ForemanInfoAnsibleModule,
)


class ForemanSnapshotInfo(ForemanInfoAnsibleModule):
    pass


def main():
    module = ForemanSnapshotInfo(
        foreman_spec=dict(
            host=dict(type='entity', required=True),
        ),
        entity_opts={'scope': ['host', 'snapshot']},
        required_plugins=[('snapshot_management', ['*'])],
    )

    with module.api_connection():
        module.run()


if __name__ == '__main__':
    main()
