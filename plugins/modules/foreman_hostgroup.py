#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2019 Manisha Singhal (ATIX AG)
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
module: foreman_hostgroup
short_description: Manage Foreman Hostgroups using Foreman API
description:
  - Create, Update and Delete Foreman Hostgroups using Foreman API
author:
  - "Manisha Singhal (@Manisha15) ATIX AG"
  - "Baptiste Agasse (@bagasse)"
requirements:
  - "apypie >= 0.0.1"
options:
  name:
    description: Name of hostgroup
    required: true
  description:
    description: Description of hostgroup
    required: false
  parent:
    description: Hostgroup parent name
    required: false
    default: None
  organizations:
    description: List of organizations names
    required: false
    default: None
    type: list
  locations:
    description: List of locations names
    required: false
    default: None
    type: list
  compute_resource:
    description: Compute resource name
    required: false
    default: None
  compute_profile:
    description: Compute profile name
    required: false
    default: None
  domain:
    description: Domain name
    required: false
    default: None
  subnet:
    description: IPv4 Subnet name
    required: false
    default: None
  subnet6:
    description: IPv6 Subnet name
    required: false
    default: None
  realm:
    description: Realm name
    required: false
    default: None
  architecture:
    description: Architecture name
    required: False
    default: None
  medium:
    description: Medium name
    required: False
    default: None
  operatingsystem:
    description: Operatingsystem title
    required: False
    default: None
  pxe_loader:
    description: PXE Bootloader
    required: false
    default: None
    choices:
      - PXELinux BIOS
      - PXELinux UEFI
      - Grub UEFI
      - Grub2 BIOS
      - Grub2 ELF
      - Grub2 UEFI
      - Grub2 UEFI SecureBoot
      - Grub2 UEFI HTTP
      - Grub2 UEFI HTTPS
      - Grub2 UEFI HTTPS SecureBoot
      - iPXE Embedded
      - iPXE UEFI HTTP
      - iPXE Chain BIOS
      - iPXE Chain UEFI
  partition_table:
    description: Partition table name
    required: False
    default: None
  root_pass:
    description: root password
    required: false
    default: None
  environment:
    description: Puppet environment name
    required: false
    default: None
  config_groups:
    description: Config groups list
    required: false
    default: None
    type: list
  puppet_proxy:
    description: Puppet server proxy name
    required: false
    default: None
  puppet_ca_proxy:
    description: Puppet CA proxy name
    required: false
    default: None
  state:
    description: Hostgroup presence
    default: present
    choices: ["present", "absent"]
extends_documentation_fragment: foreman
'''

EXAMPLES = '''
- name: "Create a Hostgroup"
  foreman_hostgroup:
    name: "new_hostgroup"
    architecture: "architecture_name"
    operatingsystem: "operatingsystem_name"
    medium: "media_name"
    ptable: "Partition_table_name"
    server_url: "https://foreman.example.com"
    username: "admin"
    password: "secret"
    state: present

- name: "Update a Hostgroup"
  foreman_hostgroup:
    name: "new_hostgroup"
    architecture: "updated_architecture_name"
    operatingsystem: "updated_operatingsystem_name"
    medium: "updated_media_name"
    ptable: "updated_Partition_table_name"
    root_pass: "password"
    server_url: "https://foreman.example.com"
    username: "admin"
    password: "secret"
    state: present

- name: "Delete a Hostgroup"
  foreman_hostgroup:
    name: "new_hostgroup"
    server_url: "https://foreman.example.com"
    username: "admin"
    password: "secret"
    state: absent
'''

RETURN = ''' # '''

from ansible.module_utils.foreman_helper import (
    build_fqn,
    ForemanEntityApypieAnsibleModule,
    split_fqn,
)


# This is the only true source for names (and conversions thereof)
name_map = {
    'name': 'name',
    'description': 'description',
    'parent': 'parent_id',
    'locations': 'location_ids',
    'organizations': 'organization_ids',
    'compute_resource': 'compute_resource_id',
    'compute_profile': 'compute_profile_id',
    'domain': 'domain_id',
    'subnet': 'subnet_id',
    'subnet6': 'subnet6_id',
    'realm': 'realm_id',
    'architecture': 'architecture_id',
    'operatingsystem': 'operatingsystem_id',
    'media': 'medium_id',
    'ptable': 'ptable_id',
    'pxe_loader': 'pxe_loader',
    'environment': 'environment_id',
    'config_groups': 'config_group_ids',
    'puppet_proxy': 'puppet_proxy_id',
    'puppet_ca_proxy': 'puppet_ca_proxy_id',
    'root_pass': 'root_pass',
}


