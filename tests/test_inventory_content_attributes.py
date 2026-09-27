import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'build' / 'collections'))

from ansible_collections.theforeman.foreman.plugins.inventory.foreman import (
    _get_content_attribute_name,
)


@pytest.mark.parametrize(
    'content_attributes, attribute, expected',
    [
        (
            {'lifecycle_environment': {'name': 'Development'}},
            'lifecycle_environment',
            'Development',
        ),
        ({'content_view': {'name': 'RHEL 9'}}, 'content_view', 'RHEL 9'),
        (
            {'lifecycle_environment_name': 'Library'},
            'lifecycle_environment',
            'Library',
        ),
        (
            {
                'lifecycle_environment': {'name': 'Development'},
                'lifecycle_environment_name': 'Library',
            },
            'lifecycle_environment',
            'Development',
        ),
        (
            {
                'lifecycle_environment': {'name': None},
                'lifecycle_environment_name': 'Library',
            },
            'lifecycle_environment',
            'Library',
        ),
        ({}, 'lifecycle_environment', None),
    ],
)
def test_get_content_attribute_name(content_attributes, attribute, expected):
    actual = _get_content_attribute_name(content_attributes, attribute)
    assert actual == expected
