import pytest
import json
from ansible.cli.playbook import PlaybookCLI


MODULES = ['organization', 'product']


def run_playbook(module, record=False, extra_vars=None):
    # Assemble parameters for playbook call
    path = 'test/test_playbooks/{}.yml'.format(module)
    playbook_opts = ['ansible-playbook', path, '--inventory', 'test/inventory/hosts']
    if record:
        # Cassettes that are to be overwritten must be deleted first
        record_mode = 'once'
    else:
        # Never reach out to the internet
        record_mode = 'none'
        # Only run the tests (skip fixtures)
        playbook_opts.extend(['--limit', 'tests'])
    if extra_vars:
        playbook_opts.extend(['--extra-vars', extra_vars])
    # Dump recording parameters to json-file
    test_params = {'test_name': module, 'serial': 0, 'record_mode': record_mode}
    with open('.vcr_params.json', 'w') as params_file:
        json.dump(test_params, params_file)
    # Call the playbook
    cli = PlaybookCLI(playbook_opts)
    cli.parse()
    return cli.run()


@pytest.mark.parametrize('module', MODULES)
def test_crud(module, record):
    assert run_playbook(module, record=record) == 0
