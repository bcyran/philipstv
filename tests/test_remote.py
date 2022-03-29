from typing import Union
from unittest.mock import Mock, create_autospec

import pytest
from pytest import MonkeyPatch

from philipstv import PhilipsTVAPI, PhilipsTVPairer, PhilipsTVRemote, PhilipsTVRemoteError
from philipstv.model import (
    AllChannels,
    AmbilightColor,
    AmbilightColors,
    AmbilightLayer,
    AmbilightPower,
    AmbilightPowerValue,
    AmbilightTopology,
    Application,
    ApplicationComponent,
    ApplicationIntent,
    Applications,
    Channel,
    ChannelID,
    ChannelList,
    ChannelShort,
    CurrentChannel,
    CurrentVolume,
    DeviceInfo,
    InputKey,
    InputKeyValue,
    PowerState,
    PowerStateValue,
    SetChannel,
    Volume,
)

CHANNELS = AllChannels(
    version=1,
    id="all",
    list_type="MixedSources",
    medium="mixed",
    operator="OPER",
    install_country="Poland",
    channel=[
        Channel(
            ccid=35,
            preset="1",
            name="Polsat HD",
            onid=1537,
            tsid=24,
            sid=2403,
            service_type="audio_video",
            type="DVB_C",
            logo_version=33,
        ),
        Channel(
            ccid=40,
            preset="3",
            name="TVN HD",
            onid=666,
            tsid=24,
            sid=2403,
            service_type="audio_video",
            type="DVB_C",
            logo_version=33,
        ),
    ],
)

APPLICATION_SPOTIFY = Application(
    intent=ApplicationIntent(
        component=ApplicationComponent(
            package_name="com.spotify.tv.android",
            class_name="com.spotify.tv.android.SpotifyTVActivity",
        ),
        action="android.intent.action.MAIN",
    ),
    label="Spotify",
    order=0,
    id="com.spotify.tv.android.SpotifyTVActivity-com.spotify.tv.android",
    type="app",
)
APPLICATION_NETFLIX = Application(
    intent=ApplicationIntent(
        component=ApplicationComponent(
            package_name="com.netflix.ninja",
            class_name="com.netflix.ninja.MainActivity",
        ),
        action="android.intent.action.MAIN",
    ),
    label="Netflix",
    order=0,
    id="com.netflix.ninja.MainActivity-com.netflix.ninja",
    type="app",
)
APPLICATIONS = Applications(
    version=0,
    applications=[APPLICATION_SPOTIFY, APPLICATION_NETFLIX],
)


@pytest.fixture
def api_mock() -> Mock:
    return create_autospec(PhilipsTVAPI, spec_set=True, instance=True)  # type: ignore


def test_host(api_mock: Mock) -> None:
    expected_host = "192.168.0.66"
    api_mock.host = expected_host

    result = PhilipsTVRemote(api_mock).host

    assert result == expected_host


def test_auth(api_mock: PhilipsTVAPI) -> None:
    expected_credentials = ("<key>", "<secret>")
    remote = PhilipsTVRemote(api_mock)

    remote.auth = expected_credentials

    assert remote.auth == expected_credentials
    assert api_mock.auth == expected_credentials


def test_pair(api_mock: Mock, monkeypatch: MonkeyPatch) -> None:
    given_id = "<id>"
    pairer_mock = create_autospec(PhilipsTVPairer)
    pairer_mock.return_value = pairer_mock
    monkeypatch.setattr("philipstv.remote.PhilipsTVPairer", pairer_mock)

    def fake_callback() -> str:
        return "str"

    PhilipsTVRemote(api_mock).pair(fake_callback, given_id)

    pairer_mock.pair.assert_called_once_with(fake_callback)
    device_info = pairer_mock.call_args.args[1]
    assert isinstance(device_info, DeviceInfo)
    assert device_info.id == given_id


def test_pair_no_id(api_mock: Mock, monkeypatch: MonkeyPatch) -> None:
    pairer_mock = create_autospec(PhilipsTVPairer)
    pairer_mock.return_value = pairer_mock
    monkeypatch.setattr("philipstv.remote.PhilipsTVPairer", pairer_mock)

    PhilipsTVRemote(api_mock).pair(lambda: "str")

    device_info = pairer_mock.call_args.args[1]
    assert isinstance(device_info, DeviceInfo)
    assert device_info.id.isalnum()
    assert len(device_info.id) == 16


def test_get_power(api_mock: Mock) -> None:
    api_mock.get_powerstate.return_value = PowerState(powerstate=PowerStateValue.STANDBY)

    result = PhilipsTVRemote(api_mock).get_power()

    assert result is False


def test_set_power(api_mock: Mock) -> None:
    PhilipsTVRemote(api_mock).set_power(True)

    api_mock.set_powerstate.assert_called_once_with(PowerState(powerstate=PowerStateValue.ON))


def test_get_volume(api_mock: Mock) -> None:
    api_mock.get_volume.return_value = CurrentVolume(muted=False, current=15, min=0, max=60)

    result = PhilipsTVRemote(api_mock).get_volume()

    assert result == 15


