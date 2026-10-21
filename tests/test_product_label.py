import importlib
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parents[1] / 'build' / 'collections'))
foreman_helper = importlib.import_module(
    'ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper'
)
product = importlib.import_module(
    'ansible_collections.theforeman.foreman.plugins.modules.product'
)


def _product_module(monkeypatch, params):
    def fake_init(module, **kwargs):
        module.foreman_params = params.copy()
        module.foreman_params['entity'] = module.foreman_params['name']
        module.foreman_spec = {'entity': {'search_by': 'name'}}

    monkeypatch.setattr(foreman_helper.KatelloEntityAnsibleModule, '__init__', fake_init)
    return product.KatelloProductModule()


def test_product_uses_label_as_identity(monkeypatch):
    module = _product_module(monkeypatch, {
        'name': 'Renamed product',
        'label': 'stable_label',
    })

    assert module.foreman_spec['entity']['search_by'] == 'label'
    assert module.foreman_params['entity'] == 'stable_label'


def test_product_keeps_name_as_identity_without_label(monkeypatch):
    module = _product_module(monkeypatch, {'name': 'Existing product'})

    assert module.foreman_spec['entity']['search_by'] == 'name'
    assert module.foreman_params['entity'] == 'Existing product'


def test_product_only_sends_label_when_creating(monkeypatch):
    calls = []

    def fake_ensure(module, resource, desired_entity, current_entity, **kwargs):
        calls.append(desired_entity.copy())
        return current_entity

    monkeypatch.setattr(foreman_helper.KatelloEntityAnsibleModule, 'ensure_entity', fake_ensure)
    module = _product_module(monkeypatch, {
        'name': 'Renamed product',
        'label': 'stable_label',
    })
    desired_entity = module.foreman_params.copy()

    module.ensure_entity('products', desired_entity, None)
    module.ensure_entity('products', desired_entity, {'id': 1, 'name': 'Old name'})

    assert calls == [
        {
            'name': 'Renamed product',
            'label': 'stable_label',
            'entity': 'stable_label',
        },
        {
            'name': 'Renamed product',
            'entity': 'stable_label',
        },
    ]
    assert desired_entity['label'] == 'stable_label'
