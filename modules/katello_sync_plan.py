#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2017, Andrew Kofink <ajkofink@gmail.com>
# (c) 2019, Matthias Dellweg <dellweg@atix.de>
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
short_description: Manage Katello sync plans
description:
    - Manage Katello sync plans
author:
    - "Andrew Kofink (@akofink)"
    - "Matthis Dellweg (@mdellweg) ATIX-AG"
requirements:
    - "nailgun >= 0.32.0"
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
      - Name of the Katello sync plan
    required: true
  description:
    description:
      - Description of the Katello sync plan
  organization:
    description:
      - Organization that the sync plan is in
    required: true
  interval:
    description:
      - How often synchronization should run
    choices:
      - hourly
      - daily
      - weekly
      - custom cron
    required: true
  enabled:
    description:
      - Whether the sync plan is active
    required: true
  sync_date:
    description:
      - Start date and time of the first synchronization
    required: true
  cron_expression:
    description:
      - A cron expression as found in crontab files
      - This must be provided together with I(interval='custom cron').
  products:
    description:
      - List of products to include in the sync plan
    required: false
    type: list
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
    sync_date: "2017/01/01 00:00:00 +0000"
    products:
      - 'Red Hat Enterprise Linux Server'
'''

RETURN = ''' # '''

from ansible.module_utils.ansible_nailgun_cement import (
    SyncPlan,
    find_organization,
    find_products,
    find_sync_plan,
    naildown_entity,
    sanitize_entity_dict,
)

from ansible.module_utils.foreman_helper import ForemanEntityAnsibleModule


# This is the only true source for names (and conversions thereof)
name_map = {
    'name': 'name',
    'description': 'description',
    'organization': 'organization',
    'interval': 'interval',
    'enabled': 'enabled',
    'sync_date': 'sync_date',
    'cron_expression': 'cron_expression',
    'products': 'product',
}


def main():
    module = ForemanEntityAnsibleModule(
        argument_spec=dict(
            name=dict(required=True),
            description=dict(),
            organization=dict(required=True),
            interval=dict(choices=['hourly', 'daily', 'weekly', 'custom cron'], required=True),
            enabled=dict(type='bool', required=True),
            sync_date=dict(required=True),
            cron_expression=dict(),
            products=dict(type='list'),
        ),
        required_if=[
            ['interval', 'custom cron', ['cron_expression']],
        ],
        supports_check_mode=True,
    )

    (entity_dict, state) = module.parse_params()

    if entity_dict['interval'] != 'custom cron':
        if 'cron_expression' in entity_dict:
            module.fail_json(msg='"cron_expression" cannot be combined with "interval"!="custom cron".')

    module.connect()

    entity_dict['organization'] = find_organization(module, entity_dict['organization'])
    products = entity_dict.pop('products', None)

    sync_plan = find_sync_plan(module, entity_dict['name'], entity_dict['organization'], failsafe=True)

    entity_dict = sanitize_entity_dict(entity_dict, name_map)

    changed, sync_plan = naildown_entity(SyncPlan, entity_dict, sync_plan, state, module)

    if products is not None:
        products = find_products(module, products, entity_dict['organization'])
        desired_product_ids = set(p.id for p in products)
        current_product_ids = set(p.id for p in sync_plan.product)

        if desired_product_ids != current_product_ids:
            if not module.check_mode:
                product_ids_to_add = desired_product_ids - current_product_ids
                if product_ids_to_add:
                    sync_plan.add_products(data={'product_ids': list(product_ids_to_add)})
                product_ids_to_remove = current_product_ids - desired_product_ids
                if product_ids_to_remove:
                    sync_plan.remove_products(data={'product_ids': list(product_ids_to_remove)})
            changed = True

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()
