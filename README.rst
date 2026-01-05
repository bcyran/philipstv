philipstv
=========

.. image:: https://github.com/bcyran/philipstv/actions/workflows/test.yml/badge.svg
   :target: https://github.com/bcyran/philipstv/actions/workflows/test.yml
   :alt: test

.. image:: https://github.com/bcyran/philipstv/actions/workflows/release.yml/badge.svg
   :target: https://github.com/bcyran/philipstv/actions/workflows/release.yml
   :alt: release

.. image:: https://codecov.io/gh/bcyran/philipstv/branch/master/graph/badge.svg?token=ROJONX34RB
   :target: https://codecov.io/gh/bcyran/philipstv
   :alt: codecov

.. image:: https://readthedocs.org/projects/philipstv/badge/?version=latest
   :target: https://philipstv.readthedocs.io/en/stable/?badge=latest
   :alt: Documentation status

.. image:: https://img.shields.io/pypi/v/philipstv
   :target: https://pypi.org/project/philipstv/
   :alt: pypi

.. image:: https://img.shields.io/pypi/pyversions/philipstv
   :target: https://pypi.org/project/philipstv/
   :alt: versions

.. image:: https://img.shields.io/github/license/bcyran/philipstv
   :target: https://github.com/bcyran/philipstv/blob/master/LICENSE
   :alt: license

.. -begin-intro-

Python package providing CLI and library for interacting with Philips Android-powered TVs.

Features:

- Get and set TV power state.
- Get and set volume.
- List and change TV channels.
- Emulate pressing remote keys.
- Get and set Ambilight power state.
- Get and set Ambilight color.
- List and launch applications.

Installation
------------

Package Repositories
^^^^^^^^^^^^^^^^^^^^

.. image:: https://repology.org/badge/vertical-allrepos/philipstv.svg
   :target: https://repology.org/project/philipstv/versions
   :alt: Packaging status

PyPI
^^^^

If you plan to use the CLI:

.. code-block:: console

   $ pip install 'philipstv[cli]'

If you only need library for use in Python code:

.. code-block:: console

   $ pip install philipstv

.. -end-intro-

Arch Linux (AUR)
^^^^^^^^^^^^^^^^

`philipstv AUR package <https://aur.archlinux.org/packages/philipstv>`_ is available.


Documentation
-------------
See full documentation: `Read the Docs: philipstv <https://philipstv.readthedocs.io>`_.

See also
--------
- `PhilipsTV GUI <https://github.com/bcyran/philipstv-gui>`_ - GUI application built with this library.

Resources
---------
- `Fantastic unofficial API documentation <https://github.com/eslavnov/pylips/blob/master/docs/Home.md>`_ and `script <https://github.com/eslavnov/pylips>`_ by `@eslavnov <https://github.com/eslavnov>`_.
- Philips `JointSpace API documentation <http://jointspace.sourceforge.net/projectdata/documentation/jasonApi/1/doc/API.html>`_.
