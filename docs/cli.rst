CLI usage
=========

Help
----
Whole CLI is documented using help messages.
You can explore every single feature using ``-h`` or ``--help`` options, like this:

.. code-block:: console

    $ philipstv -h
    $ philipstv pair -h
    $ philipstv ambilight color -h


Pairing
-------
Before you'll be able to use ``philipstv``, you need to pair it with your TV.
For this, you need to know its IP addressed.
You can find it in network settings.

Pairing is done using the following command:

.. code-block:: console

   $ philipstv --host IP [--id ID] [--save] pair

- ``--host`` (required) specifies the TV IP address.
- ``--id`` (optional) specifies the device ID to use during pairing.
  This will be later used for authentication.
  If not provided, random ID is generated.
- ``-save`` (optional) saves credentials after successful pairing.
  Use this if you don't want to provide credentials every time you run ``philipstv``.

The complete pairing process can look like this:

.. code-block:: console

    $ philipstv --host 192.168.0.100 --save pair
    Enter PIN displayed on the TV: 5639
    Pairing successful!
    ID:     JMBsfOjJDYg5gxRG
    Key:    151080ea24e06ef4acc410a98398129e9de9edf43b1569ffb8249301945f5868
    Credentials saved.

Usage
-----
Once paired, use received credentials to authenticate, e.g.:

.. code-block:: console

   $ philipstv --host 192.168.0.100 --id JMBsfOjJDYg5gxRG --key 151080ea24e06ef4acc410a98398129e9de9edf43b1569ffb8249301945f5868 power get

If you used ``--save`` option during pairing, this is just:

.. code-block:: console

   $ philipstv power get

If you did not use ``--save``, but would like to save the credentials now, just throw in ``--save`` to whatever command while providing ``--host``, ``--id`` and ``--key`` as well.

Example usage session could look like this:

.. code-block:: console

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
