Migrate Muffin from version 0.33 to version 0.40+
=================================================

Muffin 0.40+ is a completelly rewriting of the framework.

* `muffin.Application(name, *configs)` -> `muffin.Application(*configs, name=name)`
* `muffin.import_submodules(__name__)` -> `muffin.utils.import_submodules(__name__)`
* `app.register` -> `app.route`
* `app.on_exception` -> `app.on_error`
* `request.match_info` -> `request.path_params`
* `request.path_qs` -> `request.url.path_qs`
* `muffin.HTTPFound` -> `muffin.ResponseRedirect`
* `muffin.HTTPError` -> `muffin.ResponseError`
* `muffin.FileResponse` -> `muffin.ResponseFile`
* `plug = app.install(Plugin)` -> `plug = Plugin(app)`


Muffin-Rest
-----------

* `Api("/prefix")` -> `API(prefix="/prefix")`
* `RESTError` -> `APIError`
