import pathlib

import click

import sila
from unitelabs.cdk.config import get_connector_config


class MutuallyExclusiveOptions(Exception):
    """The option '--config-path' cannot be used with '--uuid' or '--host'."""


@click.group()
def certificate() -> None:
    """Handle certificates for TLS encryption."""


@certificate.command()
@click.option(
    "-cfg",
    "--config-path",
    type=click.Path(path_type=pathlib.Path, exists=True),
    required=False,
)
@click.option(
    "--uuid",
    type=str,
    required=False,
    help="The SiLA server's uuid.",
)
@click.option(
    "--host",
    type=str,
    required=False,
    help="The SiLA server's host address.",
)
@click.option(
    "--target",
    "-t",
    type=str,
    default=".",
    help="The output directory in which to store the certificate files.",
)
@click.option(
    "--update",
    "-U",
    type=bool,
    is_flag=True,
    default=False,
    help="Update the config's TLS values.",
)
def generate(config_path: pathlib.Path, uuid: str, host: str, target: str, update: bool) -> None:
    """Generate a new self-signed certificate according to the SiLA 2 specification."""
    config_cls = get_connector_config()
    if config_path and (uuid or host):
        msg = "The option '--config-path' cannot be used with '--uuid' or '--host'."
        raise MutuallyExclusiveOptions(msg)

    if config_path:
        config = config_cls.load(config_path)
        uuid = config.sila_server.uuid
        host = config.sila_server.hostname

    key, cert = sila.server.generate_certificate(uuid, host)

    directory = pathlib.Path(target)
    directory.mkdir(parents=True, exist_ok=True)

    cert_path = directory / "cert.pem"
    cert_path.write_bytes(cert)

    key_path = directory / "key.pem"
    key_path.write_bytes(key)

    if config_path:
        if not update:
            response = click.prompt("Do you want to update your configuration file? Enter Y/N")
            if response not in ["y", "Y", "yes", "YES"]:
                return

        config.sila_server.tls = True
        config.sila_server.private_key = str(key_path.resolve())
        config.sila_server.certificate_chain = str(cert_path.resolve())
        config.dump(config_path)


if __name__ == "__main__":
    certificate()
