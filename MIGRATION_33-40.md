Migrate Muffin from version 0.33 to version 0.40+
=================================================

Muffin 0.40+ is a completelly rewriting of the framework.

* `muffin.Application(name, *configs)` -> `muffin.Application(*configs, name=name)`
* `muffin.import_submodules(__name__)` -> `muffin.utils.import_submodules(__name__)`
* `plug = app.install(Plugin)` -> `plug = Plugin(app)`
* `app.ps.name` -> `app.plugins['name']`
* `app.register` -> `app.route`
* `app.on_exception` -> `app.on_error`
* `request.match_info` -> `request.path_params`
* `request.path_qs` -> `request.url.path_qs`
* `request.query_string` -> `request.url.query_string`
* `request.post` -> `request.form`
* `request.host` -> `request.url.host`
* `request.scheme` -> `request.url.scheme`
* `request.GET` -> `request.query`
* `response.set_cookie(name, value)` -> `response.cookies[name] = value`
* `muffin.HTTPFound` -> `muffin.ResponseRedirect`
* `muffin.HTTPError` (HTTPBadRequest, HTTPForbidden, HTTPMethodNotAllowed, HTTPNotFound, ...) -> `muffin.ResponseError`
* `muffin.FileResponse` -> `muffin.ResponseFile`
* `muffin.StreamResponse` -> `muffin.ResponseStream`
* `async def middleware(request, handler)` -> `async def middleware(handler, request, receive, send)`
* `app.middlewares.append` -> `@app.middleware`
* `@app.manage.command` -> `@app.manage`
* `@app.manage.command(init=True)` -> `@app.manage(lifespan=True)`
* `muffin.handler.register` -> `muffin.handler.route_method`


Muffin-Session
--------------

* `await session.load(request)` -> `session.load_from_request(request)`


Muffin-Rest
-----------

* `Api("/prefix")` -> `API(prefix="/prefix")`
* `Api.bind(app)` -> `API.setup(app)`
* `RESTError` -> `APIError`
* `api.register` -> `api.route`
* `RestHandler.get_many` -> `RestHandler.prepare_collection`
* `RestHandler.get_one` -> `RestHandler.prepare_resource`
* `RestHandler.to_simple` -> `RestHandler.dump`
* `RestHandler.name` -> `RestHandler.Meta.name`
* `RestHandler.Schema` -> `RestHandler.Meta.Schema`
* `RestHandler.Meta.per_page` -> `RestHandler.Meta.limit`
* `RestHandler.Meta.schema` -> `RestHandler.Meta.schema_fields`
* `RestHandler.Meta.schema_dump_only/schema_exclude` -> `RestHandler.Meta.schema_meta['dump_only/exclude']`
* `def RestHandler.get_schema` -> `async def RestHandler.get_schema`

Muffin-Sentry
-------------

* `muffin_sentry.Processor` -> `@plugin.processor`

Muffin-Jinja2
-------------

* `jsonify` -> `to_json`

Marshmallow
~~~~~~~~~~~

* `Field(load_from)` -> `Field(data_key)`

