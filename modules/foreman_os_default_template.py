#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2017 Matthias M Dellweg (ATIX AG)
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
module: foreman_os_default_template
short_description: Manage Foreman Default Template Associations To Operating Systems
description:
  - "Manage Foreman OSDefaultTemplate Entities"
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
  operatingsystem:
    description:
      - Name of the Operating System
    required: true
  template_kind:
    description:
      - name of the template kind
    required: true
  provisioning_template:
    description:
      - name of provisioning template
    required: false
  state:
    description:
      - State of the Association
    default: present
    choices:
      - present
      - present_with_defaults
      - absent
'''

EXAMPLES = '''
- name: "Create an Association"
  foreman_os_default_template:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    operatingsystem: "CoolOS"
    template_kind: "finish"
    provisioning_template: "CoolOS finish"
    state: present

- name: "Delete an Association"
  foreman_os_default_template:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    operatingsystem: "CoolOS"
    template_kind: "finish"
    state: absent
'''

RETURN = ''' # '''

try:
    from ansible.module_utils.ansible_nailgun_cement import (
        find_entities_by_name,
        find_os_default_template,
        find_operating_system_by_title,
        naildown_entity_state,
    )

    from nailgun.entities import (
        OperatingSystem,
        OSDefaultTemplate,
        ProvisioningTemplate,
        TemplateKind,
    )
except ImportError:
    pass

from ansible.module_utils.foreman_helper import ForemanEntityAnsibleModule


def sanitize_os_default_template_dict(entity_dict):
    # This is the only true source for names (and conversions thereof)
    name_map = {
        'operatingsystem': 'operatingsystem',
        'template_kind': 'template_kind',
        'provisioning_template': 'provisioning_template',
    }
    result = {}
    for key, value in name_map.items():
        if key in entity_dict:
            result[value] = entity_dict[key]
    return result


def main():
    module = ForemanEntityAnsibleModule(
        argument_spec=dict(
            operatingsystem=dict(required=True),
            template_kind=dict(required=True),
            provisioning_template=dict(required=False),
            state=dict(default='present', choices=['present', 'present_with_defaults', 'absent']),
        ),
        required_if=(
            ['state', 'present', ['provisioning_template']],
            ['state', 'present_with_defaults', ['provisioning_template']],
        ),
        supports_check_mode=True,
    )

    (entity_dict, state) = module.parse_params()

    module.connect()

    entity_dict['operatingsystem'] = find_operating_system_by_title(module, entity_dict['operatingsystem'])
    entity_dict['template_kind'] = find_entities_by_name(
        TemplateKind, [entity_dict['template_kind']], module)[0]

    entity = find_os_default_template(
        module,
        operatingsystem=entity_dict['operatingsystem'],
        template_kind=entity_dict['template_kind'],
        failsafe=True,
    )

    # Find Provisioning Template
    if 'provisioning_template' in entity_dict:
        if state == 'absent':
            module.fail_json(msg='Provisioning template must not be specified for deletion.')
        entity_dict['provisioning_template'] = find_entities_by_name(
            ProvisioningTemplate, [entity_dict['provisioning_template']], module)[0]
        if entity_dict['provisioning_template'].template_kind.id != entity_dict['template_kind'].id:
            module.fail_json(msg='Provisioning template kind mismatching.')

    entity_dict = sanitize_os_default_template_dict(entity_dict)

    changed = naildown_entity_state(OSDefaultTemplate, entity_dict, entity, state, module)

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()
