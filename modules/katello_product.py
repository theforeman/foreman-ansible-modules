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
module: katello_product
short_description: Create and Manage Katello products
description:
    - Create and Manage Katello products
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
    name:
        description:
            - Name of the Katello product
        required: true
    organization:
        description:
            - Organization that the Product is in
        required: true
'''

EXAMPLES = '''
- name: "Create Fedora product"
  katello_product:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "Fedora"
    organization: "My Cool new Organization"
'''

RETURN = '''# '''

try:
    from nailgun import entities
    from nailgun.config import ServerConfig
    HAS_NAILGUN_PACKAGE = True
except:
    HAS_NAILGUN_PACKAGE = False

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.foreman_helper import handle_no_nailgun


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

    def product(self, name, organization):
        updated = False
        org = self.find_organization(organization)
        product = self._entities.Product(self._server, name=name, organization=org)
        product = product.search()

        product = product[0] if len(product) == 1 else None

        if product and product.name != name:
            product = self._entities.Product(self._server, name=name, id=product.id)
            if not self.check_mode:
                product.update()
            updated = True
        elif not product:
            product = self._entities.Product(self._server, name=name, organization=org)
            if not self.check_mode:
                product.create()
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
        ),
        supports_check_mode=True,
    )

    handle_no_nailgun(module, HAS_NAILGUN_PACKAGE)

    server_url = module.params['server_url']
    username = module.params['username']
    password = module.params['password']
    verify_ssl = module.params['verify_ssl']
    name = module.params['name']
    organization = module.params['organization']

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
        changed = ng.product(name, organization)
        module.exit_json(changed=changed)
    except Exception as e:
        module.fail_json(msg=e)


if __name__ == '__main__':
    main()
