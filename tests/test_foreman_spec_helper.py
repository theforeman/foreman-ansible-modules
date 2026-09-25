from plugins.module_utils.foreman_helper import _foreman_spec_helper, _load_entity_details


def test_empty_entity():
    spec = {}
    foreman_spec, argument_spec = _foreman_spec_helper(spec)
    assert spec == {}
    assert foreman_spec == {}
    assert argument_spec == {}


def test_full_entity():
    spec = {
        'name': {},
        'count': {'type': 'int', 'aliases': ['number']},
        'facilities': {'type': 'list'},
        'street': {'type': 'entity', 'flat_name': 'street_id'},
        'quarter': {'type': 'entity', 'resource_type': 'edges'},
        'houses': {'type': 'entity_list', 'flat_name': 'house_ids'},
        'prices': {'type': 'nested_list', 'foreman_spec': {
            'value': {'type': 'int'},
        }},
        'tenant': {'invisible': True},
    }
    foreman_spec, argument_spec = _foreman_spec_helper(spec)
    assert spec == {
        'name': {},
        'count': {'type': 'int', 'aliases': ['number']},
        'facilities': {'type': 'list'},
        'street': {'type': 'entity', 'flat_name': 'street_id'},
        'quarter': {'type': 'entity', 'resource_type': 'edges'},
        'houses': {'type': 'entity_list', 'flat_name': 'house_ids'},
        'prices': {'type': 'nested_list', 'foreman_spec': {
            'value': {'type': 'int'},
        }},
        'tenant': {'invisible': True},
    }
    assert foreman_spec == {
        'name': {},
        'count': {'type': 'int'},
        'facilities': {'type': 'list'},
        'street': {'type': 'entity', 'flat_name': 'street_id', 'resource_type': 'streets'},
        'street_id': {},
        'quarter': {'type': 'entity', 'flat_name': 'quarter_id', 'resource_type': 'edges'},
        'quarter_id': {},
        'houses': {'type': 'entity_list', 'flat_name': 'house_ids', 'resource_type': 'houses'},
        'house_ids': {'type': 'list'},
        'prices': {'type': 'nested_list', 'foreman_spec': {'value': {'type': 'int'}}, 'ensure': False},
        'tenant': {},
    }
    assert argument_spec == {
        'name': {},
        'count': {'type': 'int', 'aliases': ['number']},
        'facilities': {'type': 'list'},
        'street': {},
        'quarter': {},
        'houses': {'type': 'list', 'elements': 'str'},
        'prices': {'type': 'list', 'elements': 'dict', 'options': {
            'value': {'type': 'int'},
        }},
    }


class FakeModule:
    def __init__(self, entities):
        self.entities = entities
        self.shown = []

    def show_resource(self, resource, resource_id, params):
        self.shown.append((resource, resource_id, params))
        return self.entities[resource_id]


def test_load_entity_details_keeps_complete_list_result():
    current_entity = {'id': 1, 'name': 'complete', 'input_type': 'user'}
    module = FakeModule({})

    result = _load_entity_details(
        module,
        'template_inputs',
        {'name': 'complete', 'input_type': 'user'},
        current_entity,
        params={'template_id': 42},
    )

    assert result == current_entity
    assert module.shown == []


def test_load_entity_details_fetches_missing_desired_fields():
    detailed_entity = {'id': 1, 'name': 'incomplete', 'input_type': 'user', 'value_type': 'plain'}
    module = FakeModule({1: detailed_entity})

    result = _load_entity_details(
        module,
        'template_inputs',
        {'name': 'incomplete', 'input_type': 'user', 'value_type': 'plain'},
        {'id': 1, 'name': 'incomplete', 'input_type': 'user'},
        params={'template_id': 42},
    )

    assert result == detailed_entity
    assert module.shown == [('template_inputs', 1, {'template_id': 42})]
