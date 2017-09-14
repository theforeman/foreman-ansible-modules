#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2017, Andrew Kofink <ajkofink@gmail.com>
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
module: katello_manifest
short_description: Create and Manage Katello manifests
description:
    - Create and Manage Katello manifests
author: "Andrew Kofink (@akofink)"
requirements:
    - "nailgun >= 0.29.0"
    - "python >= 2.6"
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
        default: True
    organization:
        description:
            - Organization that the manifest is in
        required: true
    manifest_path:
        description:
            - Path to the manifest zip file
    state:
        description:
            - The state of the manifest
        required: true
        choices:
            - absent
            - present
            - refreshed
    redhat_repository_url:
        description:
            - URL to retrieve content from
        default: https://cdn.redhat.com
'''
# HERE
EXAMPLES = '''
- name: "Upload the RHEL developer edition manifest"
  katello_manifest:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    verify_ssl: false
    organization: "Default Organization"
    state: present
    manifest_path: "/tmp/manifest.zip"
'''

RETURN = '''# '''

try:
    from nailgun.entities import (
        Subscription
    )

    from nailgun.entity_mixins import (
        TaskFailedError
    )
    HAS_NAILGUN_PACKAGE = True
except:
    HAS_NAILGUN_PACKAGE = False

from ansible.module_utils.ansible_nailgun_cement import (
    create_server,
    ping_server,
    find_organization,
    current_subscription_manifest,
    set_task_timeout,
)


def validate_params(module, state=None, manifest_path=None):
    if manifest_path is not None or len(manifest_path) == 0:
        if state == 'absent':
            module.fail_json(msg="manifest_path is prohibited when state is absent.")
        elif state == 'refreshed':
            module.fail_json(msg="manifest_path is prohibited when state is refreshed.")


def manifest(module, organization, state, manifest_path=None, redhat_repository_url="https://cdn.redhat.com"):
    changed = False
    organization = find_organization(module, organization).read()
    current_manifest = current_subscription_manifest(module, organization)
    manifest_present = current_manifest is not None

    if organization.redhat_repository_url != redhat_repository_url:
        if not module.check_mode():
            organization.redhat_repository_url = redhat_repository_url
            organization.update({'redhat_repository_url'})
        changed = True

    if state == 'present':
        try:
            with open(manifest_path, 'rb') as manifest_file:
                files = {'content': (manifest_path, manifest_file, 'application/zip')}
                data = {'organization_id': organization.id, 'repository_url': redhat_repository_url}
                headers = {'content_type': 'multipart/form-data', 'multipart': 'true'}
                if not module.check_mode():
                    Subscription().upload(data=data, files=files, headers=headers)
                changed = True
        except IOError as e:
            module.fail_json(msg="Unable to open the manifest file: %s" % e)
        except TaskFailedError as e:
            if "same as existing data" in e.message:
                pass
            elif "older than existing data" in e.message:
                module.fail_json(msg="Manifest is older than existing data: %s" % e)
            else:
                module.fail_json(msg="Upload of the mainfest failed: %s" % e)
    elif state == 'absent' and manifest_present:
        if not module.check_mode():
            Subscription().delete_manifest(data={'organization_id': organization.id})
        changed = True
    elif state == 'refreshed':
        if not manifest_present:
            module.fail_json(msg="No manifest found to refresh.")
        else:
            if not module.check_mode():
                Subscription().refresh_manifest(data={'organization_id': organization.id})
            changed = True
    return changed


def main():
    module = AnsibleModule(
        argument_spec=dict(
            server_url=dict(required=True),
            username=dict(required=True, no_log=True),
            password=dict(required=True, no_log=True),
            verify_ssl=dict(type='bool', default=True),
            organization=dict(required=True),
            manifest_path=dict(),
            state=dict(required=True, choices=['absent', 'present', 'refreshed']),
            redhat_repository_url=dict(),
        ),
        required_if=[
            ['state', 'present', ['manifest_path']],
        ],
        supports_check_mode=True,
    )

    if not HAS_NAILGUN_PACKAGE:
        module.fail_json(msg="Missing required nailgun module (check docs or install with: pip install nailgun")

    set_task_timeout(300000)  # 5 minutes

    server_url = module.params['server_url']
    username = module.params['username']
    password = module.params['password']
    verify_ssl = module.params['verify_ssl']
    organization = module.params['organization']
    manifest_path = module.params['manifest_path']
    redhat_repository_url = module.params['redhat_repository_url']
    state = module.params['state']

    validate_params(module, state=state, manifest_path=manifest_path)

    create_server(server_url, (username, password), verify_ssl)
    ping_server(module)

    try:
        changed = manifest(module, organization, state, manifest_path, redhat_repository_url=redhat_repository_url)
        module.exit_json(changed=changed)
    except Exception as e:
        module.fail_json(msg=e)

from ansible.module_utils.basic import AnsibleModule

if __name__ == '__main__':
    main()
