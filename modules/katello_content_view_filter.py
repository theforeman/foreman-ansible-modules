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

DOCUMENTATION = '''
---
module: katello_content_view_filter
short_description: Create and Manage Katello content View filters
description:
    - Create and Manage Katello content View filters
author: "Sean O'Keeffe (@sean797)"
requirements:
    - "nailgun >= 0.28.0"
    - "python >= 2.6"
    - "ansible >= 2.3"
options:
  server_url:
    description:
      - URL of Foreman server
    required: true
  username:
    description:
     - Username on Foreman server
    required: true
  password:
    description:
      - Password for user accessing Foreman server
    required: true
  verify_ssl:
    description:
      - Verify SSL of the Foreman server
    default: true
    type: bool
  content_view:
    description:
      - Name of the content view
    required: true
  organization:
    description:
      - Organization that the Content View is in
    required: true
  filter_state:
    description:
      - State of the content view filter
    default: present
    choices:
      - present
      - absent
  repositories:
    description:
      - List of repositories that include name and product
      - An empty Array means all current and future repositories
    default: []
    type: list
  rule_state:
    description:
      - State of the content view filter rule
    default: present
    choices:
      - present
      - absent
  filter_type:
    description:
      - Content view filter type
    required: true
    choices:
      - rpm
      - package_group
      - erratum
      - docker
  rule_name:
    description:
      - Content view filter rule name or package name
    alias:
      - package_name
      - package_group
      - tag
    default: I(name)
  date_type:
    description:
      - Search using the 'Issued On' or 'Updated On'
      - Only valid on I(filter_type=erratum).
    default: updated
    choices:
      - issued
      - updated
  end_date:
    description:
      - erratum end date (YYYY-MM-DD)
  start_date:
    description:
      - erratum start date (YYYY-MM-DD)
  errata_id:
    description:
      - erratum id
  max_version:
     description:
       - package maximum version
  min_version:
    description:
       - package minimum version
  types:
     description:
        - erratum types (enhancement, bugfix, security)
     default: ["bugfix", "enhancement", "security"]
  version:
     description:
        - package version
  inclusion:
    description:
      - Create an include filter
    default: False
'''

EXAMPLES = '''
- name: Exclude csh
  katello_content_view_filter:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "package filter 1"
    organization: "Default Organization"
    content_view: Web Servers
    filter_type: "rpm"
    package_name: tcsh

- name: Include newer csh versions
  katello_content_view_filter:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "package filter 1"
    organization: "Default Organization"
    content_view: Web Servers
    filter_type: "rpm"
    package_name: tcsh
    min_version: 6.20.00
    inclusion: True
'''

RETURN = '''# '''

try:
    from nailgun.entities import (
        AbstractContentViewFilter,
        ContentViewFilterRule,
    )

    from ansible.module_utils.ansible_nailgun_cement import (
        find_organization,
        find_content_view,
        find_content_view_filter,
        find_repositories,
        find_content_view_filter_rule,
        find_errata,
        find_package_group,
        naildown_entity_state,
        sanitize_entity_dict,
    )
except ImportError:
    pass

from ansible.module_utils.foreman_helper import ForemanAnsibleModule

content_filter_map = {
    'name': 'name',
    'description': 'description',
    'repositories': 'repository',
    'inclusion': 'inclusion',
    'content_view': 'content_view',
    'filter_type': 'type',
}

content_filter_rule_erratum_map = {
    'content_view_filter': 'content_view_filter',
    'date_type': 'date_type',
    'end_date': 'end_date',
    'start_date': 'start_date',
    'types': 'types',
}

content_filter_rule_erratum_id_map = {
    'content_view_filter': 'content_view_filter',
    'errata': 'errata',
    'date_type': 'date_type',
}

content_filter_rule_rpm_map = {
    'rule_name': 'name',
    'content_view_filter': 'content_view_filter',
    'end_date': 'end_date',
    'max_version': 'max_version',
    'min_version': 'min_version',
    'version': 'version',
    'architecture': 'architecture',
}

