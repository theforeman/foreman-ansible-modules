import sys

import pytest

from plugins.module_utils import foreman_helper

sys.modules['ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper'] = foreman_helper

from plugins.modules.cdn_configuration import (  # noqa: E402
    _configuration_needs_update,
    _configuration_payload,
    _configuration_result,
)


def test_configuration_payload_maps_upstream_credentials_and_ca():
    params = {
        'type': 'network_sync',
        'url': 'https://upstream.example.com',
        'upstream_username': 'sync-user',
        'upstream_password': 'secret',
        'upstream_organization_label': 'Default_Organization',
        'ssl_ca_credential': {'id': 42, 'name': 'Upstream CA'},
        'organization': {'id': 1},
        'force': False,
    }

    assert _configuration_payload(params) == {
        'type': 'network_sync',
        'url': 'https://upstream.example.com',
        'username': 'sync-user',
        'password': 'secret',
        'upstream_organization_label': 'Default_Organization',
        'ssl_ca_credential_id': 42,
    }


def test_existing_password_is_idempotent():
    current = {
        'type': 'network_sync',
        'url': 'https://upstream.example.com',
        'username': 'sync-user',
        'password_exists': True,
    }
    desired = {
        'type': 'network_sync',
        'url': 'https://upstream.example.com',
        'username': 'sync-user',
        'password': 'secret',
    }

    assert not _configuration_needs_update(current, desired)
    assert _configuration_needs_update(current, desired, force=True)


@pytest.mark.parametrize('current, desired', [
    ({'type': 'redhat_cdn'}, {'type': 'redhat_cdn'}),
    ({'type': 'export_sync'}, {'type': 'export_sync'}),
    (
        {'type': 'custom_cdn', 'url': 'https://cdn.example.com', 'ssl_ca_credential_id': 42},
        {'type': 'custom_cdn', 'url': 'https://cdn.example.com', 'ssl_ca_credential_id': 42},
    ),
])
def test_visible_configuration_is_idempotent(current, desired):
    assert not _configuration_needs_update(current, desired)


def test_missing_password_or_changed_visible_value_requires_update():
    current = {
        'type': 'network_sync',
        'url': 'https://upstream.example.com',
        'password_exists': False,
    }

    assert _configuration_needs_update(current, {'type': 'network_sync', 'password': 'secret'})
    assert _configuration_needs_update(current, {'type': 'network_sync', 'url': 'https://new.example.com'})
    assert _configuration_needs_update(current, {'type': 'network_sync', 'ssl_ca_credential_id': 43})


def test_configuration_result_never_returns_password():
    result = _configuration_result(
        {'type': 'redhat_cdn', 'password_exists': False},
        {'type': 'network_sync', 'password': 'secret'},
    )

    assert result == {'type': 'network_sync', 'password_exists': True}
