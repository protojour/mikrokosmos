"""
Mikrokosmos – A (test) data generator and scenario simulation framework

Copyright © 2020 Protojour AS, licensed under MIT.
See LICENSE.txt for details.
"""

import json
import random
import time

import attr
import click
import pendulum
import yaml
from faker import Faker

from .objects import resolve_attributes, recursive_resolve


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
    locale = scenario_dict.get('locale', 'en_IE')

    random.seed(seed)
    Faker.seed(seed)
    fake = Faker(locale)

    time_start = pendulum.parse(scenario_dict.get('time_start'))
    time_end = pendulum.parse(scenario_dict.get('time_end'))
    scenario_dict['time_start'] = time_start
    scenario_dict['time_end'] = time_end

    objects = []
    for cls in scenario_dict['classes']:

        print(cls)

        name = cls['name']
        count = cls['count']
        schema = cls['schema']

        @attr.s
        class Context:
            faker = attr.ib()
            scenario = attr.ib()

        ctx = Context(fake, scenario_dict)

        attributes = resolve_attributes(cls['attributes'], ctx)
        for key, factory in attributes.items():
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
