#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2016, Eric D Helms <ericdhelms@gmail.com>
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
module: katello_content_viiew
short_description: Create and Manage Katello content views
description:
    - Create and Manage Katello content views
author: "Eric D Helms (@ehelms)"
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
            - Name of the Katello product
        required: true
    organization:
        description:
            - Organization that the Product is in
        required: true
    composite:
        description:
            - Whether a composite content view or not
        default: false
        choices:
            - true
            - false
    content_views:
        description:
            - List of content views to include in the composite content view. Ignored if composite is false.
        required: false
    repositories:
        description:
            - List of repositories that include name and product. Ignored if compsite is true.
        required: false
        type: list
    state:
        description:
            - State of the content view
        default: present
        choices:
            - present
            - present_with_defaults
            - absent
'''

EXAMPLES = '''
- name: "Create or update Fedora content view"
  katello_content_view:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "Fedora CV"
    organization: "My Cool new Organization"
    repositories:
      - name: 'Fedora 26'
        product: 'Fedora'
- name: "Create a composite content view
  katello_content_view:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "Fedora CCV"
    organization: "My Cool new Organization"
    composite: true
    content_views:
    - Fedora CV
'''

RETURN = '''# '''

try:
    from nailgun.entities import (
        ContentView,
    )

    from ansible.module_utils.ansible_nailgun_cement import (
        create_server,
        ping_server,
        find_organization,
        find_content_view,
        find_content_views,
        find_content_view_version,
        find_content_view_versions,
        find_repositories,
        naildown_entity_state,
        sanitize_entity_dict,
    )

    has_import_error = False
except ImportError as e:
    has_import_error = True
    import_error_msg = str(e)

from ansible.module_utils.basic import AnsibleModule

name_map = {
    'name': 'name',
    'repositories': 'repository',
    'organization': 'organization',
    'composite': 'composite',
    'component': 'component'
}


def main():
    module = AnsibleModule(
        argument_spec=dict(
            server_url=dict(required=True),
            username=dict(required=True, no_log=True),
            password=dict(required=True, no_log=True),
            verify_ssl=dict(type='bool', default=True),
            name=dict(required=True),
            organization=dict(required=True),
            composite=dict(type='bool', default=False),
            content_views=dict(type='list'),
            repositories=dict(type='list'),
            state=dict(default='present', choices=['present_with_defaults', 'present', 'absent']),
        ),
        supports_check_mode=True,
    )

    if has_import_error:
        module.fail_json(msg=import_error_msg)

    entity_dict = dict(
        [(k, v) for (k, v) in module.params.items() if v is not None])

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

    entity_dict['organization'] = find_organization(module, name=entity_dict['organization'])
    if 'repositories' in entity_dict:
        entity_dict['repositories'] = find_repositories(module, entity_dict['repositories'], entity_dict['organization'])
    if 'content_views' in entity_dict:
        entity_dict['content_views'] = find_content_views(module, entity_dict['content_views'], entity_dict['organization'])
        entity_dict['component'] = find_content_view_versions(module, entity_dict['content_views'], environment=None, version=None)

    content_view_entity = find_content_view(module, name=entity_dict['name'], organization=entity_dict['organization'], failsafe=True)
    content_view_dict = sanitize_entity_dict(entity_dict, name_map)

    changed = naildown_entity_state(ContentView, content_view_dict, content_view_entity, state, module)

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()
