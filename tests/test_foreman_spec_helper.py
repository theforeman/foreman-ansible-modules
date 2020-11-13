from plugins.module_utils.foreman_helper import _foreman_spec_helper


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
