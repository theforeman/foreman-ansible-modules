#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2017, Andrew Kofink <ajkofink@gmail.com>
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
module: katello_lifecycle_environment
short_description: Create and Manage Katello lifecycle environments
description:
    - Create and Manage Katello lifecycle environments
author: "Andrew Kofink (@akofink)"
requirements:
    - "nailgun >= 0.28.0"
    - "python >= 2.6"
options:
    server_url:
        description:
            - URL of Foreman server
        required: true
    username:
        description:
            - Username on Foreman server
        required: true
    password:
        description:
            - Password for user accessing Foreman server
        required: true
    verify_ssl:
        description:
            - Verify SSL of the Foreman server
        default: True
    name:
        description:
            - Name of the lifecycle environment
        required: true
    label:
        description:
            - Label of the lifecycle environment. This field cannot be updated.
    description:
        description:
            - Description of the lifecycle environment
    organization:
        description:
            - Organization name that the lifecycle environment is in
        required: true
    prior:
        description:
            - Name of the parent lifecycle environment
    state:
        description:
            - Whether the lifecycle environment should be present or absent on the server
        required: true
        choices:
            - absent
            - present
'''

EXAMPLES = '''
- name: "Add a production lifecycle environment"
  katello_lifecycle_environment:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    verify_ssl: false
    name: "Production"
    label: "production"
    organization: "Default Organization"
    prior: "Library"
    description: "The production environment"
    state: "present"
'''

RETURN = '''# '''

try:
    from nailgun.entities import (
        LifecycleEnvironment
    )
    HAS_NAILGUN_PACKAGE = True
except:
    HAS_NAILGUN_PACKAGE = False

from ansible.module_utils.ansible_nailgun_cement import (
    create_server,
    ping_server,
    find_organization,
    find_lifecycle_environment,
    update_fields,
)


def validate_params(module, state, label=None, description=None, prior=None):
    message = ""
    if state != 'present':
        if label is not None:
            message += "Label cannot be specified if state is absent. "
        if description is not None:
            message += "Description cannot be specified if state is absent. "
        if prior is not None:
            message += "Prior cannot be specified if state is absent. "
    if len(message) > 0:
        module.fail_json(msg=message)
        return False


def find_prior(module, prior, organization):
    if prior is not None:
        return find_lifecycle_environment(module, prior, organization)


def lifecycle_environment(module, name, organization, state, label=None, description=None, prior=None):
    changed = False
    organization = find_organization(module, organization)
    prior = find_prior(module, prior, organization)
    current_environment = find_lifecycle_environment(module, name, organization, failsafe=True)

    if state == 'present':
        if label is not None and current_environment is not None and current_environment.label != label:
            module.fail_json(msg="Label cannot be updated on a lifecycle environment.")
        if prior is not None and current_environment is not None and current_environment.prior.id != prior.id:
            module.fail_json(msg="Prior cannot be updated on a lifecycle environment.")
        desired_environment = LifecycleEnvironment(name=name, organization=organization, label=label, description=description, prior=prior)
        fields = ['description']
        if current_environment is not None:
            (needs_update, le) = update_fields(desired_environment, current_environment, fields)
            if needs_update:
                le.update(fields)
                changed = True
        else:
            desired_environment.prior = find_prior(module, "Library", organization) if prior is None else prior
            desired_environment.create()
            changed = True
    elif current_environment is not None:
        current_environment.delete()
        changed = True
    return changed


def main():
    module = AnsibleModule(
        argument_spec=dict(
            server_url=dict(required=True),
            username=dict(required=True, no_log=True),
            password=dict(required=True, no_log=True),
            verify_ssl=dict(type='bool', default=True),
            name=dict(required=True),
            label=dict(),
            description=dict(),
            prior=dict(),
            organization=dict(required=True),
            state=dict(required=True),
        )
    )

    if not HAS_NAILGUN_PACKAGE:
        module.fail_json(msg="Missing required nailgun module (check docs or install "
                             "with: pip install nailgun)")

    server_url = module.params['server_url']
    username = module.params['username']
    password = module.params['password']
    verify_ssl = module.params['verify_ssl']
    name = module.params['name']
    label = module.params['label'] if module.params['label'] != '' else None
    description = module.params['description']
    prior = None if module.params['prior'] == '' else module.params['prior']
    organization = module.params['organization']
    state = module.params['state']

    create_server(server_url, (username, password), verify_ssl)
    ping_server(module)
    validate_params(module, state, label=label, description=description, prior=prior)

    try:
        changed = lifecycle_environment(module, name, organization, state, label=label, description=description, prior=prior)
        module.exit_json(changed=changed)
    except Exception as e:
        module.fail_json(msg=e)


from ansible.module_utils.basic import AnsibleModule

if __name__ == '__main__':
    main()
