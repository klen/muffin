Migrate Muffin from version 0.33 to version 0.40+
=================================================

Muffin 0.40+ is a completelly rewriting of the framework.

* `muffin.Application(name, *configs)` -> `muffin.Application(*configs, name=name)`
* `muffin.import_submodules(__name__)` -> `muffin.utils.import_submodules(__name__)`
* `app.register` -> `app.route`
* `app.on_exception` -> `app.on_error`
* `request.match_info` -> `request.path_params`
* `request.query` -> `request.url.query`
* `muffin.HTTPFound` -> `muffin.ResponseRedirect`
* `muffin.HTTPError` -> `muffin.ResponseError`
* `plug = app.install(Plugin)` -> `plug = Plugin(app)`


Muffin-Rest
-----------

* `Api("/prefix")` -> `API(prefix="/prefix")`
* `RESTError` -> `APIError`
