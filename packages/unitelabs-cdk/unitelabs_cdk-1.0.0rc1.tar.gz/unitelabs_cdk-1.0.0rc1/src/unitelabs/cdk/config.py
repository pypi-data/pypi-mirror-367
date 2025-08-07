import dataclasses
import functools
import json
import pathlib
import uuid

import pydantic
import typing_extensions as typing
import yaml
from pydantic import Field, model_validator
from pydantic import field_validator as validate_field

import sila

validate_config = functools.partial(model_validator, mode="after")


class ConfigurationError(ValueError):
    """Received an invalid configuration."""


class UnsupportedConfigFiletype(Exception):
    """The filetype is unsupported for reading/writing config files."""


@dataclasses.dataclass
class SILAServerConfig:
    """Configuration for a SiLA server."""

    hostname: str = "0.0.0.0"
    """The target hostname to bind to. Defaults to `0.0.0.0`."""

    port: int = 0
    """
    The target port to bind to. If set to `0` an available port is
    chosen at runtime. Defaults to `0`.
    """

    tls: bool = False
    """
    Whether to run a secure/TLS server or a plaintext server (i.e. no
    TLS), defaults to run with TLS encryption.
    """

    require_client_auth: bool = False
    """
    A boolean indicating whether or not to require clients to be
    authenticated. May only be True if root_certificates is not None.
    """

    root_certificates: typing.Optional[bytes] = None
    """
    The PEM-encoded root certificates as a byte string, or None to
    retrieve them from a default location chosen by gRPC runtime.
    """

    certificate_chain: typing.Union[str, pathlib.Path, bytes] = ""
    """
    The PEM-encoded certificate chain as a byte string to use or None
    if no certificate chain should be used.
    """

    private_key: typing.Union[str, pathlib.Path, bytes] = ""
    """
    The PEM-encoded private key as a byte string, or None if no
    private key should be used.
    """

    options: dict = dataclasses.field(default_factory=dict)
    """
    Additional options for the underlying gRPC connection.
    """

    uuid: str = dataclasses.field(default_factory=lambda: str(uuid.uuid4()))
    """
    Uniquely identifies the SiLA server. Needs to remain the same even after restarting the server.
    Follows the textual representation of UUIDs, e.g. "082bc5dc-18ae-4e17-b028-6115bbc6d21e".
    """

    name: str = "SiLA Server"
    """
    Human readable name of the SiLA server. This value is configurable during runtime via the SiLA
    Service feature's `set_server_name` command. Must not exceed 255 characters.
    """

    type: str = "ExampleServer"
    """
    Human readable identifier of the SiLA server used to describe the entity the server represents.
    Starts with a capital letter, continued by letters and digits up to a maximum of 255 characters.
    """

    description: str = ""
    """Describes the use and purpose of the SiLA Server."""

    version: str = "0.0.0"
    """
    The version of the SiLA server following the Semantic Versioning specification with pre-release
    identifiers separated by underscores, e.g. "3.19.373_mighty_lab_devices".
    """

    vendor_url: str = "https://sila-standard.com"
    """
    URL to the website of the vendor or the website of the product of this SiLA Server. Follows the
    Uniform Resource Locator specification in RFC 1738.
    """

    def __post_init__(self):
        if self.certificate_chain and isinstance(self.certificate_chain, (str, pathlib.Path)):
            self.certificate_chain = pathlib.Path(self.certificate_chain).resolve()
            if not self.certificate_chain.exists():
                msg = f"Certificate chain file not found: {self.certificate_chain}"
                raise FileNotFoundError(msg)
            self.certificate_chain = self.certificate_chain.read_bytes()
        if self.private_key and isinstance(self.private_key, (str, pathlib.Path)):
            self.private_key = pathlib.Path(self.private_key).resolve()
            if not self.private_key.exists():
                msg = f"Private key file not found: {self.private_key}"
                raise FileNotFoundError(msg)
            self.private_key = self.private_key.read_bytes()

    def to_dict(self) -> sila.server.ServerConfig:
        """Convert the configuration to a dictionary."""
        return sila.server.ServerConfig(**dataclasses.asdict(self))


