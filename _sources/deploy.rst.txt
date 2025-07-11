Deployment
==========

Deploying with Docker
---------------------

Using Docker for deployment provides advantages such as security, reproducibility, and simplicity.

Muffin has an official Docker image:

`Muffin-Docker <https://hub.docker.com/r/horneds/muffin>`_

**1. Create a Dockerfile**

In your project directory, create a `Dockerfile`:

.. code-block:: dockerfile

    FROM horneds/muffin:latest

    # Copy your application code
    COPY . /app

**2. Create application code**

Create `app.py` with:

.. code-block:: python

    from muffin import Application

    app = Application()

    @app.route('/')
    async def index(request):
        return 'Hello World!'

**3. Build the Docker image**

.. code-block:: console

    $ docker build -t myimage .

**4. Run the Docker container**

.. code-block:: console

    $ docker run -d --name mycontainer -p 80:80 myimage

Visit http://localhost or http://127.0.0.1 to check.

Deploying behind NGINX
----------------------

Running Muffin apps behind NGINX provides:

- Improved security (filters malformed HTTP requests)
- Ability to run multiple Muffin instances utilizing all CPU cores
- Faster serving of static files compared to Muffin itself

**Example NGINX configuration**

Here is a minimal setup. For a full reference, read the `Nginx tutorial <https://www.nginx.com/resources/admin-guide/>`_ and `Nginx documentation <http://nginx.org/en/docs/http/ngx_http_proxy_module.html>`_.

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
                # Serve static files
                root /path/to/app/static;
            }
        }

        upstream muffin {
            # Unix domain sockets for high performance
            server unix:/tmp/example_1.sock fail_timeout=0;
            server unix:/tmp/example_2.sock fail_timeout=0;
            server unix:/tmp/example_3.sock fail_timeout=0;
            server unix:/tmp/example_4.sock fail_timeout=0;

            # Alternatively, use TCP/IP sockets:
            # server 127.0.0.1:8081 fail_timeout=0;
            # server 127.0.0.1:8082 fail_timeout=0;
            # server 127.0.0.1:8083 fail_timeout=0;
            # server 127.0.0.1:8084 fail_timeout=0;
        }
    }

This config:

- Listens on port 80 for `example.com`
- Proxies requests to Muffin backend sockets
- Serves static files directly from `/path/to/app/static`

.. note::

   While NGINX is the most popular reverse proxy, alternatives like HAProxy can also be used.
