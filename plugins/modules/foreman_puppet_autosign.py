#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2020 Ondřej Gajdušek <ogajduse@redhat.com>
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


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: foreman_puppet_autosign
short_description: Manage Foreman (Puppet) autosign entries using Foreman API
description:
  - Create and Delete Foreman Autosign entries using Foreman API
author:
  - "Ondřej Gajdušek (@ogajduse)
options:
  id:
    description: Autosign ID
    required: true
    type: str
  puppet_proxy:
    description: Puppet server proxy name
    required: true
    type: str
  location:
    description:
      - Name of related location
    required: false
    type: str
  organization:
    description:
      - Name of related organization
    required: false
    type: str
extends_documentation_fragment:
  - foreman
  - foreman.entity_state
'''

EXAMPLES = '''
- name: Create new autosign entry
  foreman_puppet_autosign:
    id: "*.lab3.lexcorp.example.com"
    puppet_proxy: foreman.example.com
    location: "Metropolis"
    organization: "LexCorp"
    server_url: "https://foreman.example.com"
    username: "admin"
    password: "secret"
    state: present
'''

RETURN = ''' # '''

from ansible.module_utils.foreman_helper import (
    ForemanEntityAnsibleModule,
)


class ForemanPuppetAutosignModule(ForemanEntityAnsibleModule):
    pass


def main():
    module = ForemanPuppetAutosignModule(
        foreman_spec=dict(
            id=dict(type='str', required=True),
            smart_proxy=dict(type='entity', required=True, aliases=['puppet_proxy']),
            organization=dict(type='entity'),
            location=dict(type='entity'),
        ),
        entity_name='autosign',
        entity_scope=['smart_proxy'],
        entity_opts=dict(
            resource_type='autosign',
        ),
    )

    with module.api_connection():
        module.run()


if __name__ == '__main__':
    main()
