import sys
from unittest.mock import Mock

import pytest

from plugins.module_utils import foreman_helper


sys.modules['ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper'] = foreman_helper

from plugins.modules.sync_plan import _ensure_enabled  # noqa: E402


@pytest.mark.parametrize(
    ('current_enabled', 'requested_enabled', 'recurring_logic_state'),
    [
        (True, False, 'disabled'),
        (False, True, 'active'),
    ],
)
def test_ensure_enabled_uses_recurring_logic_fallback(current_enabled, requested_enabled, recurring_logic_state):
    module = Mock(check_mode=False)
    module.resource_action.return_value = {'state': recurring_logic_state}
    sync_plan = {
        'enabled': current_enabled,
        'foreman_tasks_recurring_logic_id': 42,
    }

    _ensure_enabled(module, sync_plan, requested_enabled)

    module.resource_action.assert_called_once_with(
        'recurring_logics',
        'update',
        {'id': 42, 'enabled': requested_enabled},
    )
    module.record_before.assert_called_once_with('recurring_logics', {'id': 42, 'enabled': current_enabled})
    module.record_after.assert_called_once_with('recurring_logics', {'id': 42, 'enabled': requested_enabled})
    module.set_changed.assert_called_once_with()
    assert sync_plan['enabled'] is requested_enabled


def test_ensure_enabled_does_nothing_for_matching_state():
    module = Mock(check_mode=False)
    sync_plan = {
        'enabled': False,
        'foreman_tasks_recurring_logic_id': 42,
    }

    _ensure_enabled(module, sync_plan, False)

    module.assert_not_called()