def main():
    module = ForemanEntityApypieAnsibleModule(
        argument_spec=dict(
            name=dict(required=True),
            description=dict(),
            parent=dict(),
            organizations=dict(type='list'),
            locations=dict(type='list'),
            compute_resource=dict(),
            compute_profile=dict(),
            domain=dict(),
            subnet=dict(),
            subnet6=dict(),
            realm=dict(),
            architecture=dict(),
            operatingsystem=dict(),
            media=dict(),
            ptable=dict(),
            pxe_loader=dict(choices=['PXELinux BIOS', 'PXELinux UEFI', 'Grub UEFI', 'Grub2 BIOS', 'Grub2 ELF',
                                     'Grub2 UEFI', 'Grub2 UEFI SecureBoot', 'Grub2 UEFI HTTP', 'Grub2 UEFI HTTPS',
                                     'Grub2 UEFI HTTPS SecureBoot', 'iPXE Embedded', 'iPXE UEFI HTTP', 'iPXE Chain BIOS', 'iPXE Chain UEFI']),
            root_pass=dict(no_log=True),
            environment=dict(),
            config_groups=dict(type='list'),
            puppet_proxy=dict(),
            puppet_ca_proxy=dict(),
        ),
    )
    entity_dict = module.clean_params()

    module.connect()

    # Get short name and parent from provided name
    name, parent = split_fqn(entity_dict['name'])
    entity_dict['name'] = name

    if 'parent' in entity_dict:
        if parent:
            module.fail_json(msg="Please specify the parent either separately, or as part of the title.")
        parent = entity_dict['parent']
    if parent:
        search_string = 'title="{}"'.format(parent)
        entity_dict['parent'] = module.find_resource('hostgroups', search=search_string, thin=True, failsafe=module.desired_absent)

        if module.desired_absent and entity_dict['parent'] is None:
            # Parent hostgroup does not exist so just exit here
            module.exit_json(changed=False)

    if not module.desired_absent:
        if 'organizations' in entity_dict:
            entity_dict['organizations'] = module.find_resources_by_name('organizations', entity_dict['organizations'], thin=True)

        if 'locations' in entity_dict:
            entity_dict['locations'] = module.find_resources_by_title('locations', entity_dict['locations'], thin=True)

        if 'compute_resource' in entity_dict:
            entity_dict['compute_resource'] = module.find_resource_by_name('compute_resources', name=entity_dict['compute_resource'], failsafe=False, thin=True)

        if 'compute_profile' in entity_dict:
            entity_dict['compute_profile'] = module.find_resource_by_name('compute_profiles', name=entity_dict['compute_profile'], failsafe=False, thin=True)

        if 'domain' in entity_dict:
            entity_dict['domain'] = module.find_resource_by_name('domains', name=entity_dict['domain'], failsafe=False, thin=True)

        if 'subnet' in entity_dict:
            entity_dict['subnet'] = module.find_resource_by_name('subnets', name=entity_dict['subnet'], failsafe=False, thin=True)

        if 'subnet6' in entity_dict:
            entity_dict['subnet6'] = module.find_resource_by_name('subnets', name=entity_dict['subnet6'], failsafe=False, thin=True)

        if 'realm' in entity_dict:
            entity_dict['realm'] = module.find_resource_by_name('realms', name=entity_dict['realm'], failsafe=False, thin=True)

        if 'architecture' in entity_dict:
            entity_dict['architecture'] = module.find_resource_by_name('architectures', name=entity_dict['architecture'], failsafe=False, thin=True)

        if 'operatingsystem' in entity_dict:
            entity_dict['operatingsystem'] = module.find_resource_by_title('operatingsystems', title=entity_dict['operatingsystem'], failsafe=False, thin=True)

        if 'media' in entity_dict:
            entity_dict['media'] = module.find_resource_by_name('media', name=entity_dict['media'], failsafe=False, thin=True)

        if 'ptable' in entity_dict:
            entity_dict['ptable'] = module.find_resource_by_name('ptables', name=entity_dict['ptable'], failsafe=False, thin=True)

        if 'environment' in entity_dict:
            entity_dict['environment'] = module.find_resource_by_name('environments', name=entity_dict['environment'], failsafe=False, thin=True)

        if 'config_groups' in entity_dict:
            entity_dict['config_groups'] = module.find_resources_by_name('config_groups', entity_dict['config_groups'], failsafe=False, thin=True)

        if 'puppet_proxy' in entity_dict:
            entity_dict['puppet_proxy'] = module.find_resource_by_name('smart_proxies', name=entity_dict['puppet_proxy'], failsafe=False, thin=True)

        if 'puppet_ca_proxy' in entity_dict:
            entity_dict['puppet_ca_proxy'] = module.find_resource_by_name('smart_proxies', name=entity_dict['puppet_ca_proxy'], failsafe=False, thin=True)

    entity = module.find_resource_by_title('hostgroups', title=build_fqn(name, parent), failsafe=True)
    if entity:
        entity['root_pass'] = None

    changed = module.ensure_resource_state('hostgroups', entity_dict, entity, name_map=name_map)

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()
