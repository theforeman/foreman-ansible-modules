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
  fail_on_missing:
    description:
      - controls whether the module fails when a modulemd stream is not found
      - when I(false) (default), missing module streams are silently skipped
      - when I(true), missing module streams cause the module to fail with an error
      - only valid in filter I(type=modulemd)
    type: bool
    default: false
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
  - theforeman.foreman.foreman.entity_state
  - theforeman.foreman.foreman.organization
'''

EXAMPLES = '''
# the examples assume that the content view filters have been already created
# e.g. by the theforeman.foreman.content_view_filter module

- name: "Include errata by date"
  theforeman.foreman.content_view_filter_rule:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    organization: "Default Organization"
    content_view: "Standard Operating Environment"
    content_view_filter: "errata_by_date"
    state: present
    date_type: updated
    types:
      - bugfix
      - security
      - enhancement
    end_date: "2022-05-25"

- name: "Exclude csh versions 6.20 and older"
  theforeman.foreman.content_view_filter_rule:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    organization: "Default Organization"
    content_view: "Standard Operating Environment"
    content_view_filter: "package filter 1"
    name: "tcsh"
    max_version: "6.20.00"

- name: "Exclude csh version 6.23 due to example policy"
  theforeman.foreman.content_view_filter_rule:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    organization: "Default Organization"
    content_view: "Standard Operating Environment"
    content_view_filter: "package filter 1"
    name: "tcsh"
    version: "6.23.00"

- name: "Content View Filter Rule for 389 - fully qualified NSVCA"
  theforeman.foreman.content_view_filter_rule:
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

- name: "Exclude all mariadb module streams by name only"
  theforeman.foreman.content_view_filter_rule:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    organization: "Default Organization"
    content_view: "RHEL9 Kickstart"
    content_view_filter: "Exclude CDN Duplicate Streams"
    name: "mariadb"
    state: present

- name: "Exclude mariadb module streams - fail if not found"
  theforeman.foreman.content_view_filter_rule:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    organization: "Default Organization"
    content_view: "RHEL9 Kickstart"
    content_view_filter: "Exclude CDN Duplicate Streams"
    name: "mariadb"
    fail_on_missing: true
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

content_filter_rule_deb_spec = {
    'id': {},
    'rule_name': {'flat_name': 'name'},
    'max_version': {},
    'min_version': {},
    'version': {},
    'architecture': {},
}


class KatelloContentViewFilterRuleModule(KatelloEntityAnsibleModule):
    pass


def main():
    module = KatelloContentViewFilterRuleModule(
        foreman_spec=dict(
            content_view=dict(type='entity', scope=['organization'], required=True),
            content_view_filter=dict(type='entity', scope=['content_view'], required=True),
            name=dict(aliases=['rule_name', 'module_name', 'package_name', 'package_group', 'tag']),
            fail_on_missing=dict(type='bool', default=False),
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
        search_scope = cvf_scope
        content_view_filter_rule = None

        if filter_type != 'erratum' and module.foreman_params['name'] is None:
            module.fail_json(msg="The 'name' parameter is required when creating a filter rule for rpm, container, package_group, modulemd or deb filters.")

        if filter_type == 'erratum':
            # this filter type supports many rules
            # there are really 2 erratum filter types by_date and by_id
            # however the table backing them is denormalized to support both, as is the api
            # for an erratum filter rule == errata_by_date rule, there can be only one rule per filter. So that's easy, its the only one
            if 'errata_id' in module.foreman_params:
                # we need to search by errata_id, because it really doesn't have a name field.
                rule_spec = content_filter_rule_erratum_id_spec
                search_scope['errata_id'] = module.foreman_params['errata_id']
            content_view_filter_rule = module.find_resource('content_view_filter_rules', None, params=search_scope, failsafe=True)

        elif filter_type in ('rpm', 'docker', 'package_group', 'deb'):
            # these filter types support many rules
            # the name is the key to finding the proper one and is required for these types
            search = [(key, module.foreman_params.get(key)) for key in ('name', 'architecture', 'version') if module.foreman_params.get(key)]
            search_string = ','.join('{0}="{1}"'.format(key, val) for (key, val) in search)
            content_view_filter_rule = module.find_resource('content_view_filter_rules', search_string,
                                                            params=search_scope, failsafe=True)

            if filter_type == 'package_group':
                # uuid is also a required value creating, but is implementation specific and not easily knowable to the end user - we find it for them
                package_group = module.find_resource_by_name('package_groups', module.foreman_params['name'], params=cv_scope)
                module.foreman_params['uuid'] = package_group['uuid']

        elif filter_type == 'modulemd':
            # Build NSVCA search - name is required, others are optional
            search_parts = []
            for key in ('name', 'stream', 'version', 'context'):
                val = module.foreman_params.get(key)
                if val:
                    search_parts.append('{0} = "{1}"'.format(key, val))

            if not search_parts or not module.foreman_params.get('name'):
                module.fail_json(msg="At least 'name' must be provided for modulemd filter rules.")

            nsvca_search = ' and '.join(search_parts)

            # Scope to filter repositories if defined, otherwise all CV repos
            repo_clauses = []
            if cvf.get('repositories'):
                for repo in cvf['repositories']:
                    repo_clauses.append('repository ~ "{0}"'.format(repo['name']))
            else:
                cv = module.lookup_entity('content_view')
                if cv.get('repositories'):
                    for repo in cv['repositories']:
                        repo_clauses.append('repository ~ "{0}"'.format(repo['name']))

            if repo_clauses:
                search_string = '({0}) and {1}'.format(' or '.join(repo_clauses), nsvca_search)
            else:
                search_string = nsvca_search

            response = module.resource_action('module_streams', 'index',
                                              params={'search': search_string, 'per_page': 1000})
            results = response.get('results', [])

            if not results:
                if module.desired_absent:
                    return
                if module.foreman_params.get('fail_on_missing', False):
                    module.fail_json(msg="Could not find any module streams matching: {0}. "
                                     "Verify the module stream exists in the content view "
                                     "repositories.".format(search_string))
                else:
                    return

            stream_ids = [ms['id'] for ms in results]

            # check for existing rules matching any of the found streams
            existing_rules = [rule for rule in cvf['rules'] if rule['module_stream_id'] in stream_ids]
            if existing_rules:
                existing_rule = existing_rules[0]
                content_view_filter_rule = module.find_resource_by_id(
                    'content_view_filter_rules', existing_rule['id'],
                    params=search_scope, failsafe=True)
            else:
                existing_rule = None

            if not module.desired_absent and not existing_rule:
                module.foreman_params['module_stream_ids'] = stream_ids

        module.ensure_entity(
            'content_view_filter_rules',
            module.foreman_params,
            content_view_filter_rule,
            params=cvf_scope,
            foreman_spec=rule_spec,
        )


if __name__ == '__main__':
    main()
