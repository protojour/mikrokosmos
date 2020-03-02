"""Mikrokosmos object generation"""

import random

import attr


def recursive_resolve(data, obj):
    """Recurse through a nested data structure and format strings using attributes of obj"""

    if isinstance(data, dict):
        return {k: recursive_resolve(v, obj) for k, v in data.items()}
    elif isinstance(data, list):
        return [recursive_resolve(i, obj) for i in data]
    elif isinstance(data, str):
        return data.format(**vars(obj))
    else:
        return data


def resolve_value(value, args, kwargs, ctx):
    """Resolve an attribute value spec, return a lambda to call for the value"""

    try:
        _ = iter(value)
    except TypeError:
        return lambda self, value=value: value

    if 'self.' in value:
        _, att = value.split('.', 1)
        return lambda self, att=att: getattr(self, att)

    elif 'scenario.' in value:
        _, key = value.split('.', 1)
        return lambda self, key=key, ctx=ctx: ctx.scenario[key]

    elif 'faker' in value:
        try:
            provider = kwargs.pop('provider')
        except KeyError:
            _, provider = value.split('.', 1)
        return (
            lambda self, provider=provider, args=args, kwargs=kwargs, ctx=ctx:
                ctx.faker.format(provider, *args, **kwargs)
        )

    elif 'choice' in value:
        return lambda self, args=args: random.choice(args)

    return lambda self, value=value: value


def resolve_attributes(attributes, ctx):
    """Resolve a set of class attributes"""

    result_attributes = {}
    for key, value in attributes.items():

        args = []
        kwargs = {}

        if isinstance(value, dict):
            value, rest = list(value.items())[0]
            if isinstance(rest, dict):
                kwargs = rest
            elif isinstance(rest, list):
                args = rest
            else:
                args = [rest]
        if isinstance(value, list):
            value, *args = value

        for i, arg in enumerate(args):
            args[i] = resolve_value(arg, args, kwargs, ctx)(None)

        for k, v in kwargs.items():
            kwargs[k] = resolve_value(v, args, kwargs, ctx)(None)

        value = resolve_value(value, args, kwargs, ctx)

        result_attributes[key] = value

    return result_attributes
