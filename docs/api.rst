API reference
=============

.. module:: philipstv

This part of the documentation lists the full API reference of all public classes and functions.


High level
-----------------------

The simplest and easiest to use interface to the TV. This is probably what you should use, unless
you plan some advanced API operations. One of the examples where this will *not* be enough is
manipulating individual Ambilight light points.

.. autoclass:: PhilipsTVRemote
   :class-doc-from: both
   :members:


Low level
-----------------------

More complicated, but also more powerful interface.

.. autoclass:: PhilipsTVAPI
   :class-doc-from: both
   :members:

.. autoclass:: PhilipsTVPairer
   :class-doc-from: both
   :members:

.. autoclass:: PhilipsTV
   :class-doc-from: both
   :members:

Exceptions
----------

.. autoexception:: PhilipsError

.. autoexception:: PhilipsTVError

.. autoexception:: PhilipsTVPairingError

.. autoexception:: PhilipsTVAPIError

.. autoexception:: PhilipsTVAPIUnauthorizedError

.. autoexception:: PhilipsTVAPIMalformedResponseError

.. autoexception:: PhilipsTVRemoteError

API models
-----------

.. module:: philipstv.model

Wrappers around API request payloads and responses.

Base
^^^^

.. autoclass:: APIObject
   :members:

.. autoclass:: StrEnum
   :members:


Pairing
^^^^^^^

.. autoclass:: DeviceInfo
   :members:

.. autoclass:: PairingAuthInfo
   :members:

.. autoclass:: PairingRequestPayload
   :members:

.. autoclass:: PairingGrantPayload
   :members:

.. autoclass:: PairingResponse
   :members:

.. autoclass:: PairingRequestResponse
   :show-inheritance:
   :members: error_id, error_text, auth_key, timestamp, timeout

General
^^^^^^^

.. autoenum:: PowerStateValue
   :members:

.. autoclass:: PowerState
   :members:

Audio
^^^^^

.. autoclass:: Volume
   :members:

.. autoclass:: CurrentVolume
   :members: current, muted, min, max

Channels
^^^^^^^^

.. autoclass:: ChannelID
   :members:

.. autoclass:: ChannelShort
   :show-inheritance:
   :members: ccid, preset, name

.. autoclass:: Channel
   :show-inheritance:
   :members: ccid, preset, name, onid, tsid, sid, service_type, type, logo_version

.. autoclass:: ChannelListID
   :members:

.. autoclass:: ChannelList
   :members: id, version

.. autoclass:: CurrentChannel
   :members:

.. autoclass:: SetChannel
   :members:

.. autoclass:: AllChannels
   :members:

Input
^^^^^
.. autoenum:: InputKeyValue
   :members:

.. autoclass:: InputKey
   :members:

Ambilight
^^^^^^^^^

.. autoenum:: AmbilightPowerValue
   :members:

.. autoclass:: AmbilightPower
   :members:

.. autoclass:: AmbilightTopology
   :members:

.. autoenum:: AmbilightModeValue
   :members:

.. autoclass:: AmbilightMode
   :members:

.. autoclass:: AmbilightColor
   :members:

.. autoclass:: AmbilightLayer
   :members:

.. autoclass:: AmbilightColors
   :members:

Applications
^^^^^^^^^^^^

.. autoclass:: ApplicationComponent
   :members:

.. autoclass:: ApplicationIntent
   :members:

.. autoclass:: ApplicationShort
   :members:

.. autoclass:: Application
   :show-inheritance:
   :members: intent, label, order, id, type

.. autoclass:: Applications
   :members:
