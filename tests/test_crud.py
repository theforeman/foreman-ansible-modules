import json
import os
import sys

import ansible_runner
import py.path
import pytest
import yaml

MODULES = [
    'activation_key',
    'architecture',
    'auth_source_ldap',
    'bookmark',
    'compute_attribute',
    'compute_profile',
    'compute_resource',
    'content_credential',
    'content_view',
    'content_view_filter',
    'domain',
    'environment',
    'config_group',
    'global_parameter',
    'host',
    'hostgroup',
    'host_collection',
    'installation_medium',
    'job_template',
    'katello_manifest',
    'lifecycle_environment',
    'location',
    'operatingsystem',
    'organization',
    'os_default_template',
    'product',
    'provisioning_template',
    'ptable',
    'realm',
    'redhat_manifest',
    'repository',
    'repository_set',
    'repository_sync',
    'role',
    'search_facts',
    'setting',
    'snapshot',
    'subnet',
    'sync_plan',
    'upload',
    'user',
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


def run_playbook_vcr(tmpdir, module, extra_vars=None, record=False):
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
        limit = '!fixtures'

    # Dump recording parameters to json-file and pass its name by environment
    test_params = {'test_name': module, 'serial': 0, 'record_mode': record_mode}
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

    return run_playbook(module, extra_vars=extra_vars, limit=limit)


def run_playbook(module, extra_vars=None, limit=None):
    # Assemble parameters for playbook call
    os.environ['ANSIBLE_CONFIG'] = os.path.join(os.getcwd(), 'ansible.cfg')
    playbook_path = os.path.join(os.getcwd(), 'tests', 'test_playbooks', '{}.yml'.format(module))
    inventory_path = os.path.join(os.getcwd(), 'tests', 'inventory', 'hosts')
    run = ansible_runner.run(extravars=extra_vars, playbook=playbook_path, limit=limit, verbosity=4, inventory=inventory_path)
    return run


@pytest.mark.parametrize('module', MODULES)
def test_crud(tmpdir, module, record):
    run = run_playbook_vcr(tmpdir, module, record=record)
    assert run.rc == 0
