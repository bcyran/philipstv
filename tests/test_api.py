from typing import Any, Type

import pytest

from philipstv import (
    PhilipsTVAPI,
    PhilipsTVAPIMalformedResponseError,
    PhilipsTVAPIUnauthorizedError,
    PhilipsTVError,
)
from philipstv.model import (
    AllChannels,
    AmbilightColor,
    AmbilightLayer,
    AmbilightMode,
    AmbilightModeValue,
    AmbilightPower,
    AmbilightPowerValue,
    AmbilightTopology,
    Application,
    ApplicationComponent,
    ApplicationIntent,
    Applications,
    ApplicationShort,
    Channel,
    ChannelID,
    ChannelList,
    ChannelShort,
    CurrentChannel,
    CurrentVolume,
    DeviceInfo,
    InputKey,
    InputKeyValue,
    PairingAuthInfo,
    PairingGrantPayload,
    PairingRequestPayload,
    PairingRequestResponse,
    PairingResponse,
    PowerState,
    PowerStateValue,
    SetChannel,
    Volume,
)
from tests.fakes import FakePhilipsTV

DEVICE_INFO = DeviceInfo(
    id="<device_id>",
    device_name="<device_name>",
    device_os="<device_os>",
    app_id="<app_id>",
    app_name="<app_name>",
    type="<type>",
)


def test_host() -> None:
    expected_host = "192.168.0.66"
    fake_tv = FakePhilipsTV()
    fake_tv.host = expected_host

    result = PhilipsTVAPI(fake_tv).host

    assert result == expected_host


def test_auth() -> None:
    expected_auth = ("<id>", "<key>")
    fake_tv = FakePhilipsTV()
    api = PhilipsTVAPI(fake_tv)

    api.auth = expected_auth

    assert api.auth == expected_auth
    assert fake_tv.auth == expected_auth


def test_pair_request() -> None:
    fake_tv = FakePhilipsTV(
        post_responses={
            "6/pair/request": {
                "error_id": "SUCCESS",
                "error_text": "Authorization required",
                "auth_key": "<key>",
                "timestamp": 12345,
                "timeout": 60,
            }
        }
    )

    result = PhilipsTVAPI(fake_tv).pair_request(
        PairingRequestPayload(scope=["read", "write", "control"], device=DEVICE_INFO)
    )

    assert fake_tv.post_requests["6/pair/request"] == {
        "scope": ["read", "write", "control"],
        "device": DEVICE_INFO.dump(),
    }
    assert result == PairingRequestResponse(
        error_id="SUCCESS",
        error_text="Authorization required",
        auth_key="<key>",
        timestamp=12345,
        timeout=60,
    )


def test_pair_grant() -> None:
    fake_tv = FakePhilipsTV(
        post_responses={
            "6/pair/grant": {
                "error_id": "SUCCESS",
                "error_text": "Pairing completed",
            }
        }
    )

    result = PhilipsTVAPI(fake_tv).pair_grant(
        PairingGrantPayload(
            auth=PairingAuthInfo(pin="<pin>", auth_timestamp=12345, auth_signature="<signature>"),
            device=DEVICE_INFO,
        )
    )

    assert fake_tv.post_requests["6/pair/grant"] == {
        "auth": {
            "pin": "<pin>",
            "auth_timestamp": 12345,
            "auth_signature": "<signature>",
        },
        "device": DEVICE_INFO.dump(),
    }
    assert result == PairingResponse(
        error_id="SUCCESS",
        error_text="Pairing completed",
    )


def test_get_powerstate() -> None:
    fake_tv = FakePhilipsTV(get_responses={"6/powerstate": {"powerstate": "On"}})

    result = PhilipsTVAPI(fake_tv).get_powerstate()

    assert result == PowerState(powerstate=PowerStateValue.ON)


def test_set_powerstate() -> None:
    fake_tv = FakePhilipsTV(post_responses={"6/powerstate": None})

    PhilipsTVAPI(fake_tv).set_powerstate(PowerState(powerstate=PowerStateValue.STANDBY))

    assert fake_tv.post_requests == {"6/powerstate": {"powerstate": "Standby"}}