@dataclasses.dataclass
class CloudServerConfig:
    """Configuration for a SiLA cloud server."""

    hostname: str = "localhost"
    """The target hostname to connect to."""

    port: int = 50000
    """The target port to connect to."""

    tls: bool = False
    """
    Whether to run a secure/TLS channel or a plaintext channel (i.e.
    no TLS), defaults to run with TLS encryption.
    """

    root_certificates: typing.Optional[bytes] = None
    """
    The PEM-encoded root certificates as a byte string, or None to
    retrieve them from a default location chosen by gRPC runtime.
    """

    certificate_chain: typing.Union[str, pathlib.Path, bytes] = ""
    """
    The PEM-encoded certificate chain as a byte string to use or None
    if no certificate chain should be used.
    """

    private_key: typing.Union[str, pathlib.Path, bytes] = ""
    """
    The PEM-encoded private key as a byte string, or None if no
    private key should be used.
    """

    reconnect_delay: float = 5.0
    """
    The time in ms to wait before reconnecting the channel after an
    error occurs.
    """

    options: dict = dataclasses.field(default_factory=dict)  # sila.framework.ChannelOptions
    """
    Additional options for the underlying gRPC connection.
    """

    def to_dict(self) -> sila.server.CloudServerConfig:
        """Convert the configuration to a dictionary."""
        return sila.server.CloudServerConfig(**dataclasses.asdict(self))

    def __post_init__(self):
        if self.certificate_chain and isinstance(self.certificate_chain, (str, pathlib.Path)):
            self.certificate_chain = pathlib.Path(self.certificate_chain).resolve()
            if not self.certificate_chain.exists():
                msg = f"Certificate chain file not found: {self.certificate_chain}"
                raise FileNotFoundError(msg)
            self.certificate_chain = self.certificate_chain.read_bytes()
        if self.private_key and isinstance(self.private_key, (str, pathlib.Path)):
            self.private_key = pathlib.Path(self.private_key).resolve()
            if not self.private_key.exists():
                msg = f"Private key file not found: {self.private_key}"
                raise FileNotFoundError(msg)
            self.private_key = self.private_key.read_bytes()


