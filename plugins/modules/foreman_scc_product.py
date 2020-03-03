#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2019 Manisha Singhal (ATIX AG)
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
module: foreman_scc_product
short_description: Subscribe Foreman Suse Customer Center Account Product
description:
  - "Manage Foreman Suse Customer Center Product Entities"
  - "This module requires the foreman_scc_manager plugin set up in the server"
  - "See: U(https://github.com/ATIX-AG/foreman_scc_manager)"
author:
  - "Manisha Singhal (@manisha15) ATIX AG"
options:
  friendly_name:
    description: Full name of the product of suse customer center account
    required: true
    type: str
  scc_account:
    description: Name of the suse customer center account associated with product
    required: true
    type: str
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.organization
'''

EXAMPLES = '''
- name: "Subscribe to suse customer center product"
  foreman_scc_product:
    friendly_name: "Product1"
    scc_account_name: "Test"
    organization: "Test Organization"
'''

RETURN = ''' # '''


from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import KatelloAnsibleModule


def main():
    module = KatelloAnsibleModule(
        argument_spec=dict(
            friendly_name=dict(required=True),
            scc_account=dict(required=True),
        ),
    )

    module.task_timeout = 4 * 60

    params = module.clean_params()

    with module.api_connection():
        params, scope = module.handle_organization_param(params)

        params['scc_account'] = module.find_resource_by_name('scc_accounts', name=params['scc_account'], params=scope, thin=True)

        scc_account_scope = {'scc_account_id': params['scc_account']['id']}

        # Try to find the SccProduct to work on
        # name is however not unique, but friendly_name is

        search_string = 'friendly_name="{0}"'.format(params['friendly_name'])
        scc_product = module.find_resource('scc_products', search_string, params=scc_account_scope)

        if not scc_product.get('product_id'):
            module.resource_action('scc_products', 'subscribe', {'id': scc_product['id'], 'scc_account_id': scc_account_scope['scc_account_id']})


if __name__ == '__main__':
    main()