def test_get_volume() -> None:
    fake_tv = FakePhilipsTV(
        get_responses={"6/audio/volume": {"muted": False, "current": 15, "min": 0, "max": 60}}
    )

    result = PhilipsTVAPI(fake_tv).get_volume()

    assert result == CurrentVolume(current=15, muted=False, min=0, max=60)


def test_set_volume() -> None:
    fake_tv = FakePhilipsTV(post_responses={"6/audio/volume": None})

    PhilipsTVAPI(fake_tv).set_volume(Volume(current=10))

    assert fake_tv.post_requests == {"6/audio/volume": {"muted": False, "current": 10}}


def test_get_current_channel() -> None:
    fake_tv = FakePhilipsTV(
        get_responses={
            "6/activities/tv": {
                "channel": {"ccid": 35, "preset": "10", "name": "TVN HD"},
                "channelList": {"id": "list", "version": "7"},
            }
        }
    )

    result = PhilipsTVAPI(fake_tv).get_current_channel()

    assert result == CurrentChannel(
        channel=ChannelShort(ccid=35, preset="10", name="TVN HD"),
        channel_list=ChannelList(id="list", version="7"),
    )


def test_set_current_channel() -> None:
    fake_tv = FakePhilipsTV(post_responses={"6/activities/tv": None})

    PhilipsTVAPI(fake_tv).set_channel(SetChannel(channel=ChannelID(ccid=30)))

    assert fake_tv.post_requests == {
        "6/activities/tv": {"channel": {"ccid": 30}, "channelList": {"id": "allcab"}}
    }


def test_get_all_channels() -> None:
    fake_tv = FakePhilipsTV(
        get_responses={
            "6/channeldb/tv/channelLists/all": {
                "version": 1,
                "id": "all",
                "listType": "MixedSources",
                "medium": "mixed",
                "operator": "OPER",
                "installCountry": "Poland",
                "channel": [
                    {
                        "ccid": 35,
                        "preset": "1",
                        "name": "TVPiS 1 HD",
                        "onid": 1537,
                        "tsid": 24,
                        "sid": 2403,
                        "serviceType": "audio_video",
                        "type": "DVB_C",
                        "logoVersion": 33,
                    }
                ],
            },
        }
    )

    result = PhilipsTVAPI(fake_tv).get_all_channels()

    assert result == AllChannels(
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
                name="TVPiS 1 HD",
                onid=1537,
                tsid=24,
                sid=2403,
                service_type="audio_video",
                type="DVB_C",
                logo_version=33,
            )
        ],
    )


def test_input_key() -> None:
    fake_tv = FakePhilipsTV(post_responses={"6/input/key": None})

    PhilipsTVAPI(fake_tv).input_key(InputKey(key=InputKeyValue.STANDBY))

    assert fake_tv.post_requests == {"6/input/key": {"key": "Standby"}}


def test_get_ambilight_power() -> None:
    fake_tv = FakePhilipsTV(get_responses={"6/ambilight/power": {"power": "On"}})

    result = PhilipsTVAPI(fake_tv).get_ambilight_power()

    assert result == AmbilightPower(power=AmbilightPowerValue.ON)


def test_set_ambilight_power() -> None:
    fake_tv = FakePhilipsTV(post_responses={"6/ambilight/power": None})

    PhilipsTVAPI(fake_tv).set_ambilight_power(AmbilightPower(power=AmbilightPowerValue.OFF))

    assert fake_tv.post_requests == {"6/ambilight/power": {"power": "Off"}}


def test_get_ambilight_topology() -> None:
    fake_tv = FakePhilipsTV(
        get_responses={
            "6/ambilight/topology": {"layers": 1, "left": 3, "top": 7, "right": 3, "bottom": 0}
        }
    )

    result = PhilipsTVAPI(fake_tv).get_ambilight_topology()

    assert result == AmbilightTopology(layers=1, left=3, top=7, right=3, bottom=0)


def test_get_abilight_mode() -> None:
    fake_tv = FakePhilipsTV(get_responses={"6/ambilight/mode": {"current": "internal"}})

    result = PhilipsTVAPI(fake_tv).get_ambilight_mode()

    assert result == AmbilightMode(current=AmbilightModeValue.INTERNAL)


def test_set_abilight_mode() -> None:
    fake_tv = FakePhilipsTV(post_responses={"6/ambilight/mode": None})

    PhilipsTVAPI(fake_tv).set_ambilight_mode(AmbilightMode(current=AmbilightModeValue.MANUAL))

    assert fake_tv.post_requests == {"6/ambilight/mode": {"current": "manual"}}