@dataclasses.dataclass
class ConnectorBaseConfig:
    """Base configuration for a UniteLabs SiLA2 Connector."""

    __pydantic_config__ = pydantic.ConfigDict(
        validate_assignment=True,
        revalidate_instances="always",
        use_attribute_docstrings=True,
    )

    environment: str = "development"
    sila_server: SILAServerConfig = dataclasses.field(default_factory=SILAServerConfig)
    cloud_server_endpoint: CloudServerConfig = dataclasses.field(default_factory=CloudServerConfig)

    def __post_init__(self):
        if isinstance(self.sila_server, dict):
            self.sila_server = SILAServerConfig(**self.sila_server)
        if isinstance(self.cloud_server_endpoint, dict):
            self.cloud_server_endpoint = CloudServerConfig(**self.cloud_server_endpoint)

    @classmethod
    def to_pydantic_dataclass(cls) -> type[typing.Self]:
        """Create a pydantic dataclass from the Config."""
        subclass = type(cls.__name__, (cls,), {})
        return pydantic.dataclasses.dataclass(subclass)

    @classmethod
    def get_type_adapter(cls) -> pydantic.TypeAdapter:
        """Get the type adapter for the configuration."""
        return pydantic.TypeAdapter(cls)

    @staticmethod
    def get_default() -> dict:
        """Get the default dictionary representation of the config."""
        config = get_connector_config()
        type_adapter = config.get_type_adapter()
        return json.loads(type_adapter.dump_json(config()))

    @classmethod
    def from_dict(cls, data: dict) -> typing.Self:
        """
        Create a new `ConnectorBaseConfig` instance from a dict, without validations.

        This function allows arbitrary additional data to be set on the Config object!

        This should only be used in contexts where the derived configuration is not present, e.g.
        `certificate` CLI where the subclass of `ConnectorBaseConfig` cannot be found.
        """
        fields = [field.name for field in dataclasses.fields(cls)]
        known_fields = {k: v for k, v in data.items() if k in fields}
        unknown_fields = {k: v for k, v in data.items() if k not in known_fields}

        cls.validate(known_fields)

        final = cls(**known_fields)
        for k, v in unknown_fields.items():
            setattr(final, k, v)

        return final

    @classmethod
    def validate(cls, values: typing.Optional[dict]) -> typing.Self:
        """
        Validate the configuration values.

        Args:
          values: The configuration values to validate.

        Returns:
          A validated `ConnectorBaseConfig` instance.
        """

        values = values if values is not None else {}

        if unknown_fields := [k for k in values if k not in [f.name for f in dataclasses.fields(cls)]]:
            msg = f"Provided field or fields {unknown_fields} are not valid for {cls.__name__} configuration."
            raise ConfigurationError(msg)

        try:
            configuration = cls.to_pydantic_dataclass()(**values)
        except pydantic.ValidationError as e:
            msg = f"Invalid configuration for {cls.__name__}: {e}"
            raise ConfigurationError(msg) from None

        return configuration

    @classmethod
    def load(cls, path: typing.Optional[pathlib.Path] = None) -> typing.Self:
        """
        Load a connector configuration from `path`.

        Args:
          path: The path to the configuration file, can be a yaml or json filetype,
            defaults to config.json in current working directory.
        """
        data = load_config_file(path)
        return cls.from_dict(data)

    def dump(self, path: pathlib.Path) -> None:
        """
        Write the current configuration to a file.

        Args:
          path: The path at which to write the configuration, may be yaml or json filetype.
        """
        data = dataclasses.asdict(self)
        if len(dataclasses.fields(self)) < len(self.__dict__.keys()):
            # enables dump when a config has been loaded from_dict
            known_fields = [f.name for f in dataclasses.fields(self)]
            additional_data = {k: v for k, v in self.__dict__.items() if k not in known_fields}
            for key, value in additional_data.items():
                data[key] = value

        if path.suffix == ".json":
            data = json.dumps(data)
        elif path.suffix in [".yaml", ".yml"]:
            data = yaml.dump(data)
        else:
            msg = f"Cannot write file to {path}. Only yaml and json filetypes are supported."
            raise UnsupportedConfigFiletype(msg)
        with path.open("w") as f:
            f.write(data)


def get_connector_config() -> type[ConnectorBaseConfig]:
    """Get the current connector configuration."""
    derived_configs = [c for c in ConnectorBaseConfig.__subclasses__() if c.__name__ != "ConnectorBaseConfig"]
    if len(derived_configs) > 1:
        msg = "Multiple configurations found. Please ensure only one subclass of ConnectorBaseConfig exists."
        raise ConfigurationError(msg)

    return derived_configs[0] if derived_configs else ConnectorBaseConfig


def load_config_file(path: typing.Optional[pathlib.Path] = None) -> dict:
    """
    Load in configuration data from a file.

    Args:
      path: The path to the configuration file, can be a yaml or json file,
        defaults to `./config.json`.
    """
    data = {}
    if path is None:
        path = pathlib.Path("./config.json").resolve()
        print(f"Assuming default path: {path}")  # noqa: T201, RUF100
    path.resolve()
    if not path.exists():
        msg = f"No config file found at path: {path}"
        raise FileNotFoundError(msg)
    if path.suffix == ".json":
        data = json.loads(path.read_text())
    elif path.suffix in (".yaml", ".yml"):
        data = yaml.safe_load(path.read_text())
    else:
        msg = f"Cannot read file at {path}. Only yaml and json filetypes are supported."
        raise UnsupportedConfigFiletype(msg)
    return data


__all__ = [
    "CloudServerConfig",
    "ConnectorBaseConfig",
    "Field",
    "SILAServerConfig",
    "get_connector_config",
    "load_config_file",
    "validate_config",
    "validate_field",
]
