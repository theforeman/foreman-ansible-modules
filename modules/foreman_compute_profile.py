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
module: foreman_compute_profile
short_description: Manage Foreman Compute Profiles using Foreman API
description:
  - Create and delete Foreman Compute Profiles using Foreman API
version_added: "2.0"
author:
  - "Philipp Joos (@philippj)"
  - "Baptiste Agasse (@bagasse)"
requirements:
  - "nailgun >= 0.28.0"
  - "python >= 2.6"
  - "ansible >= 2.3"
options:
  name:
    description: compute profile name
    required: true
  updated_name:
    description: new compute profile name
    required: false
  compute_attributes:
    description: Compute attributes related to this compute profile. Some of these attributes are specific to the underlying compute resource type
    required: false
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
    description: compute profile presence
    default: present
    choices: ["present", "absent"]
'''

EXAMPLES = '''
- name: compute profile
  foreman_compute_profile:
    name: example_compute_profile
    server_url: foreman.example.com
    username: admin
    password: secret
    verify_ssl: false
    state: present

- name: another compute profile
  foreman_compute_profile:
    name: another_example_compute_profile
    compute_attributes:
    - compute_resource: ovirt_compute_resource1
      vm_attrs:
        cluster: 'a96d44a4-f14a-1015-82c6-f80354acdf01'
        template: 'c88af4b7-a24a-453b-9ac2-bc647ca2ef99'
        instance_type: 'cb8927e7-a404-40fb-a6c1-06cbfc92e077'
    server_url: foreman.example.com
    username: admin
    password: secret
    verify_ssl: false
    state: present

- name: compute profile2
  foreman_compute_profile:
    name: example_compute_profile2
    compute_attributes:
    - compute_resource: ovirt_compute_resource01
      vm_attrs:
        cluster: a96d44a4-f14a-1015-82c6-f80354acdf01
        cores: 1
        sockets: 1
        memory: 1073741824
        ha: 0
        interfaces_attributes:
          0:
            name: ""
            network: 390666e1-dab3-4c99-9f96-006b2e2fd801
            interface: virtio
        volumes_attributes:
          0:
            size_gb: 16
            storage_domain: 19c50090-1ab4-4023-a63f-75ee1018ed5e
            preallocate: '1'
            wipe_after_delete: '0'
            interface: virtio_scsi
            bootable: 'true'
    - compute_resource: libvirt_compute_resource03
      vm_attrs:
        cpus: 1
        memory: 2147483648
        nics_attributes:
          0:
            type: bridge
            bridge: ""
            model: virtio
        volumes_attributes:
          0:
            pool_name: default
            capacity: 16G
            allocation: 16G
            format_type: raw
    server_url: foreman.example.com
    username: admin
    password: secret
    verify_ssl: false
    state: present

- name: Remove compute profile
  foreman_compute_profile:
    name: example_compute_profile2
    state: absent
'''

RETURN = ''' # '''

try:
    from ansible.module_utils.ansible_nailgun_cement import (
        find_compute_resource,
        find_compute_profile,
        find_compute_attribute,
        naildown_entity,
        naildown_entity_state,
        sanitize_entity_dict,
    )

    from nailgun.entities import (
        AbstractComputeResource,
        ComputeProfile,
        ComputeAttribute,
    )
except ImportError:
    pass

from ansible.module_utils.foreman_helper import ForemanEntityAnsibleModule


# This is the only true source for names (and conversions thereof)
name_map = {
    'name': 'name',
}

compute_attribute_name_map = {
    'compute_resource': 'compute_resource',
    'vm_attrs': 'vm_attrs',
}


def compute_attribute(module, compute_profile, attributes):
    # If we don't work on a copy, we hit a TypeError: Value of unknown type: <class 'nailgun.entities.ComputeProfile'> exception
    # from module.exit_json(changed=changed) method
    compute_attribute_dict = attributes.copy()
    for key in ['compute_resource', 'vm_attrs']:
        if key not in compute_attribute_dict:
            module.fail_json(msg='compute_attribute must have %s.' % key)

    try:
        compute_attribute = find_compute_attribute(module, compute_profile_name=compute_profile.name,
                                                   compute_resource_name=compute_attribute_dict['compute_resource'], failsafe=True)
        compute_attribute_dict['compute_resource'] = find_compute_resource(module, name=compute_attribute_dict['compute_resource'])
    except Exception as e:
        module.fail_json(msg='Failed to find entity: %s ' % e)

    if 'compute_profile' not in compute_attribute_dict:
        compute_attribute_dict['compute_profile'] = compute_profile

    changed = naildown_entity_state(ComputeAttribute, compute_attribute_dict, compute_attribute, 'present', module)

    return changed


def main():
    module = ForemanEntityAnsibleModule(
        argument_spec=dict(
            name=dict(required=True),
            updated_name=dict(),
            compute_attributes=dict(type='list'),
        ),
        supports_check_mode=True,
    )

    (compute_profile_dict, state) = module.parse_params()
    name = compute_profile_dict.get('name')
    updated_name = compute_profile_dict.get('updated_name')
    compute_attributes = compute_profile_dict.pop('compute_attributes', list())

    if len(compute_attributes) > 0 and state == 'absent':
        module.fail_json(msg='compute_attributes not allowed when state=absent')

    module.connect()

    try:
        # Try to find the compute_profile to work on
        compute_profile = find_compute_profile(module, name=compute_profile_dict['name'], failsafe=True)
    except Exception as e:
        module.fail_json(msg='Failed to find entity: %s ' % e)

    if state == 'present' and updated_name:
        compute_profile_dict['name'] = updated_name

    compute_profile_dict = sanitize_entity_dict(compute_profile_dict, name_map)

    (changed, compute_profile) = naildown_entity(ComputeProfile, compute_profile_dict, compute_profile, state, module)

    # Apply changes on underlying compute attributes only when present
    if state == 'present':
        # Update or create compute attributes
        for compute_attribute_dict in compute_attributes:
            changed |= compute_attribute(module, compute_profile, compute_attribute_dict)

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()


#  vim: set sts=4 ts=8 sw=4 ft=python et noro norl cin si ai :
