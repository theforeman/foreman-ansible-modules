#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2026, Jakub Duchek <jakduch@seznam.cz>
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
module: cdn_configuration
version_added: 5.13.0
short_description: Manage an organization's CDN configuration
description:
  - Manage the CDN configuration used by an organization for Red Hat content.
author:
  - "Jakub Duchek (@jakduch)"
options:
  type:
    description:
      - CDN configuration type.
    required: true
    type: str
    choices:
      - redhat_cdn
      - custom_cdn
      - network_sync
      - export_sync
  url:
    description:
      - URL of the custom CDN or upstream Foreman server.
      - Required for I(type=custom_cdn) and I(type=network_sync).
    type: str
  upstream_username:
    description:
      - Username used to authenticate to the upstream Foreman server.
      - Required for I(type=network_sync).
    type: str
  upstream_password:
    description:
      - Password used to authenticate to the upstream Foreman server.
      - Required for I(type=network_sync) when no upstream password is currently stored.
      - The API does not return this value. Use I(force=true) to rotate an existing password when no other setting changes.
    type: str
  upstream_organization_label:
    description:
      - Organization label on the upstream Foreman server.
      - Required for I(type=network_sync).
    type: str
  upstream_content_view_label:
    description:
      - Content view label on the upstream Foreman server.
      - Relevant only for I(type=network_sync).
    type: str
  upstream_lifecycle_environment_label:
    description:
      - Lifecycle environment label on the upstream Foreman server.
      - Relevant only for I(type=network_sync).
    type: str
  ssl_ca_credential:
    description:
      - Content credential containing the SSL CA certificate.
      - Required for I(type=network_sync) and optional for I(type=custom_cdn).
    type: str
  force:
    description:
      - Update the CDN configuration even when all readable settings already match.
      - This is primarily useful for rotating I(upstream_password), because the API only reports whether a password exists.
    type: bool
    default: false
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.organization
'''

EXAMPLES = '''
- name: "Use the Red Hat CDN"
  theforeman.foreman.cdn_configuration:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    organization: "Default Organization"
    type: redhat_cdn

- name: "Use a custom CDN"
  theforeman.foreman.cdn_configuration:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    organization: "Default Organization"
    type: custom_cdn
    url: "https://cdn.example.com"

- name: "Synchronize from an upstream Foreman server"
  theforeman.foreman.cdn_configuration:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    organization: "Default Organization"
    type: network_sync
    url: "https://upstream.example.com"
    upstream_username: "sync-user"
    upstream_password: "secret"
    upstream_organization_label: "Default_Organization"
    ssl_ca_credential: "Upstream CA"
'''

RETURN = '''
cdn_configuration:
  description: Effective CDN configuration, excluding the upstream password.
  returned: success
  type: dict
'''

from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import KatelloAnsibleModule


PARAMETER_MAP = {
    'type': 'type',
    'url': 'url',
    'upstream_username': 'username',
    'upstream_password': 'password',
    'upstream_organization_label': 'upstream_organization_label',
    'upstream_content_view_label': 'upstream_content_view_label',
    'upstream_lifecycle_environment_label': 'upstream_lifecycle_environment_label',
    'ssl_ca_credential': 'ssl_ca_credential_id',
}

TYPE_PARAMETERS = {
    'redhat_cdn': set(),
    'export_sync': set(),
    'custom_cdn': {'url', 'ssl_ca_credential'},
    'network_sync': {
        'url',
        'upstream_username',
        'upstream_password',
        'upstream_organization_label',
        'upstream_content_view_label',
        'upstream_lifecycle_environment_label',
        'ssl_ca_credential',
    },
}


def _configuration_payload(params):
    payload = {}
    for parameter, api_parameter in PARAMETER_MAP.items():
        if parameter not in params:
            continue
        value = params[parameter]
        if parameter == 'ssl_ca_credential':
            value = value['id']
        payload[api_parameter] = value
    return payload


def _configuration_needs_update(current, desired, force=False):
    if force:
        return True
    for key, value in desired.items():
        if key == 'password':
            if not current.get('password_exists', False):
                return True
        elif current.get(key) != value:
            return True
    return False


def _configuration_result(current, desired):
    result = current.copy()
    result.update((key, value) for key, value in desired.items() if key != 'password')
    if 'password' in desired:
        result['password_exists'] = True
    return result


def main():
    module = KatelloAnsibleModule(
        argument_spec=dict(
            type=dict(required=True, choices=['redhat_cdn', 'custom_cdn', 'network_sync', 'export_sync']),
            url=dict(),
            upstream_username=dict(),
            upstream_password=dict(no_log=True),
            upstream_organization_label=dict(),
            upstream_content_view_label=dict(),
            upstream_lifecycle_environment_label=dict(),
            force=dict(type='bool', default=False),
        ),
        foreman_spec=dict(
            organization=dict(type='entity', required=True, thin=False),
            ssl_ca_credential=dict(type='entity', resource_type='content_credentials', scope=['organization'], thin=False,
                                   flat_name='ssl_ca_credential_id'),
        ),
        required_if=[
            ['type', 'custom_cdn', ['url']],
            ['type', 'network_sync', ['url', 'upstream_username',
                                      'upstream_organization_label', 'ssl_ca_credential']],
        ],
    )
    module.task_timeout = 12 * 60 * 60

    with module.api_connection():
        configuration_type = module.foreman_params['type']
        supplied_parameters = set(module.foreman_params) & (set(PARAMETER_MAP) - {'type'})
        invalid_parameters = supplied_parameters - TYPE_PARAMETERS[configuration_type]
        if invalid_parameters:
            module.fail_json(msg="Parameters {0} are not valid for CDN configuration type {1}.".format(
                ', '.join(sorted(invalid_parameters)), configuration_type))

        organization = module.lookup_entity('organization')
        if 'ssl_ca_credential' in module.foreman_params:
            ssl_ca_credential = module.lookup_entity('ssl_ca_credential')
            if ssl_ca_credential.get('content_type') != 'cert':
                module.fail_json(msg="SSL CA credential {0} is not a certificate.".format(ssl_ca_credential['name']))

        force = module.foreman_params.pop('force')
        current = organization.get('cdn_configuration') or {}
        if configuration_type == 'network_sync' and not current.get('password_exists', False):
            if 'upstream_password' not in module.foreman_params:
                module.fail_json(msg="upstream_password is required when no upstream password is currently stored.")
        elif not force:
            module.foreman_params.pop('upstream_password', None)

        desired = _configuration_payload(module.foreman_params)
        task = None

        if _configuration_needs_update(current, desired, force):
            payload = {'id': organization['id']}
            payload.update(desired)
            task = module.resource_action('organizations', 'cdn_configuration', payload)

        module.exit_json(task=task, cdn_configuration=_configuration_result(current, desired))


if __name__ == '__main__':
    main()
