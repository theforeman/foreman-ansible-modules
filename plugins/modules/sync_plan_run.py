#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2026, Jakub Duchek <jakduch@seznam.cz>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: sync_plan_run
version_added: 5.13.0
short_description: Run a Sync Plan
description:
  - Run all products attached to a sync plan immediately.
author:
  - "Jakub Duchek (@jakduch)"
options:
  sync_plan:
    description:
      - Name of the sync plan to run.
    required: true
    type: str
extends_documentation_fragment:
  - theforeman.foreman.foreman
  - theforeman.foreman.foreman.organization
'''

EXAMPLES = '''
- name: "Run RHEL sync plan"
  theforeman.foreman.sync_plan_run:
    username: "admin"
    password: "changeme"
    server_url: "https://foreman.example.com"
    organization: "Default Organization"
    sync_plan: "RHEL repositories"
'''

RETURN = '''
task:
  description: Details of the completed Foreman task.
  returned: success
  type: dict
'''

from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import KatelloAnsibleModule


def main():
    module = KatelloAnsibleModule(
        foreman_spec=dict(
            sync_plan=dict(type='entity', scope=['organization'], required=True),
        ),
    )

    module.task_timeout = 12 * 60 * 60

    with module.api_connection():
        sync_plan = module.lookup_entity('sync_plan')
        task = module.resource_action('sync_plans', 'sync', {'id': sync_plan['id']})
        module.exit_json(task=task)


if __name__ == '__main__':
    main()
