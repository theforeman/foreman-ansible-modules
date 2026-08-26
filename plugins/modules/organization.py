#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2016, Eric D Helms <ericdhelms@gmail.com>
# (c) 2017, Matthias M Dellweg <dellweg@atix.de> (ATIX AG)
# (c) 2022, Jeffrey van Pelt <jeff@vanpelt.one>
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
module: organization
version_added: 1.0.0
short_description: Manage Organizations
description:
    - Manage Organizations
author:
    - "Eric D Helms (@ehelms)"
    - "Matthias M Dellweg (@mdellweg) ATIX AG"
    - "Jeffrey van Pelt (@Thulium-Drake)"
options:
  name:
    description:
      - Name of the Organization
    required: true
    type: str
  description:
    description:
      - Description of the Organization
    required: false
    type: str
  label:
    description:
      - Label of the Organization
    type: str
  ignore_types:
    description:
      - List of resources types that will be automatically associated
    type: list
    elements: str
    required: false
    aliases:
      - select_all_types
    version_added: 3.8.0
  upstream_type:
    description:
      - Type of upstream content source
    required: false
    type: str
    choices:
      - redhat_cdn
      - network_sync
      - export_sync
      - custom_cdn
  upstream_url:
    description:
      - URL of the upstream resource
      - Required when I(upstream_type) is C(redhat_cdn) or C(network_sync)
    required: false
    type: str
  upstream_ca_cert:
    description:
      - SSL CA certificate used to validate I(upstream_url)
    required: false
    type: str
  upstream_username:
    description:
      - Username to authenticate to the upstream Foreman server
      - Required when I(upstream_type) is C(network_sync)
    required: false
    type: str
  upstream_password:
    description:
      - Password to authenticate to the upstream Foreman server
      - Required when I(upstream_type) is C(network_sync)
    required: false
    type: str
  upstream_organization:
    description:
      - Organization in the upstream Foreman server to synchronize
      - Required when I(upstream_type) is C(network_sync)
    required: false
    type: str
  upstream_content_view:
    description:
      - Content View in the upstream Foreman server to synchronize
      - Required when I(upstream_type) is C(network_sync)
    required: false
    type: str
  upstream_lifecycle_environment:
    description:
      - Lifecycle Environment in the upstream Foreman server to synchronize
      - Required when I(upstream_type) is C(network_sync)
    required: false
    type: str
  upstream_custom_cdn_auth_enabled:
    description:
      - If product certificates should be used to authenticate to a custom CDN.
    type: bool
    required: false
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.entity_state
  - theforeman.foreman.foreman.nested_parameters
'''

EXAMPLES = '''
- name: "Create CI Organization"
  theforeman.foreman.organization:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "My Cool New Organization"
    state: present

- name: "Configure Red Hat CDN on a different URL"
  theforeman.foreman.organization:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "My Cool New Organization"
    upstream_type: "redhat_cdn"
    upstream_url: "https://internal-cdn.example.com"

- name: "Configure ISS Export Sync"
  theforeman.foreman.organization:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "My Cool New Organization"
    upstream_type: "export_sync"

- name: "Configure ISS Network Sync"
  theforeman.foreman.organization:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "My Cool New Organization"
    upstream_type: "network_sync"
    upstream_url: "https://upstream-foreman.example.com"
    upstream_ca_cert: "Upstream Foreman"
    upstream_username: sync_user
    upstream_password: changeme2
    upstream_organization: "Default Organization"
    upstream_lifecycle_environment: "Library"
    upstream_content_view: "Foreman_Network_Sync_View"
'''

RETURN = '''
entity:
  description: Final state of the affected entities grouped by their type.
  returned: success
  type: dict
  contains:
    organizations:
      description: List of organizations.
      type: list
      elements: dict
'''


from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import ForemanEntityAnsibleModule, NestedParametersMixin


class ForemanOrganizationModule(NestedParametersMixin, ForemanEntityAnsibleModule):
    pass


def main():
    module = ForemanOrganizationModule(
        foreman_spec=dict(
            name=dict(required=True),
            description=dict(),
            label=dict(),
            ignore_types=dict(type='list', elements='str', required=False, aliases=['select_all_types']),
            select_all_types=dict(type='list', invisible=True, flat_name='ignore_types'),
            upstream_type=dict(required=False, choices=['redhat_cdn', 'export_sync', 'network_sync', 'custom_cdn']),
            upstream_url=dict(required=False),
            upstream_username=dict(required=False),
            upstream_password=dict(required=False, no_log=True),
            upstream_ca_cert=dict(required=False, type='entity', resource_type='content_credentials', scope=['organization']),
            upstream_organization=dict(required=False),
            upstream_lifecycle_environment=dict(required=False),
            upstream_content_view=dict(required=False),
            upstream_custom_cdn_auth_enabled=dict(required=False, type='bool'),
        ),
    )

    with module.api_connection():
        entity = module.lookup_entity('entity')

        # workround the fact that the API expects `ignore_types` when modifying the entity
        # but uses `select_all_types` when showing one
        if entity and 'select_all_types' in entity:
            entity['ignore_types'] = entity.pop('select_all_types')

        handle_cdn_configuration = 'upstream_type' in module.foreman_params

        organization = module.run()

        if handle_cdn_configuration and not module.desired_absent:
            payload = {
                'id': organization['id'],
            }
            extra_payload = {
                'type': module.foreman_params['upstream_type'],
            }

            if module.foreman_params['upstream_type'] == 'redhat_cdn':
                cdn_config = {
                    'url': module.foreman_params['upstream_url'],
                }
                extra_payload.update(cdn_config)
            if module.foreman_params['upstream_type'] == 'network_sync':
                cdn_config = {
                    'url': module.foreman_params['upstream_url'],
                    'ssl_ca_credential_id': module.foreman_params['upstream_ca_cert'],
                    'username': module.foreman_params['upstream_username'],
                    'password': module.foreman_params['upstream_password'],
                    'upstream_organization_label': module.foreman_params['upstream_organization'],
                    'upstream_lifecycle_environment_label': module.foreman_params['upstream_lifecycle_environment'],
                    'upstream_content_view_label': module.foreman_params['upstream_content_view'],
                }
                extra_payload.update(cdn_config)
            if module.foreman_params['upstream_type'] == 'custom_cdn':
                cdn_config = {
                    'url': module.foreman_params['upstream_url'],
                    'ssl_ca_credential_id': module.foreman_params['upstream_ca_cert'],
                    'username': module.foreman_params['upstream_username'],
                    'password': module.foreman_params['upstream_password'],
                    'upstream_organization_label': module.foreman_params['upstream_organization'],
                    'upstream_lifecycle_environment_label': module.foreman_params['upstream_lifecycle_environment'],
                    'upstream_content_view_label': module.foreman_params['upstream_content_view'],
                    'custom_cdn_auth_enabled': module.foreman_params['upstream_custom_cdn_auth_enabled'],
                }
                extra_payload.update(cdn_config)

            current_cdn_config = {k: v for k, v in organization['cdn_configuration'].items() if v is not None}
            del current_cdn_config['password_exists']

            if current_cdn_config != extra_payload:
                if extra_payload:
                    payload.update(extra_payload)
                module.resource_action('organizations', 'cdn_configuration', payload)


if __name__ == '__main__':
    main()
