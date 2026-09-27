import importlib
import sys
from pathlib import Path

from ansible.plugins.inventory import BaseInventoryPlugin


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
    def __init__(self, payload):
        self.payload = payload
        self.calls = 0

    def get(self, url, params=None, verify=None):
        self.calls += 1
        return FakeResponse(self.payload)


class FakeReportSession:
    def __init__(self, payload):
        self.payload = payload
        self.calls = 0

    def post(self, url, json=None):
        self.calls += 1
        return FakeResponse({'data_url': 'ansible/inventory/1'})

    def get(self, url):
        self.calls += 1
        return FakeResponse(self.payload)


def prepare_inventory(monkeypatch, cache, session, url):
    inventory = InventoryModule()
    options = {
        'batch_size': 250,
        'cache': True,
        'max_timeout': 600,
        'poll_interval': 10,
        'report': None,
        'url': 'https://foreman.example.com',
        'validate_certs': True,
    }

    monkeypatch.setattr(BaseInventoryPlugin, 'parse', lambda self, inventory, loader, path: None)
    monkeypatch.setattr(inventory, 'load_cache_plugin', lambda: setattr(inventory, '_cache', cache))
    monkeypatch.setattr(inventory, '_read_config_data', lambda path: None)
    monkeypatch.setattr(inventory, 'get_cache_key', lambda path: 'cache-key')
    monkeypatch.setattr(inventory, 'get_option', lambda option: options[option])
    monkeypatch.setattr(inventory, '_get_session', lambda: session)
    monkeypatch.setattr(inventory, '_populate', lambda: inventory._get_json(url))

    return inventory


def test_refresh_inventory_updates_persistent_cache(monkeypatch):
    url = 'https://foreman.example.com/api/v2/hosts'
    old_hosts = [{'id': 1, 'name': 'old.example.com'}]
    new_hosts = [{'id': 2, 'name': 'new.example.com'}]
    cache = {'cache-key': {url: old_hosts}}
    session = FakeSession({'results': new_hosts, 'subtotal': 1})
    inventory = prepare_inventory(monkeypatch, cache, session, url)

    inventory.parse(None, None, 'inventory.foreman.yml', cache=False)

    assert session.calls == 1
    assert cache == {'cache-key': {url: new_hosts}}


def test_normal_inventory_parse_uses_cache(monkeypatch):
    url = 'https://foreman.example.com/api/v2/hosts'
    cached_hosts = [{'id': 1, 'name': 'cached.example.com'}]
    cache = {'cache-key': {url: cached_hosts}}
    session = FakeSession({'results': [], 'subtotal': 0})
    inventory = prepare_inventory(monkeypatch, cache, session, url)

    inventory.parse(None, None, 'inventory.foreman.yml', cache=True)

    assert session.calls == 0
    assert cache == {'cache-key': {url: cached_hosts}}


def test_normal_inventory_parse_populates_empty_cache(monkeypatch):
    url = 'https://foreman.example.com/api/v2/hosts'
    hosts = [{'id': 1, 'name': 'new.example.com'}]
    cache = {}
    session = FakeSession({'results': hosts, 'subtotal': 1})
    inventory = prepare_inventory(monkeypatch, cache, session, url)

    inventory.parse(None, None, 'inventory.foreman.yml', cache=True)

    assert session.calls == 1
    assert cache == {'cache-key': {url: hosts}}


def test_refresh_inventory_report_updates_persistent_cache(monkeypatch):
    url = 'https://foreman.example.com/ansible/api/v2/ansible_inventories/schedule'
    old_report = [{'name': 'old.example.com'}]
    new_report = [{'name': 'new.example.com'}]
    cache = {'cache-key': {url: old_report}}
    session = FakeReportSession(new_report)
    inventory = prepare_inventory(monkeypatch, cache, session, url)
    monkeypatch.setattr(inventory, '_fetch_params', lambda: {})
    monkeypatch.setattr(inventory, '_populate', inventory._post_request)

    inventory.parse(None, None, 'inventory.foreman.yml', cache=False)

    assert session.calls == 2
    assert cache == {'cache-key': {url: new_report}}
