import ast
import py.path
import pytest
import six

from .conftest import TEST_PLAYBOOKS

if six.PY2:
    ast_try = ast.TryExcept
else:
    ast_try = ast.Try

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
    if module == 'subscription_manifest':
        module = 'katello_manifest'
    return module in TEST_PLAYBOOKS


def _module_framework(module):
    module_file_path = _module_file_path(module)
    with module_file_path.open() as module_file:
        module_ast = ast.parse(module_file.read())
    return _module_framework_from_body(module_ast.body) or 'unknown'


def _module_framework_from_body(body):
    framework = None
    for entry in body:
        if isinstance(entry, ast.ImportFrom):
            if entry.module == 'ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper' and not framework:
                framework = 'apypie'
        elif isinstance(entry, ast_try) and not framework:
            framework = _module_framework_from_body(entry.body)
    return framework


@pytest.mark.parametrize('module', ALL_MODULES)
def test_module_framework(module):
    module_framework = _module_framework(module)
    assert (module_framework == 'apypie' or module == 'redhat_manifest')


@pytest.mark.parametrize('module', ALL_MODULES)
def test_module_state(module):
    assert _module_is_tested(module)
