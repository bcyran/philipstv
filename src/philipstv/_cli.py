import logging
import time
from dataclasses import dataclass
from functools import wraps
from typing import Any, Callable, Optional, Tuple, Union

import click
from click.exceptions import UsageError

from philipstv import __version__

from ._data import HostData, PhilipsTVData
from .exceptions import (
    PhilipsError,
    PhilipsTVAPIUnauthorizedError,
    PhilipsTVError,
    PhilipsTVPairingError,
    PhilipsTVRemoteError,
)
from .model import AmbilightColor, InputKeyValue
from .remote import PhilipsTVRemote

_LOGGER = logging.getLogger(__name__)

ColorArg = Tuple[int, int, int]


COMMON_ERROR_MESSAGE = """\
You can try to run the application with '--debug' option to get more info."""

UNAUTHORIZED_MESSAGE = f"""\
Could not authenticate with the TV.
Make sure you use correct credentials.
{COMMON_ERROR_MESSAGE}"""

CONNECTION_ERROR_MESSAGE = f"""\
Could not connect with the TV.
Make sure the IP address is correct and TV is powered on.
{COMMON_ERROR_MESSAGE}"""

UNKNOWN_ERROR_MESSAGE = f"""\
Unknown error occured.
{COMMON_ERROR_MESSAGE}"""


def handle_tv_errors(func: Callable[..., None]) -> Callable[..., None]:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except PhilipsTVRemoteError as err:
            _LOGGER.debug("Remote error", exc_info=True)
            raise click.ClickException(str(err))
        except PhilipsTVAPIUnauthorizedError:
            _LOGGER.debug("Authentication error", exc_info=True)
            raise click.ClickException(UNAUTHORIZED_MESSAGE)
        except PhilipsTVError:
            _LOGGER.debug("Connection error", exc_info=True)
            raise click.ClickException(CONNECTION_ERROR_MESSAGE)
        except PhilipsError:
            _LOGGER.debug("Unknown error", exc_info=True)
            raise click.ClickException(UNKNOWN_ERROR_MESSAGE)

    return wrapper


KEY_MAP = {
    "standby": InputKeyValue.STANDBY,
    "back": InputKeyValue.BACK,
    "find": InputKeyValue.FIND,
    "red": InputKeyValue.RED,
    "green": InputKeyValue.GREEN,
    "yellow": InputKeyValue.YELLOW,
    "blue": InputKeyValue.BLUE,
    "home": InputKeyValue.HOME,
    "volup": InputKeyValue.VOLUME_UP,
    "voldown": InputKeyValue.VOLUME_DOWN,
    "mute": InputKeyValue.MUTE,
    "options": InputKeyValue.OPTIONS,
    "dot": InputKeyValue.DOT,
    "0": InputKeyValue.DIGIT_0,
    "1": InputKeyValue.DIGIT_1,
    "2": InputKeyValue.DIGIT_2,
    "3": InputKeyValue.DIGIT_3,
    "4": InputKeyValue.DIGIT_4,
    "5": InputKeyValue.DIGIT_5,
    "6": InputKeyValue.DIGIT_6,
    "7": InputKeyValue.DIGIT_7,
    "8": InputKeyValue.DIGIT_8,
    "9": InputKeyValue.DIGIT_9,
    "info": InputKeyValue.INFO,
    "up": InputKeyValue.CURSOR_UP,
    "down": InputKeyValue.CURSOR_DOWN,
    "left": InputKeyValue.CURSOR_LEFT,
    "right": InputKeyValue.CURSOR_RIGHT,
    "ok": InputKeyValue.CONFIRM,
    "next": InputKeyValue.NEXT,
    "prev": InputKeyValue.PREVIOUS,
    "adjust": InputKeyValue.ADJUST,
    "tv": InputKeyValue.WATCH_TV,
    "view": InputKeyValue.VIEWMODE,
    "teletext": InputKeyValue.TELETEXT,
    "subtitle": InputKeyValue.SUBTITLE,
    "chanup": InputKeyValue.CHANNEL_STEP_UP,
    "chandown": InputKeyValue.CHANNEL_STEP_DOWN,
    "source": InputKeyValue.SOURCE,
    "ambilight": InputKeyValue.AMBILIGHT_ON_OFF,
    "play": InputKeyValue.PLAY_PAUSE,
    "pause": InputKeyValue.PAUSE,
    "forward": InputKeyValue.FAST_FORWARD,
    "stop": InputKeyValue.STOP,
    "rewind": InputKeyValue.REWIND,
    "rec": InputKeyValue.RECORD,
    "online": InputKeyValue.ONLINE,
}


