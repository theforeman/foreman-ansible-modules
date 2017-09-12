#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) Philipp Joos 2017
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
options:
  name:
    description: compute resource name
    required: true
  description: compute resource description
    required: false
  provider:
    description: provider
    required: false
    default: None
    choices: ["vmware", "libvirt", "ovirt"]
  provider_auth:
    description: provider authentication
    required: false
    default: None
  locations: List of locations the compute resource should be assigned to
    required: false
    default: None
  organizations: List of organizations the compute resource should be assigned to
    required: false
    default: None
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
  state:
    description: compute resource presence
    required: false
    default: present
    choices: ["present", "absent", "latest"]
notes:
- Nailed down version of https://github.com/Nosmoht/python-foreman (@Nosmoht). Requires nailgun
version_added: "2.0"
author: "Philipp Joos (@philippj)"
'''

EXAMPLES = '''
- name: vmware compute resource
  foreman_compute_resource:
    name: example_compute_resource
    datacenter: ax01
    locations:
    - Munich
    organizations:
    - ATIX
    provider: vmware
    provider_auth:
      url: vsphere.example.com
      user: admin
      password: secret
    server_url: vsphere.example.com
    username: admin
    password: secret
    state: present
'''

RETURN = ''' # '''

try:
    import nailgun.entity_mixins
    import nailgun.entities
    import nailgun.entity_fields
    import ansible.module_utils.ansible_nailgun_cement as cement
    HAS_NAILGUN_PACKAGE = True

except:
    HAS_NAILGUN_PACKAGE = False

from ansible.module_utils.basic import AnsibleModule


def get_provider_params(provider):
    provider_name = provider.lower()

    if provider_name == 'libvirt':
        return {
            'credentials': ['url'],
            'params': ['display_type'],
            'class': nailgun.entities.LibvirtComputeResource
        }

    elif provider_name == 'ovirt':
        return {
            'credentials': ['url', 'user', 'password'],
            'params': [],
            'class': cement.OVirtComputeResource
        }

    elif provider_name == 'vmware':
        return {
            'credentials': ['url', 'user', 'password'],
            'params': ['datacenter'],
            'class': cement.VMWareComputeResource
        }

    else:
        return False


def main(module):
    cement.handle_no_nailgun(module, HAS_NAILGUN_PACKAGE)

    name = module.params.get('name')
    state = module.params.get('state')
    provider = module.params.get('provider').title()
    description = module.params.get('description')
    locations = module.params.get('locations')
    organizations = module.params.get('organizations')

    cement.create_server(
        server_url=module.params.get('server_url'),
        auth=(module.params.get('username'), module.params.get('password')),
        verify_ssl=module.params.get('verify_ssl'),
    )

    cement.ping_server(module)

    data = {
        'name': name,
        'description': description
    }

    compute_resource = cement.find_compute_resource(module, name=data.get('name'), failsafe=True)

    if organizations:
        data['organization'] = [cement.find_organization(module, organization) for organization in organizations]

    if locations:
        data['location'] = [cement.find_location(module, location) for location in locations]

    data['provider'] = provider
    provider_params = get_provider_params(provider=provider)

    if state in ['present', 'latest']:
        if not provider_params and not compute_resource:
            module.fail_json(msg='To create a compute resource a valid provider must be supplied')

        for key in provider_params.get('credentials'):
            data.__setitem__(key, module.params.get('provider_auth').get(key))

        for key in provider_params.get('params'):
            if key not in module.params:
                module.fail_json(msg='missing required param {}'.format(key))

            data.__setitem__(key, module.params.get(key))

    changed = cement.naildown_entity_state(provider_params.get('class'), data, compute_resource, state, module)

    return changed

if __name__ == '__main__':
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type='str', required=True),
            description=dict(type='str'),
            provider=dict(type='str', choices=['vmware', 'libvirt', 'ovirt']),
            provider_auth=dict(type='dict'),
            locations=dict(type='list'),
            organizations=dict(type='list'),
            server_url=dict(type='str'),
            username=dict(required=True),
            password=dict(required=True, no_log=True),
            verify_ssl=dict(type='bool', default=True),
            state=dict(type='str', default='present', choices=['present', 'absent', 'latest']),
            # provider-params
            url=dict(type='str'),
            display_type=dict(type='str'),
            datacenter=dict(type='str'),
        ),
        required_if=(
            ['state', 'present', ['provider']],
        ),
    )
    result = main(module)
    module.exit_json(changed=result)
