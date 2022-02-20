import json
from pathlib import Path
from typing import Callable, List, Optional, Sequence, Union
from unittest.mock import Mock, call, create_autospec

import pytest
from click.testing import CliRunner, Result
from pytest import MonkeyPatch

from philipstv import AmbilightColor, InputKeyValue, PhilipsTVPairingError, PhilipsTVRemote
from philipstv.api.model.pairing import PairingResponse
from philipstv.cli import cli
from philipstv.exceptions import PhilipsTVRemoteError
from philipstv.types import Credentials


@pytest.fixture(autouse=True)
def no_saved_data(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr("philipstv.data.DATA_FILE", Path("/shurelythiscannotexist"))


@pytest.fixture
def data_file(monkeypatch: MonkeyPatch, tmp_path: Path) -> Path:
    data_file = tmp_path / "data.json"
    monkeypatch.setattr("philipstv.data.DATA_FILE", data_file)
    return data_file


@pytest.fixture
def remote(monkeypatch: MonkeyPatch) -> Mock:
    mock_remote = create_autospec(PhilipsTVRemote)
    mock_remote.new.return_value = mock_remote
    monkeypatch.setattr("philipstv.cli.PhilipsTVRemote", mock_remote)
    return mock_remote  # type: ignore


def run(*args: str, input: Optional[str] = None) -> Result:
    return CliRunner(mix_stderr=False).invoke(cli, args, input=input)


def run_with_auth(*args: str, input: Optional[str] = None) -> Result:
    return run("--host", "<host>", "--id", "<id>", "--key", "<key>", *args, input=input)


@pytest.mark.parametrize(
    "args, expected_error",
    [
        (
            ["--host", "192.168.0.1", "power"],
            "Options --host, --id and --key have to be used together.",
        ),
        (
            ["--id", "user", "power"],
            "Options --host, --id and --key have to be used together.",
        ),
        (
            ["--key", "69420", "power"],
            "Options --host, --id and --key have to be used together.",
        ),
        (
            ["--save", "power"],
            "--save requires giving --host, --id and --key.",
        ),
        (
            ["power"],
            "No TV data (--host, --id, --key) given or saved.",
        ),
        (
            ["pair"],
            "No host given (--host).",
        ),
        (
            ["--host", "192.168.0.1", "--id", "user", "--key", "secret", "pair"],
            "Option --key is invalid in pairing context.",
        ),
    ],
)
def test_errors(args: Sequence[str], expected_error: str) -> None:
    result = run(*args)

    assert result.exit_code != 0
    assert expected_error in result.stderr


def test_saves_data(data_file: Path, remote: Mock) -> None:
    given_host = "<host>"
    given_id = "<id>"
    given_key = "<key>"
    remote.get_power.return_value = True

    assert data_file.exists() is False

    run("--host", given_host, "--id", given_id, "--key", given_key, "--save", "power", "get")

    assert data_file.exists() is True
    assert data_file.read_text() == json.dumps(
        {"last_host": {"host": given_host, "id": given_id, "key": given_key}}
    )


def test_reads_saved_data(data_file: Path, remote: Mock) -> None:
    given_host = "<host>"
    given_id = "<id>"
    given_key = "<key>"
    data_file.touch()
    data_file.write_text(
        json.dumps({"last_host": {"host": given_host, "id": given_id, "key": given_key}})
    )

    run("power", "get")

    remote.new.assert_called_once_with(given_host, (given_id, given_key))


def test_pair(remote: Mock) -> None:
    given_id = "<myid>"
    given_pin = "<pin>"

    def mock_pair(callback: Callable[[], str], id: Optional[str] = None) -> Credentials:
        assert callback() == given_pin
        return (id or "<defaultid>", "<secret>")

    remote.pair.side_effect = mock_pair

    result = run("--host", "192.168.0.1", "--id", given_id, "pair", input=given_pin)

    assert f"Pairing successful!\nID:\t{given_id}\nKey:\t<secret>" in result.stdout


def test_pair_save(remote: Mock, data_file: Path) -> None:
    given_host = "<host>"
    given_id = "<id>"
    given_key = "<key>"
    remote.pair.return_value = (given_id, given_key)

    assert data_file.exists() is False

    run("--host", given_host, "--id", given_id, "--save", "pair")

    assert data_file.exists() is True
    assert data_file.read_text() == json.dumps(
        {"last_host": {"host": given_host, "id": given_id, "key": given_key}}
    )


def test_pair_error(remote: Mock) -> None:
    remote.pair.side_effect = PhilipsTVPairingError(
        PairingResponse(error_id="ERR_ID", error_text="<error>")
    )

    result = run("--host", "192.168.0.1", "pair")

    assert result.exit_code != 0
    assert "ERR_ID <error>" in result.stderr


def test_power_get(remote: Mock) -> None:
    remote.get_power.return_value = False

    result = run_with_auth("power", "get")

    assert result.stdout == "off\n"


def test_power_set(remote: Mock) -> None:
    run_with_auth("power", "set", "on")

    remote.set_power.assert_called_once_with(True)


def test_volume_get(remote: Mock) -> None:
    remote.get_volume.return_value = 15

    result = run_with_auth("volume", "get")

    assert result.stdout == "15\n"


def test_volume_set(remote: Mock) -> None:
    run_with_auth("volume", "set", "25")

    remote.set_volume.assert_called_once_with(25)


def test_channel_get(remote: Mock) -> None:
    remote.get_current_channel.return_value = "TVN HD"

    result = run_with_auth("channel", "get")

    assert result.stdout == "TVN HD\n"


def test_channel_list(remote: Mock) -> None:
    remote.get_all_channels.return_value = {1: "TVP 1 HD", 3: "Polsat HD", 5: "TVN HD"}

    result = run_with_auth("channel", "list")

    assert result.stdout == "1\tTVP 1 HD\n3\tPolsat HD\n5\tTVN HD\n"


@pytest.mark.parametrize(
    "channel, expected",
    [
        ("TVN HD", "TVN HD"),
        ("17", 17),
    ],
)
def test_channel_set(remote: Mock, channel: str, expected: Union[str, int]) -> None:
    run_with_auth("channel", "set", channel)

    remote.set_channel.assert_called_once_with(expected)


def test_channel_set_error(remote: Mock) -> None:
    remote.set_channel.side_effect = PhilipsTVRemoteError("<error message>")

    result = run_with_auth("channel", "set", "whatever")

    assert result.exit_code != 0
    assert result.stderr == "<error message>\n"


@pytest.mark.parametrize(
    "given_keys, expected_keys",
    [
        ([], []),
        (["home"], [InputKeyValue.HOME]),
        (["right", "ok"], [InputKeyValue.CURSOR_RIGHT, InputKeyValue.CONFIRM]),
    ],
)
def test_key(remote: Mock, given_keys: List[str], expected_keys: List[InputKeyValue]) -> None:
    run_with_auth("key", *given_keys)

    assert remote.input_key.call_args_list == [call(key) for key in expected_keys]


def test_ambilight_power_get(remote: Mock) -> None:
    remote.get_ambilight_power.return_value = False

    result = run_with_auth("ambilight", "power", "get")

    assert result.stdout == "off\n"


def test_ambilight_power_set(remote: Mock) -> None:
    run_with_auth("ambilight", "power", "set", "on")

    remote.set_ambilight_power.assert_called_once_with(True)


def test_ambilight_color_set(remote: Mock) -> None:
    run_with_auth("ambilight", "color", "set", "255", "0", "0")

    remote.set_ambilight_color.assert_called_once_with(AmbilightColor(r=255, g=0, b=0))


def test_app_list(remote: Mock) -> None:
    remote.get_applications.return_value = ["Netflix", "YouTube", "TED"]

    result = run_with_auth("app", "list")

    assert result.stdout == "Netflix\nYouTube\nTED\n"


def test_app_launch(remote: Mock) -> None:
    run_with_auth("app", "launch", "YouTube")

    remote.launch_application.assert_called_once_with("YouTube")


def test_app_launch_error(remote: Mock) -> None:
    remote.launch_application.side_effect = PhilipsTVRemoteError("<error message>")

    result = run_with_auth("app", "launch", "whatever")

    assert result.exit_code != 0
    assert result.stderr == "<error message>\n"