@dataclass
class TVContext:
    remote: PhilipsTVRemote
    host: Optional[str] = None
    id: Optional[str] = None
    key: Optional[str] = None
    save: bool = False


pass_tv_context = click.make_pass_decorator(TVContext)

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option("-a", "--host", type=click.STRING, help="TV IP address.")
@click.option("-i", "--id", type=click.STRING, help="Connecting device ID.")
@click.option("-k", "--key", type=click.STRING, help="Connecting device secret key.")
@click.option(
    "-s", "--save", is_flag=True, default=False, help="Save host, ID and key for future use."
)
@click.help_option("-h", "--help")
@click.version_option(__version__, "-v", "--version")
@click.option("-d", "--debug", is_flag=True, default=False, help="Enable debug log.")
@click.pass_context
@handle_tv_errors
def cli(
    ctx: click.Context,
    host: Optional[str],
    id: Optional[str],
    key: Optional[str],
    save: bool,
    debug: bool,
) -> None:
    """Welcome to philipstv - a CLI remote control for Philips Android-powered TVs.

    Before you will be able to use this program, you need to pair it with your TV. For this,
    ensure your TV is powered on. The simplest way to perform pairing is by running:

    \b
        philipstv --host IP --save pair

    To learn more about pairing process run:

    \b
        philipstv pair -h

    In fact, you can learn more about every command by running it, followed by '-h'.
    The whole tool can be explored this way.

    Enjoy!
    """
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=log_level)

    # we need to treat pairing exceptionally
    if ctx.invoked_subcommand == "pair":
        # I'm passing empty string to `PhilipsTVRemote` if no host is given...
        # This is pretty fucking bad, but I really don't want to make 'remote' field optional
        # just for this one command
        # 'pair' HAS TO VALIDATE the 'host' before doing anything!
        ctx.obj = TVContext(PhilipsTVRemote.new(host or ""), host, id, key, save)
        return

    # for all other use cases we need either all data given or none given but saved data available
    if not (host and id and key):  # if not all auth is given
        if host or id or key:  # but some is given
            raise click.UsageError("Options --host, --id and --key have to be used together.")

        # at this point we know there's no auth given at all
        if save:  # so let's exit if user tries to save non-existent data
            raise click.UsageError("--save requires giving --host, --id and --key.")

        if not (saved_data := PhilipsTVData.load()):  # let's exit if nothing is saved as well
            raise click.UsageError("No TV data (--host, --id, --key) given or saved.")

        # something was saved!
        host = saved_data.last_host.host
        id = saved_data.last_host.id
        key = saved_data.last_host.key
        _LOGGER.debug("Using saved data: %r", saved_data.last_host)
    elif save:  # if all auth is given and we want to save
        PhilipsTVData(last_host=HostData(host=host, id=id, key=key)).save()

    ctx.obj = TVContext(PhilipsTVRemote.new(host, (id, key)), host, id, key, save)


