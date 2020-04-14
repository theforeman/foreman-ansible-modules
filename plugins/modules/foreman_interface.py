#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2020 Bernhard Hopfenmüller (ATIX AG)
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
# along with This program.  If not, see <http://www.gnu.org/licenses/>.

from ansible.module_utils.foreman_helper import ForemanEntityAnsibleModule
from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: foreman_image
short_description: Manage Host Interfaces using Foreman API
description:
  - Create and Delete Host Interfaces using Foreman API
author:
  - "Bernhard Hopfenmüller (@Fobhep) ATIX AG"
options:

extends_documentation_fragment:
  - foreman
  - foreman.entity_state
'''

EXAMPLES = '''
   - name: Get interface for a host
     foreman_interface:
        name: "centos7.deploy1.dev.atix"
'''

RETURN = ''' # '''


class ForemanInterfaceModule(ForemanEntityAnsibleModule):
    pass


def main():
    module = ForemanInterfaceModule(
        foreman_spec=dict(
            username=dict(type='invisible'),
            password=dict(type='invisible', no_log=True),
            host=dict(type='entity', flat_name='host_id', resource_type='hosts', required=True),
            name=dict(type='entity', flat_name='id', resource_type='interfaces'),
        ),
        argument_spec=dict(
            interface=dict(type='dict', options=dict(
                mac=dict(type='string'),
                ip=dict(type='string'),
                type=dict(choices=['interface','bmc','bond','bridge'], default='interface'),
                #name=dict(type='string'),
                subnet=dict(type='entity', flat_name='subnet_id', resource_type='subnets'),
                domain=dict(type='entity', flat_name='domain_id', resource_type='domains'),
                identifier=dict(type='string'),
                managed=dict(type='bool'),
                primary=dict(type='bool'),
                provision=dict(type='bool'),
                virtual=dict(type='bool'),
                tag=dict(type='string'),
            )),
        ),
        entity_scope=['host', 'domain', 'subnet']
    )

    with module.api_connection():
     #   host = module.lookup_entity('hosts').get('id')
        module.run()


if __name__ == '__main__':
    main()
