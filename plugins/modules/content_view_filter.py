#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2018, Sean O'Keeffe <seanokeeffe797@gmail.com>
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
module: content_view_filter
version_added: 3.4.x
short_description: Manage content view filters
description:
    - Create and manage content view filters
author: 
    - "Sean O'Keeffe (@sean797)"
    - "Paul Armstrong (parmstro)"
options:
  name:
    description:
      - set the name of the content view filter
    type: str
    required: true
  description:
    description:
      - set the description of the content view filter
    type: str
  content_view:
    description:
      - name of the content view to add the filter to
    required: true
    type: str
  state:
    description:
      - set the presence or absence of the content view filter
    choices:
      - present
      - absent
    type: str
    required: true
  repositories:
    description:
      - list of repositories that the filter applies to including name and product
      - An empty Array means all current and future repositories
    default: []
    type: list
    elements: dict
  filter_type:
    description:
      - the type of content to apply the filter to
    required: true
    choices:
      - rpm
      - modulemd
      - package_group
      - erratum
      - erratum_id
      - erratum_date
      - docker
    type: str
  inclusion:
    description:
      - true creates an include filter
      - false creates an exclude filter
    default: False
    type: bool
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.organization
'''

EXAMPLES = '''
- name: "Include all rpms with no errata - does not need a rule attached"
  theforeman.foreman.content_view_filter:
    username: "admin"MODULE_STREAM
    password: "changeme"
    server_url: "https://foreman.example.com"
    organization: "Default Organization"
    content_view: "Standard Operating Environment"
    name: "all_rpms_no_errata"
    filter_type: "rpm"
    repositories: []
    inclusion: True
    all_no_errata: True

- name: "Include all module streams with no errata - does not need a rule attached"
  theforeman.foreman.content_view_filter:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    organization: "Default Organization"
    content_view: "Standard Operating Environment"
    name: "all_streams_no_errata"
    filter_type: "modulemd"
    repositories: []
    inclusion: True
    all_no_errata: True

- name: "Include errata by date - needs a rule attached"
  theforeman.foreman.content_view_filter:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    organization: "Default Organization"
    content_view: "Standard Operating Environment"
    name: "errata_by_date"
    filter_type: "erratum"
    repositories: []
    inclusion: True
    original_packages: True

- name: "Exclude old versions of csh - needs one or more rules attached"
  theforeman.foreman.content_view_filter:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    organization: "Default Organization"
    content_view: "Standard Operating Environment"
    name: "package filter 1"
    filter_type: "rpm"
'''

RETURN = '''
entity:
  description: Final state of the affected entities grouped by their type.
  returned: success
  type: dict
  contains:
    content_view_filters:
      description: List of content view filters.
      type: list
      elements: dict
'''

from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import KatelloMixin, ForemanStatelessEntityAnsibleModule

content_view_filter_spec = {
    'id': {},
    'name': {},
    'description': {},
    'state': {},
    'repositories': {'type': 'entity_list'},
    'inclusion': {},
    'content_view': {'type': 'entity'},
    'type': {},
    'original_packages': {},
    'original_module_streams': {},
}

class KatelloContentViewFilterModule(KatelloMixin, ForemanStatelessEntityAnsibleModule):
    pass

def main():
    module = KatelloContentViewFilterModule(
        foreman_spec=dict(
            content_view=dict(type='entity', scope=['organization'], required=True),
            name=dict(required=True),
            description=dict(),
            type=dict(required=True, choices=['rpm', 'package_group', 'erratum', 'erratum_id', 'erratum_date', 'docker', 'modulemd']),
            repositories=dict(type='list', default=[], elements='dict'),
            inclusion=dict(type='bool', default=False),
            original_packages=dict(type='bool'),
            original_module_streams=dict(type='bool'),
            state=dict(default='present', choices=['present', 'absent']),
        ),
        entity_opts=dict(scope=['content_view']),
    )

    filter_state = module.foreman_params.pop('state')

    with module.api_connection():
        scope = module.scope_for('organization')

        cv_scope = module.scope_for('content_view')
        if module.foreman_params['repositories']:
            repositories = []
            for repo in module.foreman_params['repositories']:
                product = module.find_resource_by_name('products', repo['product'], params=scope, thin=True)
                product_scope = {'product_id': product['id']}
                repositories.append(module.find_resource_by_name('repositories', repo['name'], params=product_scope, thin=True))
            module.foreman_params['repositories'] = repositories

        entity = module.lookup_entity('entity')
        content_view_filter = module.ensure_entity(
            'content_view_filters',
            module.foreman_params,
            entity,
            params=cv_scope,
            state=filter_state,
            foreman_spec=content_view_filter_spec,
        )


if __name__ == '__main__':
    main()
