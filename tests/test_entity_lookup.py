import pytest

from plugins.module_utils.foreman_helper import ForemanAnsibleModule, NoEntity


class EntityLookupFailure(Exception):
    pass


class EntityLookupModule:
    find_resource_by = ForemanAnsibleModule.find_resource_by
    _lookup_entity = ForemanAnsibleModule._lookup_entity

    def __init__(self):
        self.foreman_params = {}
        self.lookups = []

    def find_resource(self, resource, search, **kwargs):
        self.lookups.append((resource, search, kwargs))
        return {'id': 1}

    def fail_json(self, **kwargs):
        raise EntityLookupFailure(kwargs['msg'])


def entity_spec(required=False):
    return {
        'type': 'entity',
        'resource_type': 'content_views',
        'search_by': 'name',
        'required': required,
    }


def test_optional_empty_entity_is_unset_without_lookup():
    module = EntityLookupModule()

    assert module._lookup_entity('', entity_spec()) is NoEntity
    assert module.lookups == []


def test_required_empty_entity_fails_cleanly_without_lookup():
    module = EntityLookupModule()

    with pytest.raises(EntityLookupFailure, match='Found no results while searching for content_views with name=""'):
        module._lookup_entity('', entity_spec(required=True))

    assert module.lookups == []


def test_required_nonempty_entity_is_looked_up():
    module = EntityLookupModule()

    assert module._lookup_entity('Test Content View', entity_spec(required=True)) == {'id': 1}
    assert module.lookups == [
        ('content_views', 'name="Test Content View"', {'failsafe': False, 'thin': True, 'params': {}}),
    ]
