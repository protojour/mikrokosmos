import pytest

from pathlib import Path

from .conftest import runner
from mikrokosmos import mikro, __version__


def test_version():
    assert __version__ == '0.1.0'


def test_mikro(runner):
    result = runner.invoke(mikro)
    assert result.exit_code == 0


def test_mikro_gen(runner):
    scenario_path = str(Path('tests/test_scenario.yml').resolve())
    with runner.isolated_filesystem():

        result = runner.invoke(mikro, ['gen'])
        assert result.exit_code == 2
        assert 'Error: Missing argument "SCENARIO"' in result.output

        result = runner.invoke(mikro, ['gen', 'missing.yml'])
        assert result.exit_code == 2
        assert 'missing.yml: No such file or directory' in result.output

        result = runner.invoke(mikro, ['gen', scenario_path])
        assert result.exit_code == 0
        assert 'Brian Miller' in result.output

        result = runner.invoke(mikro, ['gen', '-i', '4', scenario_path])
        assert result.exit_code == 0
        assert '    ' in result.output


def test_mikro_run(runner):
    scenario_path = str(Path('tests/test_scenario.yml').resolve())
    with runner.isolated_filesystem():

        result = runner.invoke(mikro, ['run'])
        assert result.exit_code == 2
        assert 'Error: Missing argument "SCENARIO"' in result.output

        result = runner.invoke(mikro, ['run', 'missing.yml'])
        assert result.exit_code == 2
        assert 'missing.yml: No such file or directory' in result.output

        result = runner.invoke(mikro, ['run', scenario_path])
        assert result.exit_code == 0
        assert 'Running scenario' in result.output
