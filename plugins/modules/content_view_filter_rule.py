#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2022, Paul Armstrong <parmstro@redhat.com>
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
# content_view_filter_rule.py
---
module: content_view_filter_rule
version_added: 3.4.x
short_description: Manage content view filter rules
description:
    - Create and manage content view filter rules
author: 
    - "Paul Armstrong (parmstro)"
options:
  content_view_filter:
    description:
      - the name of the content view filter that the rule applies to
    required: true
    type: str
  architecture:
    description:
      - set package architecture that the rule applies to
    type: str
  state:
    description:
      - set the presence or absence of the content view filter rule
    default: present
    choices:
      - present
      - absent
    type: str
  name:
    description:
      - Content view filter rule name, package name, package_group name, module stream or docker tag
      - If omitted, the value of I(name) will be used if necessary
    aliases:
      - rule_name
      - module_name
      - package_name
      - package_group
      - tag
    type: str
  date_type:
    description:
      - set whether rule applied to erratum using the 'Issued On' or 'Updated On' date
      - Only valid on I(filter_type=erratum).
    default: updated
    choices:
      - issued
      - updated
    type: str
  end_date:
    description:
      - the rule limit for erratum end date (YYYY-MM-DD)
      - see date_type for the date the rule applies to
      - Only valid on I(filter_type=erratum_by_date).
    type: str
  start_date:
    description:
      - the rule limit for erratum start date (YYYY-MM-DD)
      - see date_type for the date the rule applies to
      - Only valid on I(filter_type=erratum).
    type: str
  errata_id:
    description:
      - erratum id
    type: str
  max_version:
    description:
      - package maximum version
    type: str
  min_version:
    description:
      - package minimum version
    type: str
  errata_types:
    description:
      - errata types the ruel applies to (enhancement, bugfix, security)
      - Only valid on I(filter_type=erratum)
    default: ["bugfix", "enhancement", "security"]
    type: list
    elements: str
  version:
    description:
      - package version
    type: str
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.organization
'''

EXAMPLES = '''

- name: "Include errata by date"
  theforeman.foreman.content_view_filter_rule:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    organization: "Default Organization"
    content_view: "Standard Operating Environment"
    content_view_filter: "errata_by_date"
    state: present
    inclusion: true
    date_type: updated
    types:
      - bugfix
      - security
      - enhancement
    end_date: "2022-05-25"

- name: "Exclude csh versions 6.20 and older"
  theforeman.foreman.content_view_filter:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    organization: "Default Organization"
    content_view: "Standard Operating Environment"
    content_view_filter: "package filter 1"
    name: "tcsh"
    max_version: "6.20.00" 

- name: "Exclude csh version 6.23 due to example policy"
  theforeman.foreman.content_view_filter:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    organization: "Default Organization"
    content_view: "Standard Operating Environment"
    content_view_filter: "package filter 1"
    name: "tcsh"
    version: "6.23.00" 
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


content_filter_rule_erratum_date_spec = {
    'id': {},
    'date_type': {},
    'end_date': {},
    'start_date': {},
    'types': {'type': 'list'},
}

content_filter_rule_erratum_id_spec = {
    'id': {},
    'errata_id': {},
}

content_filter_rule_rpm_spec = {
    'id': {},
    'name': {},
    'end_date': {},
    'max_version': {},
    'min_version': {},
    'version': {},
    'architecture': {},
}

content_filter_rule_module_stream_spec = {
    'id': {},
    'module_stream_ids': {},
}

content_filter_rule_package_group_spec = {
    'id': {},
    'name': {},
}

content_filter_rule_docker_spec = {
    'id': {},
    'name': {},
}

class KatelloContentViewFilterRuleModule(KatelloMixin, ForemanStatelessEntityAnsibleModule):
    pass

def main():
    module = KatelloContentViewFilterRuleModule(
        foreman_spec=dict(
            content_view=dict(type='entity', scope=['organization'], required=True),
            content_view_filter=dict(type='entity', scope=['content_view'], required=True),
            name=dict(aliases=['rule_name','module_name','package_name', 'package_group', 'tag']),
            state=dict(default='present', choices=['present', 'absent']),
            errata_id=dict(),
            types=dict(default=["bugfix", "enhancement", "security"], type='list', elements='str'),
            date_type=dict(default='updated', choices=['issued', 'updated']),
            start_date=dict(),
            end_date=dict(),
            architecture=dict(),
            version=dict(),
            max_version=dict(),
            min_version=dict(),
            stream=dict(),
            context=dict(),
        ),
        entity_opts=dict(scope=['content_view_filter']),
    )

    rule_state = module.foreman_params.pop('state')

    with module.api_connection():

        scope = module.scope_for('organization')
        cv_scope = module.scope_for('content_view')
        cvf_scope = module.scope_for('content_view_filter')

        content_view_filter_rule = module.lookup_entity('entity')
        
        if content_view_filter_rule is not None:    
            if 'errata_id' in module.foreman_params:
                rule_spec = content_filter_rule_erratum_id_spec
                search_scope = {'errata_id': module.foreman_params['errata_id']}
                search_scope.update(cvf_scope)
                search = None
            else:
                rule_spec = globals()['content_filter_rule_%s_spec' % (module.foreman_params['filter_type'])]
                search_scope = cv_scope
                if module.foreman_params['name'] is not None:
                    search = 'name="{0}"'.format(module.foreman_params['name'])
                else:
                    search = None
            # not using find_resource_by_name here, because not all filters (errata) have names
            content_view_filter_rule = module.find_resource('content_view_filter_rules', search, params=search_scope, failsafe=True) if entity else None

            if module.foreman_params['filter_type'] == 'package_group':
                package_group = module.find_resource_by_name('package_groups', module.foreman_params['name'], params=scope)
                module.foreman_params['uuid'] = package_group['uuid']

            if module.foreman_params['filter_type'] == 'module_stream':
                search_scope = cvf_scope
                if module.foreman_params['name'] is not None:
                  search = ','.join('{0}="{1}"'.format(key, module.foreman_params.get(key, '')) for key in ('name', 'stream', 'version', 'context', 'architecture'))
                else:
                  search = None

                rule_spec['module_stream_ids'] = module.find_resource('module_streams', search, params=search_scope, failsafe=True)
            
            # drop 'name' from the dict, as otherwise it might override 'rule_name'
            rule_dict = module.foreman_params.copy()
            # rule_dict.pop('name', None)

            module.ensure_entity(
                'content_view_filter_rules',
                rule_dict,
                content_view_filter_rule,
                params=cvf_scope,
                state=rule_state,
                foreman_spec=rule_spec,
            )


if __name__ == '__main__':
    main()
