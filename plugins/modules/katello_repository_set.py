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
module: katello_repository_set
short_description: Enable/disable repositories in Katello repository sets
description:
  - Enable/disable repositories in Katello repository sets
author: "Andrew Kofink (@akofink)"
requirements:
  - "apypie"
options:
  name:
    description:
      - Name of the repository set
    required: false
  product:
    description:
      - Name of the parent product
    required: false
  label:
    description:
      - Label of the repository set, can be used in place of I(name) & I(product)
    required: false
  repositories:
    description:
      - Release version and base architecture of the repositories to enable
    required: true
    type: list
  organization:
    description:
      - Organization name that the repository set is in
    required: true
  state:
    description:
      - Whether the repositories are enabled or not
    required: true
    choices:
      - 'enabled'
      - 'disabled'
extends_documentation_fragment: foreman
'''

EXAMPLES = '''
- name: "Enable RHEL 7 RPMs repositories"
  katello_repository_set:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: "Red Hat Enterprise Linux 7 Server (RPMs)"
    organization: "Default Organization"
    product: "Red Hat Enterprise Linux Server"
    repositories:
    - releasever: "7.0"
      basearch: "x86_64"
    - releasever: "7.1"
      basearch: "x86_64"
    - releasever: "7.2"
      basearch: "x86_64"
    - releasever: "7.3"
      basearch: "x86_64"
    state: enabled

- name: "Enable RHEL 7 RPMs repositories with label"
  katello_repository_set:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    organization: "Default Organization"
    label: rhel-7-server-rpms
    repositories:
    - releasever: "7.0"
      basearch: "x86_64"
    - releasever: "7.1"
      basearch: "x86_64"
    - releasever: "7.2"
      basearch: "x86_64"
    - releasever: "7.3"
      basearch: "x86_64"
    state: enabled

- name: "Disable RHEL 7 Extras RPMs repository"
  katello_repository_set:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    name: Red Hat Enterprise Linux 7 Server - Extras (RPMs)
    organization: "Default Organization"
    product: Red Hat Enterprise Linux Server
    state: disabled
    repositories:
      - basearch: x86_64

- name: "Enable RHEL 8 BaseOS RPMs repository with label"
  katello_repository_set:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    organization: "Default Organization"
    label: rhel-8-for-x86_64-baseos-rpms
    repositories:
      - releasever: 8
'''

RETURN = ''' # '''

from ansible.module_utils.foreman_helper import KatelloEntityAnsibleModule


def get_desired_repos(desired_substitutions, available_repos):
    desired_repos = []
    for sub in desired_substitutions:
        desired_repos += filter(lambda available: available['substitutions'] == sub, available_repos)
    return desired_repos


def main():
    module = KatelloEntityAnsibleModule(
        argument_spec=dict(
            name=dict(),
            product=dict(),
            label=dict(),
            repositories=dict(required=True, type='list', elements='dict'),
            state=dict(default='enabled', choices=['disabled', 'enabled']),
        ),
        required_one_of=[['label', 'name']],
    )

    module_params = module.clean_params()

    module.connect()

    module_params['organization'] = module.find_resource_by_name('organizations', name=module_params['organization'], thin=True)
    scope = {'organization_id': module_params['organization']['id']}
    if 'product' in module_params:
        module_params['product'] = module.find_resource_by_name('products', name=module_params['product'], params=scope, thin=True)
        scope['product_id'] = module_params['product']['id']

    if 'label' in module_params:
        search = 'label="{}"'.format(module_params['label'])
        repo_set = module.find_resource('repository_sets', search=search, params=scope)
    else:
        repo_set = module.find_resource_by_name('repository_sets', name=module_params['name'], params=scope)
    repo_set_scope = {'id': repo_set['id'], 'product_id': repo_set['product']['id']}
    repo_set_scope.update(scope)

    _, available_repos = module.resource_action('repository_sets', 'available_repositories', params=repo_set_scope)
    available_repos = available_repos['results']
    current_repos = repo_set['repositories']
    desired_repos = get_desired_repos(module_params['repositories'], available_repos)

    available_repo_names = set(map(lambda repo: repo['repo_name'], available_repos))
    current_repo_names = set(map(lambda repo: repo['name'], current_repos))
    desired_repo_names = set(map(lambda repo: repo['repo_name'], desired_repos))

    if len(desired_repo_names - available_repo_names) > 0:
        module.fail_json(msg="Desired repositories are not available on the repository set {}. Desired: {} Available: {}"
                         .format(module_params['name'], desired_repo_names, available_repo_names))

    changed = False
    if module.state == 'enabled':
        for repo in desired_repo_names - current_repo_names:
            repo_to_enable = next((r for r in available_repos if r['repo_name'] == repo))
            repo_change_params = repo_to_enable['substitutions'].copy()
            repo_change_params.update(repo_set_scope)
            if not module.check_mode:
                module.resource_action('repository_sets', 'enable', params=repo_change_params)
            changed = True
    elif module.state == 'disabled':
        for repo in current_repo_names & desired_repo_names:
            repo_to_disable = next((r for r in available_repos if r['repo_name'] == repo))
            repo_change_params = repo_to_disable['substitutions'].copy()
            repo_change_params.update(repo_set_scope)
            if not module.check_mode:
                module.resource_action('repository_sets', 'disable', params=repo_change_params)
            changed = True

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()