@pytest.mark.parametrize(
    "method, endpoint",
    [
        pytest.param("get_ambilight_measured", "6/ambilight/measured", id="measured"),
        pytest.param("get_ambilight_processed", "6/ambilight/processed", id="processed"),
        pytest.param("get_ambilight_cached", "6/ambilight/cached", id="cached"),
    ],
)
def test_get_ambilight_colors(method: str, endpoint: str) -> None:
    fake_tv = FakePhilipsTV(
        get_responses={
            endpoint: {
                "layer1": {
                    "left": {"0": {"r": 255, "g": 0, "b": 0}},
                    "top": {"0": {"r": 0, "g": 255, "b": 0}, "1": {"r": 0, "g": 0, "b": 0}},
                    "right": {"0": {"r": 0, "g": 0, "b": 255}},
                },
            }
        }
    )

    result = getattr(PhilipsTVAPI(fake_tv), method)()

    assert result["layer1"] == AmbilightLayer(
        left={"0": AmbilightColor(r=255, g=0, b=0)},
        top={"0": AmbilightColor(r=0, g=255, b=0), "1": AmbilightColor(r=0, g=0, b=0)},
        right={"0": AmbilightColor(r=0, g=0, b=255)},
    )


def test_set_ambilight_cached() -> None:
    fake_tv = FakePhilipsTV(post_responses={"6/ambilight/cached": None})

    PhilipsTVAPI(fake_tv).set_ambilight_cached(AmbilightColor(r=255, g=255, b=255))

    assert fake_tv.post_requests == {"6/ambilight/cached": {"r": 255, "g": 255, "b": 255}}


def test_get_applications() -> None:
    fake_tv = FakePhilipsTV(
        get_responses={
            "6/applications": {
                "version": 0,
                "applications": [
                    {
                        "intent": {
                            "component": {
                                "packageName": "org.droidtv.eum",
                                "className": "org.droidtv.eum.classname",
                            },
                            "action": "android.intent.action.MAIN",
                        },
                        "label": "Application",
                        "order": 0,
                        "id": "org.droidtv.eum.whatever",
                        "type": "app",
                    },
                ],
            }
        }
    )

    result = PhilipsTVAPI(fake_tv).get_applications()

    assert result == Applications(
        version=0,
        applications=[
            Application(
                intent=ApplicationIntent(
                    component=ApplicationComponent(
                        package_name="org.droidtv.eum",
                        class_name="org.droidtv.eum.classname",
                    ),
                    action="android.intent.action.MAIN",
                ),
                label="Application",
                order=0,
                id="org.droidtv.eum.whatever",
                type="app",
            )
        ],
    )


def test_launch_application() -> None:
    fake_tv = FakePhilipsTV(post_responses={"6/activities/launch": None})

    PhilipsTVAPI(fake_tv).launch_application(
        ApplicationShort(
            intent=ApplicationIntent(
                component=ApplicationComponent(
                    package_name="org.droidtv.eum",
                    class_name="org.droidtv.eum.classname",
                ),
                action="android.intent.action.MAIN",
            ),
        )
    )

    assert fake_tv.post_requests == {
        "6/activities/launch": {
            "intent": {
                "component": {
                    "packageName": "org.droidtv.eum",
                    "className": "org.droidtv.eum.classname",
                },
                "action": "android.intent.action.MAIN",
            },
        },
    }


@pytest.mark.parametrize(
    "response, expected_exception",
    [
        pytest.param(
            PhilipsTVError("GET", "6/powerstate", 401),
            PhilipsTVAPIUnauthorizedError,
            id="unauthorized request error",
        ),
        pytest.param(
            {"foo": "bar"},
            PhilipsTVAPIMalformedResponseError,
            id="malformed response error",
        ),
        pytest.param(
            PhilipsTVError("GET", "6/powerstate", 404),
            PhilipsTVError,
            id="unhandled error",
        ),
    ],
)
def test_api_error(response: Any, expected_exception: Type[Exception]) -> None:
    fake_tv = FakePhilipsTV(get_responses={"6/powerstate": response})

    with pytest.raises(expected_exception):
        PhilipsTVAPI(fake_tv).get_powerstate()
