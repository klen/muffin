The Muffin
##########

.. _description:

The Muffin -- A web framework based on Asyncio stack. **(early alpha)**

.. _badges:

.. image:: http://img.shields.io/travis/klen/muffin.svg?style=flat-square
    :target: http://travis-ci.org/klen/muffin
    :alt: Build Status

.. image:: http://img.shields.io/coveralls/klen/muffin.svg?style=flat-square
    :target: https://coveralls.io/r/klen/muffin
    :alt: Coverals

.. image:: http://img.shields.io/pypi/v/muffin.svg?style=flat-square
    :target: https://pypi.python.org/pypi/muffin

.. image:: http://img.shields.io/pypi/dm/muffin.svg?style=flat-square
    :target: https://pypi.python.org/pypi/muffin

.. image:: http://img.shields.io/gratipay/klen.svg?style=flat-square
    :target: https://www.gratipay.com/klen/
    :alt: Donate

.. _contents:

.. contents::

.. _requirements:

Requirements
=============

- python >= 3.3

.. _installation:

Installation
=============

**The Muffin** should be installed using pip: ::

    pip install muffin

.. _usage:

Usage
=====

See sources of example application.

Run example server: ::

    $ make run

Configuration
-------------

Muffin gets configuration options from python files. By default the package
tries to load a configuration from `config` module (config.py).

There are few ways to redifine configuration module:

* Set configuration module in your app initialization: ::

    app = muffin.Application('myapp', CONFIG='config.debug')

* Set environment variable `MUFFIN_CONFIG`: ::

    $ MUFFIN_CONFIG=settings_local python -m example.app runserver

Also you can define any options while initializing your application: ::

    app = muffin.Application('myapp', DEBUG=True, ANY_OPTION='Here', ONE_MORE='Yes')

When using ``gmuffin`` (see bellow): ::

    $ gmuffin -c example.config.debug example.app:app

Sessions
--------

Templates (Jade)
----------------

SQL (Peewee)
------------

CLI integration
---------------

.. _testing:

Testing
========

Set module path to your Muffin Application in pytest configuration file or use
command line option ``--muffin-app``.

Example: ::

    $ py.test -xs --muffin-app example.app:app

.. _deployment:

Deployment
==========

Use ``gmuffin`` command. By example: ::

    $ gmuffin --reload -w 4 example.app:app

See ``gmuffin --help`` for more info.

.. _bugtracker:

Bug tracker
===========

If you have any suggestions, bug reports or
annoyances please report them to the issue tracker
at https://github.com/klen/muffin/issues

.. _contributing:

Contributing
============

Development of The Muffin happens at: https://github.com/klen/muffin


Contributors
=============

* klen_ (Kirill Klenov)

.. _license:

License
=======

Licensed under a MIT license (See LICENSE)

.. _links:

.. _klen: https://github.com/klen