@cli.command("pair")
@pass_tv_context
@click.pass_context
@handle_tv_errors
def pair(ctx: click.Context, tv_ctx: TVContext) -> None:
    """Pair with the TV to obtain authentication credentials.

    In order to perform pairing, you have to provide the TV IP address (--host option).
    You can find it in the TV's network settings. Look for something like "Show network
    configuration".

    Additionally, you can also provide device ID (--id), which will be later used during
    authentication. If device ID is not provided, random 16 characters long alphanumeric string
    will be generated.

    During pairing you will be prompted to enter the PIN number displayed on the TV screen.

    After successful pairing, your credentials will be displayed. If you don't want to enter them
    every time you run any command, you can pass (--save) option. This will save the credentials
    in a file. Saved credentials will be automatically used in future, unless other credentials are
    explicitly provided.

    \b
    Example valid pairing commands:
        philipstv --host IP pair
        philipstv --host IP --id ID pair
        philipstv --host IP --id ID --save pair

    """
    if not tv_ctx.host:
        raise click.UsageError("No host given (--host).")
    if tv_ctx.key:
        raise click.UsageError("Option --key is invalid in pairing context.")

    def prompt_pin() -> str:
        return str(click.prompt(text="Enter PIN displayed on the TV", type=click.STRING))

    try:
        credentials = tv_ctx.remote.pair(prompt_pin, tv_ctx.id)
    except PhilipsTVPairingError as err:
        raise click.ClickException(str(err))

    click.echo("Pairing successful!")
    click.echo(f"ID:\t{credentials[0]}")
    click.echo(f"Key:\t{credentials[1]}")

    if tv_ctx.save:
        PhilipsTVData(
            last_host=HostData(host=tv_ctx.host, id=credentials[0], key=credentials[1])
        ).save()
        click.echo("Credentials saved.")


@cli.group("power", help="Manage power state.")
def power() -> None:
    pass


@power.command("get", help="Get current power state.")
@pass_tv_context
@handle_tv_errors
def power_get(tv_ctx: TVContext) -> None:
    click.echo("on" if tv_ctx.remote.get_power() else "off")


@power.command("set", help="Set power state.")
@click.argument("power", type=click.Choice(("on", "off")))
@pass_tv_context
@handle_tv_errors
def power_set(tv_ctx: TVContext, power: str) -> None:
    tv_ctx.remote.set_power(True if power == "on" else False)


@cli.group("volume", help="Manage audio volume.")
def volume() -> None:
    pass


@volume.command("get", help="Get current audio volume.")
@pass_tv_context
@handle_tv_errors
def volume_get(tv_ctx: TVContext) -> None:
    click.echo(tv_ctx.remote.get_volume())


@volume.command("set", help="Set audio volume.")
@click.argument("volume", type=click.INT)
@pass_tv_context
@handle_tv_errors
def volume_set(tv_ctx: TVContext, volume: int) -> None:
    tv_ctx.remote.set_volume(volume)


@cli.group("channel", help="Manage TV channels.")
def channel() -> None:
    pass


@channel.command("get", help="Get current TV channel.")
@pass_tv_context
@handle_tv_errors
def channel_get(tv_ctx: TVContext) -> None:
    click.echo(tv_ctx.remote.get_current_channel())


@channel.command("list", help="List all available TV channels.")
@pass_tv_context
@handle_tv_errors
def channel_list(tv_ctx: TVContext) -> None:
    click.echo("\n".join(f"{no}\t{chan}" for no, chan in tv_ctx.remote.get_all_channels().items()))


@channel.command("set", help="Set TV channel.")
@click.argument("channel", type=click.STRING)
@pass_tv_context
@handle_tv_errors
def channel_set(tv_ctx: TVContext, channel: str) -> None:
    set_channel: Union[str, int] = channel
    if channel.isdigit():
        set_channel = int(set_channel)
    tv_ctx.remote.set_channel(set_channel)


