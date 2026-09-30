import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'build' / 'collections'))

from ansible_collections.theforeman.foreman.plugins.modules.sync_plan import (
    _parse_sync_date,
    _same_sync_date,
)


@pytest.mark.parametrize(
    'first, second',
    [
        (
            '2022-01-01 02:02:00 UTC',
            '2022-01-01 02:02:00 +0000',
        ),
        (
            '2024-12-02 01:00:00+0200',
            '2024-12-01 23:00:00 +0000',
        ),
        (
            '2024-12-02T01:00:00+02:00',
            '2024-12-01 23:00:00Z',
        ),
    ],
)
def test_same_sync_date_compares_instants(first, second):
    assert _same_sync_date(first, second)


@pytest.mark.parametrize(
    'first, second',
    [
        (
            '2024-12-02 01:00:00 +0200',
            '2024-12-02 00:00:00 +0000',
        ),
        ('not a date', 'not a date'),
    ],
)
def test_same_sync_date_rejects_different_or_invalid_values(first, second):
    assert not _same_sync_date(first, second)


def test_parse_sync_date_rejects_naive_value():
    assert _parse_sync_date('2024-12-02 01:00:00') is None
