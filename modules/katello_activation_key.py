#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2017, Andrew Kofink <ajkofink@gmail.com>
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
module: katello_activation_key
short_description: Create and Manage Katello activation keys
description:
    - Create and Manage Katello activation keys
author: "Andrew Kofink (@akofink)"
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
            - Name of the activation key
        required: true
    organization:
        description:
            - Organization name that the activation key is in
        required: true
    lifecycle_environment:
        description:
            - Name of the lifecycle environment
    content_view:
        description:
            - Name of the content view
    subscriptions:
        description:
            - List of subscriptions that include name
        type: list
    auto_attach:
        description:
            - Set Auto-Attach on or off
        default: true
        type: bool
    state:
        description:
            - State of the Activation Key. If "copied" the key will be copied to a new one with "new_name" as the name
              and all other fields left untouched.
        default: present
        choices:
        - present
        - present_with_defaults
        - absent
        - copied
    new_name:
        description:
            - Name of the new activation key when state == copied
'''

EXAMPLES = '''
- name: "Create katello client activation key"
  katello_activation_key:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "Katello Clients"
    organization: "Default Organization"
    lifecycle_environment: "Library"
    content_view: 'client content view'
    subscriptions:
        - name: "Red Hat Enterprise Linux"
    auto_attach: False
'''

RETURN = '''# '''

try:
    from ansible.module_utils.ansible_nailgun_cement import (
        create_server,
        ping_server,
        find_organization,
        find_location,
        find_activation_key,
        find_lifecycle_environment,
        find_content_view,
        find_subscriptions,
        naildown_entity,
        sanitize_entity_dict,
    )

    from nailgun.entities import (
        ActivationKey,
        Subscription,
    )
    has_import_error = False
except ImportError as e:
    has_import_error = True
    import_error_msg = str(e)

from ansible.module_utils.basic import AnsibleModule

name_map = {
    'name': 'name',
    'new_name': 'new_name',
    'auto_attach': 'auto_attach',
    'content_view': 'content_view',
    'organization': 'organization',
    'lifecycle_environment': 'environment',
}


def main():
    module = AnsibleModule(
        argument_spec=dict(
            server_url=dict(required=True),
            username=dict(required=True, no_log=True),
            password=dict(required=True, no_log=True),
            verify_ssl=dict(type='bool', default=True),
            name=dict(required=True),
            new_name=dict(),
            organization=dict(required=True),
            lifecycle_environment=dict(),
            content_view=dict(),
            subscriptions=dict(type='list'),
            auto_attach=dict(type='bool', default=True),
            state=dict(default='present', choices=['present', 'present_with_defaults', 'absent', 'copied']),
        ),
        supports_check_mode=True,
        required_if=[
            ['state', 'copied', ['new_name']],
        ],
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
    if 'lifecycle_environment' in entity_dict:
        entity_dict['lifecycle_environment'] = find_lifecycle_environment(module, entity_dict['lifecycle_environment'], entity_dict['organization'])

    if 'content_view' in entity_dict:
        entity_dict['content_view'] = find_content_view(module, entity_dict['content_view'], entity_dict['organization'])

    activation_key_dict = sanitize_entity_dict(entity_dict, name_map)
    activation_key_entity = find_activation_key(module, name=entity_dict['name'], organization=entity_dict['organization'],
                                                failsafe=True)

    try:
        changed, activation_key_entity = naildown_entity(ActivationKey, activation_key_dict, activation_key_entity, state, module)

        # only update subscriptions of newly created or updated AKs
        # copied keys inherit the subscriptions of the origin, so one would not have to specify them again
        # deleted keys don't need subscriptions anymore either
        if state == 'present' or (state == 'present_with_defaults' and changed):
            if 'subscriptions' not in entity_dict:
                subscriptions = []
            else:
                subscriptions = entity_dict['subscriptions']
            desired_subscription_ids = map(lambda s: s.id, find_subscriptions(module, subscriptions, entity_dict['organization']))
            current_subscriptions = [Subscription(**result)
                                     for result in Subscription().search_normalize(activation_key_entity.subscriptions()['results'])]
            current_subscription_ids = map(lambda s: s.id, current_subscriptions)

            if set(desired_subscription_ids) != set(current_subscription_ids):
                if not module.check_mode:
                    for subscription_id in set(desired_subscription_ids) - set(current_subscription_ids):
                        activation_key_entity.add_subscriptions(data={'quantity': 1, 'subscription_id': subscription_id})
                    for subscription_id in set(current_subscription_ids) - set(desired_subscription_ids):
                        activation_key_entity.remove_subscriptions(data={'subscription_id': subscription_id})
                changed = True

        module.exit_json(changed=changed)
    except Exception as e:
        module.fail_json(msg=e)


if __name__ == '__main__':
    main()
