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
module: katello_content_view_version_promote
short_description: Promote Katello content view versions to environments
description:
    - Promote Katello content view versions to environments
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
    name:
        description:
            - Name of the Katello content view
        required: true
    organization:
        description:
            - Organization that the content view is in
        required: true
    from_environment:
        description:
            - The lifecycle environment that is already associated with the content view version
    version:
        description:
            - The content view version number to promote (i.e. 1.0)
    to_environments:
        description:
            - The lifecycle environments to add to the content view version
        required: true
'''

EXAMPLES = '''
- name: "Promote the 1.0 content view version to Library"
katello_content_view_version_promote:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "Fedora CV"
    organization: "Default Organization"
    version: "1.0"
    to_environment: "Library"
- name: "Promote the client content view from Library to Development"
  katello_content_view_version_promote:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "Fedora CV"
    organization: "Default Organization"
    from_environment: "Library"
    to_environment: "Development"
'''

RETURN = '''# '''

try:
    from ansible.module_utils.ansible_nailgun_cement import (
        create_server,
        handle_no_nailgun,
        find_organization,
        find_lifecycle_environment,
        find_content_view,
        find_content_view_version,
        ping_server,
    )
    HAS_NAILGUN_PACKAGE = True
except:
    HAS_NAILGUN_PACKAGE = False


def content_view_promote(module, name, organization, to_environment, from_environment=None, version=None):
    changed = False

    organization = find_organization(module, organization)
    content_view = find_content_view(module, name=name, organization=organization)
    if from_environment is not None:
        from_environment = find_lifecycle_environment(module, name=from_environment, organization=organization)
    to_environment = find_lifecycle_environment(module, name=to_environment, organization=organization)
    content_view_version = find_content_view_version(module, content_view, environment=from_environment, version=version)

    if to_environment.id not in map(lambda environment: environment.id, content_view_version.environment):
        content_view_version.promote(data={'environment_ids': [to_environment.id]})
        changed = True

    return changed


def main():
    module = AnsibleModule(
        argument_spec=dict(
            server_url=dict(required=True),
            username=dict(required=True, no_log=True),
            password=dict(required=True, no_log=True),
            verify_ssl=dict(type='bool', default=False),
            name=dict(required=True),
            organization=dict(required=True),
            from_environment=dict(),
            version=dict(),
            to_environment=dict(required=True),
        ),
        required_one_of=[['from_environment', 'version']],
        mutually_exclusive=[['from_environment', 'version']]
    )

    handle_no_nailgun(module, HAS_NAILGUN_PACKAGE)

    server_url = module.params['server_url']
    username = module.params['username']
    password = module.params['password']
    verify_ssl = module.params['verify_ssl']
    name = module.params['name']
    organization = module.params['organization']
    from_environment = module.params['from_environment']
    version = module.params['version']
    to_environment = module.params['to_environment']

    create_server(server_url, (username, password), verify_ssl)
    ping_server(module)

    try:
        changed = content_view_promote(module, name, organization, to_environment, from_environment=from_environment, version=version)
        module.exit_json(changed=changed)
    except Exception as e:
        module.fail_json(msg=e)


from ansible.module_utils.basic import AnsibleModule

if __name__ == '__main__':
    main()
