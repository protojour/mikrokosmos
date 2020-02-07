"""
Mikrokosmos – A (test) data generator and scenario simulation framework

Copyright © 2020 Protojour AS, licensed under MIT.
See LICENSE.txt for details.
"""

import json
import time

import attr
import click
import pendulum
import yaml
from faker import Faker

from .utils import recursive_resolve


@click.group()
def mikro():
    """
    Mikrokosmos – A (test) data generator and scenario simulation framework
    """
    pass


@mikro.command()
@click.argument(
    'scenario', type=click.File('r')
)
@click.option(
    '-n', '--indent',
    default=0, show_default=True,
    help='JSON output indentation'
)
def gen(scenario, indent):
    """
    Generate static data from a scenario.

    Generates objects defined in the scenario's classes.
    Output is written to stdout.
    """

    scenario_dict = yaml.safe_load(scenario)
    scenario_name = scenario_dict.get('name')

    seed = scenario_dict.get('seed', time.time())
    Faker.seed(seed)

    locale = scenario_dict.get('locale', 'en_IE')
    fake = Faker(locale)

    time_start = pendulum.parse(scenario_dict.get('time_start'))
    time_end = pendulum.parse(scenario_dict.get('time_end'))
    scenario_dict[time_start] = time_start
    scenario_dict[time_end] = time_end

    objects = []
    for cls in scenario_dict['classes']:

        name = cls['name']
        count = cls['count']
        schema = cls['schema']

        attributes = {}
        for key, values in cls['attributes'].items():

            if isinstance(values, list):
                value, *args = values
            else:
                value, args = values, []

            factory = lambda v=value: v

            if value and 'self.' in value:
                _, _attr = value.split('.', 1)
                factory = lambda self, attr=_attr: getattr(self, attr)

            elif value and 'scenario.' in value:
                _, _attr = value.split('.', 1)
                factory = lambda self, scenario_dict=scenario_dict, key=_attr: scenario_dict[key]

            elif value and 'faker.' in value:
                _, provider = value.split('.', 1)
                factory = lambda self, provider=provider, args=args: fake.format(provider, *args)

            attributes[key] = attr.ib(default=attr.Factory(factory, takes_self=True))

        Class = attr.make_class(
            name=name,
            attrs=attributes
        )

        for i in range(count):
            obj = Class()
            objects.append(recursive_resolve(schema, obj))

    output = json.dumps(objects, indent=indent)
    click.echo(output)


@mikro.command()
@click.argument(
    'scenario', type=click.File('r')
)
def run(scenario):
    """
    Run a scenario.

    Not yet implemented.
    """

    scenario_dict = yaml.safe_load(scenario)
    scenario_name = scenario_dict.get('name')

    click.echo(f'Running scenario {scenario_name}...')
    click.echo(f'Not yet implemented.')
