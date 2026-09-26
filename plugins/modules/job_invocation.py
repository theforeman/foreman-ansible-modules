#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2020 Peter Ondrejka <pondrejk@redhat.com>
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
module: job_invocation
short_description: Invoke Remote Execution Jobs
version_added: 1.4.0
description:
  - "Invoke and schedule Remote Execution Jobs"
author:
  - "Peter Ondrejka (@pondrejk)"
options:
  search_query:
    description:
      - Search query to identify hosts
    type: str
  bookmark:
    description:
      - Bookmark to infer the search query from
    type: str
  job_template:
    description:
      - Job template to execute
    type: str
  targeting_type:
    description:
      - Dynamic query updates the search results before execution (useful for scheduled jobs)
    choices:
      - static_query
      - dynamic_query
    default: static_query
    type: str
  randomized_ordering:
    description:
      - Whether to order the selected hosts randomly
    type: bool
  execution_timeout_interval:
    description:
      - Override the timeout interval from the template for this invocation only
    type: int
  ssh:
    description:
      - ssh related options
    type: dict
    suboptions:
      effective_user:
        description:
          - What user should be used to run the script (using sudo-like mechanisms)
          - Defaults to a template parameter or global setting
        type: str
  command:
    description:
      - Command to be executed on host. Required for command templates
    type: str
  inputs:
    description:
      - Inputs to use
    type: dict
  recurrence:
    description:
      - Schedule a recurring job
    type: dict
    suboptions:
      cron_line:
        description:
          - How often the job should occur, in the cron format
        type: str
      max_iteration:
        description:
          - Repeat a maximum of N times
        type: int
      end_time:
        description:
          - Perform no more executions after this time
        type: str
      purpose:
        description:
          - Designation of a special purpose
          - Acts as an idempotency key for recurring jobs
          - An active or disabled job with the same purpose is reused when its managed parameters match
          - A job with changed managed parameters is cancelled and recreated
        type: str
  scheduling:
    description:
      - Schedule the job to start at a later time
    type: dict
    suboptions:
      start_at:
        description:
          - Schedule the job for a future time
        type: str
      start_before:
        description:
          - Indicates that the action should be cancelled if it cannot be started before this time.
        type: str
  concurrency_control:
    description:
      - Control concurrency level and distribution over time
    type: dict
    suboptions:
      time_span:
        description:
          - Distribute tasks over given number of seconds
          - This is removed since foreman_remote_execution-11.0.0
        type: int
      concurrency_level:
        description:
          - Maximum jobs to be executed at once
        type: int
  description_format:
    description:
      - Override the description format from the template for this invocation only
    type: str
  feature:
    description:
      - Feature label that should be triggered
      - A job template assigned to this feature will be used
    type: str
    version_added: 5.8.0
extends_documentation_fragment:
  - theforeman.foreman.foreman
'''

EXAMPLES = '''

- name: "Run remote command on a single host once"
  theforeman.foreman.job_invocation:
    search_query: "name ^ (foreman.example.com)"
    command: 'ls'
    job_template: "Run Command - SSH Default"
    ssh:
      effective_user: "tester"

- name: "Run ansible command on active hosts once a day"
  theforeman.foreman.job_invocation:
    bookmark: 'active'
    command: 'pwd'
    job_template: "Run Command - Ansible Default"
    recurrence:
      cron_line: "30 2 * * *"
    concurrency_control:
      concurrency_level: 2

- name: "Run the katello_package_install feature to install a package on a single host"
  theforeman.foreman.job_invocation:
    search_query: "name ^ (foreman.example.com)"
    feature: 'katello_package_install'
    inputs: 'package=podman'
'''

RETURN = '''
entity:
  description: Final state of the affected entities grouped by their type.
  returned: success
  type: dict
  contains:
    job_invocations:
      description: List of job invocations
      type: list
      elements: dict
