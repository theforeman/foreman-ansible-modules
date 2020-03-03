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

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: foreman_hostgroup
short_description: Manage Foreman Hostgroups using Foreman API
description:
  - Create, Update and Delete Foreman Hostgroups using Foreman API
author:
  - "Manisha Singhal (@Manisha15) ATIX AG"
  - "Baptiste Agasse (@bagasse)"
options:
  name:
    description: Name of hostgroup
    required: true
    type: str
  updated_name:
    description: New name of hostgroup. When this parameter is set, the module will not be idempotent.
    type: str
  description:
    description: Description of hostgroup
    required: false
    type: str
  parent:
    description: Hostgroup parent name
    required: false
    type: str
  realm:
    description: Realm name
    required: false
    type: str
  architecture:
    description: Architecture name
    required: False
    type: str
  medium:
    aliases: [ media ]
    description:
      - Medium name
      - Mutually exclusive with I(kickstart_repository).
    required: False
    type: str
  operatingsystem:
    description: Operatingsystem title
    required: False
    type: str
  pxe_loader:
    description: PXE Bootloader
    required: false
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
    type: str
  ptable:
    description: Partition table name
    required: False
    type: str
  root_pass:
    description: root password
    required: false
    type: str
  environment:
    description: Puppet environment name
    required: false
    type: str
  puppetclasses:
    description: List of puppet classes to include in this host group. Must exist for hostgroup's puppet environment.
    required: false
    type: list
    elements: str
  config_groups:
    description: Config groups list
    required: false
    type: list
    elements: str
  puppet_proxy:
    description: Puppet server proxy name
    required: false
    type: str
  puppet_ca_proxy:
    description: Puppet CA proxy name
    required: false
    type: str
  openscap_proxy:
    description: OpenSCAP proxy name. Only available when the OpenSCAP plugin is installed.
    required: false
    type: str
  organization:
    description:
      - Organization for scoped resources attached to the hostgroup.
      - Only used for Katello installations.
      - This organization will implicitly be added to the I(organizations) parameter if needed.
    required: false
    type: str
  content_source:
    description:
      - Katello Content source.
      - Only available for Katello installations.
    required: false
    type: str
  lifecycle_environment:
    description:
      - Katello Lifecycle environment.
      - Only available for Katello installations.
    required: false
    type: str
  kickstart_repository:
    description:
     - Kickstart repository name.
     - You need to provide this to use the "Synced Content" feature of Katello.
     - Mutually exclusive with I(medium).
     - Only available for Katello installations.
    required: false
    type: str
  content_view:
    description:
      - Katello Content view.
      - Only available for Katello installations.
    required: false
    type: str
  parameters:
    description:
      - Hostgroup specific host parameters
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.entity_state
  - theforeman.foreman.foreman.taxonomy
  - theforeman.foreman.foreman.nested_parameters
  - theforeman.foreman.foreman.host_options
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
    organizations:
      - Org One
      - Org Two
    locations:
      - Loc One
      - Loc Two
      - Loc One/Nested loc
    medium: "updated_media_name"
    ptable: "updated_Partition_table_name"
    root_pass: "password"
    server_url: "https://foreman.example.com"
    username: "admin"
    password: "secret"
    state: present

- name: "My nested hostgroup"
  foreman_hostgroup:
    parent: "new_hostgroup"
    name: "my nested hostgroup"

- name: "My hostgroup with some proxies"
  foreman_hostgroup:
    name: "my hostgroup"
    environment: production
    puppet_proxy: puppet-proxy.example.com
    puppet_ca_proxy: puppet-proxy.example.com
    openscap_proxy: openscap-proxy.example.com

- name: "My katello related hostgroup"
  foreman_hostgroup:
    organization: "My Org"
    name: "kt hostgroup"
    content_source: capsule.example.com
    lifecycle_environment: "Production"
    content_view: "My content view"
    parameters:
      - name: "kt_activation_keys"
        value: "my_prod_ak"

- name: "Delete a Hostgroup"
  foreman_hostgroup:
    name: "new_hostgroup"
    server_url: "https://foreman.example.com"
    username: "admin"
    password: "secret"
    state: absent
