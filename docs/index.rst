Welcome to Muffin
=================

.. toctree::
   :maxdepth: 2
   
   index
   installation
   quickstart

.. image:: static/logo.png
   :height: 100px
   :width: 100px
   :alt: Muffin: A web-framework based on Asyncio stack

Welcome to Muffin's documentation.

Muffin is a web-framework based on aiohttp_, :term:`asyncio` (:pep:`3156`).

Example "Hello World" with the Muffin:

.. code-block:: python

    import muffin


    app = muffin.Application('example')


    @app.register('/', '/hello/{name}')
    def hello(request):
        name = request.match_info.get('name', 'anonymous')
        return 'Hello %s!' % name


.. _aiohttp: http://aiohttp.readthedocs.org/en/stable/
