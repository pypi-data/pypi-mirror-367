import dataclasses
import gc
import json
import re
import uuid

import pydantic
import pytest
import typing_extensions as typing
import yaml

from unitelabs.cdk.config import (
    CloudServerConfig,
    ConfigurationError,
    ConnectorBaseConfig,
    Field,
    SILAServerConfig,
    UnsupportedConfigFiletype,
    get_connector_config,
    load_config_file,
    validate_config,
    validate_field,
)


@pytest.fixture
def cleanup():
    """Garbage collect derived Config classes to ensure `get_connector_config` finds only one subclass."""
    yield
    gc.collect()


BASE_CONFIG_DEFAULT = {
    "environment": "development",
    "sila_server": {
        "hostname": "0.0.0.0",
        "port": 0,
        "tls": False,
        "require_client_auth": False,
        "root_certificates": None,
        "certificate_chain": "",
        "private_key": "",
        "options": {},
        "name": "SiLA Server",
        "type": "ExampleServer",
        "description": "",
        "version": "0.0.0",
        "vendor_url": "https://sila-standard.com",
    },
    "cloud_server_endpoint": {
        "hostname": "localhost",
        "port": 50000,
        "tls": False,
        "root_certificates": None,
        "certificate_chain": "",
        "private_key": "",
        "reconnect_delay": 5.0,
        "options": {},
    },
}
CERT = """
-----BEGIN CERTIFICATE-----
MIIC/jCCAeagAwIBAgIURXGhJmigNdNvgR3wMdlsv43VhCEwDQYJKoZIhvcNAQEL
BQAwEDEOMAwGA1UEAwwFU2lMQTIwHhcNMjQxMDA5MTMwNDU1WhcNMjUxMDA5MTMw
NDU1WjAQMQ4wDAYDVQQDDAVTaUxBMjCCASIwDQYJKoZIhvcNAQEBBQADggEPADCC
AQoCggEBAMCSToXHEzV76zHO3pATJ+M3zRqnbZ9KwyGJzWCA7jmZZWkCligW7QgQ
COf8AdOcf5eZawop63HeDDqkuQtAAKwOUiVjLgoPXpu9l9lxDSBo1XfquTIvgNGY
wN7i2W9zQQ0U78iBJ7+xcEbkf9m/s5yyKXGOds1apBVx184Qb2MKnGc2mK6WkRf3
uIBBj/o3JzNlEu040zIok/A/DtRimgoxOipjzbLYRq5xLtod1tpyw1lsQGctfCNi
27bYApcA2UUpy0PG8BUMbT2jkwLTkruKrfx9x4tcHL3PH9s0oXWzijKFw8seAx15
LIhoyjonygZeoKaEAkT2Rv+WzGeUDRsCAwEAAaNQME4wGgYDVR0RBBMwEYIJbG9j
YWxob3N0hwR/AAABMDAGCCsGAQQBg8lXBCQ1YThmZGI3MS1lZTIzLTQ1MmMtODM1
Yy1lMjI0ZGY3YmU5NTAwDQYJKoZIhvcNAQELBQADggEBAF9NbU6GItVjepD1w4UA
2V4UUfcrKdk9xO0FVEF/lRyPoRaoKzO08k5AJ47tmjqqqpijzYXspKta+UEMiAUE
qoCRhgLCvtrAIp7nhsCNw7fyK+i+866q1dyB2VogDbLwxyAj4nxd4o2flWNPaTqr
XgQ9xGuww3Izngr+MGFKsE9CJ7b5emq67lfGQ8UkwvfU2XhcPWPJAyHi2kQPVXFk
UmmzQoqnqELfSNpnd5zUrgdVVtABHZ+rsCJpldU0yO5OQ4pfm+f56VmS2Da2vDZt
GkEfLq/po/VTGOB6bZ1oV+kR+ZHbRpCh0mAQ+OvuUuWOAmuQ30m26nA+w7+VyLux
ht4=
-----END CERTIFICATE-----

"""
KEY = """
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEAwJJOhccTNXvrMc7ekBMn4zfNGqdtn0rDIYnNYIDuOZllaQKW
KBbtCBAI5/wB05x/l5lrCinrcd4MOqS5C0AArA5SJWMuCg9em72X2XENIGjVd+q5
Mi+A0ZjA3uLZb3NBDRTvyIEnv7FwRuR/2b+znLIpcY52zVqkFXHXzhBvYwqcZzaY
rpaRF/e4gEGP+jcnM2US7TjTMiiT8D8O1GKaCjE6KmPNsthGrnEu2h3W2nLDWWxA
Zy18I2LbttgClwDZRSnLQ8bwFQxtPaOTAtOSu4qt/H3Hi1wcvc8f2zShdbOKMoXD
yx4DHXksiGjKOifKBl6gpoQCRPZG/5bMZ5QNGwIDAQABAoIBAE023PFbH2Kkq2uv
TSJr6+R5rW3wkE38xj0eahE14U+LKFRwyxCMEMLY2xlZvMnCyI5a38aVhGiF5lVl
UyUlpp9Wpq2DFSTHgOHlpYt0fxTttBp/LX7n+TkRjNRSFWlQx1adfH/i+bMtTJ3A
ZVtEOJqt/VwhCZXRsFVA7o0bne4R0VZZW/5eDH4nF9JNQsvOo2Qrcx7fRzld4khx
7Y3lbf363RQndONdJ7znPMZMd1RzFWygsjbU8vjcL2rA7bDEHLkqKc6er+RDPTWq
SgnMT2vL/+lzQxuf59JaIBU3nJA02+8jLWjMpRLSbvnNuxV/YN4j9+tzC5ChPm/4
+3HnwBECgYEA/0EtN1hl8SbwEAz+hoVB6pOhjIPOBrKqT/1xRLyPPGt5zlM3vFmc
o60LV5hcWI7dajd4TRc6mYZEYpMkWPY9FQKSANH1WmHwp9rRUwDyTCn6xvza5dk/
cV1ZnvMMjwfKi531NhZQerA4Fg/3CoiToBXIWRBl4+Vhh2Tx1mcUuA8CgYEAwSJE
+nbESRR5rbKEC1Yezc+RuxzhVqIWApOVZx29O6VLMmlL+O1ZiK6Z08YUNNno6otc
Lnhi3I5bv2O5CS4ubUpqtwLuOKKJPLdx8ZBh5aJ/1LVfEmqih58FxzYiZ3+Hfsjy
PaqSwEDp3CcShZ6Tzz8eaeJFaG9k56a659QU7jUCgYAaG2FzirAKhTAChEG4IoMG
agkY5RY6ayWuPr7KB/sic9+mca5+ri+uMfG6CNRRHnOY/IlqYRjWQPxXlLMgAjdn
IbcrLE5K6z+A+4lzUuJ1VcnXdl8xKRIrFyAmeLdtHZ/ivcopuQiMM9/YqdNbmXJ3
6iJusZWqRHjAL1vo0Ow2kwKBgQCNhKTyupA91IkMpCBphiNwP8bTSug7aO2j2azC
MGJ3EDm3qLyInLLcmsQRD7XCvGIVaySS0JfwcUf9R/9QIMzYPI1RqQ4R5deV6/3M
OjXh5F6y6GvPvN93bSj4vkwbdrE8T9ZhJVn/EhHKxb6mtnoshF2uzKR7UBSqQdv2
/8qOeQKBgQDdWqFawsUcMZmq3faoipofg0Gl8pZiKYjVOV5QBz8z2mxxUuHGB3VQ
17kBvR3rnhbyhj/kS0rq7mKib+8K9WjKeZr/ypr1oiOSXKPm5UqZTctFcAqkvgyE
Sz0JRTsDjVBHrdnbVUF6QNh+hqTkqYGMu2RcArnvmMdnQ5D1jMfe0A==
-----END RSA PRIVATE KEY-----

"""


