import platform
from typing import Dict, List, Optional, Union

from ._utils import create_device_id
from .api import PhilipsTVAPI
from .exceptions import PhilipsTVRemoteError
from .model import (
    AmbilightColor,
    AmbilightPower,
    AmbilightPowerValue,
    Application,
    Channel,
    ChannelID,
    DeviceInfo,
    InputKey,
    InputKeyValue,
    PowerState,
    PowerStateValue,
    SetChannel,
    Volume,
)
from .pairing import PhilipsTVPairer, PinCallback
from .tv import PhilipsTV
from .types import Credentials

__all__ = ["AmbilightColor", "InputKeyValue", "PhilipsTVRemote"]


class PhilipsTVRemote:
    def __init__(self, api: PhilipsTVAPI) -> None:
        self._api = api
        self._channels_cache: List[Channel] = []
        self._applications_cache: List[Application] = []

    @classmethod
    def new(cls, host: str, auth: Optional[Credentials] = None) -> "PhilipsTVRemote":
        return cls(PhilipsTVAPI(PhilipsTV(host=host, auth=auth)))

    def pair(self, pin_callback: PinCallback, id: Optional[str] = None) -> Credentials:
        id = id or create_device_id()
        uname_info = platform.uname()
        device_info = DeviceInfo(
            id=id,
            device_name=uname_info.node,
            device_os=uname_info.system,
            app_id=69,
            app_name="philipstv",
            type="native",
        )
        pairer = PhilipsTVPairer(self._api, device_info)
        return pairer.pair(pin_callback)

    def get_power(self) -> bool:
        return True if self._api.get_powerstate().powerstate == PowerStateValue.ON else False

    def set_power(self, power: bool) -> None:
        value = PowerStateValue.ON if power is True else PowerStateValue.STANDBY
        self._api.set_powerstate(PowerState(powerstate=value))

    def get_volume(self) -> int:
        return self._api.get_volume().current

    def set_volume(self, volume: int) -> None:
        self._api.set_volume(Volume(current=volume))

    def get_current_channel(self) -> str:
        return self._api.get_current_channel().channel.name

    def set_channel(self, channel: Union[int, str]) -> None:
        if not self._channels_cache:
            self._channels_cache = self._api.get_all_channels().channel

        if isinstance(channel, str):
            matching = filter(lambda chan: chan.name == channel, self._channels_cache)
        elif isinstance(channel, int):
            matching = filter(lambda chan: chan.preset == str(channel), self._channels_cache)

        found_channel = next(matching, None)
        if not found_channel:
            raise PhilipsTVRemoteError(f"Channel '{channel}' not available")

        self._api.set_channel(SetChannel(channel=ChannelID(ccid=found_channel.ccid)))

    def get_all_channels(self) -> Dict[int, str]:
        self._channels_cache = self._api.get_all_channels().channel
        return {int(channel.preset): channel.name for channel in self._channels_cache}

    def input_key(self, key: InputKeyValue) -> None:
        self._api.input_key(InputKey(key=key))

    def get_ambilight_power(self) -> bool:
        return True if self._api.get_ambilight_power().power == AmbilightPowerValue.ON else False

    def set_ambilight_power(self, power: bool) -> None:
        value = AmbilightPowerValue.ON if power is True else AmbilightPowerValue.OFF
        self._api.set_ambilight_power(AmbilightPower(power=value))

    def set_ambilight_color(self, color: AmbilightColor) -> None:
        self._api.set_ambilight_cached(color)

    def get_applications(self) -> List[str]:
        self._applications_cache = self._api.get_applications().applications
        return [app.label for app in self._applications_cache]

    def launch_application(self, application: str) -> None:
        if not self._applications_cache:
            self._applications_cache = self._api.get_applications().applications

        matching = filter(lambda app: app.label == application, self._applications_cache)

        found_application = next(matching, None)
        if not found_application:
            raise PhilipsTVRemoteError(f"Application '{application}' not available")

        self._api.launch_application(found_application)
