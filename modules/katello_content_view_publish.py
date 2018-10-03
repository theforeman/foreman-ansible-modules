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

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['deprecated'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: katello_content_view_publish
deprecated:
  removed_in: "2.8"
  why: This has been replaced with another module.
  alternative: Use M(katello_content_view_version) instead.
short_description: Publish a Katello content view
description:
    - Publish a Katello content view
author: "Eric D Helms (@ehelms)"
requirements:
    - "nailgun >= 0.28.0"
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
        default: true
        type: bool
    content_view:
        description:
            - Name of the content view to publish
        required: true
    organization:
        description:
            - Organization that the content view is in
        required: true
'''

EXAMPLES = '''
- name: "Publish a content view"
  katello_content_view_publish:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    content_view: "CV 1"
    organization: "Default Organization"
'''

RETURN = '''# '''

try:
    from nailgun import entities, entity_mixins
    from nailgun.config import ServerConfig
    has_import_error = False
except ImportError as e:
    has_import_error = True
    import_error_msg = str(e)

from ansible.module_utils.basic import AnsibleModule


class NailGun(object):

    def __init__(self, server, entities, module):
        self._server = server
        self._entities = entities
        self._module = module
        entity_mixins.TASK_TIMEOUT = 180000  # Publishes can sometimes take a long, long time

    def find_organization(self, name):
        org = self._entities.Organization(self._server, name=name)
        response = org.search(set(), {'search': 'name="{}"'.format(name)})

        if len(response) == 1:
            return response[0]
        else:
            self._module.fail_json(msg="No organization found for %s" % name)

    def find_content_view(self, name, organization):
        org = self.find_organization(organization)

        content_view = self._entities.ContentView(self._server, name=name, organization=org)
        response = content_view.search()

        if len(response) == 1:
            return response[0]
        else:
            self._module.fail_json(msg="No Content View found for %s" % name)

    def publish(self, content_view, organization):
        content_view = self.find_content_view(content_view, organization)

        return content_view.publish()


def main():
    module = AnsibleModule(
        argument_spec=dict(
            server_url=dict(required=True),
            username=dict(required=True, no_log=True),
            password=dict(required=True, no_log=True),
            verify_ssl=dict(type='bool', default=True),
            content_view=dict(required=True),
            organization=dict(required=True),
        ),
        supports_check_mode=False,
    )

    if has_import_error:
        module.fail_json(msg=import_error_msg)

    server_url = module.params['server_url']
    verify_ssl = module.params['verify_ssl']
    username = module.params['username']
    password = module.params['password']
    content_view = module.params['content_view']
    organization = module.params['organization']

    server = ServerConfig(
        url=server_url,
        auth=(username, password),
        verify=verify_ssl
    )
    ng = NailGun(server, entities, module)

    # Lets make an connection to the server with username and password
    try:
        org = entities.Organization(server)
        org.search()
    except Exception as e:
        module.fail_json(msg="Failed to connect to Foreman server: %s " % e)

    try:
        changed = ng.publish(content_view, organization)
        module.exit_json(changed=changed)
    except Exception as e:
        module.fail_json(msg=e)


if __name__ == '__main__':
    main()
