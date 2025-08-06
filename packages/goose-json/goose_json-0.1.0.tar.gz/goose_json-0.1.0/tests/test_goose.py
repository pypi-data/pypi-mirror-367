import goose


def test_null_equals_none():
    assert goose.null == None
    assert None == goose.null


def test_bare_null():
    assert goose.loads("null") == goose.null


def test_bare_integer():
    assert goose.loads("5") == 5


def test_bare_string():
    assert goose.loads('"foo"') == "foo"


def test_simple_array():
    assert goose.loads('[null, -5, "foobar"]') == [None, -5, "foobar"]


def test_array_accesses():
    array = goose.loads('[null, -5, "foobar"]')
    assert array[0] == goose.null
    assert array[1] == -5
    assert array[2] == "foobar"
    assert array[3] == goose.null


def test_chained_array_object_accesses():
    array = goose.loads('[{"a": [{"b": "c"}]}]')
    assert array[0]["a"][0]["b"] == "c"
    assert array[1]["a"][0]["b"] == goose.null
    assert array[0]["b"][0]["b"] == goose.null
    assert array[0]["a"][1]["b"] == goose.null
    assert array[0]["a"][0]["a"] == goose.null