class TestInnerTypes:
    def test_sila_server_conversion(self):
        default = ConnectorBaseConfig.get_default()
        instance = ConnectorBaseConfig(**default)
        assert isinstance(instance.sila_server, SILAServerConfig)

    @pytest.mark.parametrize(
        "path,content,key", [("cert.pem", CERT, "certificate_chain"), ("key.pem", KEY, "private_key")]
    )
    def test_sila_server_cert_key_conversion(self, tmp_path, path, content, key):
        path = tmp_path / path
        path.touch()
        path.write_bytes(content.encode("ascii"))

        default = ConnectorBaseConfig.get_default()
        default["sila_server"][key] = path

        config = ConnectorBaseConfig(**default)
        assert isinstance(getattr(config.sila_server, key), bytes)
        assert getattr(config.sila_server, key).decode("ascii") == content

    def test_cloud_server_endpoint_conversion(self):
        default = ConnectorBaseConfig.get_default()
        instance = ConnectorBaseConfig(**default)
        assert isinstance(instance.cloud_server_endpoint, CloudServerConfig)

    @pytest.mark.parametrize(
        "path,content,key", [("cert.pem", CERT, "certificate_chain"), ("key.pem", KEY, "private_key")]
    )
    def test_cloud_server_endpoint_cert_key_conversion(self, tmp_path, path, content, key):
        path = tmp_path / path
        path.touch()
        path.write_bytes(content.encode("ascii"))

        default = ConnectorBaseConfig.get_default()
        default["cloud_server_endpoint"][key] = path

        config = ConnectorBaseConfig(**default)
        assert isinstance(getattr(config.cloud_server_endpoint, key), bytes)
        assert getattr(config.cloud_server_endpoint, key).decode("ascii") == content

    @pytest.mark.parametrize("key,name", [("certificate_chain", "Certificate chain"), ("private_key", "Private key")])
    def test_sila_server_cert_key_file_not_found(self, key, name):
        default = ConnectorBaseConfig.get_default()
        default.update({"sila_server": {f"{key}": "path.json"}})
        with pytest.raises(FileNotFoundError, match=rf"{name} file not found:"):
            ConnectorBaseConfig(**default)

    @pytest.mark.parametrize("key,name", [("certificate_chain", "Certificate chain"), ("private_key", "Private key")])
    def test_cloud_server_endpoint_cert_key_file_not_found(self, key, name):
        default = ConnectorBaseConfig.get_default()
        default.update({"cloud_server_endpoint": {f"{key}": "path.json"}})
        with pytest.raises(FileNotFoundError, match=rf"{name} file not found:"):
            ConnectorBaseConfig(**default)


