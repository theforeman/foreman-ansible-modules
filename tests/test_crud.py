import os
import sys

import pytest
try:
    from ansible.module_utils.compat.version import LooseVersion
except ImportError:
    from distutils.version import LooseVersion

from .conftest import TEST_PLAYBOOKS, INVENTORY_PLAYBOOKS, run_playbook, run_playbook_vcr, get_ansible_version, assert_no_warnings

ANSIBLE_SUPPORTS_MODULE_DEFAULTS = LooseVersion(get_ansible_version()) >= LooseVersion('2.12')


@pytest.mark.parametrize('module', TEST_PLAYBOOKS)
def test_crud(tmpdir, module, vcrmode):
    if module in ['module_defaults'] and not ANSIBLE_SUPPORTS_MODULE_DEFAULTS:
        pytest.skip("Module defaults only work with Ansible 2.12+")
    if vcrmode == "live":
        run = run_playbook(module)
    else:
        record = vcrmode == "record"
        run = run_playbook_vcr(tmpdir, module, record=record)
    assert run.rc == 0

    assert_no_warnings(run)


@pytest.mark.parametrize('module', TEST_PLAYBOOKS)
def test_check_mode(tmpdir, module):
    if module in ['subscription_manifest', 'templates_import', 'puppetclasses_import', 'content_rhel_role']:
        pytest.skip("This module does not support check_mode.")
    if module in ['module_defaults'] and not ANSIBLE_SUPPORTS_MODULE_DEFAULTS:
        pytest.skip("Module defaults only work with Ansible 2.12+")
    run = run_playbook_vcr(tmpdir, module, check_mode=True)
    assert run.rc == 0

    assert_no_warnings(run)


@pytest.mark.parametrize('module', INVENTORY_PLAYBOOKS)
def test_inventory(tmpdir, module):
    if sys.version_info < (3, 8) and 'GITHUB_ACTIONS' in os.environ.keys():
        pytest.skip("Inventory tests currently don't work inside a container, but Python {}.{} tests require a container on GHA."
                    .format(sys.version_info.major, sys.version_info.minor))
    inventory = [os.path.join(os.getcwd(), 'tests', 'inventory', inv) for inv in ['hosts', "{}.foreman.yml".format(module)]]
    run = run_playbook(module, inventory=inventory)
    assert run.rc == 0

    assert_no_warnings(run)
