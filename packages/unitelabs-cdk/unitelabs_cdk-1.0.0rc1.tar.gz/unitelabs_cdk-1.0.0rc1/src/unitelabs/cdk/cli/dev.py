import asyncio
import logging

import click

from unitelabs.cdk import utils

from ..logging import configure_logging
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
    "-v",
    "--verbose",
    count=True,
    help="Increase the verbosity of the default logger. Use a custom log-config for fine grained handling.",
)
@utils.coroutine
async def dev(app: str, verbose: int) -> None:
    """Application Entrypoint."""
    import watchfiles

    configure_logging(log_level=logging.WARNING - verbose * 10)

    async def callback(changes: set[tuple[watchfiles.Change, str]]) -> None:
        """Receive file changes."""

        logger = logging.getLogger("Watcher")
        logger.info("Detected file change: %s", changes.pop()[1])

    await watchfiles.arun_process(".", target=process, args=(app, verbose), callback=callback)


def process(app: str, verbose: int) -> None:
    """Run the connector in a separate process."""

    configure_logging(log_level=logging.WARNING - verbose * 10)

    asyncio.run(run(app))
