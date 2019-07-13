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
author:
    - "Eric D Helms (@ehelms)"
    - "Matthias Dellweg (@mdellweg) ATIX AG"
requirements:
    - apypie
options:
  name:
    description:
      - Name of the Katello product
    required: true
  organization:
    description:
      - Organization that the Product is in
    required: true
  label:
    description:
      - Label to show the user
    required: false
  gpg_key:
    description:
    - Content GPG key name attached to this product
    required: false
  sync_plan:
    description:
      - Sync plan name attached to this product
    required: false
  description:
    description:
      - Possibly long descriptionto show the user in detail view
    required: false
  state:
    description:
      - State of the Product
    default: present
    choices:
      - present
      - absent
      - present_with_defaults
extends_documentation_fragment: foreman
'''

EXAMPLES = '''
- name: "Create Fedora product with a sync plan"
  katello_product:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "Fedora"
    organization: "My Cool new Organization"
    sync_plan: "Fedora repos sync"
    state: present

- name: "Create CentOS 7 product with content credentials"
  katello_product:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "CentOS 7"
    gpg_key: "RPM-GPG-KEY-CentOS7"
    organization: "My Cool new Organization"
    state: present
'''

RETURN = ''' # '''


from ansible.module_utils.foreman_helper import KatelloEntityApypieAnsibleModule


# This is the only true source for names (and conversions thereof)
name_map = {
    'name': 'name',
    'organization': 'organization_id',
    'description': 'description',
    'gpg_key': 'gpg_key_id',
    'sync_plan': 'sync_plan_id',
    'label': 'label',
}


def main():
    module = KatelloEntityApypieAnsibleModule(
        argument_spec=dict(
            name=dict(required=True),
            label=dict(),
            gpg_key=dict(),
            sync_plan=dict(),
            description=dict(),
            state=dict(default='present', choices=['present_with_defaults', 'present', 'absent']),
        ),
    )

    entity_dict = module.clean_params()

    module.connect()

    entity_dict['organization'] = module.find_resource_by_name('organizations', name=entity_dict['organization'], thin=True)
    search_params = {'organization_id': entity_dict['organization']['id']}
    entity = module.find_resource_by_name('products', name=entity_dict['name'], params=search_params, failsafe=True)

    if not module.desired_absent:
        if 'gpg_key' in entity_dict:
            entity_dict['gpg_key'] = module.find_resource_by_name('content_credentials', name=entity_dict['gpg_key'], params=search_params, thin=True)

        if 'sync_plan' in entity_dict:
            entity_dict['sync_plan'] = module.find_resource_by_name('sync_plans', name=entity_dict['sync_plan'], params=search_params, thin=True)

    changed = module.ensure_resource_state('products', entity_dict, entity, name_map=name_map)

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()