'''

RETURN = ''' # '''

from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import (
    HostMixin,
    ForemanTaxonomicEntityAnsibleModule,
    OrganizationMixin,
)


class ForemanHostgroupModule(OrganizationMixin, HostMixin, ForemanTaxonomicEntityAnsibleModule):
    pass


def ensure_puppetclasses(module, entity, expected_puppetclasses=None):
    if expected_puppetclasses:
        expected_puppetclasses = module.find_puppetclasses(expected_puppetclasses, environment=entity['environment_id'], thin=True)
    current_puppetclasses = entity.pop('puppetclass_ids', [])
    if expected_puppetclasses:
        for puppetclass in expected_puppetclasses:
            if puppetclass['id'] in current_puppetclasses:
                current_puppetclasses.remove(puppetclass['id'])
            else:
                payload = {'hostgroup_id': entity['id'], 'puppetclass_id': puppetclass['id']}
                module.ensure_entity('hostgroup_classes', {}, None, params=payload, state='present', entity_spec={})
        if len(current_puppetclasses) > 0:
            for leftover_puppetclass in current_puppetclasses:
                module.ensure_entity('hostgroup_classes', {}, {'id': leftover_puppetclass}, {'hostgroup_id': entity['id']}, state='absent', entity_spec={})


def main():
    module = ForemanHostgroupModule(
        entity_spec=dict(
            name=dict(required=True),
            description=dict(),
            parent=dict(type='entity'),
            realm=dict(type='entity'),
            architecture=dict(type='entity'),
            operatingsystem=dict(type='entity'),
            medium=dict(aliases=['media'], type='entity'),
            ptable=dict(type='entity'),
            pxe_loader=dict(choices=['PXELinux BIOS', 'PXELinux UEFI', 'Grub UEFI', 'Grub2 BIOS', 'Grub2 ELF',
                                     'Grub2 UEFI', 'Grub2 UEFI SecureBoot', 'Grub2 UEFI HTTP', 'Grub2 UEFI HTTPS',
                                     'Grub2 UEFI HTTPS SecureBoot', 'iPXE Embedded', 'iPXE UEFI HTTP', 'iPXE Chain BIOS', 'iPXE Chain UEFI']),
            root_pass=dict(no_log=True),
            environment=dict(type='entity'),
            puppetclasses=dict(type='entity_list', resolve=False),
            config_groups=dict(type='entity_list'),
            puppet_proxy=dict(type='entity', resource_type='smart_proxies'),
            puppet_ca_proxy=dict(type='entity', resource_type='smart_proxies'),
            openscap_proxy=dict(type='entity', resource_type='smart_proxies'),
            content_source=dict(type='entity', scope='organization', resource_type='smart_proxies'),
            lifecycle_environment=dict(type='entity', scope='organization'),
            kickstart_repository=dict(type='entity', scope='organization', resource_type='repositories'),
            content_view=dict(type='entity', scope='organization'),
        ),
        argument_spec=dict(
            organization=dict(),
            updated_name=dict(),
        ),
        mutually_exclusive=[['medium', 'kickstart_repository']],
    )

    entity_dict = module.clean_params()
    katello_params = ['content_source', 'lifecycle_environment', 'content_view']

    if 'organization' not in entity_dict and list(set(katello_params) & set(entity_dict.keys())):
        module.fail_json(msg="Please specify the organization when using katello parameters.")

    with module.api_connection():
        if not module.desired_absent:
            if 'organization' in entity_dict:
                if 'organizations' in entity_dict:
                    if entity_dict['organization'] not in entity_dict['organizations']:
                        entity_dict['organizations'].append(entity_dict['organization'])
                else:
                    entity_dict['organizations'] = [entity_dict['organization']]
                entity_dict, scope = module.handle_organization_param(entity_dict)
        entity, entity_dict = module.resolve_entities(entity_dict=entity_dict)
        expected_puppetclasses = entity_dict.pop('puppetclasses', None)
        entity = module.run(entity_dict=entity_dict, entity=entity)
        if not module.desired_absent and 'environment_id' in entity:
            ensure_puppetclasses(module, entity, expected_puppetclasses)


if __name__ == '__main__':
    main()
