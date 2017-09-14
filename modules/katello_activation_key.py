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
'''

RETURN = '''# '''

try:
    from nailgun import entities
    from nailgun.config import ServerConfig
    HAS_NAILGUN_PACKAGE = True
except:
    HAS_NAILGUN_PACKAGE = False


class NailGun(object):

    def __init__(self, server, entities, module):
        self._server = server
        self._entities = entities
        self._module = module

    def find_organization(self, name):
        org = self._entities.Organization(self._server, name=name)
        response = org.search(set(), {'search': 'name="{}"'.format(name)})

        if len(response) == 1:
            return response[0]
        else:
            self._module.fail_json(msg="No organization found for %s" % name)

    def find_lifecycle_environment(self, name, organization):
        env = self._entities.LifecycleEnvironment(self._server, name=name,
                                                  organization=organization)
        response = env.search()

        if len(response) == 1:
            return response[0]
        else:
            self._module.fail_json(msg="No lifecycle environment found for %s" % name)

    def find_content_view(self, name, organization):
        cv = self._entities.ContentView(self._server, name=name, organization=organization)
        response = cv.search()

        if len(response) == 1:
            return response[0]
        else:
            self._module.fail_json(msg="No content view found for %s" % name)

    def find_subscription(self, name, organization):
        subscriptions = self._entities.Subscription(self._server, organization=organization)
        response = subscriptions.search(query={'search': 'name="{}"'.format(name)})
        if len(response) == 1:
            return response[0].read()
        else:
            self._module.fail_json(msg="No subscription found for %s" % name)

    def find_subscriptions(self, subscriptions, organization):
        return map(lambda subscription: self.find_subscription(subscription['name'], organization), subscriptions)

    def update_fields(self, new, old, fields):
        needs_update = False
        for field in fields:
            if hasattr(new, field) and hasattr(old, field):
                new_attr = getattr(new, field)
                old_attr = getattr(old, field)
                if old_attr is None or new_attr.id != old_attr.id:
                    setattr(old, field, new_attr)
                    needs_update = True
            elif hasattr(old, field) and getattr(old, field) is not None and not hasattr(new, field):
                setattr(old, field, None)
                needs_update = True
        return needs_update, old

    def activation_key(self, name, organization, lifecycle_environment=None, content_view=None, subscriptions=[]):
        updated = False
        organization = self.find_organization(organization)

        kwargs = {'name': name, 'organization': organization}

        if lifecycle_environment:
            kwargs['environment'] = self.find_lifecycle_environment(lifecycle_environment, organization)

        if content_view:
            kwargs['content_view'] = self.find_content_view(content_view, organization)

        activation_key = self._entities.ActivationKey(self._server, **kwargs)
        response = activation_key.search({'name', 'organization'})

        if len(response) == 0:
            if not self.check_mode():
                activation_key = activation_key.create()
            updated = True
        elif len(response) == 1:
            updated, activation_key = self.update_fields(activation_key, response[0], ['organization', 'environment', 'content_view'])
            if updated:
                if not self.check_mode():
                    activation_key.update()

        if subscriptions is None:
            subscriptions = []
        desired_subscription_ids = map(lambda s: s.id, self.find_subscriptions(subscriptions, organization))
        current_subscriptions = [entities.Subscription(self._server, **result)
                                 for result in entities.Subscription(self._server).search_normalize(activation_key.subscriptions()['results'])]
        current_subscription_ids = map(lambda s: s.id, current_subscriptions)

        if set(desired_subscription_ids) != set(current_subscription_ids):
            if not self.check_mode():
                for subscription_id in set(desired_subscription_ids) - set(current_subscription_ids):
                    activation_key.add_subscriptions(data={'quantity': 1, 'subscription_id': subscription_id})
                for subscription_id in set(current_subscription_ids) - set(desired_subscription_ids):
                    activation_key.remove_subscriptions(data={'subscription_id': subscription_id})
            updated = True

        return updated


def main():
    module = AnsibleModule(
        argument_spec=dict(
            server_url=dict(required=True),
            username=dict(required=True, no_log=True),
            password=dict(required=True, no_log=True),
            verify_ssl=dict(type='bool', default=True),
            name=dict(required=True),
            organization=dict(required=True),
            lifecycle_environment=dict(),
            content_view=dict(),
            subscriptions=dict(type='list'),
        ),
        supports_check_mode=True,
    )

    if not HAS_NAILGUN_PACKAGE:
        module.fail_json(msg="Missing required nailgun module (check docs or install "
                             "with: pip install nailgun)")

    server_url = module.params['server_url']
    username = module.params['username']
    password = module.params['password']
    verify_ssl = module.params['verify_ssl']
    name = module.params['name']
    organization = module.params['organization']
    lifecycle_environment = module.params['lifecycle_environment']
    content_view = module.params['content_view']
    subscriptions = module.params['subscriptions']

    server = ServerConfig(
        url=server_url,
        auth=(username, password),
        verify=verify_ssl
    )
    ng = NailGun(server, entities, module)

    # Lets make an connection to the server with username and password
    try:
        org = entities.Organization(server)
        org.search()
    except Exception as e:
        module.fail_json(msg="Failed to connect to Foreman server: %s " % e)

    try:
        changed = ng.activation_key(name, organization, lifecycle_environment=lifecycle_environment, content_view=content_view, subscriptions=subscriptions)
        module.exit_json(changed=changed)
    except Exception as e:
        module.fail_json(msg=e)


from ansible.module_utils.basic import AnsibleModule

if __name__ == '__main__':
    main()
