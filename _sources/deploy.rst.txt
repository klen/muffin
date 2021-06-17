Deployment
==========

Deploy with Docker
------------------

You can use Docker for deployment. It has several advantages like security,
replicability, development simplicity, etc.

If you are using Docker, you can use the official Docker images:

`Muffin-Docker  <https://hub.docker.com/r/horneds/muffin>`_

Create a Dockerfile
^^^^^^^^^^^^^^^^^^^

* Go to your project directory
* Create a `Dockerfile` with:

.. code-block:: dockerfile

    from horneds/muffin:latest

    # Copy whole application
    COPY . /app

Create the application code
^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Create an `app.py` file with:

.. code-block:: python

   from muffin import Application


   app = Application()


   @app.route('/')
   async def index(request):
       return 'Hello World!'


Build the Docker image
^^^^^^^^^^^^^^^^^^^^^^

* Build your application image

.. code-block:: sh

   docker build -t myimage .

Start the Docker container
^^^^^^^^^^^^^^^^^^^^^^^^^^

* Run a container based on your image:

.. code-block:: sh

    docker run -d --name mycontainer -p 80:80 myimage

* Check it: http://localhost, http://127.0.0.1, etc


Deploy behind NGINX
-------------------

Running muffin apps behind nginx makes several advantages.

At first, nginx is the perfect frontend server. It may prevent many attacks
based on malformed http protocol etc.

Second, running several muffin instances behind nginx allows to utilize all CPU
cores.

Third, nginx serves static files much faster than built-in muffin static file
support.

But this way requires more complex configuration.

Nginx configuration
^^^^^^^^^^^^^^^^^^^

Here is short extraction about writing Nginx configuration file. It does not
cover all available Nginx options.

For full reference read `Nginx tutorial
<https://www.nginx.com/resources/admin-guide/>` and official `Nginx
documentation <http://nginx.org/en/docs/http/ngx_http_proxy_module.html>`.

First configure HTTP server itself:

.. code-block::

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
                # path for static files
                root /path/to/app/static;
            }

        }
    }

This config listens on port 80 for server named example.com and redirects
everything to muffin backend group.

Also it serves static files from `/path/to/app/static` path as
example.com/static.

Next we need to configure muffin upstream group:

.. code-block::

    http {
        upstream muffin {
            # fail_timeout=0 means we always retry an upstream even if it failed
            # to return a good HTTP response

            # Unix domain servers
            server unix:/tmp/example_1.sock fail_timeout=0;
            server unix:/tmp/example_2.sock fail_timeout=0;
            server unix:/tmp/example_3.sock fail_timeout=0;
            server unix:/tmp/example_4.sock fail_timeout=0;

            # Unix domain sockets are used in this example due to their high performance,
            # but TCP/IP sockets could be used instead:
            # server 127.0.0.1:8081 fail_timeout=0;
            # server 127.0.0.1:8082 fail_timeout=0;
            # server 127.0.0.1:8083 fail_timeout=0;
            # server 127.0.0.1:8084 fail_timeout=0;
        }
    }

All HTTP requests for http://example.com except ones for
http://example.com/static will be redirected to example1.sock, example2.sock,
example3.sock or example4.sock backend servers. By default, Nginx uses
round-robin algorithm for backend selection.

.. note:: Nginx is not the only existing reverse proxy server but the most
   popular one. Alternatives like HAProxy may be used as well. 
