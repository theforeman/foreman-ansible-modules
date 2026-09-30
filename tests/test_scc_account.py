import sys

import pytest

from plugins.module_utils import foreman_helper

sys.modules['ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper'] = foreman_helper

from plugins.modules import scc_account


class ModuleSpecCaptured(Exception):
    pass


def test_download_policy_argument(monkeypatch):
    class CaptureModuleSpec:
        def __init__(self, **kwargs):
            raise ModuleSpecCaptured(kwargs)

    monkeypatch.setattr(scc_account, 'KatelloSccAccountModule', CaptureModuleSpec)

    with pytest.raises(ModuleSpecCaptured) as captured:
        scc_account.main()

    assert captured.value.args[0]['foreman_spec']['download_policy'] == {
        'choices': ['immediate', 'on_demand'],
    }
