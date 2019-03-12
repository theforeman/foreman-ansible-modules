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
  - "nailgun >= 0.28.0"
  - "python >= 2.6"
  - "ansible >= 2.3"
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
    default: true
  name:
    description:
      - Name of the repository set
    required: false
    type: bool
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
'''

EXAMPLES = '''
- name: "Enable RHEL 7 RPMs repositories"
  katello_repository_set:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    verify_ssl: false
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
    verify_ssl: false
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
    verify_ssl: false
    name: Red Hat Enterprise Linux 7 Server - Extras (RPMs)
    organization: "Default Organization"
    product: Red Hat Enterprise Linux Server
    state: disabled
    repositories:
      - basearch: x86_64
'''

RETURN = '''# '''

try:
    from ansible.module_utils.ansible_nailgun_cement import (
        find_organization,
        find_product,
        find_repository_set,
    )
except ImportError:
    pass

from ansible.module_utils.foreman_helper import KatelloEntityAnsibleModule


def get_desired_repos(desired_substitutions, available_repos):
    desired_repos = []
    for sub in desired_substitutions:
        desired_repos += filter(lambda available: available['substitutions'] == sub, available_repos)
    return desired_repos


def repository_set(module, name, organization, product, label, state, repositories=[]):
    changed = False
    organization = find_organization(module, organization)
    if product:
        product = find_product(module, product, organization)
    repo_set = find_repository_set(module, name=name, product=product, organization=organization, label=label)

    available_repos = repo_set.available_repositories()['results']
    current_repos = map(lambda repo: repo.read(), repo_set.repositories)
    desired_repos = get_desired_repos(repositories, available_repos)

    available_repo_names = set(map(lambda repo: repo['repo_name'], available_repos))
    current_repo_names = set(map(lambda repo: repo.name, current_repos))
    desired_repo_names = set(map(lambda repo: repo['repo_name'], desired_repos))

    if len(desired_repo_names - available_repo_names) > 0:
        module.fail_json(msg="Desired repositories are not available on the repository set {}. Desired: {} Available: {}"
                         .format(name, desired_repo_names, available_repo_names))

    if state == 'enabled':
        for repo in desired_repo_names - current_repo_names:
            repo_to_enable = next((r for r in available_repos if r['repo_name'] == repo))
            repo_to_enable['substitutions']['product_id'] = repo_set.product.id
            if not module.check_mode:
                repo_set.enable(data=repo_to_enable['substitutions'])
            changed = True
    elif state == 'disabled':
        for repo in current_repo_names & desired_repo_names:
            repo_to_disable = next((r for r in available_repos if r['repo_name'] == repo))
            repo_to_disable['substitutions']['product_id'] = repo_set.product.id
            if not module.check_mode:
                repo_set.disable(data=repo_to_disable['substitutions'])
            changed = True
    return changed


def main():
    module = KatelloEntityAnsibleModule(
        argument_spec=dict(
            name=dict(default=None),
            product=dict(default=None),
            label=dict(default=None),
            repositories=dict(required=True, type='list'),
            state=dict(default='enabled', choices=['disabled', 'enabled']),
        ),
        supports_check_mode=True,
        required_one_of=[['label', 'name']],
    )

    (module_params, state) = module.parse_params()
    name = module_params.get('name')
    product = module_params.get('product')
    label = module_params.get('label')
    organization = module_params.get('organization')
    repositories = module_params.get('repositories')

    module.connect()

    try:
        changed = repository_set(module, name, organization, product, label, state, repositories=repositories)
        module.exit_json(changed=changed)
    except Exception as e:
        module.fail_json(msg=e)


if __name__ == '__main__':
    main()
