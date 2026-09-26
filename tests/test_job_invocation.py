import sys

import pytest

from plugins.module_utils import foreman_helper

sys.modules['ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper'] = foreman_helper

from plugins.modules.job_invocation import _recurring_job_matches  # noqa: E402


@pytest.fixture
def desired_job():
    return {
        'targeting_type': 'dynamic_query',
        'search_query': 'name ~ .',
        'inputs': {'command': 'dnf upgrade -y'},
        'execution_timeout_interval': 90,
        'ssh': {'effective_user': 'root'},
        'concurrency_control': {'concurrency_level': 2},
        'recurrence': {
            'cron_line': '05 12 * * *',
            'max_iteration': 10,
            'end_time': '2030-01-02T12:00:00Z',
            'purpose': 'System update',
        },
    }


@pytest.fixture
def current_job():
    return {
        'template_id': 233,
        'template_name': 'Run Command - Ansible Default',
        'job_category': 'Ansible Commands',
        'description': 'Run dnf upgrade -y',
        'effective_user': 'root',
        'execution_timeout_interval': 90,
        'concurrency_level': 2,
        'targeting': {
            'targeting_type': 'dynamic_query',
            'search_query': 'name ~ .',
            'bookmark_id': None,
            'randomized_ordering': None,
        },
        'recurrence': {
            'cron_line': '05 12 * * *',
            'max_iteration': 10,
            'end_time': '2030-01-02 12:00:00 UTC',
            'purpose': 'System update',
        },
        'pattern_template_invocations': [{
            'template_id': 233,
            'input_values': [{
                'template_input_name': 'command',
                'value': 'dnf upgrade -y',
            }],
        }],
    }


def test_matching_recurring_job_is_idempotent(desired_job, current_job):
    assert _recurring_job_matches(desired_job, current_job, 233)


@pytest.mark.parametrize(('path', 'value'), [
    (('recurrence', 'cron_line'), '10 12 * * *'),
    (('inputs', 'command'), 'dnf upgrade -y --refresh'),
    (('concurrency_control', 'concurrency_level'), 3),
    (('ssh', 'effective_user'), 'foreman'),
])
def test_changed_managed_parameter_replaces_recurring_job(desired_job, current_job, path, value):
    desired_job[path[0]][path[1]] = value

    assert not _recurring_job_matches(desired_job, current_job, 233)


def test_changed_targeting_replaces_recurring_job(desired_job, current_job):
    desired_job['search_query'] = 'name ~ example.com'

    assert not _recurring_job_matches(desired_job, current_job, 233)


def test_changed_template_replaces_recurring_job(desired_job, current_job):
    assert not _recurring_job_matches(desired_job, current_job, 189)


def test_changed_description_format_replaces_recurring_job(desired_job, current_job):
    desired_job['description_format'] = 'Upgrade using %{command}'

    assert not _recurring_job_matches(desired_job, current_job, 233)


def test_matching_description_format_is_idempotent(desired_job, current_job):
    desired_job['description_format'] = 'Run %{command}'

    assert _recurring_job_matches(desired_job, current_job, 233)


def test_hidden_input_is_not_rotated_on_every_run(desired_job, current_job):
    current_job['pattern_template_invocations'][0]['input_values'][0]['value'] = '*****'

    assert _recurring_job_matches(desired_job, current_job, 233)


def test_bookmark_is_compared_by_id(desired_job, current_job):
    desired_job.pop('search_query')
    desired_job['bookmark'] = {'id': 10, 'name': 'ok hosts'}
    current_job['targeting']['bookmark_id'] = 10
    current_job['targeting']['search_query'] = 'resolved bookmark query'

    assert _recurring_job_matches(desired_job, current_job, 233)
