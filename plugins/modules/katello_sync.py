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

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: katello_sync
short_description: Sync a Katello repository or product
description:
  - Sync a Katello repository or product
author:
  - "Eric D Helms (@ehelms)"
  - "Matthias M Dellweg (@mdellweg) ATIX AG"
options:
  product:
    description: Product to which the I(repository) lives in
    required: true
    type: str
  repository:
    description: |
      Name of the repository to sync
      If omitted, all repositories in I(product) are synched.
    type: str
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.organization
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
    resource: repositories
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

from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import KatelloAnsibleModule


def main():
    module = KatelloAnsibleModule(
        argument_spec=dict(
            product=dict(required=True),
            repository=dict(),
        ),
    )

    module.task_timeout = 12 * 60 * 60

    params = module.clean_params()

    with module.api_connection():
        params, scope = module.handle_organization_param(params)

        params['product'] = module.find_resource_by_name('products', params['product'], params=scope, thin=True)
        if 'repository' in params:
            product_scope = {'product_id': params['product']['id']}
            params['repository'] = module.find_resource_by_name('repositories', params['repository'], params=product_scope, thin=True)
            task = module.resource_action('repositories', 'sync', {'id': params['repository']['id']})
        else:
            task = module.resource_action('products', 'sync', {'id': params['product']['id']})

        module.exit_json(task=task)


if __name__ == '__main__':
    main()
