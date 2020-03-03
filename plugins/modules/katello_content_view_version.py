#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2018, Sean O'Keeffe <seanokeeffe797@gmail.com>
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
module: katello_content_view_version
short_description: Create, remove or interact with a Katello Content View Version
description:
  - Publish, Promote or Remove a Katello Content View Version
author: Sean O'Keeffe (@sean797)
notes:
  - You cannot use this to remove a Content View Version from a Lifecycle environment, you should promote another version first.
  - For idempotency you must specify either C(version) or C(current_lifecycle_environment).
options:
  content_view:
    description:
      - Name of the content view
    required: true
    type: str
  description:
    description:
      - Description of the Content View Version
    type: str
  version:
    description:
      - The content view version number (i.e. 1.0)
    type: str
  lifecycle_environments:
    description:
      - The lifecycle environments the Content View Version should be in.
    type: list
    elements: str
  force_promote:
    description:
      - Force content view promotion and bypass lifecycle environment restriction
    default: false
    type: bool
    aliases:
      - force
  force_yum_metadata_regeneration:
    description:
      - Force metadata regeneration when performing Publish and Promote tasks
    type: bool
    default: false
  current_lifecycle_environment:
    description:
      - The lifecycle environment that is already associated with the content view version
      - Helpful for promoting a content view version
    type: str
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.entity_state
  - theforeman.foreman.foreman.organization
'''

EXAMPLES = '''
- name: "Ensure content view version 2.0 is in Test & Pre Prod"
  katello_content_view_version:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    content_view: "CV 1"
    organization: "Default Organization"
    version: 2.0
    lifecycle_environments:
      - Test
      - Pre Prod

- name: "Ensure content view version in Test is also in Pre Prod"
  katello_content_view_version:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    content_view: "CV 1"
    organization: "Default Organization"
    current_lifecycle_environment: Test
    lifecycle_environments:
      - Pre Prod

- name: "Publish a content view, not idempotent"
  katello_content_view_version:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    content_view: "CV 1"
    organization: "Default Organization"

- name: "Publish a content view and promote that version to Library & Dev, not idempotent"
  katello_content_view_version:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    content_view: "CV 1"
    organization: "Default Organization"
    lifecycle_environments:
      - Library
      - Dev

- name: "Ensure content view version 1.0 doesn't exist"
  katello_content_view_version:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    content_view: "Web Servers"
    organization: "Default Organization"
    version: 1.0
    state: absent
'''

RETURN = ''' # '''


from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import KatelloEntityAnsibleModule


def promote_content_view_version(module, content_view_version, environments, force, force_yum_metadata_regeneration):
    current_environment_ids = {environment['id'] for environment in content_view_version['environments']}
    desired_environment_ids = {environment['id'] for environment in environments}
    promote_to_environment_ids = list(desired_environment_ids - current_environment_ids)

    if promote_to_environment_ids:
        payload = {
            'id': content_view_version['id'],
            'environment_ids': promote_to_environment_ids,
            'force': force,
            'force_yum_metadata_regeneration': force_yum_metadata_regeneration,
        }

        module.record_before('content_view_versions', {'id': content_view_version['id'], 'environments': content_view_version['environments']})
        module.resource_action('content_view_versions', 'promote', params=payload)
        module.record_after('content_view_versions', {'id': content_view_version['id'], 'environments': environments})
        module.record_after_full('content_view_versions', {'id': content_view_version['id'], 'environments': environments})


def main():
    module = KatelloEntityAnsibleModule(
        entity_spec=dict(
            content_view=dict(type='entity', required=True),
            description=dict(),
            version=dict(),
            lifecycle_environments=dict(type='list', elements='str'),
            force_promote=dict(type='bool', aliases=['force'], default=False),
            force_yum_metadata_regeneration=dict(type='bool', default=False),
            current_lifecycle_environment=dict(),
        ),
        mutually_exclusive=[['current_lifecycle_environment', 'version']],
    )

    module.task_timeout = 60 * 60

    entity_dict = module.clean_params()

    with module.api_connection():
        entity_dict, scope = module.handle_organization_param(entity_dict)

        content_view = module.find_resource_by_name('content_views', name=entity_dict['content_view'], params=scope)

        if 'current_lifecycle_environment' in entity_dict:
            entity_dict['current_lifecycle_environment'] = module.find_resource_by_name(
                'lifecycle_environments', name=entity_dict['current_lifecycle_environment'], params=scope)
            search_scope = {'content_view_id': content_view['id'], 'environment_id': entity_dict['current_lifecycle_environment']['id']}
            content_view_version = module.find_resource('content_view_versions', search=None, params=search_scope)
        elif 'version' in entity_dict:
            search = "content_view_id={0},version={1}".format(content_view['id'], entity_dict['version'])
            content_view_version = module.find_resource('content_view_versions', search=search, failsafe=True)
        else:
            content_view_version = None

        if module.desired_absent:
            module.ensure_entity('content_view_versions', None, content_view_version, params=scope)
        else:
            if content_view_version is None:
                payload = {
                    'id': content_view['id'],
                }
                if 'description' in entity_dict:
                    payload['description'] = entity_dict['description']
                if 'force_yum_metadata_regeneration' in entity_dict:
                    payload['force_yum_metadata_regeneration'] = entity_dict['force_yum_metadata_regeneration']
                if 'version' in entity_dict:
                    split_version = list(map(int, str(entity_dict['version']).split('.')))
                    payload['major'] = split_version[0]
                    payload['minor'] = split_version[1]

                response = module.resource_action('content_views', 'publish', params=payload)
                # workaround for https://projects.theforeman.org/issues/28138
                if not module.check_mode:
                    content_view_version_id = response['output'].get('content_view_version_id') or response['input'].get('content_view_version_id')
                    content_view_version = module.show_resource('content_view_versions', content_view_version_id)
                else:
                    content_view_version = {'id': -1, 'environments': []}

            if 'lifecycle_environments' in entity_dict:
                lifecycle_environments = module.find_resources_by_name('lifecycle_environments', names=entity_dict['lifecycle_environments'], params=scope)
                promote_content_view_version(
                    module,
                    content_view_version,
                    lifecycle_environments,
                    force=entity_dict['force_promote'],
                    force_yum_metadata_regeneration=entity_dict['force_yum_metadata_regeneration'],
                )


if __name__ == '__main__':
    main()
