#!/usr/bin/env python3
from typing import Any, Mapping, Sequence
import requests


def access_nested_map(nested_map: Mapping[str, Any], path: Sequence[str]) -> Any:
    current: Any = nested_map
    for key in path:
        current = current[key]
    return current


def get_json(url: str) -> Any:
    response = requests.get(url)
    return response.json()


def memoize(method):
    attr_name = f"_{method.__name__}"

    def wrapper(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, method(self))
        return getattr(self, attr_name)
    return property(wrapper)
