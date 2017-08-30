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
        required: true
    product:
        description:
            - Name of the parent product
        required: true
    repositories:
        description:
            - Release version and base architecture of the repositories to enable
        required: true
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
'''

RETURN = '''# '''

try:
    from ansible.module_utils.ansible_nailgun_cement import (
        create_server,
        handle_no_nailgun,
        find_organization,
        find_product,
        find_repository_set,
        ping_server,
    )
    HAS_NAILGUN_PACKAGE = True
except:
    HAS_NAILGUN_PACKAGE = False


def get_desired_repos(desired_substitutions, available_repos):
    desired_repos = []
    for sub in desired_substitutions:
        desired_repos += filter(lambda available: available['substitutions'] == sub, available_repos)
    return desired_repos


def repository_set(module, name, organization, product, state, repositories=[]):
    changed = False
    organization = find_organization(module, organization)
    product = find_product(module, product, organization)
    repo_set = find_repository_set(module, name=name, product=product)

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
            repo_to_enable = (r for r in available_repos if r['repo_name'] == repo).next()
            repo_set.enable(data=repo_to_enable['substitutions'])
            changed = True
    elif state == 'disabled':
        for repo in current_repo_names & desired_repo_names:
            repo_to_disable = (r for r in available_repos if r['repo_name'] == repo).next()
            repo_set.disable(data=repo_to_disable['substitutions'])
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
            product=dict(),
            organization=dict(required=True),
            repositories=dict(required=True, type='list'),
            state=dict(required=True, choices=['disabled', 'enabled']),
        )
    )

    handle_no_nailgun(module, HAS_NAILGUN_PACKAGE)

    server_url = module.params['server_url']
    username = module.params['username']
    password = module.params['password']
    verify_ssl = module.params['verify_ssl']
    name = module.params['name']
    product = module.params['product']
    organization = module.params['organization']
    repositories = module.params['repositories']
    state = module.params['state']

    create_server(server_url, (username, password), verify_ssl)
    ping_server(module)

    try:
        changed = repository_set(module, name, organization, product, state, repositories=repositories)
        module.exit_json(changed=changed)
    except Exception as e:
        module.fail_json(msg=e)


from ansible.module_utils.basic import AnsibleModule

if __name__ == '__main__':
    main()
