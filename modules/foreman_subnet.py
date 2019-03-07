#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2018 Baptiste AGASSE (baptiste.agasse@gmail.com)
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
module: foreman_subnet
short_description: Manage Foreman Subnets using Foreman API
description:
  - Create and Delete Foreman Subnets using Foreman API
author:
  - "Baptiste Agasse (@bagasse)"
requirements:
  - "nailgun >= 0.32.0"
  - "ansible >= 2.3"
options:
  name:
    description: Subnet name
    required: true
  network_type:
    description: Subnet type
    default: IPv4
    choices: ["IPv4", "IPv6"]
  dns_primary:
    description: Primary DNS server for this subnet
    required: false
  dns_secondary:
    description: Secondary DNS server for this subnet
    required: false
  domains:
    description: List of DNS domains the subnet should assigned to
    required: false
    default: None
    type: list
  gateway:
    description: Subnet gateway IP address
    required: false
  network:
    description: Subnet IP address
    required: true
  cidr:
    description: CIDR prefix length; Required if no mask provided
  mask:
    description: Subnet netmask. Required if no cidr prefix length provided
  from_ip:
    description: First IP address of the host IP allocation pool
    required: false
  to_ip:
    description: Last IP address of the host IP allocation pool
    required: false
  boot_mode:
    description: Boot mode used by hosts in this subnet
    required: false
    default: DHCP
    choices: ["DHCP", "Static"]
  ipam:
    description: IPAM mode for this subnet
    required: false
    default: DHCP
    choices: ["DHCP","Internal DB"]
  dhcp_proxy:
    description: DHCP Smart proxy for this subnet
    required: false
  tftp_proxy:
    description: TFTP Smart proxy for this subnet
    required: false
  discovery_proxy:
    description: Discovery Smart proxy for this subnet
    required: false
  dns_proxy:
    description: DNS Smart proxy for this subnet
    required: false
  remote_execution_proxies:
    description: Remote execution Smart proxies for this subnet
    required: false
    default: None
    type: list
  vlanid:
    description: VLAN ID
    required: false
  mtu:
    description: MTU
    required: false
  organizations:
    description: List of oganizations the subnet should be assigned to
    required: false
    default: None
    type: list
  locations:
    description: List of locations the subnet should be assigned to
    required: false
    default: None
    type: list
  server_url:
    description: foreman url
    required: true
  username:
    description: foreman username
    required: true
  password:
    description: foreman user password
    required: true
  verify_ssl:
    description: verify ssl connection when communicating with foreman
    default: true
    type: bool
  state:
    description: subnet presence
    default: present
    choices: ["present", "absent"]
'''

EXAMPLES = '''
- name: My subnet
  foreman_subnet:
    name: "My subnet"
    network: "192.168.0.0"
    mask: "255.255.255.192"
    gateway: "192.168.0.1"
    from_ip: "192.168.0.2"
    to_ip: "192.168.0.42"
    boot_mode: "Static"
    dhcp_proxy: "smart-proxy1.foo.example.com"
    tftp_proxy: "smart-proxy1.foo.example.com"
    dns_proxy: "smart-proxy2.foo.example.com"
    vlanid: 452
    mtu: 9000
    domains:
    - "foo.example.com"
    - "bar.example.com"
    organizations:
    - "Example Org"
    locations:
    - "Toulouse"
    server_url: "https://foreman.example.com"
    username: "admin"
    password: "secret"
    verify_ssl: False
    state: present
'''

RETURN = ''' # '''

try:
    from ansible.module_utils.ansible_nailgun_cement import (
        find_subnet,
        find_domains,
        find_locations,
        find_organizations,
        find_smart_proxy,
        find_smart_proxies,
        naildown_entity_state,
        sanitize_entity_dict,
    )

    from nailgun.entities import (
        Subnet,
    )
except ImportError:
    pass

from netaddr import IPNetwork
from ansible.module_utils.foreman_helper import ForemanEntityAnsibleModule


# This is the only true source for names (and conversions thereof)
name_map = {
    'name': 'name',
    'network_type': 'network_type',
    'dns_primary': 'dns_primary',
    'dns_secondary': 'dns_secondary',
    'domains': 'domain',
    'gateway': 'gateway',
    'network': 'network',
    'cidr': 'cidr',
    'mask': 'mask',
    'from_ip': 'from_',
    'to_ip': 'to',
    'boot_mode': 'boot_mode',
    'ipam': 'ipam',
    'dhcp_proxy': 'dhcp',
    'tftp_proxy': 'tftp',
    'discovery_proxy': 'discovery',
    'dns_proxy': 'dns',
    'remote_execution_proxies': 'remote_execution_proxy',
    'vlanid': 'vlanid',
    'mtu': 'mtu',
    'organizations': 'organization',
    'locations': 'location',
}


def main():
    module = ForemanEntityAnsibleModule(
        argument_spec=dict(
            name=dict(required=True),
            network_type=dict(choices=['IPv4', 'IPv6'], default='IPv4'),
            dns_primary=dict(),
            dns_secondary=dict(),
            domains=dict(type='list'),
            gateway=dict(),
            network=dict(required=True),
            cidr=dict(type='int'),
            mask=dict(),
            from_ip=dict(),
            to_ip=dict(),
            boot_mode=dict(choices=['DHCP', 'Static'], default='DHCP'),
            ipam=dict(choices=['DHCP', 'Internal DB'], default='DHCP'),
            dhcp_proxy=dict(),
            tftp_proxy=dict(),
            discovery_proxy=dict(),
            dns_proxy=dict(),
            remote_execution_proxies=dict(type='list'),
            vlanid=dict(type='int'),
            mtu=dict(type='int'),
            locations=dict(type='list'),
            organizations=dict(type='list'),
        ),
        required_one_of=[['cidr', 'mask']],
        supports_check_mode=True,
    )

    (entity_dict, state) = module.parse_params()

    module.connect()

    try:
        # Try to find the Subnet to work on
        entity = find_subnet(module, name=entity_dict['name'], failsafe=True)
    except Exception as e:
        module.fail_json(msg='Failed to find entity: %s ' % e)

    if 'mask' in entity_dict and 'cidr' not in entity_dict:
        entity_dict['cidr'] = IPNetwork('%s/%s' % (entity_dict['network'], entity_dict['mask'])).prefixlen
    elif 'mask' not in entity_dict and 'cidr' in entity_dict:
        entity_dict['mask'] = IPNetwork('%s/%s' % (entity_dict['network'], entity_dict['cidr'])).netmask

    if 'domains' in entity_dict:
        entity_dict['domains'] = find_domains(module, entity_dict['domains'])

    for feature in ('dhcp_proxy', 'tftp_proxy', 'discovery_proxy', 'dns_proxy', 'remote_execution_proxies'):
        if feature in entity_dict:
            entity_dict[feature] = find_smart_proxy(module, entity_dict[feature])

    if 'organizations' in entity_dict:
        entity_dict['organizations'] = find_organizations(module, entity_dict['organizations'])

    if 'locations' in entity_dict:
        entity_dict['locations'] = find_locations(module, entity_dict['locations'])

    entity_dict = sanitize_entity_dict(entity_dict, name_map)

    changed = naildown_entity_state(Subnet, entity_dict, entity, state, module)

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()

#  vim: set sts=4 ts=8 sw=4 ft=python et noro norl cin si ai :