class TestToPydanticDataclass:
    def test_should_not_alter_class(self, cleanup):
        @dataclasses.dataclass
        class ExampleConfig(ConnectorBaseConfig):
            value: int = 0

        pydantic_dataclass = ExampleConfig.to_pydantic_dataclass()
        assert pydantic.dataclasses.is_pydantic_dataclass(pydantic_dataclass)
        assert not pydantic.dataclasses.is_pydantic_dataclass(ExampleConfig)

    def test_returned_class_creates_instances_of_class(self, cleanup):
        @dataclasses.dataclass
        class ExampleConfig(ConnectorBaseConfig):
            value: int = 0

        pydantic_dataclass = ExampleConfig.to_pydantic_dataclass()
        instance = pydantic_dataclass()
        assert isinstance(instance, ExampleConfig)


class TestGetDefault:
    def test_base_default(self):
        default = ConnectorBaseConfig.get_default()
        # set the uuid as this is generated from a function
        BASE_CONFIG_DEFAULT["sila_server"]["uuid"] = default["sila_server"]["uuid"]
        assert default == BASE_CONFIG_DEFAULT

    def test_added_keys_included(self, cleanup):
        @dataclasses.dataclass
        class ExampleConfig(ConnectorBaseConfig):
            a: int = 0
            b: float = 0.0
            c: str = ""
            d: bool = True
            e: list[str] = dataclasses.field(default_factory=list)
            f: dict[str, int] = dataclasses.field(default_factory=dict)

        default = ExampleConfig.get_default()
        for value in ["a", "b", "c", "d", "e", "f"]:
            assert value in default


