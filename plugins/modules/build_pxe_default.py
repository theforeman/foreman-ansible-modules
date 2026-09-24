#!/usr/bin/python
# -*- coding: utf-8 -*-
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
module: build_pxe_default
version_added: 5.5.0
short_description: Build PXE default configuration
description:
  - Update the default PXE menu on all configured TFTP servers
author:
  - "Dirk Goetz (@dgoetz)"
options:
  organization:
    description:
      - Name of related organization
    required: false
    type: str
  location:
    description:
      - Name of related location
    required: false
    type: str
extends_documentation_fragment:
  - theforeman.foreman.foreman
...
'''

EXAMPLES = '''
- name: "Build PXE default configuration"
  theforeman.foreman.build_pxe_default:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    organization: "Default Organization"
    location: "Default Location"
'''

RETURN = ''' # '''

from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import ForemanAnsibleModule


def main():
    module = ForemanAnsibleModule(
        foreman_spec=dict(
            organization=dict(type='entity'),
            location=dict(type='entity'),
        ),
    )

    with module.api_connection():
        organization = module.lookup_entity('organization')
        location = module.lookup_entity('location')
        params = {}
        if organization is not None:
            params.update({'organization_id': organization['id']})
        if location is not None:
            params.update({'location_id': location['id']})
        module.resource_action('provisioning_templates', 'build_pxe_default', params=params)


if __name__ == '__main__':
    main()
