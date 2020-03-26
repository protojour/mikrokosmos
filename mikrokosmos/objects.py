"""Mikrokosmos object generation"""

import ast
import operator
import random
import time

import attr
from faker import Faker


def recursive_resolve(data, obj, trigger=None, triggers=[]):
    """Recurse through a nested data structure and format strings using attributes of obj and triggers"""

    if isinstance(data, dict):
        if 'triggers' in data:
            return [recursive_resolve(data['triggers'], obj, trigger, triggers) for trigger in triggers]
        return {k: recursive_resolve(v, obj, trigger, triggers) for k, v in data.items()}
    elif isinstance(data, list):
        return [recursive_resolve(i, obj, trigger, triggers) for i in data]
    elif isinstance(data, str):
        if 'self.' in data:
            _, att = data.split('.', 1)
            return getattr(obj, att)
        if 'trigger.' in data:
            _, att = data.split('.', 1)
            return getattr(trigger, att)
        else:
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
    """Resolve a set of object attributes"""

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


def resolve_trigger(trigger):
    """Resolve a trigger"""

    source, op, literal = trigger.split(' ')
    cls, field = source.split('.')

    OPS_MAP = {
        'in': 'contains',
        '<':  'lt',
        '<=': 'le',
        '==': 'eq',
        '!=': 'ne',
        '>=': 'ge',
        '>':  'gt',
    }

    if op not in OPS_MAP:
        raise ValueError('Invalid operator')

    comp_func = getattr(operator, OPS_MAP[op])
    value = ast.literal_eval(literal)

    return cls, field, comp_func, value


def resolve_class(cls, ctx):
    """Resolve a class"""

    name = cls.get('name')

    attributes = resolve_attributes(cls.get('attributes'), ctx)
    for key, factory in attributes.items():
        attributes[key] = attr.ib(default=attr.Factory(factory, takes_self=True))

    Class = attr.make_class(
        name=name,
        attrs=attributes
    )

    return Class


def resolve_objects(scenario):
    """Resolve a set of classes, generate objects, resolve objects"""

    set_seed(scenario)
    faker = init_faker(scenario)

    @attr.s
    class Context:
        faker = attr.ib()
        scenario = attr.ib()

    ctx = Context(faker, scenario)

    objects = []
    triggered_objects = []
    outputs = []

    classes = [
        cls for cls in scenario['objects']
        if cls.get('count')
    ]
    triggered_classes = [
        cls for cls in scenario['objects']
        if (cls.get('trigger') or cls.get('triggers'))
    ]

    for cls in classes:
        Class = resolve_class(cls, ctx)

        output = cls.get('output')

        for i in range(cls.get('count')):
            obj = Class()
            objects.append(obj)

            if output:
                resolved_output = recursive_resolve(output, obj)
                outputs.append(resolved_output)

    for cls in triggered_classes:
        Class = resolve_class(cls, ctx)

        triggers = [cls.get('trigger')]
        if not triggers[0]:
            triggers = cls.get('triggers')

        trigger_objs = []

        for obj in objects:
            obj_class = obj.__class__.__name__

            for trigger in triggers:

                tri_class, field, comp_func, tri_value = resolve_trigger(trigger)
                obj_value = getattr(obj, field)

                if obj_class == tri_class and comp_func(obj_value, tri_value):
                    if obj not in trigger_objs:
                        trigger_objs.append(obj)

        output = cls.get('output')

        def gen_obj_output(trigger_obj):
            obj = Class()
            triggered_objects.append(obj)

            if output:
                resolved_output = recursive_resolve(output, obj, trigger_obj, trigger_objs)
                outputs.append(resolved_output)

        # TODO: This is crazy wrong, but will do for now
        if len(triggers) > 1:
            gen_obj_output(trigger_objs[0])
        else:
            for trigger_obj in trigger_objs:
                gen_obj_output(trigger_obj)

    return outputs


def set_seed(scenario):
    seed = scenario.get('seed', time.time())
    random.seed(seed)
    Faker.seed(seed)


def init_faker(scenario):
    locale = scenario.get('locale', 'en_US')
    return Faker(locale)