@cli.command("key")
@click.argument(
    "keys", type=click.Choice(tuple(KEY_MAP), case_sensitive=False), nargs=-1, required=True
)
@click.option(
    "--delay", "-d", type=int, default=0, help="Delay (in milliseconds) between consecutive keys."
)
@pass_tv_context
@handle_tv_errors
def key(tv_ctx: TVContext, keys: Tuple[str, ...], delay: Optional[int]) -> None:
    """Emulate pressing keys on the TV remote.

    You can provide any number of key names, separated by a space. They will be sent to the TV in
    the given order.

    When providing multiple keys, they can be sent faster than the TV can react. To prevent this,
    you can use '--delay' option.
    """
    tv_ctx.remote.input_key(KEY_MAP[keys[0]])
    for key in keys[1:]:
        if delay:
            time.sleep(delay / 1000)
        tv_ctx.remote.input_key(KEY_MAP[key])


@cli.group("ambilight", help="Manage ambilight.")
def ambilight() -> None:
    pass


@ambilight.group("power", help="Manage ambilight power.")
def ambilight_power() -> None:
    pass


@ambilight_power.command("get", help="Get current ambilight power state.")
@pass_tv_context
@handle_tv_errors
def ambilight_power_get(tv_ctx: TVContext) -> None:
    click.echo("on" if tv_ctx.remote.get_ambilight_power() else "off")


@ambilight_power.command("set", help="Set ambilight power state.")
@click.argument("power", type=click.Choice(("on", "off")))
@pass_tv_context
@handle_tv_errors
def ambilight_power_set(tv_ctx: TVContext, power: str) -> None:
    tv_ctx.remote.set_ambilight_power(True if power == "on" else False)


@ambilight.group("color", help="Manage ambilight color.")
def ambilight_color() -> None:
    pass


@ambilight_color.command("set")
@click.argument("color", type=(int, int, int), required=False)
@click.option("--left", "-l", type=(int, int, int), help="Color to set on the left side.")
@click.option("--top", "-t", type=(int, int, int), help="Color to set on the top side.")
@click.option("--right", "-r", type=(int, int, int), help="Color to set on the right side.")
@click.option("--bottom", "-b", type=(int, int, int), help="Color to set on the bottom side.")
@pass_tv_context
@handle_tv_errors
def ambilight_color_set(
    tv_ctx: TVContext,
    color: Optional[ColorArg],
    left: Optional[ColorArg],
    top: Optional[ColorArg],
    right: Optional[ColorArg],
    bottom: Optional[ColorArg],
) -> None:
    """Set ambilight color.

    If 'COLOR' positional argument is given, it will be set on all sides. If value for any of the
    sides is specified, it overrides the 'COLOR' value. Sides which aren't specified either through
    positional argument or through options, will keep their current color.

    Each color value should be specified in RGB as three integers in range 0-255.

    \b
    Examples:
        philipstv ambilight color set 255 0 0
        philipstv ambilight color set 255 0 0 --top 0 255 0
        philipstv ambilight color set --left 0 0 255 --right 0 0 255

    """
    if not any((color, left, top, right, bottom)):
        raise UsageError(
            "Missing argument 'COLOR' or one of: '--left', '--top', '--right', '--bottom'."
        )

    tv_ctx.remote.set_ambilight_color(
        color=AmbilightColor.from_tuple(color) if color else None,
        left=AmbilightColor.from_tuple(left) if left else None,
        top=AmbilightColor.from_tuple(top) if top else None,
        right=AmbilightColor.from_tuple(right) if right else None,
        bottom=AmbilightColor.from_tuple(bottom) if bottom else None,
    )


@cli.group("app", help="Manage applications.")
def app() -> None:
    pass


@app.command("list", help="List all available applications.")
@pass_tv_context
@handle_tv_errors
def app_list(tv_ctx: TVContext) -> None:
    click.echo("\n".join(tv_ctx.remote.get_applications()))


@app.command("launch", help="Launch an application.")
@click.argument("application", type=click.STRING)
@pass_tv_context
@handle_tv_errors
def app_launch(tv_ctx: TVContext, application: str) -> None:
    tv_ctx.remote.launch_application(application)
