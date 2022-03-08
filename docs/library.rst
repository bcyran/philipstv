Library usage
=============

The library is split into classes providing functionality at differing levels of abstraction.
Each higher layer uses a lower layer and builds some functionality on top of it.
Those layers are described here from the highest to the lowest, because I think the higher ones are much more useful in most cases.

This page does not show every library functionality, it aims to explain general intention of how specific components should be used.
For full description of provided features, see :doc:`api`.

High level
----------
The highest level of interaction with the TV is provided via :class:`~philipstv.PhilipsTVRemote` class.
It can be instantiated using :func:`~philipstv.PhilipsTVRemote.new` method or by injecting lower level :class:`~philipstv.PhilipsTVAPI` instance into the constructor.

:func:`~philipstv.PhilipsTVRemote.new` accepts the TV's IP address, and optionally, credentials tuple, as arguments.
Credentials should be omitted only when the class instantiated with intention of pairing.

Pairing is performed using :func:`~philipstv.PhilipsTVRemote.pair` method which accepts callback function as a single argument.
The callback function should accept no parameters and return PIN displayed on the TV as a string.
There's no way to know the PIN in advance, before starting the pairing process, so this will always require some kind of user input.

.. doctest::

    >>> from philipstv import PhilipsTVRemote
    >>>
    >>> def pin_callback():
    ...     return str(input("Enter PIN: "))
    ...
    >>> remote = PhilipsTVRemote.new("192.168.0.100")
    >>> remote.pair(pin_callback)
    Enter PIN: 5860
    ('hda0Uuxzt0kzq5Hl', '94451f736ce6cdad6248d377eb356211f1eda85cea35b62bf2d96505f800fbcd')

Pair returns a tuple of credentials which can be used to authenticate with the TV from now on:

.. doctest::

    >>> credentials = ("hda0Uuxzt0kzq5Hl", "94451f736ce6cdad6248d377eb356211f1eda85cea35b62bf2d96505f800fbcd")
    >>> remote = PhilipsTVRemote.new("192.168.0.100", credentials)
    >>> remote.get_power()
    True

Authenticated :class:`~philipstv.PhilipsTVRemote` instance gives you access to most of the library features in the most convenient form, for instance:

.. doctest::

    >>> from philipstv import AmbilightColor, InputKeyValue
    >>>
    >>> remote.get_volume()
    10
    >>> remote.get_applications()
    ['YouTube', 'TED', 'Twitch', 'Prime Video', 'Netflix', 'TV', 'CANAL+', 'HBO Max', 'Spotify', 'HBO GO']
    >>> remote.launch_application("Netflix")
    >>> remote.input_key(InputKeyValue.CONFIRM)
    >>> remote.set_ambilight_color(AmbilightColor(r=255, g=0, b=0))


Low level
---------
Lower level of interaction is provided via :class:`~philipstv.PhilipsTVAPI` class.
Each method of this class wraps a single `GET` or `POST` request to one of the available API endpoints.
Request and response payloads are preserved in original shapes but wrapped in `pydantic` model objects.
The models make it impossible to send total gibberish to the TV, nethertheless you have to be familiar with the actual TV API in order to use it.

The only way to instantiate :class:`~philipstv.PhilipsTVAPI` is to pass :class:`~philipstv.PhilipsTV` instance to constructor:

.. doctest::

    >>> from philipstv import PhilipsTV, PhilipsTVAPI
    >>> api = PhilipsTVAPI(PhilipsTV("192.168.0.100"))

Pairing on this level can be performed fully manually using :func:`~philipstv.PhilipsTVAPI.pair_request` and :func:`~philipstv.PhilipsTVAPI.pair_grant` methods, but it's definitely not recommended.
Another way it to automate it using :class:`~philipstv.PhilipsTVPairer`.
You still have to provide full information describing requesting device (it was automated and hidden at the higher level), but the process is simplified to a single call of a :func:`~philipstv.PhilipsTVPairer.pair` method:

.. doctest::

    >>> from philipstv import DeviceInfo, PhilipsTV, PhilipsTVAPI, PhilipsTVPairer
    >>>
    >>> api = PhilipsTVAPI(PhilipsTV("192.168.0.100"))
    >>> device_info = DeviceInfo(id="<id>", device_name="<name>", device_os="<os>", app_id="<id>", app_name="<name>", type="<type>")
    >>>
    >>> def pin_callback():
    ...     return str(input("Enter PIN: "))
    ...
    >>> PhilipsTVPairer(api, device_info).pair(pin_callback)
    Enter PIN: 7182
    ('<id>', 'c3a82e73e8b3daa5ab2fff81542c07f05eaf40ad698443836664831d31499065')

As far as I'm aware the only value of :class:`~philipstv.model.DeviceInfo` which makes any actual difference is the ``id``.
As visible in the example, after successful pairing, this value will be used as a first value in credentials tuple.

Some usage examples:

.. doctest::

    >>> from philipstv import PhilipsTV, PhilipsTVAPI
    >>> from philipstv.model import Volume
    >>>
    >>> credentials = ("<id>", "c3a82e73e8b3daa5ab2fff81542c07f05eaf40ad698443836664831d31499065")
    >>> api = PhilipsTVAPI(PhilipsTV("192.168.0.100", auth=credentials))
    >>>
    >>> api.get_powerstate()
    PowerState(powerstate='On')
    >>> api.set_volume(Volume(current=15))
    >>> api.get_ambilight_topology()
    AmbilightTopology(layers=1, left=3, top=7, right=3, bottom=0)
    >>> api.get_current_channel()
    CurrentChannel(channel=ChannelShort(ccid=44, preset='12', name='Polsat Comedy Central Extra'), channel_list=ChannelList(id='allcab', version='1'))


Direct TV access
----------------
There's also a possibility of sending raw authenticated requests to the tv using :class:`~philipstv.PhilipsTV` class.

.. doctest::

    >>> tv = PhilipsTV("192.168.0.100", auth=("<id>", "<key>"))
    >>> tv.get("6/audio/volume")
    {'muted': False, 'current': 15, 'min': 0, 'max': 60}
    >>> tv.post("6/audio/volume", {"current": 10})
