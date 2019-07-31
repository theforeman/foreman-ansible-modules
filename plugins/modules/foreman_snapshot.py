#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2019 Manisha Singhal (ATIX AG)
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
module: foreman_snapshot
short_description: Manage Foreman Snapshots
description:
  - "Manage Foreman Snapshots for Host Entities"
  - "This module can create, update, revert and delete snapshots"
  - "This module requires the foreman_snapshot_management plugin set up in the server"
  - "See: U(https://github.com/ATIX-AG/foreman_snapshot_management)"
author:
  - "Manisha Singhal (@Manisha15) ATIX AG"
requirements:
    - "apypie"
options:
  name:
    description:
      - Name of Snapshot
    required: true
  description:
    description:
      - Description of Snapshot
    required: false
  host:
    description:
      - Name of related Host
    required: true
  state:
    description:
      - State of Snapshot
    default: present
    choices: ["present", "reverted", "absent"]
extends_documentation_fragment: foreman
'''

EXAMPLES = '''
- name: "Create a Snapshot"
  foreman_snapshot:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "snapshot_before_software_upgrade"
    host: "server.example.com"
    state: present

- name: "Update a Snapshot"
  foreman_snapshot:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "snapshot_before_software_upgrade"
    host: "server.example.com"
    description: "description of snapshot"
    state: present

- name: "Revert a Snapshot"
  foreman_snapshot:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "snapshot_before_software_upgrade"
    host: "server.example.com"
    state: reverted

- name: "Delete a Snapshot"
  foreman_snapshot:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "snapshot_before_software_upgrade"
    host: "server.example.com"
    state: absent
'''

RETURN = ''' # '''


from ansible.module_utils.foreman_helper import ForemanEntityApypieAnsibleModule


entity_spec = {
    'id': {},
    'name': {},
    'description': {},
}


def main():
    module = ForemanEntityApypieAnsibleModule(
        argument_spec=dict(
            name=dict(required=True),
            description=dict(),
            host=dict(required=True),
            state=dict(default='present', choices=['present', 'absent', 'reverted']),
        ),
        entity_spec=entity_spec,
    )
    snapshot_dict = module.clean_params()

    module.connect()

    host = module.find_resource_by_name('hosts', name=snapshot_dict['host'], failsafe=False, thin=True)

    entity = module.find_resource_by_name('snapshots', name=snapshot_dict['name'], params={'host_id': host['id']}, failsafe=True)

    changed = module.ensure_entity_state('snapshots', snapshot_dict, entity, params={'host_id': host['id']})

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()
