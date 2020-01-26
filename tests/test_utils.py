import enum
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Dict, List, Mapping, NamedTuple, Optional, Set, Tuple, Union

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


def test_primitive_types_dataclass_fromjson() -> None:
    @dataclass
    class Item:
        id: int
        name: str
        is_active: bool
        price: float

    item = utils.fromjson(
        Item, {"id": "1", "name": "foo-1", "is_active": True, "price": "20.5"}
    )
    assert item == Item(id=1, name="foo-1", is_active=True, price=20.5)


def test_complex_types_dataclass_fromjson() -> None:
    @dataclass
    class Author:
        name: str

    @dataclass
    class Song:
        duration: Decimal
        author: Author

    data = {
        "duration": 8.5,
        "author": {"name": "Unknown"},
    }

    song = utils.fromjson(Song, data)
    assert song == Song(duration=Decimal(8.5), author=Author(name="Unknown"))


@pytest.mark.parametrize("rating", [None, 10])
def test_optional_dataclass_fromjson(rating) -> None:
    @dataclass
    class Album:
        rating: Optional[int]

    data = {"rating": rating}
    album = utils.fromjson(Album, data)
    assert album == Album(rating=rating)


def test_union_dataclass_fromjson() -> None:
    @dataclass
    class Song:
        duration: Union[int, float]

    data = {"duration": 8}
    with pytest.raises(TypeError) as excinfo:
        utils.fromjson(Song, data)

    assert str(excinfo.value) == "Union is not supported"


def test_any_dataclass_fromjson() -> None:
    @dataclass
    class Album:
        band: Any

    data = {"band": {"title": "The Apiwrappers"}}

    album = utils.fromjson(Album, data)
    assert album == Album(band={"title": "The Apiwrappers"})


def test_list_dataclass_fromjson() -> None:
    @dataclass
    class Song:
        id: int

    @dataclass
    class Album:
        songs: List[Song]

    data = {
        "id": 1,
        "songs": [{"id": 1}, {"id": 2}],
    }

    album = utils.fromjson(Album, data)
    assert album == Album(songs=[Song(1), Song(2)])


def test_fix_length_tuple_dataclass_fromjson() -> None:
    @dataclass
    class Sudoku:
        box_size: Tuple[int, str]

    data = {"box_size": ["3", "3"]}
    sudoku = utils.fromjson(Sudoku, data)
    assert sudoku == Sudoku(box_size=(3, "3"))


def test_variable_length_tuple_fromjson() -> None:
    @dataclass
    class Sudoku:
        cells: Tuple[int, ...]

    data = {"cells": ["1", "5", "3"]}
    sudoku = utils.fromjson(Sudoku, data)
    assert sudoku == Sudoku(cells=(1, 5, 3))


def test_set_fromjson() -> None:
    @dataclass
    class UniqueFibonacci:
        digits: Set[int]

    data = {"digits": [1, 1, 3, 5, 8]}
    fibonacci = utils.fromjson(UniqueFibonacci, data)
    assert fibonacci == UniqueFibonacci(digits={1, 3, 5, 8})


def test_list_from_not_list():
    @dataclass
    class Album:
        songs: List[str]

    data = {"songs": {"song-1": 2.5, "song-2": 3.5}}
    with pytest.raises(ValueError) as excinfo:
        utils.fromjson(Album, data)

    assert str(excinfo.value) == "Expected value to be list, got: <class 'dict'>"


def test_dict_fromjson() -> None:
    @dataclass
    class Config:
        extras: Dict[str, str]

    data = {"extras": {"persist": "1", "multithread": "0"}}
    config = utils.fromjson(Config, data)
    assert config == Config(extras={"persist": "1", "multithread": "0"})


def test_dict_from_not_dict():
    @dataclass
    class Album:
        songs: Dict[str, str]

    data = {"songs": ["song-1", "song-2"]}
    with pytest.raises(ValueError) as excinfo:
        print(utils.fromjson(Album, data))

    assert str(excinfo.value) == "Expected value to be mapping, got: <class 'list'>"


def test_default_field_value_fromjson() -> None:
    @dataclass
    class Sudoku:
        size: int = field(default=81)

    data: Dict[str, Any] = {}
    sudoku = utils.fromjson(Sudoku, data)
    assert sudoku == Sudoku(size=81)


def test_default_factory_field_value_fromjson() -> None:
    @dataclass
    class Sudoku:
        cells: List[int] = field(default_factory=list)

    data: Dict[str, Any] = {}
    sudoku = utils.fromjson(Sudoku, data)
    assert sudoku == Sudoku(cells=[])


def test_no_default_field_value_fromjson() -> None:
    @dataclass
    class Sudoku:
        size: int

    data: Dict[str, Any] = {}
    with pytest.raises(KeyError):
        utils.fromjson(Sudoku, data)


def test_abstract_types_fromjson() -> None:
    @dataclass
    class Config:
        extras: Mapping[str, str]

    data = {"extras": {"persist": "1", "multithread": "0"}}
    with pytest.raises(TypeError) as excinfo:
        utils.fromjson(Config, data)

    assert str(excinfo.value) == "Abstract types is not supported"


def test_enum_fromjson() -> None:
    class Genre(enum.Enum):
        indie = 1
        shoegaze = 2

    @dataclass
    class Song:
        genre: Genre

    data = {"genre": 1}
    song = utils.fromjson(Song, data)
    assert song.genre == Genre.indie


@pytest.mark.parametrize("data", [[1, 0], {"x": 1, "y": 0}])
def test_namedtuple_fromjson(data) -> None:
    class Position(NamedTuple):
        x: int
        y: int

    position = utils.fromjson(Position, data)
    assert position == Position(1, 0)


def test_namedtuple_fromjson_defaults() -> None:
    class Position(NamedTuple):
        x: int
        y: int = 0

    data = {"x": 1}
    position = utils.fromjson(Position, data)
    assert position == Position(1, 0)


def test_namedtuple_fromjson_without_defaults() -> None:
    class Position(NamedTuple):
        x: int
        y: int

    data = {"x": 1}
    with pytest.raises(KeyError):
        utils.fromjson(Position, data)


def test_namedtuple_fromjson_invalid_type() -> None:
    class Position(NamedTuple):
        x: int
        y: int = 0

    data = 1
    with pytest.raises(ValueError) as excinfo:
        utils.fromjson(Position, data)

    assert str(excinfo.value) == "Expected value to be list or dict, got: <class 'int'>"