content_filter_rule_package_group_map = {
    'rule_name': 'name',
    'content_view_filter': 'content_view_filter',
    'uuid': 'uuid',

}

content_filter_rule_docker_map = {
    'rule_name': 'name',
    'content_view_filter': 'content_view_filter',

}


def main():
    module = ForemanAnsibleModule(
        argument_spec=dict(
            name=dict(required=True),
            description=dict(),
            repositories=dict(type='list', default=[]),
            inclusion=dict(type='bool', default=False),
            content_view=dict(required=True),
            filter_type=dict(required=True, choices=['rpm', 'package_group', 'erratum', 'docker']),
            organization=dict(required=True),
            filter_state=dict(default='present', choices=['present', 'absent']),
            rule_state=dict(default='present', choices=['present', 'absent']),
            rule_name=dict(aliases=['package_name', 'package_group', 'tag']),
            date_type=dict(default='updated', choices=['issued', 'updated']),
            end_date=dict(),
            errata_id=dict(),
            max_version=dict(),
            min_version=dict(),
            start_date=dict(),
            types=dict(default=["bugfix", "enhancement", "security"], type='list'),
            version=dict(),
        ),
        supports_check_mode=False,
    )

    entity_dict = module.parse_params()
    filter_state = entity_dict.pop('filter_state')
    rule_state = entity_dict.pop('rule_state')

    module.connect()

    organization = find_organization(module, name=entity_dict.pop('organization'))
    entity_dict['content_view'] = find_content_view(module, name=entity_dict['content_view'], organization=organization)
    if len(entity_dict['repositories']) > 0:
        entity_dict['repositories'] = find_repositories(module, entity_dict['repositories'], organization)

    content_view_filter_entity = find_content_view_filter(module, name=entity_dict['name'], content_view=entity_dict['content_view'], failsafe=True)
    content_view_filter_dict = sanitize_entity_dict(entity_dict, content_filter_map)

    content_view_filter_changed = naildown_entity_state(AbstractContentViewFilter, content_view_filter_dict, content_view_filter_entity, filter_state, module)

    if entity_dict['filter_type'] == 'erratum':
        entity_dict['rule_name'] = None
    elif 'rule_name' not in entity_dict:
        entity_dict['rule_name'] = entity_dict['name']

    # Find content_view_filter again as it may have just been created
    entity_dict['content_view_filter'] = find_content_view_filter(module, name=entity_dict['name'], content_view=entity_dict['content_view'], failsafe=True)

    if entity_dict['content_view_filter'] is not None:
        if 'errata_id' in entity_dict:
            rule_map = content_filter_rule_erratum_id_map
            entity_dict['errata'] = find_errata(module, id=entity_dict['errata_id'], organization=organization)
            content_view_filter_rule_entity = find_content_view_filter_rule(module, content_view_filter=entity_dict['content_view_filter'],
                                                                            errata=entity_dict['errata'], failsafe=True)
        else:
            rule_map = globals()['content_filter_rule_%s_map' % (entity_dict['filter_type'])]
            content_view_filter_rule_entity = find_content_view_filter_rule(module, content_view_filter=entity_dict['content_view_filter'],
                                                                            name=entity_dict['rule_name'], failsafe=True)

        if entity_dict['filter_type'] == 'package_group':
            entity_dict['uuid'] = find_package_group(module, name=entity_dict['rule_name']).uuid

        content_view_filter_rule_dict = sanitize_entity_dict(entity_dict, rule_map)
        check_missing = ['min_version', 'max_version', 'version', 'start_date', 'end_date', 'architecture', 'date_type']
        content_view_filter_rule_changed = naildown_entity_state(ContentViewFilterRule, content_view_filter_rule_dict, content_view_filter_rule_entity,
                                                                 rule_state, module, check_missing)
        changed = content_view_filter_changed or content_view_filter_rule_changed
    else:
        changed = content_view_filter_changed

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()
