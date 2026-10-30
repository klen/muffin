Walkthrough
===========

Build a small app end to end: package layout, configuration, a template, a form
and tests. The code below runs as written with ``muffin`` and ``muffin-jinja2``
installed.

Layout
------

::

    todo/
        __init__.py          application object, imports the rest
        settings.py          configuration module
        storage.py           the "database"
        views.py             routes
        manage.py            CLI commands
        templates/
            index.html
    tests/
        conftest.py
        test_app.py

``__init__.py`` creates the application and pulls in the modules that register
routes and commands:

.. code-block:: python

    # todo/__init__.py
    from muffin import Application

    app = Application("todo.settings")
    app.import_submodules("views", "manage")

``import_submodules`` imports the named submodules of the calling package, in
order, so registration order is explicit instead of alphabetical. Called without
arguments it imports every submodule, which is fine while the project is small.

Configuration
-------------

.. code-block:: python

    # todo/settings.py
    NAME = "todo"
    DEBUG = False

    JINJA2_TEMPLATE_FOLDERS = ["todo/templates"]

Set ``NAME`` first: it prefixes environment variables. With the module above,
every option is overridable as ``TODO_*``:

.. code-block:: console

  $ TODO_DEBUG=true uvicorn todo:app

Template folders are resolved against the process working directory, so they are
written relative to the project root. Precedence rules are in
:doc:`configuration`.

Storage
-------

.. code-block:: python

    # todo/storage.py
    ITEMS = []

    async def save(title):
        ITEMS.append(title)

    async def load_items():
        return list(ITEMS)

A real project would talk to a database here, through one of the plugins.

Routes and templates
--------------------

``views.py`` registers routes on the application object imported from the package:

.. code-block:: python

    # todo/views.py
    import muffin_jinja2

    from . import app
    from .storage import load_items, save

    jinja2 = muffin_jinja2.Plugin(app)

    @app.route("/", methods=["GET", "POST"])
    async def index(request):
        if request.method == "POST":
            form = await request.form()
            title = form.get("title", "")
            if title:
                app.run_after_response(save(title))
                return 303, {"Location": "/"}, ""

        items = await load_items()
        return await jinja2.render("index.html", items=items)

The handler reads the form, schedules storage work that does not need to delay
the response, and renders a template. ``303`` with ``Location`` is a redirect the
browser replays as a ``GET``, so refreshing the page does not resubmit the form.
Returning a tuple of ``(status, headers, content)`` is what makes the redirect
possible; a two-element tuple is read as ``(status, content)``.

.. code-block:: html

    <!-- todo/templates/index.html -->
    <form method="post">
      <input name="title" placeholder="What needs doing?">
      <button>Add</button>
    </form>
    <ul>
      {% for item in items %}<li>{{ item }}</li>{% endfor %}
    </ul>

Commands
--------

.. code-block:: python

    # todo/manage.py
    from . import app
    from .storage import save

    @app.manage
    async def add(title):
        """Add an item without opening the browser.

        :param title: Item text
        """
        await save(title)
        print(f"added: {title}")

.. code-block:: console

  $ muffin todo add "buy milk"
  added: buy milk

The function name becomes the command name, ``:param`` lines become its help.
The command API is described in :doc:`cli`.

Tests
-----

The local fixtures below override the ones from the pytest plugin, which keeps
application state between tests otherwise: the plugin's ``app`` fixture is
session-scoped.

.. code-block:: python

    # tests/conftest.py
    import pytest

    from muffin import TestClient


    @pytest.fixture
    def app():
        from todo import app as todo_app
        return todo_app


    @pytest.fixture
    def client(app):
        return TestClient(app)

.. code-block:: python

    # tests/test_app.py
    async def test_index(client):
        response = await client.get("/")
        assert response.status_code == 200
        assert "Add" in await response.text()

    async def test_add(client):
        response = await client.post("/", data={"title": "buy milk"}, follow_redirect=False)
        assert response.status_code == 303
        assert response.headers["location"] == "/"

Async tests need a runner; ``pytest-aio`` is what Muffin itself uses, and it
parametrizes the backend. Details in :doc:`testing`.

Running it
----------

.. code-block:: console

  $ uvicorn todo:app --reload             # development
  $ muffin todo run --port 8000           # the same app through the CLI
  $ pytest tests -xs                     # tests

Deployment notes (Docker, NGINX, workers) are in :doc:`deploy`.
