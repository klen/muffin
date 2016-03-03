Quickstart
==========

This page gives an introduction to Muffin. It assumes you already have the
library installed, how it described in :ref:`installation` section.

An Example Application
----------------------

Example "Hello User" with the Muffin:

.. code-block:: python

    import muffin

    app = muffin.Application('example')

    @app.register('/', '/hello/{name}')
    def hello(request):
        name = request.match_info.get('name', 'anonymous')
        return 'Hello %s!' % name

What did that code do?

1. First we imported the :class:`~muffin.Application` class.  An instance of
   this class will be our application.
2. Next we create an instance of this class. The first argument is the name of
   the application.
3. We then use the :meth:`~muffin.Application.register` decorator to tell Muffin
   what URLs should trigger our handler function.
4. The function returns the message we want to display in the user's browser.

Save the script as example.py and run it:

.. code-block:: console

    $ python3 example.py run
