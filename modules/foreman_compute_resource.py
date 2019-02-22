#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) Philipp Joos 2017
# (c) Baptiste Agasse 2019
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
module: foreman_compute_resource
short_description: Manage Foreman Compute resources using Foreman API
description:
  - Create and delete Foreman Compute Resources using Foreman API
author:
  - "Philipp Joos (@philippj)"
  - "Baptiste Agasse (@bagasse)"
requirements:
  - "nailgun >= 0.32.0"
  - "ansible >= 2.3"
options:
  name:
    description: compute resource name
    required: true
  updated_name:
    description: new compute resource name
    required: false
  description:
    description: compute resource description
    required: false
  provider:
    description: Compute resource provider. Required if I(state=present).
    required: false
    default: None
    choices: ["vmware", "libvirt", "ovirt"]
  provider_auth:
    description: Deprecated, use I(provider_params) instead. Provider authentication
    required: false
    default: None
  provider_params:
    description: Parameter specific to compute resource provider
    required: false
    default: None
  locations:
    description: List of locations the compute resource should be assigned to
    required: false
    default: None
    type: list
  organizations:
    description: List of organizations the compute resource should be assigned to
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
    required: false
    default: true
    type: bool
  state:
    description: compute resource presence
    required: false
    default: present
    choices: ["present", "absent", "present_with_defaults"]
version_added: "2.0"
'''

EXAMPLES = '''
- name: vmware compute resource
  foreman_compute_resource:
    name: example_compute_resource
    locations:
      - Munich
    organizations:
      - ATIX
    provider: vmware
    provider_params:
      url: vsphere.example.com
      user: admin
      password: secret
      datacenter: ax01
    server_url: foreman.example.com
    username: admin
    password: secret
    state: present

- name: ovirt compute resource
  foreman_compute_resource:
    name: ovirt_compute_resource
    locations:
      - France/Toulouse
    organizations:
      - Example Org
    provider: ovirt
    provider_params:
      url: ovirt.example.com
      user: ovirt-admin@example.com
      password: ovirtsecret
      datacenter: aa92fb54-0736-4066-8fa8-b8b9e3bd75ac
      ovirt_quota: 24868ab9-c2a1-47c3-87e7-706f17d215ac
      use_v4: true
    server_url: foreman.example.com
    username: admin
    password: secret
    state: present
'''

RETURN = ''' # '''

try:
    from ansible.module_utils.ansible_nailgun_cement import (
        find_compute_resource,
        find_organizations,
        find_locations,
        naildown_entity_state,
        sanitize_entity_dict,
    )

    from nailgun.entities import (
        AbstractComputeResource,
        LibvirtComputeResource,
        OVirtComputeResource,
        VMWareComputeResource,
    )

    has_import_error = False
except ImportError as e:
    has_import_error = True
    import_error_msg = str(e)

from ansible.module_utils.foreman_helper import ForemanEntityAnsibleModule

# This is the only true source for names (and conversions thereof)
name_map = {
    'name': 'name',
    'description': 'description',
    'provider': 'provider',
    'organizations': 'organization',
    'locations': 'location',
    'datacenter': 'datacenter',
}


def get_provider_infos(provider):
    provider_name = provider.lower()

    if provider_name == 'libvirt':
        return {
            'params': ['url', 'display_type'],
            'class': LibvirtComputeResource
        }

    elif provider_name == 'ovirt':
        return {
            'params': ['url', 'user', 'password', 'datacenter', 'use_v4', 'ovirt_quota'],
            'class': OVirtComputeResource
        }

    elif provider_name == 'vmware':
        return {
            'params': ['url', 'user', 'password', 'datacenter'],
            'class': VMWareComputeResource
        }

    else:
        return {
            'params': [],
            'class': AbstractComputeResource
        }


def main():
    module = ForemanEntityAnsibleModule(
        argument_spec=dict(
            name=dict(type='str', required=True),
            updated_name=dict(type='str'),
            description=dict(type='str'),
            provider=dict(type='str', choices=['vmware', 'libvirt', 'ovirt']),
            provider_params=dict(type='dict'),
            locations=dict(type='list'),
            organizations=dict(type='list'),
            state=dict(type='str', default='present', choices=['present', 'absent', 'present_with_defaults']),

            # Deprecated provider's specific params, use nested keys in provider_params param instead
            provider_auth=dict(type='dict'),
            url=dict(type='str'),
            display_type=dict(type='str'),
            datacenter=dict(type='str'),
        ),
        required_if=(
            ['state', 'present', ['provider']],
        ),
        supports_check_mode=True,
    )

    (entity_dict, state) = module.parse_params()

    if 'provider' in entity_dict:
        entity_dict['provider'] = entity_dict['provider'].title()

    provider_infos = get_provider_infos(provider=entity_dict.get('provider', ''))
    provider_params = entity_dict.pop('provider_params', dict())
    provider_auth = entity_dict.pop('provider_auth', dict())

    module.connect()

    try:
        # Try to find the compute_resource to work on
        entity = find_compute_resource(module, name=entity_dict['name'], failsafe=True)
    except Exception as e:
        module.fail_json(msg='Failed to find entity: %s ' % e)

    if 'updated_name' in entity_dict and state == 'present':
        entity_dict['name'] = entity_dict['updated_name']

    if 'organizations' in entity_dict:
        entity_dict['organizations'] = find_organizations(module, entity_dict['organizations'])

    if 'locations' in entity_dict:
        entity_dict['locations'] = find_locations(module, entity_dict['locations'])

    entity_dict = sanitize_entity_dict(entity_dict, name_map)

    # Add provider specific params
    if state in ['present', 'present_with_defaults']:
        if not provider_infos and not entity:
            module.fail_json(msg='To create a compute resource a valid provider must be supplied')

        for key in provider_infos['params']:
            # Manage deprecated params
            if key in provider_auth:
                entity_dict[key] = provider_auth[key]

            if key in provider_params:
                entity_dict[key] = provider_params[key]

    changed = naildown_entity_state(provider_infos['class'], entity_dict, entity, state, module)

    module.exit_json(changed=changed)


if __name__ == '__main__':
    changed = main()

#  vim: set sts=4 ts=8 sw=4 ft=python et noro norl cin si ai :
