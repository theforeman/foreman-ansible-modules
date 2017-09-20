#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) Philipp Joos 2017
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
module: foreman_compute_profile
short_description: Manage Foreman Compute Profiles using Foreman API
description:
- Create and delete Foreman Compute Profiles using Foreman API
options:
  name:
    description: compute profile name
    required: true
  updated_name:
    description: new compute profile name
    required: false
  server_url:
    description: foreman url
    required: true
  username:
    description: foreman username
    required: true
  password:
    description: foreman user password
    required: true
  verify_ssl:
    description: verify ssl connection when communicating with foreman
    default: true
  state:
    description: compute profile presence
    default: present
    choices: ["present", "absent", "latest"]
notes:
- Requires nailgun
version_added: "2.0"
author: "Philipp Joos (@philippj)"
'''

EXAMPLES = '''
- name: compute profile
  foreman_compute_profile:
    name: example_compute_profile
    server_url: foreman.example.com
    username: admin
    password: secret
    verify_ssl: false
    state: present
'''

RETURN = ''' # '''

try:
    import nailgun.entities
    import ansible.module_utils.ansible_nailgun_cement as cement
    HAS_NAILGUN_PACKAGE = True

except:
    HAS_NAILGUN_PACKAGE = False

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.foreman_helper import handle_no_nailgun


def sanitize_compute_profile_dict(entity_dict):
    # This is the only true source for names (and conversions thereof)
    name_map = {
        'name': 'name',
    }
    result = {}
    for key, value in name_map.iteritems():
        if key in entity_dict:
            result[value] = entity_dict[key]
    return result


def main(module):
    handle_no_nailgun(module, HAS_NAILGUN_PACKAGE)

    updated_name = module.params.get('updated_name')
    state = module.params.get('state')

    cement.create_server(
        server_url=module.params.get('server_url'),
        auth=(module.params.get('username'), module.params.get('password')),
        verify_ssl=module.params.get('verify_ssl'),
    )

    cement.ping_server(module)

    data = {
        'name': module.params.get('name')
    }

    compute_profile = cement.find_compute_profile(module, name=data.get('name'), failsafe=True)

    if state == 'latest':
        data['name'] = updated_name

    data = sanitize_compute_profile_dict(data)

    changed = cement.naildown_entity_state(nailgun.entities.ComputeProfile, data, compute_profile, state, module)

    return changed


if __name__ == '__main__':
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(required=True),
            updated_name=dict(),
            server_url=dict(required=True),
            username=dict(required=True),
            password=dict(required=True, no_log=True),
            verify_ssl=dict(type='bool', default=True),
            state=dict(default='present', choices=['present', 'absent', 'latest']),
        ),
        required_if=(['state', 'latest', ['updated_name']],),
    )
    changed = main(module)
    module.exit_json(changed=changed)
