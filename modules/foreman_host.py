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

from ansible.module_utils.foreman_helper import ForemanEntityAnsibleModule
ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: foreman_host
short_description: Manage Foreman hosts
description:
  - "Manage Foreman host Entities"
  - "This beta version can create, power on/off, delete hosts from preexisting host groups"
  - "Uses https://github.com/SatelliteQE/nailgun"
version_added: "2.7"
author:
  - "Bernhard Hopfenmueller (@Fobhep) ATIX AG"
requirements:
  - "nailgun >= 0.29.0"
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

# NEEDS REWORK


'''

EXAMPLES = '''
- name: "Create a host"
  foreman_host:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "new_host"
    hostgroup: my_hostgroup
    state: present

- name: "Switch off an existing host"
  foreman_host:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "new_host"
    enabled: false
    state: present

- name: "Delete a host"
  foreman_host:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "new_host"
    state: absent
'''

RETURN = ''' # '''

try:
    from nailgun.entities import (
        Host,
        HostGroup,
    )

    from ansible.module_utils.ansible_nailgun_cement import (
        find_host,
        find_hostgroup,
        find_location,
        find_organization,
        find_parameter_from_hostgroup,
        # set_power_state,
        naildown_entity_state,
        sanitize_entity_dict,
    )
except ImportError:
    pass


# This is the only true source for names (and conversions thereof)
name_map = {
    'name': 'name',
    # 'mac': 'mac',
    'enabled': 'enabled',
    'hostgroup': 'hostgroup',
    'location': 'location',
    'organization': 'organization',
}


def main():
    module = ForemanEntityAnsibleModule(
        argument_spec=dict(
            name=dict(required=True),
            hostgroup=dict(),
            location=dict(),
            # mac=dict(default='00-00-00-00-00-00'),
            organization=dict(),
            # power_state=dict(default='on'),
            enabled=dict(default='true', type='bool'),
            state=dict(default='present', choices=[
                       'present_with_defaults', 'present', 'absent']),
        ),
        required_if=(
            ['state', 'present_with_defaults', ['hostgroup']],
            ['state', 'present', ['hostgroup']],
        ),
        supports_check_mode=True,
    )

    (host_dict, state) = module.parse_params()

    module.connect()
    host_dict['hostgroup'] = find_hostgroup(
        module, host_dict['hostgroup'], failsafe=True)
    host_dict['name'] = host_dict['name'] + '.' + \
        find_parameter_from_hostgroup(
            module, host_dict['hostgroup'], 'domain_name')

    entity = find_host(module, host_dict['name'], failsafe=True)

    if 'location' in host_dict:
        host_dict['location'] = find_location(module, host_dict['location'])

    if 'organization' in host_dict:
        host_dict['organization'] = find_organization(
            module, host_dict['organization'])

    host_dict = sanitize_entity_dict(host_dict, name_map)

    changed = naildown_entity_state(Host, host_dict, entity, state, module)

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()
