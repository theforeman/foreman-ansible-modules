import yaml

from tests.utils import ALL_MODULES

META_RUNTIME = 'meta/runtime.yml'
EXCLUDED_MODULES = ['redhat_manifest']


class IndentedListDumper(yaml.SafeDumper):

    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)


with open(META_RUNTIME) as runtime_file:
    runtime = yaml.safe_load(runtime_file)

runtime['action_groups']['foreman'] = sorted(set(ALL_MODULES) - set(EXCLUDED_MODULES))

with open(META_RUNTIME, 'w') as runtime_file:
    yaml.dump(runtime, runtime_file, Dumper=IndentedListDumper, default_flow_style=False, explicit_start=True)
