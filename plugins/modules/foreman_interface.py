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

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: foreman_interface
short_description: Manage Host Interfaces using Foreman API
description:
  - Create and Delete Host Interfaces using Foreman API
author:
  - "Bernhard Hopfenmüller (@Fobhep) ATIX AG"
options:
  host:
    description:
      - Name of the host of the interface
    required: true
    type: str
  name:
    description: (DNS) Name of the interface
    required: true
    type: str
  mac:
    description: Mac address of the interface
    type: str
  ip:
    description: IP address of the interface
    type: str
  type:
    description: Type of the interface
   choices:
      - 'interface'
      - 'bmc'
      - 'bond'
      - 'bridge'
    default: 'interface'
    type: str
    required: false
  subnet:
    description: Subnet of the interface
    type: str
  domain:
    description: Domain of the interface
    type: str
  identifier:
    description: Device identifier, e.g. eth0 or eth1.1
    type: str
  managed:
    description:
      - Should this interface be managed via DHCP and DNS smart proxy and should it be configured during provisioning?
    type: boolean
  primary:
    description:
      - Should this interface be used for constructing the FQDN of the host?
      - Each managed hosts needs to have one primary interface.
    type: boolean
  provision:
    description:
      - Should this interface be used for TFTP of PXELinux (or SSH for image-based hosts)?
      - Each managed hosts needs to have one provision interface.
    type: boolean
  virtual:
    description:
      - Alias or VLAN device
    type: boolean
  tag:
    description:
      - VLAN tag, this attribute has precedence over the subnet VLAN ID. Only for virtual interfaces.
    type: string

extends_documentation_fragment:
  - foreman
  - foreman.entity_state
'''

EXAMPLES = '''

'''

RETURN = ''' # '''

from ansible.module_utils.foreman_helper import ForemanEntityAnsibleModule

class ForemanInterfaceModule(ForemanEntityAnsibleModule):
    pass


def main():
    module = ForemanInterfaceModule(
        foreman_spec=dict(
            host=dict(type='entity', required=True),
            name=dict(required=True),
            mac=dict(),
            ip=dict(),
            type=dict(choices=['interface', 'bmc', 'bond', 'bridge'], default='interface'),
            subnet=dict(type='entity'),
            domain=dict(type='entity'),
            identifier=dict(),
            managed=dict(type='bool'),
            primary=dict(type='bool'),
            provision=dict(type='bool'),
            virtual=dict(type='bool'),
            tag=dict(),
        ),
        entity_scope=['host'],
    )

    with module.api_connection():
        module.run()


if __name__ == '__main__':
    main()
