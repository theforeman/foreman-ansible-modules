import pytest
import os
import tempfile
import json
from ansible.utils.display import Display
import __main__
__main__.display = Display()
from ansible.cli.playbook import PlaybookCLI


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
]


def run_playbook_vcr(module, extra_vars=None, extra_args=None, record=False):
    # Assemble extra parameters for playbook call
    if extra_args is None:
        extra_args = []
    if record:
        # Cassettes that are to be overwritten must be deleted first
        record_mode = 'once'
        extra_args.extend(['--extra-vars', 'recording=true'])
    else:
        # Never reach out to the internet
        record_mode = 'none'
        # Only run the tests (skip fixtures)
        extra_args.extend(['--limit', '!fixtures'])

    # Dump recording parameters to json-file and pass its name by environment
    test_params = {'test_name': module, 'serial': 0, 'record_mode': record_mode}
    with tempfile.NamedTemporaryFile('w', suffix='json', prefix='fam-vcr-') as params_file:
        json.dump(test_params, params_file.file)
        params_file.file.close()
        os.environ['FAM_TEST_VCR_PARAMS_FILE'] = params_file.name
        return run_playbook(module, extra_vars=extra_vars, extra_args=extra_args)


def run_playbook(module, extra_vars=None, extra_args=None):
    # Assemble parameters for playbook call
    path = 'test/test_playbooks/{}.yml'.format(module)
    playbook_opts = ['ansible-playbook', '-vvvv', path]
    if extra_vars:
        playbook_opts.extend(['--extra-vars', extra_vars])
    if extra_args:
        playbook_opts.extend(extra_args)

    cli = PlaybookCLI(playbook_opts)
    cli.parse()
    return cli.run()


@pytest.mark.parametrize('module', MODULES)
def test_crud(module, record):
    assert run_playbook_vcr(module, record=record) == 0
