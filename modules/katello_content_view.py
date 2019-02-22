#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2016, Eric D Helms <ericdhelms@gmail.com>
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
module: katello_content_view
short_description: Create and Manage Katello content views
description:
    - Create and Manage Katello content views
author: "Eric D Helms (@ehelms)"
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
  name:
    description:
      - Name of the Katello Content View
    required: true
  organization:
    description:
      - Organization that the Content View is in
    required: true
  repositories:
    description:
      - List of repositories that include name and product.
      - Ignored if I(composite=True).
    type: list
  state:
    description:
      - State of the content view
    default: present
    choices:
      - present
      - present_with_defaults
      - absent
  auto_publish:
    description:
      - Auto publish composite view when a new version of a component content view is created.
      - Also note auto publish will only happen when the component is marked "latest".
    default: false
    type: bool
  composite:
    description:
      - A composite view contains other content views.
    default: false
    type: bool
  components:
    description:
      - List of content views to includes content_view and either version or latest.
      - Ignored if I(composite=False).
    type: list
'''

EXAMPLES = '''
- name: "Create or update Fedora content view"
  katello_content_view:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "Fedora CV"
    organization: "My Cool new Organization"
    repositories:
      - name: 'Fedora 26'
        product: 'Fedora'

- name: "Create a composite content view"
  katello_content_view:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "Fedora CCV"
    organization: "My Cool new Organization"
    composite: true
    auto_publish: true
    components:
      - content_view: Fedora CV
        version: 1.0
      - content_view: Internal CV
        latest: true
'''

RETURN = '''# '''

try:
    from nailgun.entities import (
        ContentView,
        ContentViewComponent,
    )

    from ansible.module_utils.ansible_nailgun_cement import (
        find_organization,
        find_content_view,
        find_content_view_version,
        find_repositories,
        naildown_entity_state,
        naildown_entity,
        sanitize_entity_dict,
    )
except ImportError:
    pass

from ansible.module_utils.foreman_helper import KatelloEntityAnsibleModule

name_map = {
    'name': 'name',
    'repositories': 'repository',
    'organization': 'organization',
    'composite': 'composite',
    'auto_publish': 'auto_publish'
}

cvc_map = {
    'composite_content_view': 'composite_content_view',
    'content_view': 'content_view',
    'latest': 'latest',
    'version': 'content_view_version',
}


def main():
    module = KatelloEntityAnsibleModule(
        argument_spec=dict(
            name=dict(required=True),
            composite=dict(type='bool', default=False),
            auto_publish=dict(type='bool', default=False),
            components=dict(type='list'),
            repositories=dict(type='list'),
            state=dict(default='present', choices=['present_with_defaults', 'present', 'absent']),
        ),
        supports_check_mode=True,
        mutually_exclusive=[['repositories', 'components']],
    )

    (entity_dict, state) = module.parse_params()

    module.connect()

    entity_dict['organization'] = find_organization(module, name=entity_dict['organization'])
    if 'repositories' in entity_dict and not entity_dict['composite']:
        entity_dict['repositories'] = find_repositories(module, entity_dict['repositories'], entity_dict['organization'])

    content_view_entity = find_content_view(module, name=entity_dict['name'], organization=entity_dict['organization'], failsafe=True)
    content_view_dict = sanitize_entity_dict(entity_dict, name_map)

    changed, content_view_entity = naildown_entity(ContentView, content_view_dict, content_view_entity, state, module)

    # only update CVC's of newly created or updated CCV's
    if state == 'present' or (state == 'present_with_defaults' and changed):
        current_cvcs = []
        if hasattr(content_view_entity, 'content_view_component'):
            current_cvcs = [cvc.read() for cvc in content_view_entity.content_view_component]
        if 'components' in entity_dict and content_view_entity.composite:
            for component in entity_dict['components']:
                cvc = component.copy()
                cvc['content_view'] = find_content_view(module, name=component['content_view'], organization=entity_dict['organization'])
                cvc_matched = None
                for _cvc in current_cvcs:
                    if _cvc.content_view.id == cvc['content_view'].id:
                        cvc_matched = _cvc
                force_update = list()
                if 'version' in component:
                    cvc['version'] = find_content_view_version(module, cvc['content_view'], version=component['version'])
                    cvc['latest'] = False
                    if cvc_matched and cvc_matched.latest:
                        # When changing to latest=False & version is the latest we must send 'content_view_version' to the server
                        force_update.append('content_view_version')
                if cvc_matched:
                    cvc['composite_content_view'] = content_view_entity
                    cvc_dict = sanitize_entity_dict(cvc, cvc_map)
                    cvc_changed = naildown_entity_state(ContentViewComponent, cvc_dict, cvc_matched, 'present', module, force_update=force_update)
                    current_cvcs.remove(cvc_matched)
                    if cvc_changed:
                        changed = cvc_changed
                else:
                    for attr in ['latest', 'version']:
                        if attr not in cvc:
                            cvc[attr] = None
                    ContentViewComponent(composite_content_view=content_view_entity, content_view=cvc['content_view'],
                                         latest=cvc['latest'], content_view_version=cvc['version']).add()
                    changed = True
        for cvc in current_cvcs:
            # desired cvcs have already been updated and removed from `current_cvcs`
            cvc.remove()
            changed = True

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()
