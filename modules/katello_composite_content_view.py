#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2017, Greg Swift <gregswift@gmail.com>
# Copied from katello_content_view.py by Eric Helms
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
module: katello_composite_content_view
short_description: Create and Manage Katello composite content views
description:
    - Create and Manage Katello composite content views
author: "Greg Swift (@gregswift)"
requirements:
    - "nailgun >= 0.28.0"
    - "python >= 2.6"
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
            - Name of the Katello composite content view
        required: true
    organization:
        description:
            - Organization that the Content Views are in
        required: true
    content_views:
        description:
            - List of content views that include name and version
        required: false
        type: list
'''

EXAMPLES = '''
- name: "Create or update a Fedora composite content view"
  katello_composite_content_view:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    state: present
    name: "OurFedora CCV"
    organization: "My Cool new Organization"
    content_views:
      - name: 'Fedora CV'
        version: '2.0'
      - name: 'Ansible CV'
        version: '1.0'
'''

RETURN = '''# '''

try:
    from ansible.module_utils.ansible_nailgun_cement import (
        ContentView,
        create_server,
        find_organization,
        find_content_views,
        find_content_view,
        find_content_view_version,
        ping_server,
        set_task_timeout,
    )
    HAS_NAILGUN_PACKAGE = True
except:
    HAS_NAILGUN_PACKAGE = False
from ansible.module_utils.foreman_helper import handle_no_nailgun

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.foreman_helper import handle_no_nailgun


def sanitize_composite_content_view_dict(entity_dict):
    # This is the only true source for names (and conversions thereof)
    name_map = {
        'name': 'name',
        'organization': 'organization',
        'content_views': 'content_views',
    }
    result = {}
    for key, value in name_map.items():
        if key in entity_dict:
            result[value] = entity_dict[key]
    return result


def main():
    module = AnsibleModule(
        argument_spec=dict(
            server_url=dict(required=True),
            username=dict(required=True, no_log=True),
            password=dict(required=True, no_log=True),
            verify_ssl=dict(type='bool', default=True),
            name=dict(required=True),
            organization=dict(required=True),
            content_views=dict(type='list'),
        ),
        supports_check_mode=True,
    )

    handle_no_nailgun(module, HAS_NAILGUN_PACKAGE)

    entity_dict = dict(
        [(k, v) for (k, v) in module.params.items() if v is not None])

    server_url = entity_dict.pop('server_url')
    username = entity_dict.pop('username')
    password = entity_dict.pop('password')
    verify_ssl = entity_dict.pop('verify_ssl')
    state = entity_dict.pop('state')

    name = module.params['name']
    organization = module.params['organization']
    content_views = module.params['content_views']

    try:
        create_server(server_url, (username, password), verify_ssl)
    except Exception as e:
        module.fail_json(msg="Failed to connect to Foreman server: %s " % e)

    ping_server(module)

    entity_dict['organization'] = find_organization(module, name=entity_dict['organization'])

    entity = find_content_view(module, name=entity_dict['name'], organization=entity_dict['organization'], failsafe=True)

    entity_dict['content_views'] = find_content_views(module, entity_dict['content_views'], organization=entity_dict['organization'], failsafe=True)

    entity_dict = sanitize_composite_content_view_dict(entity_dict)

    changed = naildown_entity_state(ContentView, entity_dict, entity, state, module)


if __name__ == '__main__':
    main()
