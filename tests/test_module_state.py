import pytest

from .conftest import TEST_PLAYBOOKS
from .utils import ALL_MODULES, MODULES_PATH


def _module_file_path(module):
    module_file_name = "{}.py".format(module)
    return MODULES_PATH / module_file_name


def _module_is_tested(module):
    return module in TEST_PLAYBOOKS


@pytest.mark.parametrize('module', ALL_MODULES)
def test_module_is_tested(module):
    assert _module_is_tested(module)
