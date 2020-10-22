import py.path
import pytest

from .conftest import TEST_PLAYBOOKS

MODULES_PATH = py.path.local(__file__).realpath() / '..' / '..' / 'plugins' / 'modules'


def find_all_modules():
    for module in MODULES_PATH.listdir(sort=True):
        module = module.basename
        if module.endswith('.py') and not module.startswith('_'):
            yield module.replace('.py', '')


ALL_MODULES = list(find_all_modules())


def _module_file_path(module):
    module_file_name = "{}.py".format(module)
    return MODULES_PATH / module_file_name


def _module_is_tested(module):
    return module in TEST_PLAYBOOKS


@pytest.mark.parametrize('module', ALL_MODULES)
def test_module_is_tested(module):
    assert _module_is_tested(module)