'''

from datetime import datetime, timezone
import re

from ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper import (
    ForemanAnsibleModule,
)

ssh_foreman_spec = {
    'effective_user': dict(),
}

recurrence_foreman_spec = {
    'cron_line': dict(),
    'max_iteration': dict(type='int'),
    'end_time': dict(),
    'purpose': dict(),
}

scheduling_foreman_spec = {
    'start_at': dict(),
    'start_before': dict(),
}

concurrency_control_foreman_spec = {
    'time_span': dict(type='int'),
    'concurrency_level': dict(type='int'),
}


class ForemanJobInvocationModule(ForemanAnsibleModule):
    pass


def _normalize_datetime(value):
    if not value:
        return value

    normalized = value.strip()
    if normalized.endswith(' UTC'):
        normalized = normalized[:-4] + '+0000'
    elif normalized.endswith('Z'):
        normalized = normalized[:-1] + '+0000'
    normalized = re.sub(r'([+-]\d{2}):(\d{2})$', r'\1\2', normalized)

    parsed = None
    for date_format in (
        '%Y-%m-%dT%H:%M:%S.%f%z',
        '%Y-%m-%dT%H:%M:%S%z',
        '%Y-%m-%d %H:%M:%S.%f%z',
        '%Y-%m-%d %H:%M:%S%z',
        '%Y-%m-%dT%H:%M:%S.%f',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%d %H:%M:%S.%f',
        '%Y-%m-%d %H:%M:%S',
    ):
        try:
            parsed = datetime.strptime(normalized, date_format)
            break
        except ValueError:
            pass
    if parsed is None:
        return value
    if parsed.tzinfo:
        parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)
    return parsed.replace(second=0, microsecond=0)


def _normalize_input(value):
    if value is None:
        return value
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


def _render_description(description_format, current, inputs):
    values = {
        'job_category': current.get('job_category'),
        'template_name': current.get('template_name'),
    }
    values.update(inputs)
    return re.sub(r'%{([^}]+)}', lambda match: _normalize_input(values.get(match.group(1), "''")), description_format)


def _recurring_job_matches(desired, current, template_id):
    if current is None or current.get('template_id') != template_id:
        return False

    targeting = current.get('targeting', {})
    if targeting.get('targeting_type') != desired.get('targeting_type'):
        return False
    if 'bookmark' in desired:
        if targeting.get('bookmark_id') != desired['bookmark']['id']:
            return False
    elif targeting.get('search_query') != desired.get('search_query'):
        return False
    if 'randomized_ordering' in desired and targeting.get('randomized_ordering') != desired['randomized_ordering']:
        return False

    if 'execution_timeout_interval' in desired and current.get('execution_timeout_interval') != desired['execution_timeout_interval']:
        return False
    if 'ssh' in desired and current.get('effective_user') != desired['ssh'].get('effective_user'):
        return False
    if 'concurrency_control' in desired:
        for key in ('concurrency_level', 'time_span'):
            if key in desired['concurrency_control'] and current.get(key) != desired['concurrency_control'][key]:
                return False

    current_recurrence = current.get('recurrence', {})
    for key, value in desired['recurrence'].items():
        current_value = current_recurrence.get(key)
        if key == 'end_time':
            value = _normalize_datetime(value)
            current_value = _normalize_datetime(current_value)
        if current_value != value:
            return False

    current_inputs = {}
    for invocation in current.get('pattern_template_invocations', []):
        if invocation.get('template_id') == template_id:
            current_inputs = {
                item['template_input_name']: item.get('value')
                for item in invocation.get('input_values', [])
            }
            break
    for name, value in desired.get('inputs', {}).items():
        current_value = current_inputs.get(name)
        if isinstance(current_value, str) and current_value and set(current_value) == {'*'}:
            continue
        if _normalize_input(current_value) != _normalize_input(value):
            return False

    if 'description_format' in desired:
        desired_description = _render_description(desired['description_format'], current, desired.get('inputs', {}))
        if current.get('description') != desired_description:
            return False

    return True


def _find_active_recurring_logic(module, purpose):
    purpose = purpose.replace('\\', '\\\\').replace('"', '\\"')
    recurring_logics = module.list_resource('recurring_logics', search='purpose="{0}"'.format(purpose))
    active_logics = [logic for logic in recurring_logics if logic.get('state') in ('active', 'disabled')]
    if len(active_logics) > 1:
        module.fail_json(msg='Found multiple active or disabled recurring jobs with purpose {0}'.format(purpose))
    return active_logics[0] if active_logics else None


def _find_recurring_job(module, recurring_logic):
    jobs = module.list_resource('job_invocations', search='recurring_logic.id={0}'.format(recurring_logic['id']))
    if len(jobs) > 1:
        module.fail_json(msg='Found multiple job invocations for recurring logic {0}'.format(recurring_logic['id']))
    if not jobs:
        return None
    return module.show_resource('job_invocations', jobs[0]['id'], params={'include_hosts': False})


def _feature_template_id(module, feature):
    features = [item for item in module.list_resource('remote_execution_features') if item.get('label') == feature]
    if len(features) != 1:
        module.fail_json(msg='Found {0} remote execution features with label {1}'.format(len(features), feature))
    return features[0]['job_template_id']


def main():
    module = ForemanJobInvocationModule(
        foreman_spec=dict(
            search_query=dict(),
            bookmark=dict(type='entity'),
            job_template=dict(type='entity'),
            targeting_type=dict(default='static_query', choices=['static_query', 'dynamic_query']),
            randomized_ordering=dict(type='bool'),
            command=dict(),
            inputs=dict(type='dict'),
            execution_timeout_interval=dict(type='int'),
            ssh=dict(type='dict', options=ssh_foreman_spec),
            recurrence=dict(type='dict', options=recurrence_foreman_spec),
            scheduling=dict(type='dict', options=scheduling_foreman_spec),
            concurrency_control=dict(type='dict', options=concurrency_control_foreman_spec),
            description_format=dict(),
            feature=dict(),
        ),
        required_one_of=[['search_query', 'bookmark'], ['job_template', 'feature']],
        required_if=[
            ['job_template', 'Run Command - SSH Default', ['command']],
            ['job_template', 'Run Command - Ansible Default', ['command']],
        ],
    )

    # command input required by api
    if 'command' in module.foreman_params:
        module.foreman_params['inputs'] = {"command": module.foreman_params.pop('command')}

    with module.api_connection():
        if 'bookmark' in module.foreman_params:
            module.set_entity('bookmark', module.find_resource('bookmarks', search='name="{0}",controller="hosts"'.format(
                module.foreman_params['bookmark']),
                failsafe=False,
            ))
        module.auto_lookup_entities()
        recurrence = module.foreman_params.get('recurrence', {})
        purpose = recurrence.get('purpose')
        current_logic = _find_active_recurring_logic(module, purpose) if purpose else None
        current_job = _find_recurring_job(module, current_logic) if current_logic else None

        if current_logic:
            if 'job_template' in module.foreman_params:
                template_id = module.foreman_params['job_template']['id']
            else:
                template_id = _feature_template_id(module, module.foreman_params['feature'])

            if _recurring_job_matches(module.foreman_params, current_job, template_id):
                module.record_before('job_invocations', current_job)
                module.record_after('job_invocations', current_job)
                module.record_after_full('job_invocations', current_job)
                if current_logic['state'] == 'disabled':
                    module.resource_action('recurring_logics', 'update', {'id': current_logic['id'], 'enabled': True})
                return

            module.resource_action('recurring_logics', 'cancel', {'id': current_logic['id']})

        module.ensure_entity('job_invocations', module.foreman_params, None, state='present')


if __name__ == '__main__':
    main()
