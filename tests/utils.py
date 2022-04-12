import py.path


MODULES_PATH = py.path.local(__file__).realpath() / '..' / '..' / 'plugins' / 'modules'


def find_all_modules():
    for module in MODULES_PATH.listdir(sort=True):
        module = module.basename
        if module.endswith('.py') and not module.startswith('_'):
            yield module.replace('.py', '')


ALL_MODULES = list(find_all_modules())
