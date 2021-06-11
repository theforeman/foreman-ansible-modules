import distutils.version
import os
import sys

import pkg_resources
import pytest

from .conftest import TEST_PLAYBOOKS, INVENTORY_PLAYBOOKS, run_playbook, run_playbook_vcr

IGNORED_WARNINGS = [
    "Activation Key 'Test Activation Key Copy' already exists.",
]

if sys.version_info[0] == 2:
    for envvar in os.environ.keys():
        try:
            os.environ[envvar] = os.environ[envvar].decode('utf-8').encode('ascii', 'ignore')
        except UnicodeError:
            os.environ.pop(envvar)


@pytest.mark.parametrize('module', TEST_PLAYBOOKS)
def test_crud(tmpdir, module, vcrmode):
    if vcrmode == "live":
        run = run_playbook(module)
    else:
        record = vcrmode == "record"
        run = run_playbook_vcr(tmpdir, module, record=record)
    assert run.rc == 0

    _assert_no_warnings(run)


@pytest.mark.parametrize('module', TEST_PLAYBOOKS)
def test_check_mode(tmpdir, module):
    if module in ['subscription_manifest', 'templates_import', 'puppetclasses_import', 'content_rhel_role']:
        pytest.skip("This module does not support check_mode.")
    run = run_playbook_vcr(tmpdir, module, check_mode=True)
    assert run.rc == 0

    _assert_no_warnings(run)


@pytest.mark.parametrize('module', INVENTORY_PLAYBOOKS)
def test_inventory(tmpdir, module):
    ansible_version = None
    for ansible_name in ['ansible', 'ansible-base', 'ansible-core']:
        try:
            ansible_version = pkg_resources.get_distribution(ansible_name).version
        except pkg_resources.DistributionNotFound:
            pass
    if ansible_version is None:
        pytest.skip("Couldn't figure out Ansible version?!")
    if distutils.version.LooseVersion(ansible_version) < distutils.version.LooseVersion('2.9'):
        pytest.skip("This module should not be tested on Ansible before 2.9")
    inventory = [os.path.join(os.getcwd(), 'tests', 'inventory', inv) for inv in ['hosts', "{}.foreman.yml".format(module)]]
    run = run_playbook(module, inventory=inventory)
    assert run.rc == 0

    _assert_no_warnings(run)


def _assert_no_warnings(run):
    for event in run.events:
        # check for play level warnings
        assert not event.get('event_data', {}).get('warning', False)

        # check for task level warnings
        event_warnings = [warning for warning in event.get('event_data', {}).get('res', {}).get('warnings', []) if warning not in IGNORED_WARNINGS]
        assert [] == event_warnings, str(event_warnings)
