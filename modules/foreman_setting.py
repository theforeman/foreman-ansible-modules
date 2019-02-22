#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2018 Matthias M Dellweg (ATIX AG)
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
module: foreman_setting
short_description: Manage Foreman Settings
description:
  - "Manage Foreman Setting Entities"
  - "Uses https://github.com/SatelliteQE/nailgun"
version_added: "2.4"
author:
  - "Matthias M Dellweg (@mdellweg) ATIX AG"
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
  name:
    description:
      - Name of the Setting
    required: true
  value:
    description:
      - value to set the Setting to
      - if missing, reset to default
      - use a comma separated list for an array
    required: false
'''

EXAMPLES = '''
- name: "Set a Setting"
  foreman_setting:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "http_proxy"
    value: "http://localhost:8088"

- name: "Reset a Setting"
  foreman_setting:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "http_proxy"
'''

RETURN = '''
foreman_setting:
  description: Created / Updated state of the setting
'''

try:
    from ansible.module_utils.ansible_nailgun_cement import (
        find_setting,
        naildown_entity,
        sanitize_entity_dict,
    )

    from nailgun.entities import (
        Setting,
    )
except ImportError:
    pass

from ansible.module_utils.foreman_helper import ForemanAnsibleModule


name_map = {
    'name': 'name',
    'value': 'value',
}


def main():
    module = ForemanAnsibleModule(
        argument_spec=dict(
            name=dict(required=True),
            value=dict(),
        ),
        supports_check_mode=True,
    )

    entity_dict = module.parse_params()

    module.connect()

    entity = find_setting(
        module,
        name=entity_dict['name'],
        failsafe=False,
    )

    if 'value' not in entity_dict:
        entity_dict['value'] = entity.default or ""

    entity_dict = sanitize_entity_dict(entity_dict, name_map)

    changed, entity = naildown_entity(Setting, entity_dict, entity, 'present', module, check_type=True)

    module.exit_json(changed=changed, foreman_setting=entity.to_json_dict())


if __name__ == '__main__':
    main()
