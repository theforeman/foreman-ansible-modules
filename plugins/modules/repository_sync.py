#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2016, Eric D Helms <ericdhelms@gmail.com>
# (c) 2019, Matthias M Dellweg <dellweg@atix.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: repository_sync
version_added: 1.0.0
short_description: Sync a Repository or Product
description:
  - Sync a repository or product
author:
  - "Eric D Helms (@ehelms)"
  - "Matthias M Dellweg (@mdellweg) ATIX AG"
options:
  product:
    description: Product to which the I(repository) lives in
    required: true
    type: str
  repository:
    description:
      - Names of the repositories to sync.
      - If omitted or empty, all repositories in I(product) are synced.
    type: list
    elements: str
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.organization
...
'''

EXAMPLES = '''
- name: "Sync repository"
  theforeman.foreman.repository_sync:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    repository:
      - "My repository"
      - "My other repository"
    product: "My Product"
    organization: "Default Organization"
'''

RETURN = ''' # '''

from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import KatelloAnsibleModule


def _sync_repositories(module, product, repositories):
    if not repositories:
        return module.resource_action('products', 'sync', {'id': product['id']})
    if len(repositories) == 1:
        return module.resource_action('repositories', 'sync', {'id': repositories[0]['id']})
    return module.resource_action(
        'repositories_bulk_actions',
        'sync_repositories',
        {'ids': [repository['id'] for repository in repositories]},
    )


def main():
    module = KatelloAnsibleModule(
        foreman_spec=dict(
            product=dict(type='entity', scope=['organization'], required=True),
            repository=dict(type='list', elements='str'),
            repositories=dict(type='entity_list', scope=['product'], invisible=True),
        ),
    )

    module.task_timeout = 12 * 60 * 60

    with module.api_connection():
        product = module.lookup_entity('product')
        repository_names = module.foreman_params.pop('repository', [])
        module.foreman_params['repositories'] = repository_names
        repositories = module.lookup_entity('repositories') if repository_names else []
        task = _sync_repositories(module, product, repositories)

        module.exit_json(task=task)


if __name__ == '__main__':
    main()
