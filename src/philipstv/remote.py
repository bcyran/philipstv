import platform
from typing import Dict, List, Optional, Union

from ._utils import create_device_id
from .api import PhilipsTVAPI
from .exceptions import PhilipsTVRemoteError
from .model import (
    AmbilightColor,
    AmbilightColors,
    AmbilightLayer,
    AmbilightPower,
    AmbilightPowerValue,
    AmbilightTopology,
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
    """High level interface to the TV.

    Wraps the API into convenient methods simulating functions that could be found on a TV remote.

    Can be used either with existing :class:`PhilipsTVAPI` instance, or create it itself.
    In the following example ``remote_one`` and ``remote_two`` are equivalent::

        api = PhilipsTVAPI(PhilipsTV("192.169.0.100", auth=("id", "key")))
        remote_one = PhilipsTVRemote(api)
        remote_two = PhilipsTVRemote.new("192.168.0.100", ("id", "key"))

    """

    def __init__(self, api: PhilipsTVAPI) -> None:
        """
        Args:
            api: Instance of an API to be used by the remote.

        """
        self._api = api
        self._channels_cache: List[Channel] = []
        self._applications_cache: List[Application] = []
        self._ambilight_topology_cache: Optional[AmbilightTopology] = None

    @property
    def host(self) -> str:
        """IP address of the underlying :class:`PhilipsTVAPI` instance.

        Warning:
            This value is read-only.

        """
        return self._api.host

    @property
    def auth(self) -> Optional[Credentials]:
        """Credentials used for authentication in the underlying :class:`PhilipsTVAPI` instance.

        Hint:
            This value can be set and changed at any moment during :class:`PhilipsTVRemote` usage.

        """
        return self._api.auth

    @auth.setter
    def auth(self, value: Optional[Credentials]) -> None:
        self._api.auth = value

    @classmethod
    def new(cls, host: str, auth: Optional[Credentials] = None) -> "PhilipsTVRemote":
        """Create a new remote for given host without the need to inject:class:`PhilipsTVAPI`
        instance.

        Args:
            host: IP address of the TV.
            auth: Authentication credentials. If not given, the only feature you will be able to
                use is pairing: :func:`pair`.

        """
        return cls(PhilipsTVAPI(PhilipsTV(host=host, auth=auth)))

    def pair(self, pin_callback: PinCallback, id: Optional[str] = None) -> Credentials:
        """Perform pairing with the TV.

        After successful pairing this remote instance will be authenticated, even if you didn't
        provide credentials when creating it.

        Args:
            pin_callback: A function taking no arguments and returning the PIN displayed
                on TV as a string.
            id: Device ID to use for pairing. This will be later used as a first value in
                credentials tuple. If not given, a random, 16 characters, alphanumeric string will
                be used.

        Returns:
            A tuple of acquired authentication credentials.

        """
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
        """Return the current power state.

        Returns:
            A power state. `True` means on, `False` means standby.

        """
        return True if self._api.get_powerstate().powerstate == PowerStateValue.ON else False

    def set_power(self, power: bool) -> None:
        """Set current power state.

        Args:
            power: Power state to set. `True` means on, `False` means standby.

        """
        value = PowerStateValue.ON if power is True else PowerStateValue.STANDBY
        self._api.set_powerstate(PowerState(powerstate=value))

    def get_volume(self) -> int:
        """Return current volume."""
        return self._api.get_volume().current

    def set_volume(self, volume: int) -> None:
        """Set current volume.

        Args:
            volume: Volume value to set.

        """
        self._api.set_volume(Volume(current=volume))

    def get_current_channel(self) -> str:
        """Return current TV channel.

        If the TV currently displays something different than television (any app), this will return
        the last watched channel.

        Returns:
            Current TV channel name.

        """
        return self._api.get_current_channel().channel.name

    def set_channel(self, channel: Union[int, str]) -> None:
        """Change to the given TV channel.

        Use :func:`get_all_channels` to find valid values.

        If the TV currently displays something different than television (any app), it will go to
        the television.

        Args:
            channel: Number or name of the channel to change to.

        Raises:
            PhilipsTVRemoteError: If invalid channel number or name is given.

        """
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
        """Return all available channels and their numbers.

        Returns:
            A mapping of channel number to channel name.

        """
        self._channels_cache = self._api.get_all_channels().channel
        return {int(channel.preset): channel.name for channel in self._channels_cache}

    def input_key(self, key: InputKeyValue) -> None:
        """Emulate pressing a key on the TV remote.

        Args:
            key: A key value to send to the TV.

        """
        self._api.input_key(InputKey(key=key))

    def get_ambilight_power(self) -> bool:
        """Return current ambilight power state.

        Returns:
            Ambilight power state. `True` means on, `False` means off.

        """
        return True if self._api.get_ambilight_power().power == AmbilightPowerValue.ON else False

    def set_ambilight_power(self, power: bool) -> None:
        """Set ambilight power state.

        Args:
            power: Ambilight power state to set. `True` means on, `False` means off.

        """
        value = AmbilightPowerValue.ON if power is True else AmbilightPowerValue.OFF
        self._api.set_ambilight_power(AmbilightPower(power=value))

    def set_ambilight_color(
        self,
        color: Optional[AmbilightColor] = None,
        *,
        left: Optional[AmbilightColor] = None,
        top: Optional[AmbilightColor] = None,
        right: Optional[AmbilightColor] = None,
        bottom: Optional[AmbilightColor] = None,
    ) -> None:
        """Set ambilight color.

        On sides without given color, the color will not be changed. ``color`` defines color for all
        sides. If any of ``left``, ``top``, ``right`` or ``bottom`` args are given, they override
        ``color`` on that side.

        Args:
            color: A color to set on all sides.
            left: A color to set on the left side.
            top: A color to set on the top side.
            right: A color to set on the right side.
            bottom: A color to set on the bottom side.

        """
        if color and not any((left, top, right, bottom)):
            self._api.set_ambilight_cached(color)
            return

        if not self._ambilight_topology_cache:
            self._ambilight_topology_cache = self._api.get_ambilight_topology()

        topology = self._ambilight_topology_cache
        sides = {}
        if set_left := (left or color):
            sides["left"] = self._create_ambilight_side(set_left, topology.left)
        if set_top := (top or color):
            sides["top"] = self._create_ambilight_side(set_top, topology.top)
        if set_right := (right or color):
            sides["right"] = self._create_ambilight_side(set_right, topology.right)
        if set_bottom := (bottom or color):
            sides["bottom"] = self._create_ambilight_side(set_bottom, topology.bottom)

        colors = AmbilightColors(__root__={"layer1": AmbilightLayer(**sides)})
        self._api.set_ambilight_cached(colors)

    def _create_ambilight_side(
        self, color: AmbilightColor, points: int
    ) -> Dict[str, AmbilightColor]:
        return {str(point): color for point in range(points)}

    def get_applications(self) -> List[str]:
        """Return a list of available applications.

        Returns:
            List of application names.

        """
        self._applications_cache = self._api.get_applications().applications
        return [app.label for app in self._applications_cache]

    def launch_application(self, application: str) -> None:
        """Launch an application.

        Use :func:`get_applications` to find valid values.

        Args:
            application: An application name.

        Raises:
            PhilipsTVRemoteError: If invalid application name is given.

        """
        if not self._applications_cache:
            self._applications_cache = self._api.get_applications().applications

        matching = filter(lambda app: app.label == application, self._applications_cache)

        found_application = next(matching, None)
        if not found_application:
            raise PhilipsTVRemoteError(f"Application '{application}' not available")

        self._api.launch_application(found_application)
