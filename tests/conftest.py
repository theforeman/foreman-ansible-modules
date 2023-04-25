import json
import os

import ansible_runner
import pkg_resources
import pytest
import py.path
import yaml


TEST_PLAYBOOKS_PATH = py.path.local(__file__).realpath() / '..' / 'test_playbooks'


def find_all_test_playbooks():
    excluded_playbooks = os.environ.get('FAM_TEST_EXCLUDE_PLAYBOOKS', '').split(',')
    for playbook in TEST_PLAYBOOKS_PATH.listdir(sort=True):
        playbook = playbook.basename
        if playbook.endswith('.yml') and playbook not in excluded_playbooks:
            yield playbook.replace('.yml', '')


ALL_TEST_PLAYBOOKS = list(find_all_test_playbooks())
TEST_PLAYBOOKS = sorted([playbook for playbook in ALL_TEST_PLAYBOOKS if not playbook.startswith('inventory_plugin')])
INVENTORY_PLAYBOOKS = sorted(set(ALL_TEST_PLAYBOOKS) - set(TEST_PLAYBOOKS))


def pytest_addoption(parser):
    parser.addoption(
        "--vcrmode",
        action="store",
        default="replay",
        choices=["replay", "record", "live"],
        help="mode for vcr recording; one of ['replay', 'record', 'live']",
    )


@pytest.fixture
def vcrmode(request):
    return request.config.getoption("vcrmode")


def get_foreman_url():
    server_yml = py.path.local(__file__).realpath() / '..' / 'test_playbooks/vars/server.yml'
    with open(server_yml.strpath) as server_yml_file:
        server_yml_content = yaml.safe_load(server_yml_file)

    return server_yml_content['foreman_server_url']


def run_playbook(module, extra_vars=None, limit=None, inventory=None, check_mode=False, extra_env=None):
    # Assemble parameters for playbook call
    os.environ['ANSIBLE_CONFIG'] = os.path.join(os.getcwd(), 'ansible.cfg')
    if extra_env is not None:
        os.environ.update(extra_env)
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


def run_playbook_vcr(tmpdir, module, extra_vars=None, limit=None, inventory=None, record=False, check_mode=False, extra_env=None):
    if extra_vars is None:
        extra_vars = {}
    if extra_env is None:
        extra_env = {}
    if record:
        # Cassettes that are to be overwritten must be deleted first
        record_mode = 'once'
        extra_vars['recording'] = True
    else:
        # Never reach out to the internet
        record_mode = 'none'
        if limit is None:
            # Only run the tests (skip fixtures)
            limit = 'tests:container'

    # Dump recording parameters to json-file and pass its name by environment
    test_params = {'test_name': module, 'serial': 0, 'record_mode': record_mode, 'check_mode': check_mode}
    params_file = tmpdir.join('{}_test_params.json'.format(module))
    params_file.write(json.dumps(test_params), ensure=True)
    extra_env['FAM_TEST_VCR_PARAMS_FILE'] = params_file.strpath

    cache_dir = tmpdir.join('cache')
    cache_dir.ensure(dir=True)
    extra_env['XDG_CACHE_HOME'] = cache_dir.strpath
    apypie_cache_folder = get_foreman_url().replace(':', '_').replace('/', '_')
    json_cache = cache_dir / 'apypie' / apypie_cache_folder / 'v2/default.json'
    json_cache.ensure()
    apidoc = 'apidoc/{}.json'.format(module)
    fixture_dir = py.path.local(__file__).realpath() / '..' / 'fixtures'
    fixture_dir.join(apidoc).copy(json_cache)

    return run_playbook(module, extra_vars=extra_vars, limit=limit, inventory=inventory, check_mode=check_mode, extra_env=extra_env)


def get_ansible_version():
    ansible_version = '2.14.0'
    for ansible_name in ['ansible', 'ansible-base', 'ansible-core']:
        try:
            ansible_version = pkg_resources.get_distribution(ansible_name).version
        except pkg_resources.DistributionNotFound:
            pass
    return ansible_version
