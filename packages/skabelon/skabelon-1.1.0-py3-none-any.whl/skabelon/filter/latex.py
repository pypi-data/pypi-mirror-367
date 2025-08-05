import re
from typing import Any

from skabelon.filter.common import join_newline


def latex_escape(value: Any) -> str:
    """Escape special LaTeX characters"""
    characters = {
        "&": "\\&",
        "%": "\\%",
        "$": "\\$",
        "#": "\\#",
        "_": "\\_",
        # "{": "\\{",
        # "}": "\\}",
        "~": "\\textasciitilde",
        "^": "\\textasciicircum",
        # "\\": "\\textbackslash",
    }

    if isinstance(value, str):
        value = "".join([characters.get(x, x) for x in value])
        value = re.sub(r"\\+", r"\\", value)

    return value


def latex_command(
    value: str, command: str, options: list[str] | None = None, **kwargs
) -> str:
    """Wrap a string in LaTeX command"""
    _keywords = ",".join([f"{k}={v}" for k, v in kwargs.items()])
    _value = latex_escape(value)

    components = [f"\\{command}"]

    if kwargs:
        components.append(f"[{_keywords}]")

    components.append(f"{{{_value}}}")

    if options is not None and command == "begin":
        components.append(f"{{{' '.join(options or [])}}}")

    return "".join(components)


def latex_heading(value: str, level: int = 1) -> str:
    """Transform a string into a LaTeX heading of a given level"""
    levels = {
        0: "part",
        1: "section",
        2: "subsection",
        3: "subsubsection",
        4: "paragraph",
        5: "subparagraph",
    }

    return latex_command(value, command=levels.get(level, levels[1]))


def latex_join_newline(value: list[str]) -> str:
    """Transform a list of strings into a single, linebreak-delimited LaTeX string"""
    return "\n\n".join(value)


def latex_align_left(value: str) -> str:
    """Wrap a string so that LaTeX left-aligns it"""
    return latex_command(value, command="raggedright")


def latex_align_right(value: str) -> str:
    """Wrap a string so that LaTeX right-aligns it"""
    return latex_command(value, command="raggedleft")


def latex_table_row(value: list[Any]) -> str:
    """Wrap a list of strings as a LaTeX table row"""
    return f"{' & '.join(latex_escape(value))} \\\\"


def latex_environment(
    value: str, environment: str, options: list[str] | None = None, block: bool = False
) -> str:
    """Wrap a string in a LaTeX environment"""
    body = [
        latex_command(environment, command="begin", options=options),
        value,
        latex_command(environment, command="end", options=options),
    ]

    return join_newline(body) if block else "".join(body)


def latex_list(value: list[Any]) -> str:
    """Transform a list of values into a LaTeX list"""
    body = join_newline([f"\\item {latex_escape(x)}" for x in value])

    return latex_environment(body, environment="itemize", block=True)


def latex_enumeration(value: list[Any]) -> str:
    """Transform a list of values into a LaTeX enumeration"""
    body = join_newline([f"\\item {latex_escape(x)}" for x in value])

    return latex_environment(body, environment="enumerate", block=True)


def latex_description(value: dict[str, Any]) -> str:
    """Transform a list of key/value-pairs into a LaTeX description"""
    body = join_newline(
        [f"\\item [{latex_escape(k)}] {latex_escape(v)}" for k, v in value.items()]
    )

    return latex_environment(body, environment="description", block=True)


def latex_codeblock(value: list[Any] | str) -> str:
    """Wrap a string or list of strings in LaTeX verbatim formatting"""
    body = latex_escape(join_newline(value) if isinstance(value, list) else value)

    return latex_environment(body, environment="verbatim", block=True)


def latex_quote(value: list[Any] | str) -> str:
    """Wrap a string or list of strings in LaTeX verse formatting"""
    body = latex_escape(join_newline(value) if isinstance(value, list) else value)

    return latex_environment(body, environment="verse", block=True)


def latex_table(
    value: list[list[Any]],
    header: list[str] | None = None,
    alignment: str = "l",
    lines: str | None = None,
    use_booktabs: bool = False,
) -> str:
    """Wrap a list of lists of strings in LaTeX table formatting"""
    assert alignment in {"l", "c", "r"}
    assert lines in {None, "|", "||"}

    value = list(value)
    options = [alignment] * max(map(len, value))

    body = []

    if header:
        header = header[0 : len(options)]
        body.append(latex_table_row(value=header))
        body.append("\\midrule" if use_booktabs else "\\hline")

    body.extend(list(map(latex_table_row, value)))
    body = join_newline(body)

    if lines:
        options = [f" {lines} ".join(options)]

    return latex_environment(body, environment="tabular", block=True, options=options)


def latex_emphasis(value: str) -> str:
    """Wrap a string with LaTeX emphasis formatting"""
    return latex_command(value, command="emph")


def latex_bold(value: str) -> str:
    """Wrap a string with LaTeX bold formatting"""
    return latex_command(value, command="textbf")


def latex_italic(value: str) -> str:
    """Wrap a string with LaTeX italic formatting"""
    return latex_command(value, command="textit")


def latex_serif(value: str) -> str:
    """Wrap a string with LaTeX serif formatting"""
    return latex_command(value, command="textrm")


def latex_sans(value: str) -> str:
    """Wrap a string with LaTeX sans-serif formatting"""
    return latex_command(value, command="textsf")


def latex_monospace(value: str) -> str:
    """Wrap a string with LaTeX monospace formatting"""
    return latex_command(value, command="texttt")