def test_set_volume(api_mock: Mock) -> None:
    PhilipsTVRemote(api_mock).set_volume(20)

    api_mock.set_volume.assert_called_once_with(Volume(current=20, muted=False))


def test_get_current_channel(api_mock: Mock) -> None:
    api_mock.get_current_channel.return_value = CurrentChannel(
        channel=ChannelShort(ccid=5, preset="10", name="TVN HD"),
        channel_list=ChannelList(id="allcab", version="1"),
    )

    result = PhilipsTVRemote(api_mock).get_current_channel()

    assert result == "TVN HD"


@pytest.mark.parametrize(
    "input, expected",
    [
        (1, SetChannel(channel=ChannelID(ccid=35))),
        ("Polsat HD", SetChannel(channel=ChannelID(ccid=35))),
        (3, SetChannel(channel=ChannelID(ccid=40))),
        ("TVN HD", SetChannel(channel=ChannelID(ccid=40))),
    ],
)
def test_set_channel(api_mock: Mock, input: Union[int, str], expected: SetChannel) -> None:
    api_mock.get_all_channels.return_value = CHANNELS
    remote = PhilipsTVRemote(api_mock)

    remote.set_channel(input)
    api_mock.set_channel.assert_called_once_with(expected)

    remote.set_channel(input)
    api_mock.get_all_channels.assert_called_once()


def test_set_channel_error(api_mock: Mock) -> None:
    api_mock.get_current_channel.return_value = CHANNELS

    with pytest.raises(PhilipsTVRemoteError):
        PhilipsTVRemote(api_mock).set_channel("random channel")


def test_get_all_channels(api_mock: Mock) -> None:
    api_mock.get_all_channels.return_value = CHANNELS
    result = PhilipsTVRemote(api_mock).get_all_channels()

    assert result == {1: "Polsat HD", 3: "TVN HD"}


def test_input_key(api_mock: Mock) -> None:
    PhilipsTVRemote(api_mock).input_key(InputKeyValue.STANDBY)

    api_mock.input_key.assert_called_once_with(InputKey(key=InputKeyValue.STANDBY))


def test_get_ambilight_power(api_mock: Mock) -> None:
    api_mock.get_ambilight_power.return_value = AmbilightPower(power=AmbilightPowerValue.OFF)

    result = PhilipsTVRemote(api_mock).get_ambilight_power()

    assert result is False


def test_set_ambilight_power(api_mock: Mock) -> None:
    PhilipsTVRemote(api_mock).set_ambilight_power(True)

    api_mock.set_ambilight_power.assert_called_once_with(
        AmbilightPower(power=AmbilightPowerValue.ON)
    )


def test_set_ambilight_color(api_mock: Mock) -> None:
    PhilipsTVRemote(api_mock).set_ambilight_color(AmbilightColor(r=0, g=69, b=255))

    api_mock.set_ambilight_cached.assert_called_once_with(AmbilightColor(r=0, g=69, b=255))


def test_set_ambilight_color_sides(api_mock: Mock) -> None:
    left_color = AmbilightColor(r=255, g=0, b=0)
    top_color = AmbilightColor(r=0, g=255, b=0)
    right_color = AmbilightColor(r=0, g=0, b=255)
    bottom_color = AmbilightColor(r=125, g=0, b=125)
    topology = AmbilightTopology(layers=1, left=2, top=3, right=2, bottom=3)
    api_mock.get_ambilight_topology.return_value = topology

    PhilipsTVRemote(api_mock).set_ambilight_color(
        left=left_color, top=top_color, right=right_color, bottom=bottom_color
    )

    api_mock.set_ambilight_cached.assert_called_once_with(
        AmbilightColors(
            __root__={
                "layer1": AmbilightLayer(
                    left={str(point): left_color for point in range(topology.left)},
                    top={str(point): top_color for point in range(topology.top)},
                    right={str(point): right_color for point in range(topology.right)},
                    bottom={str(point): bottom_color for point in range(topology.bottom)},
                )
            }
        )
    )


def test_get_applications(api_mock: Mock) -> None:
    api_mock.get_applications.return_value = APPLICATIONS

    result = PhilipsTVRemote(api_mock).get_applications()

    assert result == ["Spotify", "Netflix"]


@pytest.mark.parametrize(
    "app, expected",
    [
        ("Spotify", APPLICATION_SPOTIFY),
        ("Netflix", APPLICATION_NETFLIX),
    ],
)
def test_launch_application(api_mock: Mock, app: str, expected: ApplicationIntent) -> None:
    api_mock.get_applications.return_value = APPLICATIONS
    remote = PhilipsTVRemote(api_mock)

    remote.launch_application(app)
    api_mock.launch_application.assert_called_once_with(expected)

    remote.launch_application(app)
    api_mock.get_applications.assert_called_once()


def test_launch_application_error(api_mock: Mock) -> None:
    api_mock.get_applications.return_value = APPLICATIONS

    with pytest.raises(PhilipsTVRemoteError):
        PhilipsTVRemote(api_mock).launch_application("whatever")
