import functools
import itertools
from typing import Any

from skabelon.filter.common import join_newline
import skabelon.helper


def markdown_heading(value: str, level: int = 1) -> str:
    """Transform a string into a Markdown heading of a given level"""
    return f"{'#' * level} {value}"


def markdown_list(value: list[Any]) -> str:
    """Transform a list of values into a Markdown list"""
    return join_newline([f"- {x}" for x in value])


def markdown_enumeration(value: list[Any]) -> str:
    """Transform a list of values into a Markdown enumeration"""
    return join_newline([f"{idx}. {x}" for idx, x in enumerate(value, start=1)])


def markdown_monospace(value: str) -> str:
    """Wrap a string with Markdown monospace formatting"""
    return f"`{value}`"


def markdown_codeblock(value: list[str] | str, language: str | None = None) -> str:
    """Wrap a string or list of strings in Markdown code block formatting"""
    prefix = f"```{language}" if language else "```"
    suffix = "```"

    components = [prefix, *(value if isinstance(value, list) else [value]), suffix]

    return join_newline(components)


def markdown_table_row(value: list[Any]) -> str:
    """Wrap a list of strings as a Markdown table row"""
    return f"| {' | '.join(value)} |"


def markdown_table(
    value: list[list[Any]],
    header: list[str] | None = None,
    fill_values: bool = False,
    align_columns: bool = False,
    alignment: str = "left",
) -> str:
    """Wrap a list of strings in Markdown table formatting"""
    assert alignment in (
        "left",
        "right",
        "center",
    ), "alignment needs be one of left|right|center"

    body = []
    empty = ""
    separator = "---"

    # If alignment is anything but left, we need align_columns to be True, otherwise
    # we don't pad, and thus have nothing to align
    align_columns = alignment in ("center", "right") or align_columns

    # If align_columns is True, we need all columns filled to have something to pad
    fill_values = align_columns or fill_values

    value = [[str(x) for x in v] for v in value]  # Convert values to strings
    element_count = max(map(len, value))

    header = header[0:element_count] if header else []

    # Optionally fill missing body values up to maximum line length
    if fill_values and any([len(x) < element_count for x in value]):
        value = [
            [
                v
                for _, v in itertools.zip_longest(
                    [empty] * element_count, x, fillvalue=empty
                )
            ]
            for x in value
        ]

    # Optionally fill cells to have a uniform length *per column*
    if align_columns:
        headers = []
        separators = []
        columns = []

        for idx, column in enumerate([x for x in value if len(x) == element_count][0]):
            _header = [header[idx]] if header else []

            max_length = max(map(len, [*_header, *[x[idx] for x in value]]))
            pad = functools.partial(
                skabelon.helper.pad_string, length=max_length, alignment=alignment
            )

            if _header:
                headers.append(pad(value=_header[0]))

            separators.append(pad(value=separator, fill_char="-"))
            columns.append([pad(value=x[idx]) for x in value])

        header = headers
        value = list(itertools.zip_longest(*columns))
    else:
        separators = [separator] * element_count

    if header:
        body.append(markdown_table_row(value=header))
        body.append(markdown_table_row(separators))

    body.extend(list(map(markdown_table_row, value)))

    return join_newline(body)
