"""
Mikrokosmos – A (test) data generator and scenario simulation framework

Copyright © 2020 Protojour AS, licensed under MIT.
See LICENSE.txt for details.
"""

import json

import click
import yaml

from .objects import resolve_objects


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

    Generates objects defined in the scenario's list of objects.
    Output is written to stdout.
    """

    scenario_dict = yaml.safe_load(scenario)

    objects = resolve_objects(scenario_dict)
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
