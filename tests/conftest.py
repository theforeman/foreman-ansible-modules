import pytest
import py.path


TEST_PLAYBOOKS_PATH = py.path.local(__file__).realpath() / '..' / 'test_playbooks'


def find_all_test_playbooks():
    for playbook in TEST_PLAYBOOKS_PATH.listdir(sort=True):
        playbook = playbook.basename
        if playbook.endswith('.yml'):
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
