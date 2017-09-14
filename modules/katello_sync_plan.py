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
module: katello_sync_plan
short_description: Create and Manage Katello sync plans
description:
    - Create and Manage Katello sync plans
author: "Andrew Kofink (@akofink)"
requirements:
    - "nailgun >= 0.29.0"
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
            - Name of the Katello sync plan
        required: true
    organization:
        description:
            - Organization that the sync plan is in
        required: true
    interval:
        description:
            - How often synchronization should run ('hourly', 'daily', 'weekly')
        required: true
    enabled:
        description:
            - Whether the sync plan is active
        required: true
    sync_date:
        description:
            - Start date and time of the first synchronization (default: now)
        required: true
    products:
        description:
            - List of products to include in the sync plan
        required: false
'''

EXAMPLES = '''
- name: "Create or update weekly RHEL sync plan"
  katello_sync_plan:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "Weekly RHEL Sync"
    organization: "Default Organization"
    interval: "weekly"
    enabled: false
    sync_date: "2017-01-01 00:00:00"
    products:
      - name: 'Red Hat Enterprise Linux Server'
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

    def find_product(self, name, organization):
        product = self._entities.Product(self._server, name=name, organization=organization)
        del(product._fields['sync_plan'])
        response = product.search()

        if len(response) == 1:
            return response[0]
        else:
            self._module.fail_json(msg="No Product found for %s" % name)

    def find_products(self, products, organization):
        return map(lambda product: self.find_product(product['name'], organization), products)

    def update_fields(self, new, old, fields):
        needs_update = False
        for field in fields:
            if hasattr(new, field) and hasattr(old, field):
                new_attr = getattr(new, field)
                old_attr = getattr(old, field)
                if old_attr is None or (hasattr(new_attr, 'id') and hasattr(old_attr, 'id') and new_attr.id != old_attr.id) or new_attr != old_attr:
                    setattr(old, field, new_attr)
                    needs_update = True
            elif hasattr(old, field) and getattr(old, field) is not None and not hasattr(new, field):
                setattr(old, field, None)
                needs_update = True
        return needs_update, old

    def sync_plan(self, name, organization, interval=None, enabled=None, sync_date=None, products=[]):
        updated = False
        organization = self.find_organization(organization)

        enabled = enabled.lower() == "true"

        sync_plan = self._entities.SyncPlan(self._server, name=name, organization=organization, interval=interval, enabled=enabled, sync_date=sync_date)
        response = sync_plan.search({'name', 'organization'})

        if len(response) == 1:
            response[0].sync_date = datetime.strptime(response[0].sync_date, '%Y/%m/%d %H:%M:%S %Z')
            updated, sync_plan = self.update_fields(sync_plan, response[0], ['interval', 'enabled', 'sync_date'])
            if updated and not self.check_mode():
                sync_plan.update()
        elif len(response) == 0:
            if not self.check_mode():
                sync_plan = sync_plan.create()
            updated = True

        desired_product_ids = map(lambda p: p.id, self.find_products(products, organization))
        current_product_ids = map(lambda p: p.id, sync_plan.product)

        if set(desired_product_ids) != set(current_product_ids):
            if not self.check_mode():
                product_ids_to_add = set(desired_product_ids) - set(current_product_ids)
                if len(product_ids_to_add) > 0:
                    sync_plan.add_products(data={'product_ids': list(product_ids_to_add)})
                product_ids_to_remove = set(current_product_ids) - set(desired_product_ids)
                if len(product_ids_to_remove) > 0:
                    sync_plan.remove_products(data={'product_ids': list(product_ids_to_remove)})
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
            interval=dict(required=True),
            enabled=dict(required=True),
            sync_date=dict(required=True),
            products=dict(type='list', default=[]),
        ),
        supports_check_mode=True
    )

    if not HAS_NAILGUN_PACKAGE:
        module.fail_json(msg="Missing required nailgun module (check docs or install with: pip install nailgun")

    server_url = module.params['server_url']
    username = module.params['username']
    password = module.params['password']
    verify_ssl = module.params['verify_ssl']
    name = module.params['name']
    organization = module.params['organization']
    interval = module.params['interval']
    enabled = module.params['enabled']
    sync_date = datetime.strptime(module.params['sync_date'], '%Y-%m-%d %H:%M:%S')
    products = module.params['products']

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
        changed = ng.sync_plan(name, organization, interval=interval, enabled=enabled, sync_date=sync_date, products=products)
        module.exit_json(changed=changed)
    except Exception as e:
        module.fail_json(msg=e)

from ansible.module_utils.basic import AnsibleModule
from datetime import datetime

if __name__ == '__main__':
    main()
