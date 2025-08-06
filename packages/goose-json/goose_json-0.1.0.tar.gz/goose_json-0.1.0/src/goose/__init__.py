"""
Goose is a library for conveniently navigating unstructured blobs of data.

It functions like Python's built-in JSON module, but handles bad keys or indices
by returning a None-like null object, rather than throwing an exception.

>>> import json
>>> import goose
>>> data = '{"foo": 3, "bar": 5, "baz": {"spam": "yep", "eggs": null}}'
>>> json_version = json.loads(data)
>>> goose_version = goose.loads(data)
>>> json_version["foo"]
3
>>> goose_version["foo"]
3
>>> json_version["foobar"]
Traceback (most recent call last):
    ...
KeyError: 'foobar'
>>> goose_version["foobar"]
null
>>> goose_version["foobar"][5]["blob"][9]["potato"]
null

Note that strings and integers behave as normal.

>>> goose_version["foo"]["bar"]
Traceback (most recent call last):
    ...
TypeError: 'int' object is not subscriptable
>>> goose_version["baz"]["spam"]
'yep'
>>> goose_version["baz"]["spam"][4]
Traceback (most recent call last):
    ...
IndexError: string index out of range
"""

from __future__ import annotations

import json
from typing import SupportsIndex, overload

type Goose = _Null | bool | int | float | str | Array | Map


class _Null:
    """The empty value, null."""

    __slots__ = ()

    def __repr__(self) -> str:
        return "null"

    def __bool__(self) -> bool:
        return False

    def __getitem__(self, _: int | str) -> _Null:
        return self

    def __eq__(self, other: object) -> bool:
        return other is null or other is None

    def __hash__(self) -> int:
        return hash(id(self))


null = _Null()


class Map(dict[str, Goose]):
    """A dict subclass which returns null on missing keys."""

    def __getitem__(self, k: str) -> Goose:
        return self.get(k, null)

    def __repr__(self):
        return f"to_goose({from_goose(self)!r})"


class Array(list[Goose]):
    """A list subclass which returns null for out-of-range indices."""

    @overload
    def __getitem__(self, k: SupportsIndex) -> Goose: ...
    @overload
    def __getitem__(self, k: slice) -> list[Goose]: ...
    @overload
    def __getitem__(self, k: str) -> _Null: ...
    def __getitem__(self, k: SupportsIndex | slice | str):
        if isinstance(k, str):
            return null
        try:
            return super().__getitem__(k)
        except IndexError:
            return null

    def __repr__(self):
        return f"to_goose({from_goose(self)!r})"


def to_goose(o: Json, /) -> Goose:
    """Create a Goose value from a JSON-like Python object."""
    match o:
        case None:
            return null
        case bool(x) | int(x) | float(x) | str(x):
            return x
        case [*elements]:
            return Array(map(to_goose, elements))
        case {**items}:
            return Map({k: to_goose(v) for k, v in items.items()})
        case _:
            msg = f"the provided {o!r} can not be converted to a Goose value"
            raise BadGoose(msg)


def from_goose(value: Goose, /) -> Json:
    """Convert a Goose value to normal Python types."""
    match value:
        case _Null():
            return None
        case bool(x) | int(x) | float(x) | str(x):
            return x
        case [*elements]:
            return [from_goose(x) for x in elements]
        case {**items}:
            return {k: from_goose(v) for k, v in items.items()}
        case _:
            msg = f"the provided {value!r} is not a Goose value"
            raise NotGoose(msg)


class BadGoose(Exception):
    pass


class NotGoose(Exception):
    pass


type Json = None | bool | int | float | str | list[Json] | dict[str, Json]


def loads(*args, **kwargs) -> Goose:
    """Deserialise a JSON str-like object to a Goose wrapper."""
    return to_goose(json.loads(*args, **kwargs))


def load(*args, **kwargs) -> Goose:
    """Deserialise a JSON file-like object to a Goose wrapper."""
    return to_goose(json.load(*args, **kwargs))
