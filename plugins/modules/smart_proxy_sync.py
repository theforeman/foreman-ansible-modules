#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2026, Pablo Méndez Hernández <pmendezh@redhat.com>
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
module: smart_proxy_sync
version_added: 5.11.0
short_description: Sync content on a Smart Proxy
description:
  - Synchronize content on a Smart Proxy.
author:
  - "Pablo Méndez Hernández (@pablomh)"
options:
  smart_proxy:
    description:
      - Name of the Smart Proxy to synchronize content on.
    required: true
    type: str
  lifecycle_environment:
    description:
      - Name of the Lifecycle Environment to limit the synchronization on.
    required: false
    type: str
  content_view:
    description:
      - Name of the Content View to limit the synchronization on.
    required: false
    type: str
  product:
    description:
      - Name of the Product the I(repository) belongs to.
      - Required when I(repository) is specified.
    required: false
    type: str
  repository:
    description:
      - Name of the Repository to limit the synchronization on.
      - Requires I(product) to be specified.
    required: false
    type: str
  skip_metadata_check:
    description:
      - Skip metadata check on each repository on the Smart Proxy.
    required: false
    type: bool
attributes:
  check_mode:
    support: none
  diff_mode:
    support: none
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.organization
...
'''

EXAMPLES = '''
- name: "Sync all content on a Smart Proxy"
  theforeman.foreman.smart_proxy_sync:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    organization: "Default Organization"
    smart_proxy: "capsule.example.com"

- name: "Sync a specific lifecycle environment on a Smart Proxy"
  theforeman.foreman.smart_proxy_sync:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    organization: "Default Organization"
    smart_proxy: "capsule.example.com"
    lifecycle_environment: "Production"

- name: "Sync a specific repository on a Smart Proxy"
  theforeman.foreman.smart_proxy_sync:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    organization: "Default Organization"
    smart_proxy: "capsule.example.com"
    product: "Red Hat Enterprise Linux for x86_64"
    repository: "Red Hat Enterprise Linux 9 for x86_64 - BaseOS RPMs 9"
'''

RETURN = ''' # '''

from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import KatelloAnsibleModule


def main():
    module = KatelloAnsibleModule(
        foreman_spec=dict(
            smart_proxy=dict(type='entity', required=True),
            lifecycle_environment=dict(type='entity', scope=['organization']),
            content_view=dict(type='entity', scope=['organization']),
            product=dict(type='entity', scope=['organization']),
            repository=dict(type='entity', scope=['product']),
            skip_metadata_check=dict(type='bool'),
        ),
        supports_check_mode=False,
    )

    if 'repository' in module.foreman_params and 'product' not in module.foreman_params:
        module.fail_json(msg="'product' is required when 'repository' is specified")

    module.task_timeout = 12 * 60 * 60

    with module.api_connection():
        smart_proxy = module.lookup_entity('smart_proxy')

        payload = {'id': smart_proxy['id']}

        if 'lifecycle_environment' in module.foreman_params:
            lce = module.lookup_entity('lifecycle_environment')
            payload['environment_id'] = lce['id']

        if 'content_view' in module.foreman_params:
            cv = module.lookup_entity('content_view')
            payload['content_view_id'] = cv['id']

        if 'repository' in module.foreman_params:
            module.lookup_entity('product')
            repo = module.lookup_entity('repository')
            payload['repository_id'] = repo['id']

        if 'skip_metadata_check' in module.foreman_params:
            payload['skip_metadata_check'] = module.foreman_params['skip_metadata_check']

        task = module.resource_action('capsule_content', 'sync', payload)
        module.exit_json(task=task)


if __name__ == '__main__':
    main()
