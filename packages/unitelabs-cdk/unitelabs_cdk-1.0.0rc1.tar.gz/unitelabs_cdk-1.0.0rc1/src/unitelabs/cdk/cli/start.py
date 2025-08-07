import logging
import pathlib
import typing

import click

from unitelabs.cdk import utils
from unitelabs.cdk.config import get_connector_config, load_config_file
from unitelabs.cdk.logging import configure_logging

from ..main import run


class TLSConfigurationError(Exception):
    """TLS Configuration is invalid."""


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
    "-cfg",
    "--config-path",
    type=click.Path(path_type=pathlib.Path),
    default=pathlib.Path("./config.json"),
    help="Path to the configuration file.",
)
@click.option(
    "-v",
    "--verbose",
    count=True,
    help="Increase the verbosity of the default logger. Use a custom log-config for fine grained handling.",
)
@click.option(
    "--log-config",
    type=click.Path(exists=True),
    default=None,
    help="The path to the logging configuration file. Supported formats: .ini, .json, .yaml.",
)
@utils.coroutine
async def start(app, config_path: pathlib.Path, verbose: int, log_config: typing.Optional[str]) -> None:  # noqa: ANN001
    """Application Entrypoint."""

    configure_logging(log_config, logging.WARNING - verbose * 10)
    try:
        config = load_config_file(config_path)
    except FileNotFoundError:
        print("No config file was found or provided, creating a default configuration.")  # noqa: T201,RUF100
        config = get_connector_config().get_default()

    await run(app, config=config)