class TestFromDict:
    def test_type_conversion(self):
        default = ConnectorBaseConfig.get_default()
        instance = ConnectorBaseConfig.from_dict(default)
        assert isinstance(instance.sila_server, SILAServerConfig)
        assert isinstance(instance.cloud_server_endpoint, CloudServerConfig)

    def test_should_allow_arbitrary_fields(self):
        default = ConnectorBaseConfig.get_default()
        default["this"] = "that"
        instance = ConnectorBaseConfig.from_dict(default)
        assert instance.this == "that"

    def test_should_validate_known_fields(self):
        default = ConnectorBaseConfig.get_default()
        default["sila_server"]["port"] = "invalid"
        with pytest.raises(
            ConfigurationError,
            match="Invalid configuration for ConnectorBaseConfig: "
            "1 validation error for ConnectorBaseConfig\n"
            "sila_server.port\n  "
            "Input should be a valid integer, unable to parse string as an integer",
        ):
            ConnectorBaseConfig.from_dict(default)


class TestFieldValidation:
    def test_basic_validation(self, cleanup):
        @dataclasses.dataclass
        class ExampleConfig(ConnectorBaseConfig):
            value: int = 0

        with pytest.raises(
            ConfigurationError,
            match="Invalid configuration for ExampleConfig: "
            "1 validation error for ExampleConfig\n"
            "value\n  "
            "Input should be a valid integer, unable to parse string as an integer",
        ):
            ExampleConfig.validate({"value": "string"})

    def test_validation_with_field_annotation(self, cleanup):
        @dataclasses.dataclass
        class ExampleConfig(ConnectorBaseConfig):
            large_int: typing.Annotated[int, Field(gt=9000)] = 9001

        default = ExampleConfig.get_default()
        assert ExampleConfig.validate(default)

        default.update({"large_int": 29})
        with pytest.raises(
            ConfigurationError,
            match="Invalid configuration for ExampleConfig: 1 validation error for ExampleConfig"
            "\nlarge_int"
            "\n  Input should be greater than 9000",
        ):
            ExampleConfig.validate(default)

    def test_validation_with_validate_field_decorator(self, cleanup):
        @dataclasses.dataclass
        class ExampleConfig(ConnectorBaseConfig):
            simple: bool = False

            @validate_field("simple")
            @classmethod
            def must_be_true(cls, value: bool) -> bool:
                if not value:
                    msg = "simple must be True."
                    raise ConfigurationError(msg)
                return value

        default = ExampleConfig.get_default()
        with pytest.raises(
            ConfigurationError,
            match="Invalid configuration for ExampleConfig: 1 validation error for ExampleConfig"
            "\nsimple"
            "\n  Value error, simple must be True.",
        ):
            ExampleConfig.validate(default)

        default.update({"simple": True})
        assert ExampleConfig.validate(default)

    def test_validation_with_validate_config_decorator(self, cleanup):
        @dataclasses.dataclass
        class ExampleConfig(ConnectorBaseConfig):
            complex: bool = False
            complex_name: typing.Optional[str] = ""

            @validate_config()
            def must_be_true(self) -> typing.Self:
                if self.complex and not self.complex_name:
                    msg = "complex configuration requires additional complex_name value."
                    raise ConfigurationError(msg)
                return self

        default = ExampleConfig.get_default()
        config = ExampleConfig.validate(default)

        assert hasattr(config, "complex")
        assert hasattr(config, "complex_name")

        with pytest.raises(
            ConfigurationError,
            match="Invalid configuration for ExampleConfig: 1 validation error for ExampleConfig"
            "\n  Value error, complex configuration requires additional complex_name value.",
        ):
            default.update({"complex": True})
            ExampleConfig.validate(default)

    def test_should_raise_for_invalid_field_name(self, cleanup):
        @dataclasses.dataclass
        class ExampleConfig(ConnectorBaseConfig):
            value: bool = False

        with pytest.raises(
            ConfigurationError,
            match=re.escape(
                "Provided field or fields ['invalid_field'] are not valid for ExampleConfig configuration."
            ),
        ):
            ExampleConfig.validate({"invalid_field": True, "value": True})


