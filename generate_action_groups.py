import yaml

from tests.utils import ALL_MODULES

META_RUNTIME = 'meta/runtime.yml'
EXCLUDED_MODULES = ['redhat_manifest']

with open(META_RUNTIME) as runtime_file:
    runtime = yaml.safe_load(runtime_file)

runtime['action_groups']['foreman'] = sorted(set(ALL_MODULES) - set(EXCLUDED_MODULES))

with open(META_RUNTIME, 'w') as runtime_file:
    yaml.safe_dump(runtime, runtime_file,  default_flow_style=False, explicit_start=True)
