Testing
========

Requirements
------------

You should have the WebTest package installed.

Setup tests
-----------

Set module path to your Muffin Application in pytest configuration file or use
command line option ``--muffin-app``.

Example: ::

    $ py.test -xs --muffin-app example

Testing application
-------------------

See examples:

.. code-block:: python

    import pytest

    @pytest.mark.async
    def test_async_code():
        from aiohttp import request
        response = yield from request('GET', 'http://google.com')
        text = yield from response.text()
        assert 'html' in text

    def test_app(app):
        """ Get your app in your tests as fixture. """
        assert app.name == 'my app name'
        assert app.cfg.MYOPTION == 'develop'

    def test_view(client):
        """ Make HTTP request to your application. """
        response = client.get('/my-handler')
        assert 'mydata' in response.text
