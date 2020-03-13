#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2020, Anton Nesterov (@nesanton)
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


ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: foreman_templates_import
short_description: Sync templates from a repository
description:
  - Sync provisioning templates, report_templates, partition tables and job templates from external git repository and/or file system.
  - Based on foreman_templates plugin U(https://github.com/theforeman/foreman_templates).
  - Some defaults can be set in TemplateSync settings using M(foreman_setting) or GUI.
  - Module attempts to be idempotent as much as the plugin allows.
author:
  - "Anton Nesterov (@nesanton)"
options:
  location:
    description: Scope by location
    required: false
    type: str
  organization:
    description: Scope by organization
    required: false
    type: str
  prefix:
    description: Adds specified string to beginning of the template, but only if the template name does not start with the prefix already.
    required: false
    type: str
  associate:
    description: Associate to OSes, Locations and Organizations based on metadata.
    required: false
    type: str
    choices:
     - always
     - new
     - never
  verbose:
    description: Add template diffs to the output.
    required: false
    type: bool
  force:
    description: Update templates that are locked.
    required: false
    type: bool
  lock:
    description: Lock imported templates.
    required: false
    type: bool
  branch:
    description: Branch in Git repo.
    required: false
    type: str
  repo:
    description: Filesystem path or repo (with protocol), for example /tmp/dir or git://example.com/repo.git or https://example.com/repo.git.
    required: false
    type: str
  filter:
    description:
      - Sync only templates with name matching this regular expression, after I(prefix) was applied.
      - Case-insensitive, snippets are not filtered.
    required: false
    type: str
  negate:
    description: Negate the prefix.
    required: false
    type: bool
  dirname:
    description: The directory within Git repo containing the templates.
    required: false
    type: str
  locations:
    description: REPLACE locations with given list.
    required: false
    type: list
    elements: str
  organizations:
    description: REPLACE organizations with given list.
    required: false
    type: list
    elements: str
extends_documentation_fragment:
  - foreman
'''

EXAMPLES = '''
- name: Sync templates from git repo
  foreman_templates_import:
    repo: https://github.com/theforeman/community-templates.git
    branch: 1.24-stable
    associate: new
    server_url: "https://foreman.example.com"
    username: "admin"
    password: "changeme"
'''

RETURN = ''' # '''

from ansible.module_utils.foreman_helper import ForemanAnsibleModule


def main():
    module = ForemanAnsibleModule(
        foreman_spec=dict(
            location=dict(type='entity', flat_name='location_id'),
            organization=dict(type='entity', flat_name='organization_id'),
            associate=dict(choices=['always', 'new', 'never']),
            prefix=dict(),
            branch=dict(),
            repo=dict(),
            filter=dict(),
            dirname=dict(),
            verbose=dict(type='bool'),
            force=dict(type='bool'),
            lock=dict(type='bool'),
            negate=dict(type='bool'),
            locations=dict(type='entity_list', flat_name='location_ids'),
            organizations=dict(type='entity_list', flat_name='organization_ids'),
        ),
        supports_check_mode=False,
    )

    module_params = module.clean_params()
    module.connect()

    if 'template' in module.foremanapi.resources:
        resource_name = 'template'
    elif 'templates' in module.foremanapi.resources:
        resource_name = 'template'
    else:
        raise Exception('The server does not seem to have the foreman_templates plugin installed.')

    # Build a list of all existing templates of all supported types to check if we are adding any new
    all_templates = []

    template_types = ['provisioning_templates', 'report_templates', 'ptables']
    if 'job_templates' in module.foremanapi.resources:
        template_types.append('job_templates')

    for template_type in template_types:
        resources = module.list_resource(template_type)
        for resource in resources:
            all_templates.append([resource['name'], resource['id']])

    result = module.resource_action(resource_name, 'import', record_change=False, params=module_params)
    msg_templates = result['message'].pop('templates', [])

    diff = {'changed': [], 'new': []}
    templates = {}

    for template in msg_templates:
        if template['changed']:
            diff['changed'].append(template['name'])
            module.set_changed()
        elif template['imported']:
            if [template['name'], template['id']] not in all_templates:
                diff['new'].append(template['name'])
                module.set_changed()
        templates[template.pop('name')] = template

    module.exit_json(templates=templates, message=result['message'], diff=diff)


if __name__ == '__main__':
    main()
