import pytest
from ansible.cli.playbook import PlaybookCLI


MODULES = ['organization', 'product', 'realm']


def run_playbook(path, extra_vars=""):
    cli = PlaybookCLI(['ansible-playbook', path, "--extra-vars", extra_vars])
    cli.parse()
    return cli.run()


@pytest.mark.parametrize("module", MODULES)
def test_crud(module):
    assert run_playbook("test/test_playbooks/{}.yml".format(module)) == 0
