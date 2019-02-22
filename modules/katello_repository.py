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
module: katello_repository
short_description: Create and manage Katello repository
description:
    - Crate and manage a Katello repository
author: "Eric D Helms (@ehelms)"
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
      - Name of the repository
    required: true
  product:
    description:
      - Product to which the repository lives in
    required: true
  label:
    description:
      - label of the repository
  organization:
    description:
      - Organization that the Product is in
    required: true
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
  url:
    description:
      - Repository URL to sync from
    required: true
  docker_upstream_name:
    description:
      - name of the upstream docker repository
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
  gpg_key:
    description:
    - Repository GPG key
    required: false
  state:
    description:
      - State of the Repository
    default: present
    choices:
      - present_with_defaults
      - present
      - absent
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

RETURN = '''# '''

try:
    from nailgun.entities import (
        Repository,
    )

    from ansible.module_utils.ansible_nailgun_cement import (
        find_organization,
        find_product,
        find_content_credential,
        find_repository,
        naildown_entity_state,
        sanitize_entity_dict,
    )
except ImportError:
    pass

from ansible.module_utils.foreman_helper import KatelloEntityAnsibleModule


# This is the only true source for names (and conversions thereof)
name_map = {
    'name': 'name',
    'product': 'product',
    'content_type': 'content_type',
    'label': 'label',
    'url': 'url',
    'gpg_key': 'gpg_key',
    'docker_upstream_name': 'docker_upstream_name',
    'download_policy': 'download_policy',
    'mirror_on_sync': 'mirror_on_sync',
}


def main():
    module = KatelloEntityAnsibleModule(
        argument_spec=dict(
            product=dict(required=True),
            label=dict(),
            name=dict(required=True),
            content_type=dict(required=True, choices=['docker', 'ostree', 'yum', 'puppet', 'file', 'deb']),
            url=dict(),
            gpg_key=dict(),
            docker_upstream_name=dict(),
            download_policy=dict(choices=['background', 'immediate', 'on_demand']),
            mirror_on_sync=dict(type='bool', default=True),
            state=dict(default='present', choices=['present_with_defaults', 'present', 'absent']),
        ),
        supports_check_mode=True,
    )

    (entity_dict, state) = module.parse_params()

    if entity_dict['content_type'] != 'docker' and 'docker_upstream_name' in entity_dict:
        module.fail_json(msg="docker_upstream_name should not be set unless content_type: docker")

    module.connect()

    entity_dict['organization'] = find_organization(module, name=entity_dict['organization'])

    entity_dict['product'] = find_product(module, name=entity_dict['product'], organization=entity_dict['organization'])

    if 'gpg_key' in entity_dict:
        entity_dict['gpg_key'] = find_content_credential(module, name=entity_dict['gpg_key'], organization=entity_dict['organization'])

    entity = find_repository(module, name=entity_dict['name'], product=entity_dict['product'], failsafe=True)

    entity_dict = sanitize_entity_dict(entity_dict, name_map)

    changed = naildown_entity_state(Repository, entity_dict, entity, state, module)

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()
