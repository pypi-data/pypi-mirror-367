import json
import pathlib
import typing
import uuid

import pytest
from click.testing import CliRunner

from unitelabs.cdk import ConnectorBaseConfig
from unitelabs.cdk.cli.certificate import MutuallyExclusiveOptions


@pytest.fixture
def temp_config(tmp_path) -> typing.Generator[tuple[ConnectorBaseConfig, pathlib.Path], None, None]:
    config_path = tmp_path / "config.json"
    config = ConnectorBaseConfig()
    config.dump(config_path)
    yield (config, config_path)


class TestGenerate:
    def test_should_accept_config_file(self, temp_config):
        from unitelabs.cdk.cli import certificate

        runner = CliRunner()
        config, config_path = temp_config

        result = runner.invoke(
            certificate, ["generate", "--config-path", config_path, "--target", config_path.parent], input="n"
        )
        assert result.exit_code == 0

        config_file_contents = ConnectorBaseConfig.load(config_path)

        assert config_file_contents == config

    def test_should_update_config_file_with_prompt(self, temp_config):
        from unitelabs.cdk.cli import certificate

        runner = CliRunner()
        config, config_path = temp_config

        result = runner.invoke(
            certificate, ["generate", "--config-path", config_path, "--target", config_path.parent], input="y"
        )
        assert result.exit_code == 0

        config_file_contents = ConnectorBaseConfig.load(config_path)

        # cert, key, and tls values have been updated
        assert config_file_contents.sila_server.tls
        assert isinstance(config_file_contents.sila_server.certificate_chain, bytes)
        assert isinstance(config_file_contents.sila_server.private_key, bytes)

        # all other values are the same
        assert config_file_contents != config

        config_file_contents.sila_server.certificate_chain = ""
        config_file_contents.sila_server.private_key = ""
        config_file_contents.sila_server.tls = False

        assert config_file_contents == config

    def test_update_should_suppress_prompt_and_update_config(self, temp_config):
        from unitelabs.cdk.cli import certificate

        runner = CliRunner()
        config, config_path = temp_config

        result = runner.invoke(
            certificate, ["generate", "--config-path", config_path, "--target", config_path.parent, "-U"]
        )
        assert result.exit_code == 0

        config_file_contents = ConnectorBaseConfig.load(config_path)

        # cert, key, and tls values have been updated
        assert config_file_contents.sila_server.tls
        assert isinstance(config_file_contents.sila_server.certificate_chain, bytes)
        assert isinstance(config_file_contents.sila_server.private_key, bytes)

        # all other values are the same
        assert config_file_contents != config

        config_file_contents.sila_server.certificate_chain = ""
        config_file_contents.sila_server.private_key = ""
        config_file_contents.sila_server.tls = False

        assert config_file_contents == config

    def test_uuid_and_host_should_generate_certs(self, tmp_path):
        from unitelabs.cdk.cli import certificate

        cert_path = tmp_path / "cert.pem"
        key_path = tmp_path / "key.pem"

        assert not cert_path.exists()
        assert not key_path.exists()

        runner = CliRunner()
        result = runner.invoke(
            certificate, ["generate", "--uuid", str(uuid.uuid4()), "--host", "localhost", "--target", tmp_path]
        )
        assert result.exit_code == 0

        assert cert_path.exists()
        assert key_path.exists()

    def test_should_not_allow_config_path_and_uuid(self, temp_config):
        from unitelabs.cdk.cli import certificate

        _, config_path = temp_config

        runner = CliRunner()
        result = runner.invoke(certificate, ["generate", "--config-path", config_path, "--uuid", str(uuid.uuid4())])

        assert result.exit_code == 1
        print(result.exc_info)
        assert result.exc_info
        assert result.exc_info[0] == MutuallyExclusiveOptions

    def test_should_not_allow_config_path_and_host(self, temp_config):
        from unitelabs.cdk.cli import certificate

        _, config_path = temp_config

        runner = CliRunner()
        result = runner.invoke(certificate, ["generate", "--config-path", config_path, "--host", "localhost"])

        assert result.exit_code == 1
        assert result.exc_info
        assert result.exc_info[0] == MutuallyExclusiveOptions

    def test_should_not_allow_config_path_and_uuid_and_host(self, temp_config):
        from unitelabs.cdk.cli import certificate

        _, config_path = temp_config

        runner = CliRunner()
        result = runner.invoke(
            certificate, ["generate", "--config-path", config_path, "--uuid", str(uuid.uuid4()), "--host", "localhost"]
        )

        assert result.exit_code == 1
        assert result.exc_info
        assert result.exc_info[0] == MutuallyExclusiveOptions

    def test_should_preserve_unknown_config_keys(self, tmp_path):
        from unitelabs.cdk.cli import certificate

        config_data = ConnectorBaseConfig.get_default()
        config_data["simple"] = True

        config_path = tmp_path / "config.json"
        with config_path.open("w") as f:
            f.write(json.dumps(config_data))

        runner = CliRunner()
        result = runner.invoke(
            certificate, ["generate", "--config-path", config_path, "--target", config_path.parent, "-U"]
        )
        assert result.exit_code == 0

        with config_path.open("r") as f:
            updated = json.load(f)

        assert "simple" in updated
