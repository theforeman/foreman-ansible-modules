#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2018 Matthias M Dellweg (ATIX AG)
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


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: foreman_setting
short_description: Manage Foreman Settings
description:
  - "Manage Foreman Setting Entities"
author:
  - "Matthias M Dellweg (@mdellweg) ATIX AG"
options:
  name:
    description:
      - Name of the Setting
    required: true
    type: str
  value:
    description:
      - value to set the Setting to
      - if missing, reset to default
    required: false
    type: raw
extends_documentation_fragment:
  - foreman
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
  returned: success
  type: dict
'''


from ansible.module_utils.foreman_helper import ForemanAnsibleModule, parameter_value_to_str


foreman_spec = {
    'name': {},
    'value': {},
}


class ForemanSettingModule(ForemanAnsibleModule):
    pass


def main():
    module = ForemanSettingModule(
        foreman_spec=dict(
            name=dict(type='entity', resource_type='settings', required=True, failsafe=False, thin=False, ensure=False),
            value=dict(type='raw'),
        ),
    )

    module_params = module.foreman_params.copy()

    with module.api_connection():
        entity = module.lookup_entity('name')

        if 'value' not in module_params:
            module_params['value'] = entity['default'] or ''

        settings_type = entity['settings_type']
        new_value = module_params['value']
        # Allow to pass integers as string
        if settings_type == 'integer':
            new_value = int(new_value)
        module_params['value'] = parameter_value_to_str(new_value, settings_type)
        old_value = entity['value']
        entity['value'] = parameter_value_to_str(old_value, settings_type)

        entity = module.ensure_entity('settings', module_params, entity, state='present', foreman_spec=foreman_spec)

        if entity:
            # Fake the not serialized input value as output
            entity['value'] = new_value

        module.exit_json(foreman_setting=entity)


if __name__ == '__main__':
    main()
