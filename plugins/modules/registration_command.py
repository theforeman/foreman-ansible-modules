#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2021 Stejskal Leos, lstejska@redhat.com
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
module: registration_command
version_added: 1.0.0
short_description: Generate registration command
description:
  - Generate registration command
author:
  - "Stejskal Leos (@lstejska)"

'''

EXAMPLES = '''
- name: "Generate registration command"
  theforeman.foreman.registration_command:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
'''

RETURN = '''
entity:
  description: Final state of the affected entities grouped by their type.
  returned: success
  type: dict
  contains:
    registration_commands:
      description: List of registration commands
      type: list
      elements: dict
'''

from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import ForemanEntityAnsibleModule, NestedParametersMixin


class ForemanRegistrationCommandModule(NestedParametersMixin, ForemanEntityAnsibleModule):
    pass


def main():
    module = ForemanRegistrationCommandModule(
        foreman_spec=dict(
            organization=dict(type='entity'),
            location=dict(type='entity'),
            hostgroup=dict(type='entity'),
            operatingsystem=dict(type='entity'),
            smart_proxy=dict(type='entity'),
            insecure=dict(type='bool'),
            setup_remote_execution=dict(type='bool'),
            setup_insights=dict(type='bool'),
            packages=dict(type='str'),
            update_packages=dict(type='bool'),
            repo=dict(type='str'),
            repo_gpg_key_url=dict(type='str'),
            jwt_expiration=dict(type='int', default=4),
            remote_execution_interface=dict(type='str'),
            lifecycle_environment=dict(type='entity', flat_name='lifecycle_environment_id'),
            ignore_subman_errors=dict(type='bool'),
            force=dict(type='bool'),
            activation_keys=dict(type='list', elements='str'),
        ),
    )

    with module.api_connection():
        module.run()


if __name__ == '__main__':
    main()
