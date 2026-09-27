import importlib
import sys
from pathlib import Path

from ansible.inventory.data import InventoryData


sys.path.insert(0, str(Path(__file__).parents[1] / 'build' / 'collections'))
InventoryModule = importlib.import_module(
    'ansible_collections.theforeman.foreman.plugins.inventory.foreman'
).InventoryModule


class FakeResponse:
    status_code = 200

    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self.payload


class FakeSession:
    def __init__(self):
        self.calls = []

    def post(self, url, json=None):
        self.calls.append((url, json))
        hostvars = {}
        for host_id in json['host_ids']:
            hostvars['host%s.example.com' % host_id] = {
                'foreman_ansible_roles': ['namespace.role%s' % host_id],
                'ansible_password': 'must-not-be-cached',
            }
        return FakeResponse({'_meta': {'hostvars': hostvars}})


def test_get_ansible_roles_is_batched_and_only_caches_roles(monkeypatch):
    inventory = InventoryModule()
    inventory.foreman_url = 'https://foreman.example.com'
    inventory.cache_key = 'cache-key'
    inventory._cache = {}
    inventory.use_cache = False
    session = FakeSession()
    monkeypatch.setattr(inventory, 'get_option', lambda option: {'batch_size': 2}[option])
    monkeypatch.setattr(inventory, '_get_session', lambda: session)

    result = inventory._get_ansible_roles([
        {'id': 1, 'name': 'host1.example.com'},
        None,
        {'id': 2, 'name': 'host2.example.com'},
        {'id': 3, 'name': 'host3.example.com'},
    ])

    assert [call[1] for call in session.calls] == [
        {'host_ids': [1, 2]},
        {'host_ids': [3]},
    ]
    assert result == {
        'host1.example.com': ['namespace.role1'],
        'host2.example.com': ['namespace.role2'],
        'host3.example.com': ['namespace.role3'],
    }
    assert 'must-not-be-cached' not in str(inventory._cache)


def test_get_ansible_roles_uses_inventory_cache(monkeypatch):
    inventory = InventoryModule()
    inventory.foreman_url = 'https://foreman.example.com'
    inventory.cache_key = 'cache-key'
    inventory.use_cache = True
    url = 'https://foreman.example.com/ansible/api/v2/ansible_inventories/hosts?host_ids=1'
    inventory._cache = {
        'cache-key': {
            url: {'host1.example.com': ['namespace.cached']},
        },
    }
    session = FakeSession()
    monkeypatch.setattr(inventory, 'get_option', lambda option: {'batch_size': 250}[option])
    monkeypatch.setattr(inventory, '_get_session', lambda: session)

    result = inventory._get_ansible_roles([{'id': 1, 'name': 'host1.example.com'}])

    assert result == {'host1.example.com': ['namespace.cached']}
    assert session.calls == []


def test_host_api_exposes_ansible_roles_as_host_variable(monkeypatch):
    inventory = InventoryModule()
    inventory.inventory = InventoryData()
    inventory._cache = {}
    options = {
        'compose': {},
        'group_prefix': 'foreman_',
        'groups': {},
        'hostnames': ['name'],
        'keyed_groups': [],
        'legacy_hostvars': False,
        'strict': False,
        'vars_prefix': 'foreman_',
        'want_ansible_roles': True,
        'want_facts': False,
        'want_hostcollections': False,
        'want_params': False,
    }
    hosts = [{'id': 1, 'name': 'host1.example.com'}]
    monkeypatch.setattr(inventory, 'get_option', lambda option: options[option])
    monkeypatch.setattr(inventory, '_get_hosts', lambda: hosts)
    monkeypatch.setattr(inventory, '_get_ansible_roles', lambda value: {
        'host1.example.com': ['namespace.direct', 'namespace.inherited'],
    })
    monkeypatch.setattr(inventory, '_get_hostname', lambda host, hostnames, strict=False: host['name'])
    monkeypatch.setattr(inventory, '_set_composite_vars', lambda *args: None)
    monkeypatch.setattr(inventory, '_add_host_to_composed_groups', lambda *args: None)
    monkeypatch.setattr(inventory, '_add_host_to_keyed_groups', lambda *args: None)

    inventory._populate_host_api()

    hostvars = inventory.inventory.get_host('host1.example.com').get_vars()
    assert hostvars['foreman_ansible_roles'] == ['namespace.direct', 'namespace.inherited']


def test_report_api_exposes_ansible_roles_as_host_variable(monkeypatch):
    inventory = InventoryModule()
    inventory.inventory = InventoryData()
    inventory._cache = {}
    inventory.want_hostcollections = False
    options = {
        'compose': {},
        'group_prefix': 'foreman_',
        'groups': {},
        'hostnames': ['name'],
        'keyed_groups': [],
        'legacy_hostvars': False,
        'strict': False,
        'vars_prefix': 'foreman_',
        'want_ansible_roles': True,
        'want_facts': False,
        'want_hostcollections': False,
        'want_params': False,
    }
    hosts = [{'id': 1, 'name': 'host1.example.com'}]
    monkeypatch.setattr(inventory, 'get_option', lambda option: options[option])
    monkeypatch.setattr(inventory, '_post_request', lambda: hosts)
    monkeypatch.setattr(inventory, '_get_ansible_roles', lambda value: {
        'host1.example.com': ['namespace.direct', 'namespace.inherited'],
    })
    monkeypatch.setattr(inventory, '_get_hostname', lambda host, hostnames, strict=False: host['name'])
    monkeypatch.setattr(inventory, '_set_composite_vars', lambda *args: None)
    monkeypatch.setattr(inventory, '_add_host_to_composed_groups', lambda *args: None)
    monkeypatch.setattr(inventory, '_add_host_to_keyed_groups', lambda *args: None)

    inventory._populate_report_api()

    hostvars = inventory.inventory.get_host('host1.example.com').get_vars()
    assert hostvars['foreman_ansible_roles'] == ['namespace.direct', 'namespace.inherited']
