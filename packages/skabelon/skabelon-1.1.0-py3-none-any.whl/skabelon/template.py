import importlib
import os
import pathlib
from types import FunctionType
from typing import Callable

import jinja2

import skabelon.helper


def get_template_environment(
    path: pathlib.Path | str | None = None,
    custom_filter_modules: list[str] | None = None,
    **kwargs,
) -> jinja2.Environment:
    """Return a Jinja2 environment with built-in location and custom filters"""
    if path:
        path = pathlib.Path(path).resolve()
    else:
        path = pathlib.Path().cwd()

    environment = jinja2.Environment(
        loader=jinja2.FileSystemLoader(path),
        **kwargs,
    )

    # Dynamically load filters defined in skabelon,filter/*.py and other custom modules
    filters = []

    for m in ["skabelon.filter", *(custom_filter_modules or [])]:
        for f in vars(importlib.import_module(m)).values():
            if isinstance(f, FunctionType):
                filters.append(f)

    for f in filters:
        environment.filters[f.__name__] = f

    return environment


def render_template(
    path: pathlib.Path | str,
    transformers: dict[str, Callable] | None = None,
    **kwargs,
) -> str:
    """Render a given template after applying transformations to keyword arguments"""
    transformers = transformers or {}
    template_path, template_name = os.path.split(pathlib.Path(path).resolve())

    environment = get_template_environment(path=template_path or None)
    template = environment.get_template(name=template_name)

    for k, f in transformers.items():
        _value = skabelon.helper.get_dict_path(data=kwargs, path=k)
        kwargs = skabelon.helper.put_dict_path(data=kwargs, path=k, value=f(_value))

    return template.render(**kwargs)
