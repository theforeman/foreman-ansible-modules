#!/usr/bin/python
# -*- coding: utf-8 -*-
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
module: foreman_smart_proxy
short_description: Manage Foreman Smart Proxy
description:
  - Manage Foreman Smart Proxy
requirements:
  - "nailgun >= 0.28.0"
  - "python >= 2.6"
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
  validate_certs:
    aliases: [ verify_ssl ]
    description:
      - Verify SSL of the Foreman server
    required: false
    default: true
    type: bool
  name:
    description:
      - Name or title of the Foreman Smart Proxy
    required: true
  url:
    description:
      - URL of the Smart Proxy
    required: true
  download_policy:
    description:
      - The download policy for the Smart Proxy
    choices:
      - background
      - immediate
      - on_demand
    default: on_demand
    required: false
  organizations:
    description:
      - List of organizations the Smart Proxy should be assigned to
    type: list
    required: false
  locations:
    description:
      - List of locations the Smart Proxy should be assigned to
    type: list
    required: false
  state:
    description:
      - State of the Smart Proxy
    default: present
    choices:
      - present
      - absent
'''

EXAMPLES = '''
# Create a local Smart Proxy
- name: "Create Smart Proxy"
  foreman_smart_proxy:
    username: "admin"
    password: "changeme"
    server_url: "https://{{ ansible_fqdn }}"
    name: "{{ ansible_fqdn }}"
    url: "https://{{ ansible_fqdn }}:9090"
    download_policy: "immediate"
    organizations:
      - "Default Organization"
    locations:
      - "Default Location"
    state: present
'''

RETURN = ''' # '''

try:
    from ansible.module_utils.ansible_nailgun_cement import (
        find_entities,
        find_locations,
        find_organizations,
        find_smart_proxy,
        naildown_entity_state,
        sanitize_entity_dict,
    )
    from nailgun.entities import SmartProxy
except ImportError:
    pass


from ansible.module_utils.foreman_helper import ForemanEntityAnsibleModule


# This is the only true source for names (and versions thereof)
name_map = {
    'name': 'name',
    'download_policy': 'download_policy',
    'url': 'url',
    'locations': 'location',
    'organizations': 'organization',
}


def main():
    module = ForemanEntityAnsibleModule(
        argument_spec=dict(
            name=dict(required=True),
            url=dict(required=True),
            download_policy=dict(choices=['background', 'immediate', 'on_demand']),
            locations=dict(type='list'),
            organizations=dict(type='list'),
        ),
        supports_check_mode=True
    )

    (entity_dict, state) = module.parse_params()

    module.connect()

    if 'locations' in entity_dict:
        entity_dict['locations'] = find_locations(module, entity_dict['locations'])

    if 'organizations' in entity_dict:
        entity_dict['organizations'] = find_organizations(module, entity_dict['organizations'])

    # Try to find the Smart Proxy to work on
    entity = find_smart_proxy(module, name=entity_dict['name'], failsafe=True)
    # Re-map names
    entity_dict = sanitize_entity_dict(entity_dict, name_map)

    # Make the changes
    changed = naildown_entity_state(SmartProxy, entity_dict, entity, state, module)

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()

#  vim: set sts=4 ts=8 sw=4 ft=python et noro norl cin si ai :
