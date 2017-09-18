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
  - nailgun >= 0.29.0
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
    required: true
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
        create_server,
        ping_server,
        find_entities_by_name,
        find_os_default_template,
        naildown_entity_state,
    )

    from nailgun.entities import (
        OperatingSystem,
        OSDefaultTemplate,
        ProvisioningTemplate,
        TemplateKind,
    )

    HAS_NAILGUN_PACKAGE = True
except:
    HAS_NAILGUN_PACKAGE = False
    raise

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.foreman_helper import handle_no_nailgun


def sanitize_os_default_template_dict(entity_dict):
    # This is the only true source for names (and conversions thereof)
    name_map = {
        'operatingsystem': 'operatingsystem',
        'template_kind': 'template_kind',
        'provisioning_template': 'provisioning_template',
    }
    result = {}
    for key, value in name_map.iteritems():
        if key in entity_dict:
            result[value] = entity_dict[key]
    return result


def main():
    module = AnsibleModule(
        argument_spec=dict(
            server_url=dict(required=True),
            username=dict(required=True),
            password=dict(required=True, no_log=True),
            verify_ssl=dict(type='bool', default=True),
            operatingsystem=dict(required=True),
            template_kind=dict(required=True),
            provisioning_template=dict(required=False),
            state=dict(required=True, choices=['present', 'present_with_defaults', 'absent']),
        ),
        required_if=(
            ['state', 'present', ['provisioning_template']],
            ['state', 'present_with_defaults', ['provisioning_template']],
        ),
        supports_check_mode=True,
    )

    handle_no_nailgun(module, HAS_NAILGUN_PACKAGE)

    entity_dict = dict(
        [(k, v) for (k, v) in module.params.iteritems() if v is not None])

    server_url = entity_dict.pop('server_url')
    username = entity_dict.pop('username')
    password = entity_dict.pop('password')
    verify_ssl = entity_dict.pop('verify_ssl')
    state = entity_dict.pop('state')

    try:
        create_server(server_url, (username, password), verify_ssl)
    except Exception as e:
        module.fail_json(msg="Failed to connect to Foreman server: %s " % e)

    ping_server(module)
    os_list = OperatingSystem().search(set(), {'search': 'title~"{}"'.format(entity_dict['operatingsystem'])})
    if len(os_list) == 0:
        module.fail_json(msg='Operating system "{}" not found.'.format(entity_dict['operatingsystem']))
    if len(os_list) > 1:
        module.fail_json(msg='Provided operating system ({}) is not unique.'.format(entity_dict['operatingsystem']))

    entity_dict['operatingsystem'] = os_list[0]
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
