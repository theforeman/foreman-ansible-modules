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
module: foreman_template_sync
short_description: Sync templates from or to a repository
description:
  - Sync provisioning templates, partition tables and job templates from external git repository and/or file system.
  - Based on foreman_templates plugin U(https://github.com/theforeman/foreman_templates).
  - Some defaults can be set in TemplateSync settings using M(foreman_setting) or GUI.
  - Module attempts to be idempotent as much as the plugin allows.    # Issues
  - Known issues:
  - I(direction=export) exports all templates if one changes, there also could be 500 responses on C(export).
    # the are three fields in the api response that are of interest: changed (bool), imported(bool), diff
    # changed works as expected - set as true for each changed template, diff shows, well, the diff (if verbose=true)
    # imported, on the other hand seems to misbehave - it returns as true when changed=false and diff=nil.
    # It is impossible to tell if the template was added as new or existed before.
    # The workaround below collects name:id pairs of existing templates to check for new after import.

    ## Export:
    # 1. Metadata changes are not detected
    # 2. When one template changes, all templates in the response have "exported=true"

    # Build a list of ['template_name', 'template_id'] elements for all existing templates of all types handled by plugin
author:
  - "Anton Nesterov (@nesanton)"
options:
  direction:
    description:
      - Direction of the sync.
      - If C(export) is chosen, new commit will be added to the I(branch) if any template has changed.
    required: false
    default: import
    choices:
      - import
      - export
  location:
    description: Scope by location
	  required: false
  organization:
    description: Scope by organization
	  required: false
  prefix:
    description: Adds specified string to beginning of the template on import, but only if the template name does not start with the prefix already.
	  required: false
  associate:
    description: Associate to OSes, Locations and Organizations based on metadata.
	  required: false
	  choices:
	   - always
	   - new
	   - never
  verbose:
    description: Add template diffs to the output.
	  required: false
	  type: bool
  metadata_export_mode:
    description:
      - Only for I(direction=export).
      - C(refresh) generates new metadata based on current associations and attributes,
      - C(remove) strips all metadata from template,
      - C(keep) keeps the same metadata that are part of template code.
      - If omited - metadata changes are ignored.
    choices:
      - refresh
      - remove
      - keep
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
      - On I(direction=import) import only templates with name matching this regular expression, after $prefix was applied.
      - On I(direction=export) export templates with names matching this regex.
      - Case-insensitive, snippets are not filtered.
	  required: false
	  type: str
  negate:
    description: Negate the prefix (for purging).
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
extends_documentation_fragment: foreman
'''

EXAMPLES = '''
- name: Sync templates from git repo
  foreman_template_sync:
    repo: https://github.com/theforeman/community-templates.git
    branch: 1.24-stable
    associate: new
    server_url: "https://foreman.example.com"
    username: "admin"
    password: "changeme"
'''

RETURN = ''' # '''

from ansible.module_utils.foreman_helper import ForemanEntityAnsibleModule, parameter_entity_spec


def main():
    module = ForemanEntityAnsibleModule(
        argument_spec=dict(
            updated_name=dict(),
        ),
        entity_spec=dict(
            direction=dict(choices=['import', 'export'], default='import'),
            location=dict(type='entity', flat_name='location_id'),
            organization=dict(type='entity', flat_name='organization_id'),
            associate=dict(choices=['always', 'new', 'never']),
            metadata_export_mode=dict(choices=['refresh', 'remove', 'keep']),
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
    )

    entity_dict = module.clean_params()
    module.connect()

    if 'template' not in module.foremanapi.resources:
        raise Exception('The server does not seem to have the foreman_templates plugin installed.')

    all_templates = []

    template_types = ['provisioning_templates', 'report_templates', 'ptables']
    if 'job_templates' in module.foremanapi.resources:
        template_types.append('job_templates')
    for template_type in template_types:
        resources = module.list_resource(template_type)
        for resource in resources:
            all_templates.append([resource['name'], resource['id']])

    result = module.resource_action('template', entity_dict['direction'], record_change=False, params=entity_dict)
    changed = False
    msg_templates = result['message'].pop('templates', [])

    if entity_dict['direction'] == 'import':
        diff={'changed': [], 'new': []}
    else:
        if result['message'].get('warning', '') != 'No change detected, skipping the commit and push':
            changed = True
        templates = { template.pop('name'): template for template in msg_templates }
        module.exit_json(changed=changed, message=result['message'], templates=templates, diff=None)

    templates = {}
    for template in msg_templates:
        if template['changed']:
            diff['changed'].append(template['name'])
            changed = True
        elif template['imported']:
            if [template['name'], template['id']] not in all_templates:
                diff['new'].append(template['name'])
                changed = True
        tmpl_name = template.pop('name')
        templates[tmpl_name] = template

    module.exit_json(changed=changed, templates=templates, message=result['message'], diff=diff)

if __name__ == '__main__':
    main()