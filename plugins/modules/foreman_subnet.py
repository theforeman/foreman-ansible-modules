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
  - apypie
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
    description:
      - Discovery Smart proxy for this subnet
      - This option is only available, if the discovery plugin is installed.
    required: false
  dns_proxy:
    description: DNS Smart proxy for this subnet
    required: false
  remote_execution_proxies:
    description:
      - Remote execution Smart proxies for this subnet
      - This option is only available, if the remote_execution plugin is installed.
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
  state:
    description: subnet presence
    default: present
    choices: ["present", "absent"]
extends_documentation_fragment: foreman
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
    state: present
'''

RETURN = ''' # '''


from netaddr import IPNetwork
from ansible.module_utils.foreman_helper import ForemanEntityApypieAnsibleModule


# This is the only true source for names (and conversions thereof)
name_map = {
    'name': 'name',
    'network_type': 'network_type',
    'dns_primary': 'dns_primary',
    'dns_secondary': 'dns_secondary',
    'domains': 'domain_ids',
    'gateway': 'gateway',
    'network': 'network',
    'cidr': 'cidr',
    'mask': 'mask',
    'from_ip': 'from',
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
    'organizations': 'organization_ids',
    'locations': 'location_ids',
}


def main():
    module = ForemanEntityApypieAnsibleModule(
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
    )

    entity_dict = module.clean_params()

    module.connect()

    entity = module.find_resource_by_name('subnets', entity_dict['name'], failsafe=True)

    if not module.desired_absent:
        if 'mask' in entity_dict and 'cidr' not in entity_dict:
            entity_dict['cidr'] = IPNetwork('%s/%s' % (entity_dict['network'], entity_dict['mask'])).prefixlen
        elif 'mask' not in entity_dict and 'cidr' in entity_dict:
            entity_dict['mask'] = IPNetwork('%s/%s' % (entity_dict['network'], entity_dict['cidr'])).netmask

        if 'domains' in entity_dict:
            entity_dict['domains'] = module.find_resources('domains', entity_dict['domains'], thin=True)

        # TODO should remote_execution seach for a list?
        for feature in ('dhcp_proxy', 'tftp_proxy', 'discovery_proxy', 'dns_proxy', 'remote_execution_proxies'):
            if feature in entity_dict:
                entity_dict[feature] = module.find_resource_by_name('smart_proxies', entity_dict[feature], thin=True)

        if 'organizations' in entity_dict:
            entity_dict['organizations'] = module.find_resources_by_name('organizations', entity_dict['organizations'], thin=True)

        if 'locations' in entity_dict:
            entity_dict['locations'] = module.find_resources_by_title('locations', entity_dict['locations'], thin=True)

    changed = module.ensure_resource_state('subnets', entity_dict, entity, name_map=name_map)

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()

#  vim: set sts=4 ts=8 sw=4 ft=python et noro norl cin si ai :