class TestLoad:
    def test_should_load_yaml_file(self, tmp_path):
        config_file_path = tmp_path / "config.yaml"
        config = BASE_CONFIG_DEFAULT.copy()
        config["sila_server"]["uuid"] = str(uuid.uuid4())
        with config_file_path.open("w") as f:
            yaml.dump(config, f)

        instance = ConnectorBaseConfig.load(config_file_path)
        data = dataclasses.asdict(instance)
        assert data == config

    def test_should_load_json_file(self, tmp_path):
        config_file_path = tmp_path / "config.json"
        config = BASE_CONFIG_DEFAULT.copy()
        config["sila_server"]["uuid"] = str(uuid.uuid4())
        with config_file_path.open("w") as f:
            json.dump(config, f)

        instance = ConnectorBaseConfig.load(config_file_path)
        data = dataclasses.asdict(instance)
        assert data == config

    @pytest.mark.parametrize("ext", ["toml", "ini"])
    def test_should_raise_unsupported_filetype(self, tmp_path, ext):
        config_file_path = tmp_path / f"config.{ext}"
        config_file_path.touch()
        with pytest.raises(
            UnsupportedConfigFiletype,
            match=f"Cannot read file at {config_file_path.resolve()}. Only yaml and json filetypes are supported.",
        ):
            ConnectorBaseConfig.load(config_file_path)


class TestDump:
    def test_should_dump_yaml_file(self, tmp_path):
        config_file_path = tmp_path / "config.yaml"
        config = BASE_CONFIG_DEFAULT.copy()
        config["sila_server"]["uuid"] = str(uuid.uuid4())

        ConnectorBaseConfig.from_dict(config).dump(config_file_path)

        with config_file_path.open("r") as f:
            data = yaml.safe_load(f)

        assert data == config

    def test_should_dump_json_file(self, tmp_path):
        config_file_path = tmp_path / "config.json"
        config = BASE_CONFIG_DEFAULT.copy()
        config["sila_server"]["uuid"] = str(uuid.uuid4())

        ConnectorBaseConfig.from_dict(config).dump(config_file_path)

        with config_file_path.open("r") as f:
            data = json.load(f)

        assert data == config

    @pytest.mark.parametrize("ext", ["toml", "ini"])
    def test_should_raise_unsupported_filetype(self, tmp_path, ext):
        config_file_path = tmp_path / f"config.{ext}"
        config_file_path.touch()

        config = BASE_CONFIG_DEFAULT.copy()
        config["sila_server"]["uuid"] = str(uuid.uuid4())

        instance = ConnectorBaseConfig.from_dict(config)
        with pytest.raises(
            UnsupportedConfigFiletype,
            match=f"Cannot write file to {config_file_path.resolve()}. Only yaml and json filetypes are supported.",
        ):
            instance.dump(config_file_path)


class TestGetConnectorConfig:
    def test_should_return_base_if_no_derived_config_exists(self):
        assert get_connector_config() == ConnectorBaseConfig

    def test_should_find_derived_config(self, cleanup):
        class ExampleConfig(ConnectorBaseConfig):
            value: bool = False

        assert get_connector_config() == ExampleConfig

    def test_should_raise_for_multiple_configs(self, cleanup):
        @dataclasses.dataclass
        class ExampleConfig(ConnectorBaseConfig):
            simple: bool = False

        @dataclasses.dataclass
        class SecondaryExampleConfig(ConnectorBaseConfig):
            simple: bool = True

        with pytest.raises(
            ConfigurationError,
            match="Multiple configurations found. Please ensure only one subclass of ConnectorBaseConfig exists.",
        ):
            get_connector_config()


class TestLoadConnectorConfig:
    def test_should_raise_if_default_not_found(self):
        with pytest.raises(FileNotFoundError, match="No config file found at path:"):
            load_config_file()

    def test_should_load_from_path(self, tmp_path):
        config_path = tmp_path / "config.json"
        config = ConnectorBaseConfig()
        config.dump(config_path)

        reloaded = load_config_file(config_path)
        assert reloaded == dataclasses.asdict(config)
