from unittest.mock import MagicMock, patch

import pytest

from mikrokosmos.objects import *


def test_recursive_resolve():

    data = {
        'a': {
            'key': 'value',
            'test': '{a}',
        },
        'b': ['value', '{b}'],
        'c': '{c}',
        'd': 'test'
    }
    obj = MagicMock()
    obj.a = 'a'
    obj.b = 'b'
    obj.c = 'c'

    assert recursive_resolve({}, obj) == {}
    assert recursive_resolve([], obj) == []
    assert recursive_resolve('test', obj) == 'test'
    assert recursive_resolve(1, obj) == 1
    assert recursive_resolve(0, obj) == 0
    assert recursive_resolve(None, obj) is None
    assert recursive_resolve(data, obj) == {
        'a': {
            'key': 'value',
            'test': 'a',
        },
        'b': ['value', 'b'],
        'c': 'c',
        'd': 'test'
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
    with patch('mikrokosmos.objects.resolve_value', side_effect=resolve):
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
