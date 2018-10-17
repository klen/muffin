Welcome to Muffin
=================

.. image:: static/logo.png
   :height: 100px
   :width: 100px
   :alt: Muffin: A web-framework based on Asyncio stack

Welcome to Muffin's documentation.

.. _important:

    The framework has been created in 2015 when asyncio/aiohttp stack was very
    young and small. It was an attempt to build a foundation for asyncio web
    based project with all required tools (plugins system, admin interfaces,
    REST API and etc). For current moment (2018) aiohttp stack is quite good
    and the Muffin is depricated. It can be supported because some projects
    still use it but if you are planning to start a new project I would
    recomend to have a look on something else.

.. _danger:

    The documentation can be outdated.

Muffin is a web-framework based on aiohttp_, :term:`asyncio` (:pep:`3156`).

Example "Hello World" with the Muffin:

.. code-block:: python

    import muffin


    app = muffin.Application('example')


    @app.register('/', '/hello/{name}')
    def hello(request):
        name = request.match_info.get('name', 'anonymous')
        return 'Hello %s!' % name

    if __name__ == '__main__':
        app.manage()
        
      
Table of Contents
=================
        
.. toctree::
   
   installation
   quickstart
   configuration
   cli
   testing
   plugins


.. _aiohttp: http://aiohttp.readthedocs.org/en/stable/
