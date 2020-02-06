"""Mikrokosmos utilitiy functions"""


def recursive_resolve(data, obj):
    """Recurse through a nested data structure and format strings using attributes of obj"""

    if isinstance(data, dict):
        return {k: recursive_resolve(v, obj) for k, v in data.items()}
    elif isinstance(data, list):
        return [recursive_resolve(i, obj) for i in data]
    elif isinstance(data, str):
        return data.format(**vars(obj))
    else:
        return
