import distutils.version
import json
import os
import sys

import ansible_runner
import pkg_resources
import py.path
import pytest
import yaml

from .conftest import TEST_PLAYBOOKS, INVENTORY_PLAYBOOKS

IGNORED_WARNINGS = [
    "Activation Key 'Test Activation Key Copy' already exists.",
]

if sys.version_info[0] == 2:
    for envvar in os.environ.keys():
        try:
            os.environ[envvar] = os.environ[envvar].decode('utf-8').encode('ascii', 'ignore')
        except UnicodeError:
            os.environ.pop(envvar)


def get_foreman_url():
    server_yml = py.path.local(__file__).realpath() / '..' / 'test_playbooks/vars/server.yml'
    with open(server_yml.strpath) as server_yml_file:
        server_yml_content = yaml.safe_load(server_yml_file)

    return server_yml_content['foreman_server_url']


def run_playbook_vcr(tmpdir, module, extra_vars=None, inventory=None, record=False, check_mode=False):
    if extra_vars is None:
        extra_vars = {}
    limit = None
    if record:
        # Cassettes that are to be overwritten must be deleted first
        record_mode = 'once'
        extra_vars['recording'] = True
    else:
        # Never reach out to the internet
        record_mode = 'none'
        # Only run the tests (skip fixtures)
        limit = 'tests:container'

    # Dump recording parameters to json-file and pass its name by environment
    test_params = {'test_name': module, 'serial': 0, 'record_mode': record_mode, 'check_mode': check_mode}
    params_file = tmpdir.join('{}_test_params.json'.format(module))
    params_file.write(json.dumps(test_params), ensure=True)
    os.environ['FAM_TEST_VCR_PARAMS_FILE'] = params_file.strpath

    cache_dir = tmpdir.join('cache')
    cache_dir.ensure(dir=True)
    os.environ['XDG_CACHE_HOME'] = cache_dir.strpath
    apypie_cache_folder = get_foreman_url().replace(':', '_').replace('/', '_')
    json_cache = cache_dir / 'apypie' / apypie_cache_folder / 'v2/default.json'
    json_cache.ensure()
    apidoc = 'apidoc/{}.json'.format(module)
    fixture_dir = py.path.local(__file__).realpath() / '..' / 'fixtures'
    fixture_dir.join(apidoc).copy(json_cache)

    return run_playbook(module, extra_vars=extra_vars, limit=limit, inventory=inventory, check_mode=check_mode)


def run_playbook(module, extra_vars=None, limit=None, inventory=None, check_mode=False):
    # Assemble parameters for playbook call
    os.environ['ANSIBLE_CONFIG'] = os.path.join(os.getcwd(), 'ansible.cfg')
    kwargs = {}
    kwargs['playbook'] = os.path.join(os.getcwd(), 'tests', 'test_playbooks', '{}.yml'.format(module))
    if inventory is None:
        inventory = os.path.join(os.getcwd(), 'tests', 'inventory', 'hosts')
    kwargs['inventory'] = inventory
    kwargs['verbosity'] = 4
    if extra_vars:
        kwargs['extravars'] = extra_vars
    if limit:
        kwargs['limit'] = limit
    if check_mode:
        kwargs['cmdline'] = "--check"
    return ansible_runner.run(**kwargs)


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
    if module in ['subscription_manifest', 'templates_import', 'puppetclasses_import']:
        pytest.skip("This module does not support check_mode.")
    run = run_playbook_vcr(tmpdir, module, check_mode=True)
    assert run.rc == 0

    _assert_no_warnings(run)


@pytest.mark.parametrize('module', INVENTORY_PLAYBOOKS)
def test_inventory(tmpdir, module):
    try:
        ansible_version = pkg_resources.get_distribution('ansible').version
    except pkg_resources.DistributionNotFound:
        ansible_version = pkg_resources.get_distribution('ansible-base').version
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
