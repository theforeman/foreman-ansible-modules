from plugins.module_utils.foreman_helper import _recursive_dict_keys


def test_recursive_dict_keys():
    a_dict = {'level1': 'has value', 'level2': {'real_level2': 'more value', 'level3': {'real_level3': 'nope'}}}
    expected_keys = set(['level1', 'level2', 'level3', 'real_level2', 'real_level3'])
    assert _recursive_dict_keys(a_dict) == expected_keys
