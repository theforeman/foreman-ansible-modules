import importlib
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parents[1] / 'build' / 'collections'))
ensure_ansible_roles = importlib.import_module(
    'ansible_collections.theforeman.foreman.plugins.modules.host'
).ensure_ansible_roles


class FakeModule:
    def __init__(self, host_roles=None, hostgroup_roles=None):
        self.host_roles = host_roles or []
        self.hostgroup_roles = hostgroup_roles or []
        self.calls = []

    def resource_action(self, resource, action, params, **kwargs):
        self.calls.append((resource, action, params, kwargs))
        if action == 'ansible_roles':
            if resource == 'hostgroups':
                return [{'id': role_id} for role_id in self.hostgroup_roles]
            return [{'id': role_id} for role_id in self.host_roles]
        return {}


def test_ensure_ansible_roles_is_idempotent_with_inherited_roles():
    module = FakeModule(host_roles=[1, 2], hostgroup_roles=[1])

    ensure_ansible_roles(
        module,
        {'id': 10, 'hostgroup_id': 20},
        {'id': 10},
        [{'id': 2}],
    )

    assert [call[1] for call in module.calls] == ['ansible_roles', 'ansible_roles']


def test_ensure_ansible_roles_updates_only_direct_roles():
    module = FakeModule(host_roles=[1, 2], hostgroup_roles=[1])

    ensure_ansible_roles(
        module,
        {'id': 10, 'hostgroup_id': 20},
        {'id': 10},
        [{'id': 3}],
    )

    assert module.calls[-1] == (
        'hosts',
        'assign_ansible_roles',
        {'id': 10, 'ansible_role_ids': [3]},
        {},
    )


def test_ensure_ansible_roles_handles_host_without_hostgroup():
    module = FakeModule(host_roles=[2])

    ensure_ansible_roles(
        module,
        {'id': 10, 'hostgroup_id': None},
        {'id': 10},
        [],
    )

    assert [call[0] for call in module.calls] == ['hosts', 'hosts']
    assert module.calls[-1][1] == 'assign_ansible_roles'
    assert module.calls[-1][2] == {'id': 10, 'ansible_role_ids': []}


def test_ensure_ansible_roles_assigns_roles_to_new_host():
    module = FakeModule(hostgroup_roles=[1])

    ensure_ansible_roles(
        module,
        {'id': 10, 'hostgroup_id': 20},
        None,
        [{'id': 2}],
    )

    assert module.calls[-1][1] == 'assign_ansible_roles'
    assert module.calls[-1][2] == {'id': 10, 'ansible_role_ids': [2]}
