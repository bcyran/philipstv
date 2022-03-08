# philipstv

[![CI](https://github.com/bcyran/philipstv/workflows/CI/badge.svg?event=push)](https://github.com/bcyran/philipstv/actions?query=event%3Apush+branch%3Amaster+workflow%3ACI)
[![codecov](https://codecov.io/gh/bcyran/philipstv/branch/master/graph/badge.svg?token=ROJONX34RB)](https://codecov.io/gh/bcyran/philipstv)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![pypi](https://img.shields.io/pypi/v/philipstv)](https://pypi.org/project/philipstv/)
[![Documentation Status](https://readthedocs.org/projects/philipstv/badge/?version=latest)](https://philipstv.readthedocs.io/en/latest/?badge=latest)
[![versions](https://img.shields.io/pypi/pyversions/philipstv)](https://pypi.org/project/philipstv/)
[![license](https://img.shields.io/github/license/bcyran/philipstv)](https://github.com/bcyran/philipstv/blob/master/LICENSE)

Python CLI and library for controlling Philips Android-powered TV's.

Features:
- Get and set current TV power state.
- Get and set current volume
- List and change TV channels.
- Emulate pressing remote keys.
- Get and set ambilight power state.
- Set ambilight RGB color.
- List and launch applications.

## Installation
If you plan to use the CLI:
```shell
pip install 'philipstv[cli]'
```

If you only need a library for use in Python code:
```shell
pip install philipstv
```

## CLI

### Pairing
First, you need to pair *philipstv* with your TV.
For this, you need to know its IP address.
You can find it in network settings.

Pairing is done using the following command:
```shell
philipstv --host IP [--id ID] [--save] pair
```

- `--host` (required) specifies the TV IP address.
- `--id` (optional) specifies the device ID to use during pairing.
  This will be later used for authentication.
  If not provided, the ID is generated randomly.
- `--save` saves received credentials after successful pairing.
  Use this if you don't want to provide credentials every time you run *philipstv*.

After running `pair` command, you will be prompted to enter PIN number displayed on the TV's screen.
This completes the process and outputs your credentials.

The complete process should look like this:
```
$ philipstv --host 192.168.0.100 --save pair
Enter PIN displayed on the TV: 5639
Pairing successful!
ID:     JMBsfOjJDYg5gxRG
Key:    151080ea24e06ef4acc410a98398129e9de9edf43b1569ffb8249301945f5868
Credentials saved.
```

### Usage
Once paired, use received credentials to authenticate. E.g.:
```shell
philipstv --host 192.168.0.100 --id JMBsfOjJDYg5gxRG --key 151080ea24e06ef4acc410a98398129e9de9edf43b1569ffb8249301945f5868 power get
```
If you used the `--save` option during pairing, this is just:
```shell
philipstv power get
```
The CLI is fully documented, so you can explore commands using `-h` option: `philipstv -h`, `philipstv power -h`, etc...

Example usage session could look like this:
```
$ philipstv power set on
$ philipstv volume set 15
$ philipstv ambilight set on
$ philipstv app list
YouTube
TED
Twitch
Prime Video
Netflix
$ philipstv launch Netflix
$ philipstv key ok
$ philipstv key play
```

## Library
I really hope I will find strength to create proper documentation, for now those few examples + source code will have to be enough.

### `PhilipsTVRemote`
High level TV interaction interface.
It wraps API functionality into convenient and easy to use methods.

Pairing:
```python
from philipstv import PhilipsTVRemote

def pin_callback():
    return str(input("Enter PIN: "))

remote = PhilipsTVRemote.new("192.168.0.100")
id, key = remote.pair(pin_callback)
```

Usage with credentials:
```python
from philipstv import InputKeyValue, PhilipsTVRemote

remote = PhilipsTVRemote.new("192.168.0.100", ("<id>", "<key>"))
remote.set_power(True)
current_volume = remote.get_volume()
remote.set_volume(current_volume + 10)
remote.set_ambilight_power(True)
remote.launch_application("Netflix")
remote.input_key(InputKeyValue.OK)
remote.input_key(InputKeyValue.PLAY)
```

### `PhilipsTVAPI`
Lower level interface.
Each method mirrors one request to one API endpoint.
Input and output values have original shape, just like in API, but are wrapped in [`pydantic`](https://github.com/samuelcolvin/pydantic) models.

Pairing:
```python
from philipstv import DeviceInfo, PhilipsTV, PhilipsTVAPI, PhilipsTVPairer

api = PhilipsTVAPI(PhilipsTV("192.168.0.100"))
device_info = DeviceInfo(
    id="<id>",
    device_name="<name>",
    device_os="<os>",
    app_id="<id>",
    app_name="<name>",
    type="<type>",
)


def pin_callback():
    return str(input("Enter PIN: "))

id, key = PhilipsTVPairer(api, device_info).pair(pin_callback)
```

And using with credentials:
```python
from philipstv import PhilipsTV, PhilipsTVAPI
from philipstv.model import PowerState, PowerStateValue, Volume

api = PhilipsTVAPI(PhilipsTV("192.168.0.100", auth=("<id>", "<key>")))

api.set_powerstate(PowerState(powerstate=PowerStateValue.ON))
api.set_volume(Volume(current=15, muted=False))
```

### `PhilipsTV`
Lowest level interface. Acts as a helper for sending authenticated requests to the TV.

For instance:
```python
tv = PhilipsTV("192.168.0.100", auth=("<id>", "<key>"))
volume_resp = tv.get("6/audio/volume")
volume = volume_resp["current"]
tv.post("6/audio/volume", {"current": volume + 10})
```

## Resources
- [Fantastic unofficial API documentation](https://github.com/eslavnov/pylips/blob/master/docs/Home.md) and [script](https://github.com/eslavnov/pylips) by [@eslavnov](https://github.com/eslavnov).
- Philips [JointSpace API documentation](http://jointspace.sourceforge.net/projectdata/documentation/jasonApi/1/doc/API.html).
