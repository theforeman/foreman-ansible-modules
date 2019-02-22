#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2016, Eric D Helms <ericdhelms@gmail.com>
# (c) 2019, Matthias M Dellweg <dellweg@atix.de>
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
module: katello_sync
short_description: Sync a Katello repository or product
description:
  - Sync a Katello repository or product
author:
  - "Eric D Helms (@ehelms)"
  - "Matthias M Dellweg (@mdellweg) ATIX AG"
requirements:
  - "nailgun >= 0.28.0"
options:
  organization:
    description: Organization that the I(product) is in
    required: true
  product:
    description: Product to which the I(repository) lives in
    required: true
  repository:
    description: |
      Name of the repository to sync
      If omitted, all repositories in I(product) are synched.
  synchronous:
    description: Wait for the Sync task to complete if True. Immediately return if False.
    default: true
  server_url:
    description: foreman url
    required: true
  username:
    description: foreman username
    required: true
  password:
    description: foreman user password
    required: true
  verify_ssl:
    description: verify ssl connection when communicating with foreman
    default: true
    type: bool
...
'''

EXAMPLES = '''
- name: "Sync repository"
  katello_sync:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    repository: "My repository"
    product: "My Product"
    organization: "Default Organization"

# Sync all repositories
- name: Get all repositories
  foreman_search_facts:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    resource: Repository
  register: repositories

- name: Kick off repository Sync tasks
  katello_sync:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    product: "{{ item.product.name }}"
    repository:  "{{ item.name }}"
    organization: "Default Organization"
  loop: "{{ repositories.resources }}"
  when: item.url  # Not all repositories have a URL
  async: 999999
  poll: 0
  register: repo_sync_sleeper

- name: Wait until all Syncs have finished
  async_status:
    jid: "{{ repo_sync_sleeper_item.ansible_job_id }}"
  loop: "{{ repo_sync_sleeper.results }}"
  loop_control:
    loop_var: repo_sync_sleeper_item
  when: repo_sync_sleeper_item.ansible_job_id is defined  # Skip items that were skipped in the previous task
  register: async_job_result
  until: async_job_result.finished
  retries: 999
  delay: 10
'''

RETURN = ''' # '''

try:
    from ansible.module_utils.ansible_nailgun_cement import (
        find_organization,
        find_product,
        find_repository,
    )

    from nailgun import entity_mixins
    entity_mixins.TASK_TIMEOUT = 180000  # Publishes can sometimes take a long, long time
except ImportError:
    pass

from ansible.module_utils.foreman_helper import ForemanAnsibleModule


def main():
    module = ForemanAnsibleModule(
        argument_spec=dict(
            organization=dict(required=True),
            product=dict(required=True),
            repository=dict(),
            synchronous=dict(type='bool', default=True),
        ),
        supports_check_mode=False,
    )

    params = module.parse_params()

    module.connect()

    try:
        organization = find_organization(module, params['organization'])
        product = find_product(module, params['product'], organization)
        if 'repository' in params:
            repository = find_repository(module, params['repository'], product)
        else:
            repository = None
    except Exception as e:
        module.fail_json(msg='Failed to find entity: %s ' % e)

    try:
        if repository is None:
            changed = product.sync(params['synchronous'])
        else:
            changed = repository.sync(params['synchronous'])
        module.exit_json(changed=changed)
    except Exception as e:
        module.fail_json(msg=e)


if __name__ == '__main__':
    main()
