import json

import boltons.ecoutils as ecoutils


def test_module_level_dumps_uses_json():
    assert ecoutils.dumps({'b': 1, 'a': [None, True]}, 0) == \
        json.dumps({'b': 1, 'a': [None, True]}, sort_keys=True)
    assert ecoutils.dumps({'a': 1}, 2) == '{\n  "a": 1\n}'


def test_get_profile_json_roundtrip():
    assert 'python' in json.loads(ecoutils.get_profile_json())
    pretty = ecoutils.get_profile_json(indent=True)
    assert '\n' in pretty
    assert json.loads(pretty)['python'] == json.loads(ecoutils.get_profile_json())['python']
