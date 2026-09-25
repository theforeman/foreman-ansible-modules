from plugins.modules.job_template import _current_template_inputs


class FakeModule:
    def __init__(self, template_inputs, detailed_template_inputs):
        self.template_inputs = template_inputs
        self.detailed_template_inputs = detailed_template_inputs
        self.shown = []

    def list_resource(self, resource, params):
        assert resource == 'template_inputs'
        assert params == {'template_id': 42}
        return self.template_inputs

    def show_resource(self, resource, resource_id, params):
        assert resource == 'template_inputs'
        assert params == {'template_id': 42}
        self.shown.append(resource_id)
        return self.detailed_template_inputs[resource_id]


def test_current_template_inputs_uses_complete_list_results():
    module = FakeModule(
        template_inputs=[{'id': 1, 'name': 'complete', 'input_type': 'user'}],
        detailed_template_inputs={},
    )

    result = _current_template_inputs(
        module,
        [{'name': 'complete', 'input_type': 'user'}],
        {'template_id': 42},
    )

    assert result == {'complete': {'id': 1, 'name': 'complete', 'input_type': 'user'}}
    assert module.shown == []


def test_current_template_inputs_loads_missing_desired_fields():
    module = FakeModule(
        template_inputs=[
            {'id': 1, 'name': 'incomplete', 'input_type': 'user'},
            {'id': 2, 'name': 'obsolete', 'input_type': 'user'},
        ],
        detailed_template_inputs={
            1: {'id': 1, 'name': 'incomplete', 'input_type': 'user', 'value_type': 'plain'},
        },
    )

    result = _current_template_inputs(
        module,
        [{'name': 'incomplete', 'input_type': 'user', 'value_type': 'plain'}],
        {'template_id': 42},
    )

    assert result == {
        'incomplete': {'id': 1, 'name': 'incomplete', 'input_type': 'user', 'value_type': 'plain'},
        'obsolete': {'id': 2, 'name': 'obsolete', 'input_type': 'user'},
    }
    assert module.shown == [1]
