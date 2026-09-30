import sys

import pytest

from plugins.module_utils import foreman_helper

sys.modules['ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper'] = foreman_helper

from plugins.modules import host_collection


class ModuleSpecCaptured(Exception):
    pass


def test_hosts_argument(monkeypatch):
    class CaptureModuleSpec:
        def __init__(self, **kwargs):
            raise ModuleSpecCaptured(kwargs)

    monkeypatch.setattr(host_collection, 'KatelloHostCollectionModule', CaptureModuleSpec)

    with pytest.raises(ModuleSpecCaptured) as captured:
        host_collection.main()

    assert captured.value.args[0]['foreman_spec']['hosts'] == {
        'type': 'entity_list',
        'scope': ['organization'],
    }


def test_hosts_are_flattened_to_host_ids():
    foreman_spec, argument_spec = foreman_helper._foreman_spec_helper({
        'hosts': {'type': 'entity_list', 'scope': ['organization']},
    })

    assert argument_spec['hosts'] == {'type': 'list', 'elements': 'str'}
    assert foreman_helper._flatten_entity({'hosts': [{'id': 2}, {'id': 1}]}, foreman_spec) == {
        'host_ids': [1, 2],
    }
    assert foreman_helper._flatten_entity({'host_ids': [1, 2]}, foreman_spec) == {
        'host_ids': [1, 2],
    }
