import sys

import pytest

from plugins.module_utils import foreman_helper

sys.modules['ansible_collections.theforeman.foreman.plugins.module_utils.foreman_helper'] = foreman_helper

from plugins.modules.smart_proxy import _lookup_lifecycle_environments


class FakeSmartProxyModule:
    def __init__(self, organizations, lifecycle_environments):
        self.foreman_params = {
            'lifecycle_environments': lifecycle_environments,
        }
        if organizations is not None:
            self.foreman_params['organizations'] = organizations
        self.foreman_spec = {
            'lifecycle_environments': {
                'resource_type': 'lifecycle_environments',
                'type': 'entity_list',
            },
        }
        self.lookups = []

    def lookup_entity(self, key):
        if key not in self.foreman_params:
            return None
        if key == 'organizations':
            organizations = [
                {'id': index, 'name': organization}
                for index, organization in enumerate(self.foreman_params[key], start=1)
            ]
            self.foreman_params[key] = organizations
            return organizations
        return self.foreman_params[key]

    def find_resource_by(self, resource, value, search_field, **kwargs):
        self.lookups.append({
            'resource': resource,
            'value': value,
            'search_field': search_field,
            **kwargs,
        })
        return {
            'id': kwargs['params']['organization_id'] * 10,
            'name': value,
            'organization_id': kwargs['params']['organization_id'],
        }

    def set_entity(self, key, entity):
        self.foreman_params[key] = entity

    def fail_json(self, **kwargs):
        pytest.fail(kwargs['msg'])


def test_lifecycle_environment_lookup_is_scoped_to_each_organization():
    module = FakeSmartProxyModule(['Organization A', 'Organization B'], ['Development'])

    lifecycle_environments = _lookup_lifecycle_environments(module)

    assert [environment['id'] for environment in lifecycle_environments] == [10, 20]
    assert [lookup['params'] for lookup in module.lookups] == [
        {'organization_id': 1},
        {'organization_id': 2},
    ]
    assert all(lookup['failsafe'] for lookup in module.lookups)
    assert all(lookup['value'] == 'Development' for lookup in module.lookups)


def test_lifecycle_environment_lookup_remains_global_without_organizations():
    module = FakeSmartProxyModule(None, [{'id': 10, 'name': 'Development'}])

    lifecycle_environments = _lookup_lifecycle_environments(module)

    assert lifecycle_environments == [{'id': 10, 'name': 'Development'}]
    assert module.lookups == []
