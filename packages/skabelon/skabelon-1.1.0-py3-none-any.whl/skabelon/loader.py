import json
import pathlib

import yaml


def from_json(path: pathlib.Path | str, ndjson: bool = False) -> dict:
    """Read data from a JSON file"""
    with open(pathlib.Path(path), mode="r", encoding="utf-8") as infile:
        if ndjson:
            data = [json.loads(line) for line in infile]
        else:
            data = json.load(infile)

        return data


def from_yaml(path: pathlib.Path | str) -> dict:
    """Read data from a YAML file"""
    with open(pathlib.Path(path), mode="r", encoding="utf-8") as infile:
        return yaml.load(infile, Loader=yaml.Loader)
