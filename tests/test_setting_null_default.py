import importlib
import sys
from pathlib import Path

import pytest


sys.path.insert(0, str(Path(__file__).parents[1] / 'build' / 'collections'))
setting = importlib.import_module(
    'ansible_collections.theforeman.foreman.plugins.modules.setting'
)


class FakeConnection:
    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, traceback):
        pass


class FakeSettingModule:
    def __init__(self, entity, value_is_set=False, value=None):
        self.entity = entity
        self.foreman_params = {'name': entity['name']}
        if value_is_set:
            self.foreman_params['value'] = value
        self.desired_entity = None
        self.current_entity = None
        self.result = None

    def api_connection(self):
        return FakeConnection()

    def lookup_entity(self, key):
        return self.entity.copy()

    def ensure_entity(self, resource, desired_entity, current_entity, state):
        self.desired_entity = desired_entity.copy()
        self.current_entity = current_entity.copy()
        return current_entity.copy()

    def fail_json(self, **kwargs):
        raise RuntimeError(kwargs['msg'])

    def exit_json(self, **kwargs):
        self.result = kwargs


def test_setting_with_null_integer_default_is_unchanged(monkeypatch):
    module = FakeSettingModule({
        'id': 'batch_size',
        'name': 'batch_size',
        'settings_type': 'integer',
        'default': None,
        'value': None,
    })
    monkeypatch.setattr(setting, 'ForemanSettingModule', lambda **kwargs: module)

    setting.main()

    assert 'value' not in module.desired_entity
    assert module.current_entity['value'] is None
    assert module.result['foreman_setting']['value'] is None


def test_setting_reset_uses_empty_string_for_null_string_default(monkeypatch):
    module = FakeSettingModule({
        'id': 'cockpit_url',
        'name': 'cockpit_url',
        'settings_type': 'string',
        'default': None,
        'value': 'https://cockpit.example.com',
    })
    monkeypatch.setattr(setting, 'ForemanSettingModule', lambda **kwargs: module)

    setting.main()

    assert module.desired_entity['value'] == ''
    assert module.result['foreman_setting']['value'] is None


def test_setting_reports_unsupported_null_integer_reset(monkeypatch):
    module = FakeSettingModule({
        'id': 'batch_size',
        'name': 'batch_size',
        'settings_type': 'integer',
        'default': None,
        'value': 10,
    })
    monkeypatch.setattr(setting, 'ForemanSettingModule', lambda **kwargs: module)

    with pytest.raises(RuntimeError, match='cannot be restored through the Foreman API'):
        setting.main()


def test_setting_keeps_integer_output_type(monkeypatch):
    module = FakeSettingModule({
        'id': 'batch_size',
        'name': 'batch_size',
        'settings_type': 'integer',
        'default': None,
        'value': 10,
    }, value_is_set=True, value='20')
    monkeypatch.setattr(setting, 'ForemanSettingModule', lambda **kwargs: module)

    setting.main()

    assert module.desired_entity['value'] == '20'
    assert module.result['foreman_setting']['value'] == 20
