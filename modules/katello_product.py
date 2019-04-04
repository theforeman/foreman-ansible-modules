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
    - "nailgun >= 0.32.0"
    - "python >= 2.6"
    - "ansible >= 2.3"
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

RETURN = '''# '''

try:
    from nailgun.entities import (
        Product,
    )

    from ansible.module_utils.ansible_nailgun_cement import (
        find_organization,
        find_content_credential,
        find_sync_plan,
        find_product,
        naildown_entity_state,
        sanitize_entity_dict,
    )
except ImportError:
    pass

from ansible.module_utils.foreman_helper import KatelloEntityAnsibleModule


# This is the only true source for names (and conversions thereof)
name_map = {
    'name': 'name',
    'organization': 'organization',
    'description': 'description',
    'gpg_key': 'gpg_key',
    'sync_plan': 'sync_plan',
    'label': 'label',
}


def main():
    module = KatelloEntityAnsibleModule(
        argument_spec=dict(
            name=dict(required=True),
            label=dict(),
            gpg_key=dict(),
            sync_plan=dict(),
            description=dict(),
            state=dict(default='present', choices=['present_with_defaults', 'present', 'absent']),
        ),
        supports_check_mode=True,
    )

    (entity_dict, state) = module.parse_params()

    module.connect()

    entity_dict['organization'] = find_organization(module, name=entity_dict['organization'])

    if 'gpg_key' in entity_dict:
        entity_dict['gpg_key'] = find_content_credential(module, name=entity_dict['gpg_key'], organization=entity_dict['organization'])

    if 'sync_plan' in entity_dict:
        entity_dict['sync_plan'] = find_sync_plan(module, name=entity_dict['sync_plan'], organization=entity_dict['organization'])

    entity = find_product(module, name=entity_dict['name'], organization=entity_dict['organization'], failsafe=True)

    entity_dict = sanitize_entity_dict(entity_dict, name_map)

    changed = naildown_entity_state(Product, entity_dict, entity, state, module)

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()
