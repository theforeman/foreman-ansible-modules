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

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: katello_repository
short_description: Create and manage Katello repository
description:
    - Crate and manage a Katello repository
author: "Eric D Helms (@ehelms)"
options:
  name:
    description:
      - Name of the repository
    required: true
    type: str
  product:
    description:
      - Product to which the repository lives in
    required: true
    type: str
  label:
    description:
      - label of the repository
    type: str
  organization:
    description:
      - Organization that the Product is in
    required: true
    type: str
  content_type:
    description:
      - The content type of the repository (e.g. yum)
    required: true
    choices:
      - deb
      - docker
      - file
      - ostree
      - puppet
      - yum
    type: str
  url:
    description:
      - Repository URL to sync from
    required: false
    type: str
  docker_upstream_name:
    description:
      - name of the upstream docker repository
    type: str
  mirror_on_sync:
    description:
      - toggle "mirror on sync" where the state of the repository mirrors that of the upstream repository at sync time
    default: true
    type: bool
    required: false
  download_policy:
    description:
      - download policy for sync from upstream
    choices:
      - background
      - immediate
      - on_demand
    required: false
    type: str
  gpg_key:
    description:
    - Repository GPG key
    required: false
    type: str
  state:
    description:
      - State of the Repository
      - C(present_with_defaults) will ensure the entity exists, but won't update existing ones
    default: present
    choices:
      - present_with_defaults
      - present
      - absent
    type: str
extends_documentation_fragment: foreman
'''

EXAMPLES = '''
- name: "Create repository"
  katello_repository:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "My repository"
    state: present
    content_type: "yum"
    product: "My Product"
    organization: "Default Organization"
    url: "http://yum.theforeman.org/plugins/latest/el7/x86_64/"
    mirror_on_sync: true
    download_policy: background

- name: "Create repository with content credentials"
  katello_repository:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "My repository 2"
    state: present
    content_type: "yum"
    product: "My Product"
    organization: "Default Organization"
    url: "http://yum.theforeman.org/releases/latest/el7/x86_64/"
    download_policy: background
    mirror_on_sync: true
    gpg_key: RPM-GPG-KEY-my-product2
'''

RETURN = ''' # '''


from ansible.module_utils.foreman_helper import KatelloEntityAnsibleModule


def main():
    module = KatelloEntityAnsibleModule(
        argument_spec=dict(
            product=dict(required=True),
        ),
        entity_spec=dict(
            label=dict(),
            name=dict(required=True),
            content_type=dict(required=True, choices=['docker', 'ostree', 'yum', 'puppet', 'file', 'deb']),
            url=dict(),
            gpg_key=dict(type='entity', flat_name='gpg_key_id'),
            docker_upstream_name=dict(),
            download_policy=dict(choices=['background', 'immediate', 'on_demand']),
            mirror_on_sync=dict(type='bool', default=True),
            state=dict(default='present', choices=['present_with_defaults', 'present', 'absent']),
        ),
    )

    entity_dict = module.clean_params()

    if entity_dict['content_type'] != 'docker' and 'docker_upstream_name' in entity_dict:
        module.fail_json(msg="docker_upstream_name should not be set unless content_type: docker")

    module.connect()

    entity_dict['organization'] = module.find_resource_by_name('organizations', name=entity_dict['organization'], thin=True)
    scope = {'organization_id': entity_dict['organization']['id']}
    entity_dict['product'] = module.find_resource_by_name('products', name=entity_dict['product'], params=scope, thin=True)

    if not module.desired_absent:
        if 'gpg_key' in entity_dict:
            entity_dict['gpg_key'] = module.find_resource_by_name('content_credentials', name=entity_dict['gpg_key'], params=scope, thin=True)

    scope['product_id'] = entity_dict['product']['id']
    entity = module.find_resource_by_name('repositories', name=entity_dict['name'], params=scope, failsafe=True)

    changed = module.ensure_entity_state('repositories', entity_dict, entity, params=scope)

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()
