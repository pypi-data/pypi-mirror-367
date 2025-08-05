import functools
from typing import Any, TypeVar, Callable

T = TypeVar("T")


def merge_dict(
    left: dict[str, Any], right: dict[str, Any], merge_lists: bool = False
) -> dict[str, Any]:
    """Recursively merge two dictionaries, key by key"""
    result = {}

    # Combine keys via iteration instead of a set to maintain key ordering
    for k in [*left.keys(), *[x for x in right.keys() if x not in left.keys()]]:
        _left = left.get(k)
        _right = right.get(k)

        if isinstance(_left, dict) and isinstance(_right, dict):
            merged = merge_dict(left=_left, right=_right, merge_lists=merge_lists)
        elif isinstance(_left, list) and isinstance(_right, list) and merge_lists:
            merged = [*_left, *_right]
        elif not _left and _right is not None:
            merged = _right
        else:
            merged = _right or _left

        result[k] = merged

    return result


def get_dict_path(
    data: dict[str, dict | T], path: list[str] | str, default: Any | None = None
) -> T | None:
    """Get a value at a given path from a dictionary"""
    path = path.split(".") if isinstance(path, str) else path
    result = functools.reduce(lambda a, b: a.get(b, {}), path, data)

    return default if (result == {} and default) else result


def put_dict_path(data: dict[str, dict], path: list[str] | str, value: Any) -> dict:
    """Put a value at a given path into a dictionary"""
    path = path.split(".") if isinstance(path, str) else path
    branch = functools.reduce(lambda a, b: {b: a}, reversed(path), value)

    return merge_dict(left=data, right=branch, merge_lists=False)


def pad_string(
    value: Any, length: int, fill_char: str = " ", alignment: str = "left"
) -> str:
    """Pad a given string to length n by filling it with a given string"""
    assert length > 0, "length cannot be <1"
    assert len(fill_char) == 1, "fill_char needs to be exactly one character long"
    assert alignment in (
        "left",
        "right",
        "center",
    ), "alignment needs be one of left|right|center"

    operators: dict[str, Callable[..., str]] = {
        "left": str.ljust,
        "right": str.rjust,
        "center": str.center,
    }

    return operators[alignment](value, length, fill_char)
