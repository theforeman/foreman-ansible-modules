import sys
from unittest.mock import Mock

import pytest

from plugins.module_utils import foreman_helper


sys.modules['ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper'] = foreman_helper

from plugins.modules.repository_sync import _sync_repositories  # noqa: E402


@pytest.mark.parametrize(
    ('product', 'repositories', 'resource', 'action', 'params'),
    [
        ({'id': 1}, [], 'products', 'sync', {'id': 1}),
        ({'id': 1}, [{'id': 2}], 'repositories', 'sync', {'id': 2}),
        (
            {'id': 1},
            [{'id': 2}, {'id': 3}],
            'repositories_bulk_actions',
            'sync_repositories',
            {'ids': [2, 3]},
        ),
    ],
)
def test_sync_repositories(product, repositories, resource, action, params):
    module = Mock()
    module.resource_action.return_value = {'id': 'task-id'}

    task = _sync_repositories(module, product, repositories)

    module.resource_action.assert_called_once_with(resource, action, params)
    assert task == {'id': 'task-id'}
