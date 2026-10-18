import io

import tomlkit


def test_dump_docstring_has_example():
    doc = tomlkit.dump.__doc__
    assert ":Example:" in doc
    assert "tomlkit.dump(data, fp)" in doc


def test_dump_writes_to_file(tmp_path):
    data = {"a": 1, "b": {"c": "x"}}
    path = tmp_path / "output.toml"
    with open(path, "w") as fp:
        tomlkit.dump(data, fp)
    assert tomlkit.loads(path.read_text()) == data


def test_dump_sort_keys():
    fp = io.StringIO()
    tomlkit.dump({"b": 1, "a": 2}, fp, sort_keys=True)
    assert fp.getvalue().index("a") < fp.getvalue().index("b")
