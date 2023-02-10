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
---
module: content_view_filter_rule
version_added: 3.9.0
short_description: Manage content view filter rules
description:
    - Create, manage and remove content view filter rules
author:
    - "Paul Armstrong (@parmstro)"
options:
  architecture:
    description:
      - set package, module_stream, etc. architecture that the rule applies to
    aliases:
      - arch
    type: str
  content_view:
    description:
      - the name of the content view that the filter applies to
    required: true
    type: str
  content_view_filter:
    description:
      - the name of the content view filter that the rule applies to
    required: true
    type: str
  context:
    description:
      - the context for a module
      - only valid in filter I(type=modulemd)
    type: str
  date_type:
    description:
      - set whether rule applied to erratum using the 'Issued On' or 'Updated On' date
      - only valid on filter I(type=erratum).
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
  name:
    description:
      - Content view filter rule name, package name, package_group name, module stream or docker tag
      - If omitted, the value of I(name) will be used if necessary
      - for module stream filters, this is the name of the module stream to search for
    aliases:
      - rule_name
      - module_name
      - package_name
      - package_group
      - tag
    type: str
  start_date:
    description:
      - the rule limit for erratum start date (YYYY-MM-DD)
      - see date_type for the date the rule applies to
      - Only valid on I(filter_type=erratum).
    type: str
  state:
    description:
      - set the presence or absence of the content view filter rule
    default: present
    choices:
      - present
      - absent
    type: str
  stream:
    description:
      - the context for a module
      - only valid in filter I(type=modulemd)
    type: str
  types:
    description:
      - errata types the ruel applies to (enhancement, bugfix, security)
      - Only valid on I(filter_type=erratum)
    default: ["bugfix", "enhancement", "security"]
    type: list
    elements: str
  version:
    description:
      - package or module version
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

- name: "Content View Filter Rule for 389"
  content_view_filter_rule:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    validate_certs: "true"
    organization: "Default Organization"
    content_view: "Standard Operating Environment"
    content_view_filter: "modulemd filter"
    name: "389-directory-server"
    stream: "next"
    version: "820220325123957"
    context: "9edba152"
    state: present
'''

RETURN = '''
entity:
  description: Final state of the affected entities grouped by their type.
  returned: success
  type: dict
  contains:
    content_view_filters_rules:
      description: List of content view filter rule(s).
      type: list
      elements: dict
