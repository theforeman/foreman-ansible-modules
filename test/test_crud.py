import pytest
import os
import tempfile
import json
from ansible.cli.playbook import PlaybookCLI


MODULES = [
    'compute_profile',
    'global_parameter',
    'location',
    'lifecycle_environment',
    'operating_system',
    'organization',
    'product',
    'repository',
    'sync_plan',
]


def run_playbook_vcr(module, extra_vars=None, extra_args=None, record=False):
    # Assemble extra parameters for playbook call
    if extra_args is None:
        extra_args = []
    extra_args.extend(['--inventory', 'test/inventory/hosts'])
    if record:
        # Cassettes that are to be overwritten must be deleted first
        record_mode = 'once'
    else:
        # Never reach out to the internet
        record_mode = 'none'
        # Only run the tests (skip fixtures)
        extra_args.extend(['--limit', 'tests'])

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
    playbook_opts = ['ansible-playbook', path]
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
