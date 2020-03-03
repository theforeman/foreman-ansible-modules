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

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: katello_sync_plan
short_description: Manage Katello sync plans
description:
    - Manage Katello sync plans
author:
    - "Andrew Kofink (@akofink)"
    - "Matthis Dellweg (@mdellweg) ATIX-AG"
options:
  name:
    description:
      - Name of the Katello sync plan
    required: true
    type: str
  description:
    description:
      - Description of the Katello sync plan
    type: str
  interval:
    description:
      - How often synchronization should run
    choices:
      - hourly
      - daily
      - weekly
      - custom cron
    required: true
    type: str
  enabled:
    description:
      - Whether the sync plan is active
    required: true
    type: bool
  sync_date:
    description:
      - Start date and time of the first synchronization
    required: true
    type: str
  cron_expression:
    description:
      - A cron expression as found in crontab files
      - This must be provided together with I(interval='custom cron').
    type: str
  products:
    description:
      - List of products to include in the sync plan
    required: false
    type: list
    elements: str
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.entity_state_with_defaults
  - theforeman.foreman.foreman.organization
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
    sync_date: "2017-01-01 00:00:00 UTC"
    products:
      - 'Red Hat Enterprise Linux Server'
    state: present
'''

RETURN = ''' # '''


from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import KatelloEntityAnsibleModule


def main():
    module = KatelloEntityAnsibleModule(
        entity_spec=dict(
            name=dict(required=True),
            description=dict(),
            interval=dict(choices=['hourly', 'daily', 'weekly', 'custom cron'], required=True),
            enabled=dict(type='bool', required=True),
            sync_date=dict(required=True),
            cron_expression=dict(),
            state=dict(default='present', choices=['present_with_defaults', 'present', 'absent']),
        ),
        argument_spec=dict(
            products=dict(type='list', elements='str'),
        ),
        required_if=[
            ['interval', 'custom cron', ['cron_expression']],
        ],
    )

    entity_dict = module.clean_params()

    if (entity_dict['interval'] != 'custom cron') and ('cron_expression' in entity_dict):
        module.fail_json(msg='"cron_expression" cannot be combined with "interval"!="custom cron".')

    with module.api_connection():
        entity_dict, scope = module.handle_organization_param(entity_dict)

        entity = module.find_resource_by_name('sync_plans', name=entity_dict['name'], params=scope, failsafe=True)

        products = entity_dict.pop('products', None)

        sync_plan = module.ensure_entity('sync_plans', entity_dict, entity, params=scope)

        if not (module.desired_absent or module.state == 'present_with_defaults') and products is not None:
            products = module.find_resources_by_name('products', products, params=scope, thin=True)
            desired_product_ids = set(product['id'] for product in products)
            current_product_ids = set(product['id'] for product in entity['products']) if entity else set()

            module.record_before('sync_plans/products', {'id': sync_plan['id'], 'product_ids': current_product_ids})
            module.record_after('sync_plans/products', {'id': sync_plan['id'], 'product_ids': desired_product_ids})
            module.record_after_full('sync_plans/products', {'id': sync_plan['id'], 'product_ids': desired_product_ids})

            if desired_product_ids != current_product_ids:
                if not module.check_mode:
                    product_ids_to_add = desired_product_ids - current_product_ids
                    if product_ids_to_add:
                        payload = {
                            'id': sync_plan['id'],
                            'product_ids': list(product_ids_to_add),
                        }
                        payload.update(scope)
                        module.resource_action('sync_plans', 'add_products', payload)
                    product_ids_to_remove = current_product_ids - desired_product_ids
                    if product_ids_to_remove:
                        payload = {
                            'id': sync_plan['id'],
                            'product_ids': list(product_ids_to_remove),
                        }
                        payload.update(scope)
                        module.resource_action('sync_plans', 'remove_products', payload)
                else:
                    module.set_changed()


if __name__ == '__main__':
    main()
