from unittest.mock import MagicMock, patch

import pytest

from mikrokosmos.objects import *


def test_recursive_resolve():

    obj = MagicMock()
    obj.a = 'a'
    obj.b = 'b'
    obj.c = 123
    obj.d = [1, 2, 3]
    obj.e = None

    assert recursive_resolve({}, obj) == {}
    assert recursive_resolve([], obj) == []
    assert recursive_resolve('test', obj) == 'test'
    assert recursive_resolve(1, obj) == 1
    assert recursive_resolve(0, obj) == 0
    assert recursive_resolve(None, obj) is None

    data = {
        'a': {
            'key': 'value',
            'test': '{a}',
        },
        'b': ['value', '{b}'],
        'c': 'self.c',
        'd': 'self.d',
        'e': 'self.e',
        'f': 'test',
        'g': {
            'triggers': {
                'a': 'trigger.a',
                'b': 'trigger.b',
            },
        },
    }

    trigger_1 = MagicMock()
    trigger_1.a = '1a'
    trigger_1.b = '1b'

    trigger_2 = MagicMock()
    trigger_2.a = '2a'
    trigger_2.b = '2b'

    triggers = [
        trigger_1,
        trigger_2
    ]

    assert recursive_resolve(data, obj, None, triggers) == {
        'a': {
            'key': 'value',
            'test': 'a',
        },
        'b': ['value', 'b'],
        'c': 123,
        'd': [1, 2, 3],
        'e': None,
        'f': 'test',
        'g': [
            {
                'a': '1a',
                'b': '1b'
            },
            {
                'a': '2a',
                'b': '2b'
            }
        ],
    }


def test_resolve_value():

    ctx = MagicMock()
    self = MagicMock()

    basic_values = [None, 0, 1, 'test']
    args = []
    kwargs = {}
    for value in basic_values:
        assert resolve_value(value, args, kwargs, ctx)(self) == value

    value = 'self.test'
    self.test = 'test value'
    assert resolve_value(value, args, kwargs, ctx)(self) == 'test value'

    value = 'scenario.name'
    ctx.scenario = {'name': 'name value'}
    assert resolve_value(value, args, kwargs, ctx)(self) == 'name value'

    value = 'faker.thing'
    ctx.faker.format = MagicMock(return_value='thing value')
    assert resolve_value(value, args, kwargs, ctx)(self) == 'thing value'
    ctx.faker.format.assert_called_with('thing', *args, **kwargs)

    value = 'choice'
    args = ['a', 'b', 'c']
    assert resolve_value(value, args, kwargs, ctx)(self) in args


def test_resolve_attributes():

    ctx = MagicMock()
    self = MagicMock()

    attributes = {}
    assert resolve_attributes(attributes, ctx) == {}

    attributes = {
        'a': None,
        'b': 0,
        'c': 1,
        'd': 'test',
    }
    resolved = resolve_attributes(attributes, ctx)
    for key in resolved:
        assert resolved[key](self) == attributes[key]

    resolve = MagicMock(return_value=lambda self: 'resolved value')
    with patch('mikrokosmos.objects.resolve_value', resolve):
        attributes = {
            'attribute': {
                'to_resolve': 'arg'
            }
        }
        resolved = resolve_attributes(attributes, ctx)
        assert resolved['attribute'](self) == 'resolved value'
        resolve.assert_called_with('to_resolve', ['resolved value'], {}, ctx)

        attributes = {
            'attribute': {
                'to_resolve': {'kw': 'arg'}
            }
        }
        resolved = resolve_attributes(attributes, ctx)
        assert resolved['attribute'](self) == 'resolved value'
        resolve.assert_called_with('to_resolve', [], {'kw': 'resolved value'}, ctx)

        attributes = {
            'attribute': {
                'to_resolve': ['arg']
            }
        }
        resolved = resolve_attributes(attributes, ctx)
        assert resolved['attribute'](self) == 'resolved value'
        resolve.assert_called_with('to_resolve', ['resolved value'], {}, ctx)

        attributes = {
            'attribute': ['to_resolve', 'arg']
        }
        resolved = resolve_attributes(attributes, ctx)
        assert resolved['attribute'](self) == 'resolved value'
        resolve.assert_called_with('to_resolve', ['resolved value'], {}, ctx)


def test_resolve_trigger():

    pass # in flux


def test_resolve_class():

    pass # in flux


def test_resolve_objects():

    pass # in flux


def test_set_seed():

    time_mock = MagicMock(return_value=0)
    with patch('time.time', time_mock):
        scenario = {}
        set_seed(scenario)
        time_mock.assert_called_once()
        assert random.randint(1, 100) == 50
        assert Faker().random_int() == 6311

    scenario = {
        'seed': 123
    }
    set_seed(scenario)
    assert random.randint(1, 100) == 7
    assert Faker().random_int() == 857


def test_init_faker():

    scenario = {}
    faker = init_faker(scenario)
    assert faker._locales == ['en_US']

    scenario = {
        'locale': 'no_NO'
    }
    faker = init_faker(scenario)
    assert faker._locales == ['no_NO']
