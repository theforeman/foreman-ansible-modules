import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'build' / 'collections'))

from ansible_collections.theforeman.foreman.plugins.modules \
    import external_usergroup as external_usergroup_module


@pytest.mark.parametrize(
    'external_usergroup, expected',
    [
        ({'auth_source_id': 1}, 1),
        ({'auth_source': {'id': 2}}, 2),
        ({'auth_source_ldap': {'id': 3}}, 3),
        ({'auth_source_external': {'id': 4}}, 4),
        ({}, None),
    ],
)
def test_external_usergroup_auth_source_id(external_usergroup, expected):
    actual = external_usergroup_module._external_usergroup_auth_source_id(
        external_usergroup
    )
    assert actual == expected


def test_find_external_usergroup_matches_name_and_auth_source():
    external_usergroups = [
        {'id': 10, 'name': 'admins', 'auth_source_ldap': {'id': 1}},
        {'id': 11, 'name': 'admins', 'auth_source_external': {'id': 2}},
    ]

    match = external_usergroup_module._find_external_usergroup(
        external_usergroups, 'admins', 2
    )
    assert match['id'] == 11
    no_match = external_usergroup_module._find_external_usergroup(
        external_usergroups, 'admins', 3
    )
    assert no_match is None
