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
module: katello_content_view_version
short_description: Create, remove or interact with a Katello Content View Version
description:
    - Publish, Promote or Remove a Katello Content View Version
author: Sean O'Keeffe (@sean797)
requirements:
    - "nailgun"
    - "python >= 2.6"
notes:
    - You cannot use this to remove a Contnet View Version from a Lifecycle environment, you should promote another version first.
    - For idempotency you must specify either C(version) or C(current_lifecycle_environment).
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
            - Organization that the content view is in
        required: true
    state:
       description:
            - Content View Version state
       default: present
       choices:
           - absent
           - present
    version:
        description:
           - The content view version number (i.e. 1.0)
    lifecycle_environments:
        description:
            - The lifecycle environments the Content View Version should be in.
        default: Library
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
    synchronous:
        description:
            - Wait for the Publish or Promote task to complete if True. Immediately return if False.
        default: true
    current_lifecycle_environment:
        description:
            - The lifecycle environment that is already associated with the content view version
            - Helpful for promoting a content view version
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

RETURN = '''# '''

try:
    from nailgun.entities import (
        ContentViewVersion,
    )

    from ansible.module_utils.ansible_nailgun_cement import (
        create_server,
        find_organization,
        find_lifecycle_environments,
        find_lifecycle_environment,
        find_content_view,
        find_content_view_version,
        ping_server,
        set_task_timeout,
        naildown_entity_state,
    )
    has_import_error = False
except ImportError as e:
    has_import_error = True
    import_error_msg = str(e)
from ansible.module_utils.basic import AnsibleModule


def promote_content_view_version(module, content_view_version, organization, environments, synchronous, **kwargs):
    changed = False

    current_environment_ids = map(lambda environment: environment.id, content_view_version.environment)
    desired_environment_ids = map(lambda environment: environment.id, environments)
    promote_to_environment_ids = list(set(desired_environment_ids) - set(current_environment_ids))

    request_data = {'environment_ids': promote_to_environment_ids}
    request_data.update({k: v for k, v in kwargs.items() if v is not None})

    if promote_to_environment_ids:
        if not module.check_mode:
            content_view_version.promote(synchronous, data=request_data)
        changed = True
    return changed


def main():
    module = AnsibleModule(
        argument_spec=dict(
            server_url=dict(required=True),
            username=dict(required=True, no_log=True),
            password=dict(required=True, no_log=True),
            verify_ssl=dict(type='bool', default=True),
            content_view=dict(required=True),
            organization=dict(required=True),
            state=dict(default='present', choices=['present', 'absent']),
            version=dict(),
            lifecycle_environments=dict(type='list', default=['Library']),
            force=dict(type='bool', aliases=['force_promote'], default=False),
            force_yum_metadata_regeneration=dict(type='bool', default=False),
            synchronous=dict(type='bool', default=True),
            current_lifecycle_environment=dict(),
        ),
        mutually_exclusive=[['current_lifecycle_environment', 'version']],
        supports_check_mode=True,
    )

    if has_import_error:
        module.fail_json(msg=import_error_msg)

    set_task_timeout(3600000)  # 60 minutes

    params_dict = dict(
        [(k, v) for (k, v) in module.params.items() if v is not None])

    server_url = module.params['server_url']
    username = module.params['username']
    password = module.params['password']
    verify_ssl = module.params['verify_ssl']
    state = module.params['state']

    try:
        create_server(server_url, (username, password), verify_ssl)
    except Exception as e:
        module.fail_json(msg="Failed to connect to Foreman server: %s " % e)

    ping_server(module)

    organization = find_organization(module, params_dict['organization'])
    content_view = find_content_view(module, name=params_dict['content_view'], organization=organization)

    if 'current_lifecycle_environment' in params_dict:
        params_dict['current_lifecycle_environment'] = find_lifecycle_environment(module, name=params_dict['current_lifecycle_environment'],
                                                                                  organization=organization)
        content_view_version = find_content_view_version(module, content_view, environment=params_dict['current_lifecycle_environment'])
    elif 'version' in params_dict:
        content_view_version = find_content_view_version(module, content_view, version=params_dict['version'], failsafe=True)
    else:
        content_view_version = None

    changed = False
    if state == 'present':
        if content_view_version is None:
            kwargs = dict(data=dict())
            if 'description' in params_dict:
                kwargs['data'].update(description=params_dict['description'])
            if 'force_metadata_regeneration' in params_dict:
                kwargs['data'].update(force_yum_metadata_regeneration=params_dict['force_metadata_regeneration'])
            if 'version' in params_dict:
                kwargs['data'].update(major=list(map(int, str(params_dict['version']).split('.')))[0])
                kwargs['data'].update(minor=list(map(int, str(params_dict['version']).split('.')))[1])

            response = content_view.publish(params_dict['synchronous'], **kwargs)
            changed = True
            content_view_version = ContentViewVersion(id=response['output']['content_view_version_id']).read()

        if 'lifecycle_environments' in params_dict:
            lifecycle_environments = find_lifecycle_environments(module, names=params_dict['lifecycle_environments'], organization=organization)
            le_changed = promote_content_view_version(module, content_view_version, organization, lifecycle_environments, params_dict['synchronous'],
                                                      force=params_dict['force'],
                                                      force_yum_metadata_regeneration=params_dict['force_yum_metadata_regeneration'])
    elif state == 'absent':
        changed = naildown_entity_state(ContentViewVersion, dict(), content_view_version, state, module)

    module.exit_json(changed=changed or le_changed)


if __name__ == '__main__':
    main()
