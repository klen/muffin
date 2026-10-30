Deployment
==========

Deploying with Docker
---------------------

Muffin has an official image, `horneds/muffin
<https://hub.docker.com/r/horneds/muffin>`_: it carries Python, an ASGI server and
Muffin, so a deployment only has to copy the application code.

Write ``app.py``:

.. code-block:: python

    from muffin import Application

    app = Application()

    @app.route("/")
    async def index(request):
        return "Hello World!"

and a ``Dockerfile`` next to it:

.. code-block:: dockerfile

    FROM horneds/muffin:latest

    COPY . /app

Build and run:

.. code-block:: console

    $ docker build -t myimage .
    $ docker run -d --name mycontainer -p 80:80 myimage

Open http://localhost. Configuration still comes from the environment, so
``MUFFIN_*`` variables (see :doc:`configuration`) are the way to change behavior
per deployment.

Ways to run it
--------------

Pick the server by what you need:

- ``uvicorn app:app --reload``: development, restarts on file changes
- ``muffin app run``: the same uvicorn, with the app's ``LOG_CONFIG`` applied
- ``gunicorn app:app -k uvicorn.workers.UvicornWorker -w 4``: production, several
  worker processes in one container

Workers are separate processes with separate memory: application state, plugin
clients and in-memory caches are not shared between them. Anything that must be
shared (sessions, background jobs, rate limits) belongs in Redis or a database, not
in a module-level dict. ``MUFFIN_AIOLIB`` applies per process, so set it in the
container environment, not in code.

Safety
------

A few settings matter more in production than anywhere else:

- **Host header**: set ``USE_HOSTS = True`` and pass ``hosts=`` to the routes that
  are only valid for one domain; the router then rejects requests for unknown
  hosts instead of answering them. See :doc:`usage`.
- **Form size**: ``await request.form(max_size=...)`` raises
  ``ASGIRequestEntityTooLargeError`` instead of buffering whatever arrives. Large
  uploads need ``upload_to`` or a size limit that matches reality.
- **Proxies**: behind a proxy, the client address and scheme come from the
  ``X-Forwarded-*`` headers, which any client can forge. Trust them only from your
  proxy, and keep the proxy's own limits (body size, timeouts) as the outer line of
  defense.
- **Debug**: ``DEBUG = True`` leaks tracebacks and is never deployed. Set it from
  the environment so the default is safe.

Deploying behind NGINX
----------------------

A reverse proxy in front of the application buys three things: it filters
malformed requests, it can run several Muffin workers on all CPU cores, and it
serves static files faster than the application does.

.. code-block:: nginx

    http {
        server {
            listen 80;
            client_max_body_size 4G;

            server_name example.com;

            location / {
                proxy_set_header Host $http_host;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_redirect off;
                proxy_buffering off;
                proxy_pass http://muffin;
            }

            location /static {
                root /path/to/app/static;
            }
        }

        upstream muffin {
            # Unix sockets are faster and survive port collisions
            server unix:/tmp/example_1.sock fail_timeout=0;
            server unix:/tmp/example_2.sock fail_timeout=0;
            server unix:/tmp/example_3.sock fail_timeout=0;
            server unix:/tmp/example_4.sock fail_timeout=0;

            # Alternatively, TCP sockets:
            # server 127.0.0.1:8081 fail_timeout=0;
            # server 127.0.0.1:8082 fail_timeout=0;
            # server 127.0.0.1:8083 fail_timeout=0;
            # server 127.0.0.1:8084 fail_timeout=0;
        }
    }

The config listens on port 80 for ``example.com``, proxies requests to the Muffin
workers and serves ``/path/to/app/static`` itself. See the `nginx proxy module
docs <http://nginx.org/en/docs/http/ngx_http_proxy_module.html>`_ for the rest of
the directives; HAProxy and other proxies work the same way.
