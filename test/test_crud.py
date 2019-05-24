import pytest
import os
import sys
import tempfile
import json
import ansible_runner

MODULES = [
    'activation_key',
    'bookmark',
    'compute_profile',
    'compute_resource',
    'content_credential',
    'content_view',
    'content_view_filter',
    'domain',
    'environment',
    'global_parameter',
    'host',
    'installation_medium',
    'job_template',
    'lifecycle_environment',
    'location',
    'operating_system',
    'organization',
    'os_default_template',
    'product',
    'provisioning_template',
    'ptable',
    'redhat_manifest',
    'repository',
    'repository_set',
    'repository_sync',
    'search_facts',
    'setting',
    'subnet',
    'sync_plan',
    'upload',
    'host_collection',
]


if sys.version_info[0] == 2:
    for envvar in os.environ.keys():
        try:
            os.environ[envvar] = os.environ[envvar].decode('utf-8').encode('ascii', 'ignore')
        except UnicodeError:
            os.environ.pop(envvar)


def run_playbook_vcr(module, extra_vars=None, record=False):
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
    with tempfile.NamedTemporaryFile('w', suffix='json', prefix='fam-vcr-') as params_file:
        json.dump(test_params, params_file.file)
        params_file.file.close()
        os.environ['FAM_TEST_VCR_PARAMS_FILE'] = params_file.name
        return run_playbook(module, extra_vars=extra_vars, limit=limit)


def run_playbook(module, extra_vars=None, limit=None):
    # Assemble parameters for playbook call
    os.environ['ANSIBLE_CONFIG'] = os.path.join(os.getcwd(), 'ansible.cfg')
    playbook_path = os.path.join(os.getcwd(), 'test', 'test_playbooks', '{}.yml'.format(module))
    inventory_path = os.path.join(os.getcwd(), 'test', 'inventory', 'hosts')
    run = ansible_runner.run(extravars=extra_vars, playbook=playbook_path, limit=limit, verbosity=4, inventory=inventory_path)
    return run


@pytest.mark.parametrize('module', MODULES)
def test_crud(module, record):
    run = run_playbook_vcr(module, record=record)
    print(run.stdout.read())
    assert run.rc == 0