'''

from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import KatelloEntityAnsibleModule

content_filter_rule_erratum_spec = {
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
    'rule_name': {'flat_name': 'name'},
    'max_version': {},
    'min_version': {},
    'version': {},
    'architecture': {},
}

content_filter_rule_modulemd_spec = {
    'id': {},
    'module_stream_ids': {'type': 'list'},
}

content_filter_rule_package_group_spec = {
    'id': {},
    'rule_name': {'flat_name': 'name'},
    'uuid': {},
}

content_filter_rule_docker_spec = {
    'id': {},
    'rule_name': {'flat_name': 'name'},
}


class KatelloContentViewFilterRuleModule(KatelloEntityAnsibleModule):
    pass


def main():
    module = KatelloContentViewFilterRuleModule(
        foreman_spec=dict(
            content_view=dict(type='entity', scope=['organization'], required=True),
            content_view_filter=dict(type='entity', scope=['content_view'], required=True),
            name=dict(aliases=['rule_name', 'module_name', 'package_name', 'package_group', 'tag']),
            state=dict(default='present', choices=['present', 'absent']),
            errata_id=dict(),
            types=dict(default=["bugfix", "enhancement", "security"], type='list', elements='str'),
            date_type=dict(default='updated', choices=['issued', 'updated']),
            start_date=dict(),
            end_date=dict(),
            architecture=dict(aliases=['arch']),
            version=dict(),
            max_version=dict(),
            min_version=dict(),
            stream=dict(),
            context=dict(),
        ),
        entity_opts=dict(scope=['content_view_filter']),
    )

    with module.api_connection():

        # A filter always exists before we create a rule
        # Get a reference to the content filter that owns the rule we want to manage
        cv_scope = module.scope_for('content_view')
        cvf_scope = module.scope_for('content_view_filter')
        cvf = module.lookup_entity('content_view_filter')

        # figure out what kind of filter we are working with
        filter_type = cvf['type']
        rule_spec = globals()['content_filter_rule_%s_spec' % (filter_type)]

        # trying to find the existing rule is not simple...
        search = None
        search_scope = cvf_scope
        content_view_filter_rule = None

        # there are really 2 erratum filter types by_date and by_id
        # however the table backing them is denormalized to support both, as is the api

        if 'errata_id' in module.foreman_params:
            # this filter type supports many rules
            # we need to search by errata_id, because it really doesn't have a name field.
            rule_spec = content_filter_rule_erratum_id_spec
            search_scope = {'errata_id': module.foreman_params['errata_id']}
            search_scope.update(cvf_scope)
            search = None
            content_view_filter_rule = module.find_resource('content_view_filter_rules', search, params=search_scope, failsafe=True)

        if filter_type == 'erratum':
            # for an erratum filter rule == errata_by_date rule, there can be only one rule per filter. So that's easy, its the only one
            # if the state is present, we create it or update it, if absent, we delete it
            search = None
            content_view_filter_rule = module.find_resource('content_view_filter_rules', search, params=search_scope, failsafe=True)

        if filter_type in ('rpm', 'docker'):
            # these filter types support many rules
            # the name is the key to finding the proper one and is required for these types
            if module.foreman_params['name'] is not None:
                search = 'name="{0}"'.format(module.foreman_params['name'])
                content_view_filter_rule = module.find_resource('content_view_filter_rules', search, params=search_scope, failsafe=True)
            else:
                # raise an error as name is required for this kind of rule
                search = None

        if filter_type == 'package_group':
            # this filter type support many rules
            # the name is the key to finding the proper one and is required for these types
            # uuid is also a required value creating, but is implementation specific and not easily knowable to the end user - we find it for them
            search = 'name="{0}"'.format(module.foreman_params['name'])
            content_view_filter_rule = module.find_resource('content_view_filter_rules', search, params=search_scope, failsafe=True)

            package_group = module.find_resource_by_name('package_groups', module.foreman_params['name'], params=cv_scope)
            module.foreman_params['uuid'] = package_group['uuid']

        if filter_type == 'modulemd':
            # this filter type support many rules
            # module_stream_ids are internal and non-searchable
            # find the module_stream_id by NSVCA
            content_view_filter_rule = None
            if module.foreman_params['name'] is not None:
                # we have to dig to find the right rule
                # find the module stream's id
                module.foreman_params['module_stream_ids'] = []
                search = ','.join('{0}="{1}"'.format(key, module.foreman_params.get(key, '')) for key in ('name', 'stream', 'version', 'context'))
                module_stream = module.find_resource('module_streams', search, failsafe=True)
                # determine if there is a rule for the module_stream
                existing_rule = [rule for rule in cvf['rules'] if rule['module_stream_id'] == module_stream['id']]
                # if the rule exists, return it in a form ammenable to the API
                if len(existing_rule) > 0:
                    search_scope = cvf_scope
                    search = 'id={0}'.format(existing_rule[0]['id'])
                    content_view_filter_rule = module.find_resource('content_view_filter_rules', search, params=search_scope, failsafe=True)

                # if the state is present and the module_id is NOT in the exising list, add module_stream_id.
                if not module.desired_absent and len(existing_rule) == 0:
                    module.foreman_params['module_stream_ids'].append(module_stream['id'])

                # if the state is present and the module_id IS in the list,
                # make sure that the current and desired state are identical
                elif not module.desired_absent and len(existing_rule) > 0:
                    content_view_filter_rule = module.foreman_params

                # if the state is absent and the module_id IS in the existing list, add the module_stream_id.
                elif module.desired_absent:
                    module.foreman_params['module_stream_ids'].append(module_stream['id'])

        module.ensure_entity(
            'content_view_filter_rules',
            module.foreman_params,
            content_view_filter_rule,
            params=cvf_scope,
            foreman_spec=rule_spec,
        )


if __name__ == '__main__':
    main()
