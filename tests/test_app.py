from typer.testing import CliRunner

from todoist_cli import __version__
from todoist_cli.app import app

runner = CliRunner()


def test_help_includes_global_options() -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "--token" in result.output
    assert "--format" in result.output
    assert "--base-url" in result.output
    assert "--verbose" in result.output
    assert "--no-color" in result.output
    assert "tasks" in result.output
    assert "projects" in result.output


def test_version_option() -> None:
    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert __version__ in result.output
