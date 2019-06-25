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

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: foreman_snapshot
short_description: Manage Foreman Snapshots
description:
  - "Manage Foreman Snapshots for Host Entities"
  - "This beta version can create, update and delete snapshots from preexisting host"
author:
  - "Manisha Singhal (@Manisha15) ATIX AG"
requirements:
  - "nailgun >= 0.32"
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
  verify_ssl:
    description:
      - Verify SSL of the Foreman server
    required: false
    default: true
    type: bool
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

'''

EXAMPLES = '''
- name: "Create a Snapshot"
  foreman_snapshot:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "new_host"
    host: host_name
    state: present

- name: "Update a Snapshot"
  foreman_snapshot:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "new_host"
    host: host_name
    description: "description"
    state: present

- name: "Revert a Snapshot"
  foreman_snapshot:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "new_host"
    host: host_name
    state: reverted

- name: "Delete a Snapshot"
  foreman_snapshot:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "new_host"
    host: host_name
    state: absent
'''

RETURN = ''' # '''

try:
    from nailgun.entities import (
        Snapshot,
        Host,
    )

    from ansible.module_utils.ansible_nailgun_cement import (
        find_entities,
        find_snapshot,
        find_host,
        naildown_entity_state,
        sanitize_entity_dict,
    )
except ImportError:
    pass

from ansible.module_utils.foreman_helper import ForemanEntityAnsibleModule

# This is the only true source for names (and conversions thereof)
name_map = {
    'name': 'name',
    'description': 'description',
    'host': 'host',
}


def main():
    module = ForemanEntityAnsibleModule(
        argument_spec=dict(
            name=dict(required=True),
            description=dict(),
            host=dict(required=True),
            state=dict(default='present', choices=['present', 'absent', 'reverted']),
        ),
        supports_check_mode=True,
    )

    (snapshot_dict, state) = module.parse_params()

    module.connect()

    host = snapshot_dict['host'] = find_host(module, snapshot_dict['host'], failsafe=False)

    entity = find_snapshot(module, host=host.id, name=snapshot_dict['name'], failsafe=True)

    snapshot_dict = sanitize_entity_dict(snapshot_dict, name_map)

    if state == 'reverted':
        try:
            if not module.check_mode:
                entity.revert()
        except Exception as e:
            module.fail_json(msg='Error while reverting {0}: {1}'.format(
                                 entity.__class__.__name__, str(e)))
        changed = True
    else:
        changed = naildown_entity_state(Snapshot, snapshot_dict, entity, state, module)

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()
