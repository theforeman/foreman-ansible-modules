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

    def __init__(self, text):
        self.text = text

    def raise_for_status(self):
        pass


class FakeSession:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def get(self, url, verify=None):
        self.calls.append((url, verify))
        return self.response


def test_get_puppetclass_parameters_only_caches_classes(monkeypatch):
    inventory = InventoryModule()
    inventory.foreman_url = 'https://foreman.example.com'
    inventory.cache_key = 'cache-key'
    inventory._cache = {}
    inventory.use_cache = False
    session = FakeSession(FakeResponse('''---
classes:
  ntp:
    servers:
      - ntp1.example.com
parameters:
  secret: must-not-be-cached
'''))
    monkeypatch.setattr(inventory, 'get_option', lambda option: {'validate_certs': False}[option])
    monkeypatch.setattr(inventory, '_get_session', lambda: session)

    result = inventory._get_puppetclass_parameters('host1.example.com')

    assert session.calls == [
        ('https://foreman.example.com/foreman_puppet/node/host1.example.com.yml', False),
    ]
    assert result == {'ntp': {'servers': ['ntp1.example.com']}}
    assert 'must-not-be-cached' not in str(inventory._cache)


def test_get_puppetclass_parameters_uses_inventory_cache(monkeypatch):
    inventory = InventoryModule()
    inventory.foreman_url = 'https://foreman.example.com'
    inventory.cache_key = 'cache-key'
    inventory.use_cache = True
    url = 'https://foreman.example.com/foreman_puppet/node/host1.example.com.yml'
    inventory._cache = {
        'cache-key': {
            url: {'ntp': {'servers': ['cached.example.com']}},
        },
    }
    session = FakeSession(FakeResponse(''))
    monkeypatch.setattr(inventory, '_get_session', lambda: session)

    result = inventory._get_puppetclass_parameters('host1.example.com')

    assert result == {'ntp': {'servers': ['cached.example.com']}}
    assert session.calls == []


def _inventory_options():
    return {
        'compose': {},
        'group_prefix': 'foreman_',
        'groups': {},
        'hostnames': ['name'],
        'keyed_groups': [],
        'legacy_hostvars': False,
        'strict': False,
        'vars_prefix': 'foreman_',
        'want_facts': False,
        'want_hostcollections': False,
        'want_params': False,
        'want_puppetclass_params': True,
    }


def _prepare_inventory(monkeypatch):
    inventory = InventoryModule()
    inventory.inventory = InventoryData()
    inventory._cache = {}
    monkeypatch.setattr(inventory, 'get_option', lambda option: _inventory_options()[option])
    monkeypatch.setattr(inventory, '_get_hostname', lambda host, hostnames, strict=False: host['name'])
    monkeypatch.setattr(inventory, '_get_puppetclass_parameters', lambda host_name: {
        'ntp': {'servers': ['ntp1.example.com']},
    })
    monkeypatch.setattr(inventory, '_set_composite_vars', lambda *args: None)
    monkeypatch.setattr(inventory, '_add_host_to_composed_groups', lambda *args: None)
    monkeypatch.setattr(inventory, '_add_host_to_keyed_groups', lambda *args: None)
    return inventory


def test_host_api_exposes_puppetclass_parameters_as_host_variable(monkeypatch):
    inventory = _prepare_inventory(monkeypatch)
    hosts = [{'id': 1, 'name': 'host1.example.com'}]
    monkeypatch.setattr(inventory, '_get_hosts', lambda: hosts)

    inventory._populate_host_api()

    hostvars = inventory.inventory.get_host('host1.example.com').get_vars()
    assert hostvars['foreman_puppetclass_parameters'] == {
        'ntp': {'servers': ['ntp1.example.com']},
    }


def test_report_api_exposes_puppetclass_parameters_as_host_variable(monkeypatch):
    inventory = _prepare_inventory(monkeypatch)
    inventory.want_hostcollections = False
    hosts = [{'id': 1, 'name': 'host1.example.com'}]
    monkeypatch.setattr(inventory, '_post_request', lambda: hosts)

    inventory._populate_report_api()

    hostvars = inventory.inventory.get_host('host1.example.com').get_vars()
    assert hostvars['foreman_puppetclass_parameters'] == {
        'ntp': {'servers': ['ntp1.example.com']},
    }
