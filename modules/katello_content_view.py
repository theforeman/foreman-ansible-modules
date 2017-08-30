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
    name:
        description:
            - Name of the Katello product
        required: true
    organization:
        description:
            - Organization that the Product is in
        required: true
    repositories:
        description:
            - List of repositories that include name and product
        required: false
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
'''

RETURN = '''# '''

try:
    from nailgun import entities, entity_fields
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

    def find_product(self, name, organization):
        product = self._entities.Product(self._server, name=name, organization=organization)
        response = product.search()

        if len(response) == 1:
            return response[0]
        else:
            self._module.fail_json(msg="No Product found for %s" % name)

    def find_repository(self, name, product, organization):
        product = self.find_product(product, organization)

        repository = self._entities.Repository(self._server, name=name, product=product)
        repository._fields['organization'] = entity_fields.OneToOneField(entities.Organization)
        repository.organization = product.organization
        response = repository.search()

        if len(response) == 1:
            return response[0]
        else:
            self._module.fail_json(msg="No Repository found for %s" % name)

    def find_repositories(self, repositories, organization):
        return map(lambda repository: self.find_repository(repository['name'], repository['product'], organization), repositories)

    def content_view(self, name, organization, repositories=[]):
        updated = False
        organization = self.find_organization(organization)

        content_view = self._entities.ContentView(self._server, name=name, organization=organization)
        response = content_view.search()

        if len(response) == 1:
            content_view = response[0]
        elif len(response) == 0:
            content_view = content_view.create()
            updated = True

        repositories = self.find_repositories(repositories, organization)

        if set(map(lambda r: r.id, repositories)) != set(map(lambda r: r.id, content_view.repository)):
            content_view.repository = repositories
            content_view.update(['repository'])
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
            repositories=dict(type='list'),
        ),
        supports_check_mode=False,
    )

    if not HAS_NAILGUN_PACKAGE:
        module.fail_json(msg="Missing required nailgun module (check docs or install with: pip install nailgun")

    server_url = module.params['server_url']
    username = module.params['username']
    password = module.params['password']
    verify_ssl = module.params['verify_ssl']
    name = module.params['name']
    organization = module.params['organization']
    repositories = module.params['repositories']

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

    kwargs = {}
    if repositories:
        kwargs['repositories'] = repositories

    try:
        changed = ng.content_view(name, organization, **kwargs)
        module.exit_json(changed=changed)
    except Exception as e:
        module.fail_json(msg=e)


from ansible.module_utils.basic import AnsibleModule

if __name__ == '__main__':
    main()
