import logging
from dataclasses import dataclass
from typing import Optional, Tuple, Union

import click

from philipstv import InputKeyValue, PhilipsTVRemote, __version__
from philipstv.api.model.ambilight import AmbilightColor
from philipstv.data import HostData, PhilipsTVData
from philipstv.exceptions import PhilipsTVPairingError, PhilipsTVRemoteError

_LOGGER = logging.getLogger(__name__)

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
def cli(
    ctx: click.Context,
    host: Optional[str],
    id: Optional[str],
    key: Optional[str],
    save: bool,
    debug: bool,
) -> None:
    """Welcome to philipstv - a CLI remote control for Philips Android-powered TVs.

    Before you will be able to use this program, you need to pair it with your TV. Before starting,
    ensure your TV is powered on. The simplest way to perform pairing is by running:

    \b
        philipstv --host IP --save pair

    You will be asked to enter the PIN number displayed on the TV screen. After the pairing process
    is complete, your credentials will be saved for future use. From now on, you can just use the
    remote.

    To learn more about usage, just try to run any of the commands listed below, followed by '-h'.
    You will receive help regarding any subcommands or arguments. Try:

    \b
        philipstv ambilight -h

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
        ctx.obj = TVContext(PhilipsTVRemote.new(host or ""), host, id, None, save)
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
        _LOGGER.debug("Using saved data: host=%s, id=%s", host, id)
    elif save:  # if all auth is given and we want to save
        PhilipsTVData(last_host=HostData(host=host, id=id, key=key)).save()

    ctx.obj = TVContext(PhilipsTVRemote.new(host, (id, key)), host, id, key, save)


@cli.command("pair", help="Pair with the TV to obtain credentials.")
@pass_tv_context
@click.pass_context
def pair(ctx: click.Context, tv_ctx: TVContext) -> None:
    if not tv_ctx.host:
        raise click.UsageError("No host given (--host).")
    if tv_ctx.key:
        raise click.UsageError("Option --key is invalid in pairing context.")

    def prompt_pin() -> str:
        return str(click.prompt(text="Enter PIN displayed on the TV", type=click.STRING))

    try:
        credentials = tv_ctx.remote.pair(prompt_pin, tv_ctx.id)
    except PhilipsTVPairingError as err:
        click.echo(str(err), err=True)
        ctx.exit(1)

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
def get_power(tv_ctx: TVContext) -> None:
    click.echo("on" if tv_ctx.remote.get_power() else "off")


@power.command("set", help="Set power state.")
@click.argument("power", type=click.Choice(("on", "off")))
@pass_tv_context
def set_power(tv_ctx: TVContext, power: str) -> None:
    tv_ctx.remote.set_power(True if power == "on" else False)


@cli.group("volume", help="Manage audio volume.")
def volume() -> None:
    pass


@volume.command("get", help="Get current audio volume.")
@pass_tv_context
def get_volume(tv_ctx: TVContext) -> None:
    click.echo(tv_ctx.remote.get_volume())


@volume.command("set", help="Set audio volume.")
@click.argument("volume", type=click.INT)
@pass_tv_context
def set_volume(tv_ctx: TVContext, volume: int) -> None:
    tv_ctx.remote.set_volume(volume)


@cli.group("channel", help="Manage TV channels.")
def channel() -> None:
    pass


@channel.command("get", help="Get current TV channel.")
@pass_tv_context
def get_current_channel(tv_ctx: TVContext) -> None:
    click.echo(tv_ctx.remote.get_current_channel())


@channel.command("list", help="List all available TV channels.")
@pass_tv_context
def get_all_channels(tv_ctx: TVContext) -> None:
    click.echo("\n".join(f"{no}\t {chan}" for no, chan in tv_ctx.remote.get_all_channels().items()))


@channel.command("set", help="Set TV channel.")
@click.argument("channel", type=click.STRING)
@pass_tv_context
@click.pass_context
def set_channel(ctx: click.Context, tv_ctx: TVContext, channel: str) -> None:
    set_channel: Union[str, int] = channel
    if channel.isdigit():
        set_channel = int(set_channel)
    try:
        tv_ctx.remote.set_channel(set_channel)
    except PhilipsTVRemoteError as err:
        click.echo(err, err=True)
        ctx.exit(1)


@cli.command("key")
@click.argument("keys", type=click.Choice(tuple(KEY_MAP), case_sensitive=False), nargs=-1)
@pass_tv_context
def key(tv_ctx: TVContext, keys: Tuple[str]) -> None:
    """Emulate pressing keys on the TV remote.

    You can provide any number of key names, separated by a space. They will be sent to the TV in
    the given order.
    """
    for key in keys:
        tv_ctx.remote.input_key(KEY_MAP[key])


@cli.group("ambilight", help="Manage ambilight.")
def ambilight() -> None:
    pass


@ambilight.group("power", help="Manage ambilight power.")
def ambilight_power() -> None:
    pass


@ambilight_power.command("get", help="Get current ambilight power state.")
@pass_tv_context
def get_ambilight_power(tv_ctx: TVContext) -> None:
    click.echo("on" if tv_ctx.remote.get_ambilight_power() else "off")


@ambilight_power.command("set", help="Set ambilight power state.")
@click.argument("power", type=click.Choice(("on", "off")))
@pass_tv_context
def set_ambilight_power(tv_ctx: TVContext, power: str) -> None:
    tv_ctx.remote.set_ambilight_power(True if power == "on" else False)


@ambilight.group("color", help="Manage ambilight color.")
def ambilight_color() -> None:
    pass


@ambilight_color.command("set", help="Set ambilight color.")
@click.argument("r", type=click.IntRange(0, 255))
@click.argument("g", type=click.IntRange(0, 255))
@click.argument("b", type=click.IntRange(0, 255))
@pass_tv_context
def set_ambilight_color(tv_ctx: TVContext, r: int, g: int, b: int) -> None:
    tv_ctx.remote.set_ambilight_color(AmbilightColor(r=r, g=g, b=b))


@cli.group("app", help="Manage applications.")
def app() -> None:
    pass


@app.command("list", help="List all available applications.")
@pass_tv_context
def list_applications(tv_ctx: TVContext) -> None:
    click.echo("\n".join(tv_ctx.remote.get_applications()))


@app.command("launch", help="Launch an application.")
@click.argument("application", type=click.STRING)
@pass_tv_context
@click.pass_context
def launch_application(ctx: click.Context, tv_ctx: TVContext, application: str) -> None:
    try:
        tv_ctx.remote.launch_application(application)
    except PhilipsTVRemoteError as err:
        click.echo(err, err=True)
        ctx.exit(1)
