import json
import pathlib

import click

from unitelabs.cdk import utils
from unitelabs.cdk.config import get_connector_config
from unitelabs.cdk.main import load


@click.group(context_settings=dict(show_default=True))
def config() -> click.Group:
    """Configure a connector."""


@click.command()
@click.option(
    "--app",
    type=str,
    metavar="IMPORT",
    default=utils.find_factory,
    show_default=False,
    help="The application factory function to load, in the form 'module:name'.",
)
@click.option(
    "-p",
    "--path",
    type=click.Path(
        exists=False,
        dir_okay=False,
        writable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
    default=pathlib.Path("./schema.json"),
    help="Path to the configuration schema file.",
)
@utils.coroutine
async def schema(app, path: pathlib.Path) -> None:  # noqa: ANN001
    """Create a configuration jsonschema."""
    await load(app)
    config = get_connector_config().get_type_adapter()
    with path.open("w") as file:
        json.dump(config.json_schema(), file)


@click.command()
@click.option(
    "--app",
    type=str,
    metavar="IMPORT",
    default=utils.find_factory,
    show_default=False,
    help="The application factory function to load, in the form 'module:name'.",
)
@click.option(
    "--path",
    type=click.Path(
        exists=False,
        dir_okay=False,
        writable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
    default=pathlib.Path("./config.json"),
    help="Path to the configuration file.",
)
@utils.coroutine
async def create(app, path: pathlib.Path) -> None:  # noqa: ANN001
    """Create a configuration file."""
    await load(app)
    config = get_connector_config()
    default = config.get_default()
    config.from_dict(default).dump(path)


config.add_command(schema)
config.add_command(create)

if __name__ == "__main__":
    config()
