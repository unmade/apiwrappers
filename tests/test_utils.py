import enum
from dataclasses import dataclass, field
from decimal import Decimal
from typing import (
    Any,
    Dict,
    List,
    Mapping,
    NamedTuple,
    Optional,
    Set,
    Tuple,
    Union,
    cast,
)

import pytest

from apiwrappers import utils


@pytest.mark.parametrize("host", ["http://example.com", "http://example.com/"])
@pytest.mark.parametrize(
    ["path", "expected"],
    [
        ("/join", "http://example.com/join"),
        ("join", "http://example.com/join"),
        ("join/", "http://example.com/join/"),
    ],
)
def test_build_url(host, path, expected):
    url = utils.build_url(host, path)
    assert expected == url


@pytest.mark.parametrize("host", ["http://example.com/api"])
@pytest.mark.parametrize(
    ["path", "expected"],
    [
        ("/join", "http://example.com/api/join"),
        ("join", "http://example.com/api/join"),
        ("join/", "http://example.com/api/join/"),
    ],
)
def test_build_url_with_prefix(host, path, expected):
    url = utils.build_url(host, path)
    assert expected == url


@pytest.mark.parametrize(
    ["data", "key", "expected"],
    [
        ({"id": 1}, None, {"id": 1}),
        ({"id": 1}, "id", 1),
        ({"item": {"id": 1}}, "item.id", 1),
        ({"items": [1, 2]}, "items.0", 1),
    ],
)
def test_getitem(data, key, expected):
    item = utils.getitem(data, key)
    assert item == expected


def test_getitem_raises_error():
    with pytest.raises(TypeError):
        utils.getitem("id", "id")


@pytest.mark.parametrize(
    ["tp", "given", "expected"],
    [
        (int, 1, 1),
        (str, "1", "1"),
        (bool, True, True),
        (float, 8.5, 8.5),
        (Decimal, 8.5, Decimal(8.5)),
        (Any, {"x": 1, "y": 0}, {"x": 1, "y": 0}),
        (List[int], ["1", "3"], [1, 3]),
        (Tuple[int, ...], ["1", "3", "5"], (1, 3, 5)),
        (Tuple[int, str], ["1", "3"], (1, "3")),
        (Set[int], ["1", "1", "3", "5"], {1, 3, 5}),
        (Dict[str, int], {"x": "1", "y": "0"}, {"x": 1, "y": 0}),
        (Optional[int], None, None),
        (Optional[int], "1", 1),
    ],
)
def test_fromjson_generic_types(tp, given, expected) -> None:
    assert utils.fromjson(tp, given) == expected


@pytest.mark.parametrize(
    ["tp", "given", "expected"],
    [
        (List[int], {"x": 1, "y": 0}, "Expected `List`, got: <class 'dict'>"),
        (Dict[str, str], [1, 0], "Expected `Mapping`, got: <class 'list'>"),
    ],
)
def test_fromjson_generic_types_invalid_data(tp, given, expected):
    with pytest.raises(ValueError) as excinfo:
        utils.fromjson(tp, given)

    assert str(excinfo.value) == expected


def test_fromjson_union_are_not_supported() -> None:
    with pytest.raises(TypeError) as excinfo:
        utils.fromjson(Union[int, float], {})  # type: ignore

    assert str(excinfo.value) == "Union is not supported"


def test_fromjson_abstract_types() -> None:
    with pytest.raises(TypeError) as excinfo:
        utils.fromjson(Mapping[str, str], {})

    assert str(excinfo.value) == "Abstract types is not supported"


def test_fromjson_enum() -> None:
    class Genre(enum.Enum):
        INDIE = 1
        SHOEGAZE = 2

    genre = utils.fromjson(Genre, 1)
    assert genre == Genre.INDIE


def test_fromjson_dataclass() -> None:
    @dataclass
    class Song:
        title: str

    @dataclass
    class Album:
        title: str
        songs: List[Song]

    data = {"title": "The Apiwrappers", "songs": [{"title": "Waiting for my driver"}]}
    album = utils.fromjson(Album, data)
    assert album == Album(
        title="The Apiwrappers", songs=[Song(title="Waiting for my driver")]
    )


def test_fromjson_dataclass_with_defaults() -> None:
    @dataclass
    class Sudoku:
        size: int = field(default=81)

    data: Dict[str, Any] = {}
    sudoku = utils.fromjson(Sudoku, data)
    assert sudoku == Sudoku(size=81)


def test_fromjson_dataclass_with_default_factory() -> None:
    @dataclass
    class Sudoku:
        cells: List[int] = field(default_factory=list)

    data: Dict[str, Any] = {}
    sudoku = utils.fromjson(Sudoku, data)
    assert sudoku == Sudoku(cells=[])


def test_fromjson_dataclass_empty_data() -> None:
    @dataclass
    class Sudoku:
        size: int

    data: Dict[str, Any] = {}
    with pytest.raises(KeyError):
        utils.fromjson(Sudoku, data)


def test_fromjson_dataclass_invalid_data() -> None:
    @dataclass
    class Album:
        songs: List[int]

    data = [1]
    with pytest.raises(ValueError) as excinfo:
        utils.fromjson(Album, data)

    assert str(excinfo.value) == "Expected `Mapping`, got: <class 'list'>"


@pytest.mark.parametrize("data", [[1, 0], {"x": 1, "y": 0}])
def test_fromjson_namedtuple(data) -> None:
    class Position(NamedTuple):
        x: int
        y: int

    position = utils.fromjson(Position, data)
    assert position == Position(1, 0)


def test_fromjson_namedtuple_with_defaults() -> None:
    class Position(NamedTuple):
        x: int
        y: int = 0

    data = {"x": 1}
    position = utils.fromjson(Position, data)
    assert position == Position(1, 0)


def test_fromjson_namedtuple_empty_data() -> None:
    class Position(NamedTuple):
        x: int
        y: int

    data = {"x": 1}
    with pytest.raises(KeyError):
        utils.fromjson(Position, data)


def test_fromjson_namedtuple_invalid_data() -> None:
    class Position(NamedTuple):
        x: int
        y: int = 0

    data = 1
    with pytest.raises(ValueError) as excinfo:
        utils.fromjson(Position, data)

    assert str(excinfo.value) == "Expected `List` or `Mapping`, got: <class 'int'>"


def test_fromjson_callable() -> None:
    def get_x(data) -> int:
        return cast(int, data["x"])

    data = {"x": 1}
    value = utils.fromjson(get_x, data)
    assert value == 1
