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
module: katello_repository
short_description: Create and manage Katello repository
description:
    - Crate and manage a Katello repository
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
        default: true
        type: bool
    name:
        description:
            - Name of the repository
        required: true
    product:
        description:
            - Product to which the repository lives in
        required: true
    organization:
        description:
            - Organization that the Product is in
        required: true
    content_type:
        description:
            - The content type of the repository (e.g. yum)
        required: true
    url:
        description:
            - Repository URL to sync from
        required: true
    download_policy:
        description:
            - download policy for sync from upstream
        choices:
            - background
            - immediate
            - on_demand
        required: false
    state:
        description:
            - State of the Repository
        default: true
        choices:
        - present_with_defaults
        - present
        - absent
'''

EXAMPLES = '''
- name: "Create repository"
  katello_repository:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "My repository"
    content_type: "yum"
    product: "My Product"
    organization: "Default Organization"
    url: "http://yum.theforeman.org/releases/latest/el7/x86_64/"
    download_policy: background
'''

RETURN = '''# '''

try:
    from ansible.module_utils.ansible_nailgun_cement import (
        Repository,
        create_server,
        ping_server,
        find_organization,
        find_product,
        find_repository,
        naildown_entity_state,
    )
    HAS_NAILGUN_PACKAGE = True
except:
    HAS_NAILGUN_PACKAGE = False

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.foreman_helper import handle_no_nailgun


def sanitize_repository_dict(entity_dict):
    # This is the only true source for names (and conversions thereof)
    name_map = {
        'name': 'name',
        'product': 'product',
        'content_type': 'content_type',
        'url': 'url',
        'download_policy': 'download_policy',
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
            product=dict(required=True),
            organization=dict(required=True),
            name=dict(required=True),
            content_type=dict(required=True),
            url=dict(),
            download_policy=dict(choices=['background', 'immediate', 'on_demand']),
            state=dict(required=True, choices=['present_with_defaults', 'present', 'absent']),
        ),
        supports_check_mode=True,
    )

    handle_no_nailgun(module, HAS_NAILGUN_PACKAGE)

    entity_dict = dict(
        [(k, v) for (k, v) in module.params.items() if v is not None])

    server_url = entity_dict.pop('server_url')
    verify_ssl = entity_dict.pop('verify_ssl')
    username = entity_dict.pop('username')
    password = entity_dict.pop('password')
    state = entity_dict.pop('state')

    try:
        create_server(server_url, (username, password), verify_ssl)
    except Exception as e:
        module.fail_json(msg="Failed to connect to Foreman server: %s " % e)

    ping_server(module)

    entity_dict['organization'] = find_organization(module, name=entity_dict['organization'])

    entity_dict['product'] = find_product(module, name=entity_dict['product'], organization=entity_dict['organization'])

    entity = find_repository(module, name=entity_dict['name'], product=entity_dict['product'], failsafe=True)

    entity_dict = sanitize_repository_dict(entity_dict)

    changed = naildown_entity_state(Repository, entity_dict, entity, state, module)

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()
