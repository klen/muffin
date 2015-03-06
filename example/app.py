import muffin


from .models import Test, db, User


app = muffin.Application('example', CONFIG='example.config.debug')

# Manual installation of plugin
app.install(db)


# Add to context providers
@app.plugins.jade.ctx_provider
def add_constant():
    return {'MUFFIN': 'ROCKS'}


# Setup an user loader
@app.plugins.session.user_loader
def get_user(user_id):
    return User.select().where(User.id == user_id).get()


# Views
# =====


@app.view('/')
def hello(request):
    user = yield from app.plugins.session.load_user(request)
    return app.plugins.jade.render('index.jade', user=user)


@app.view('/login', method='POST')
def login(request):
    data = yield from request.post()
    user = User.select().where(User.email == data.get('email')).get()
    if user.check_password(data.get('password')):
        app.plugins.session.login_user(request, user.pk)

    return muffin.HTTPFound('/')


@app.view('/logout')
def logout(request):
    app.plugins.session.logout_user(request)
    return muffin.HTTPFound('/')


@app.view('/profile')
@app.plugins.session.user_pass(lambda u: u, '/')
def profile(request):
    return app.plugins.jade.render('profile.jade')


@app.view('/db-sync')
def db_sync(request):
    return [t.data for t in Test.select()]


@app.view('/json')
def json(request):
    return {'json': 'here'}


@app.view('/404')
def raise404(request):
    raise muffin.HTTPNotFound


# @app.view('/oauth')
# @app.oauth.handle
# def oauth(request):
    # return 'OAuth Here'


@app.view('/db-async')
def db_async(request):
    results = yield from app.peewee.query(Test.select())
    return [t.data for t in results]


# Commands
# ========

@app.plugins.manage.command
def hello_world():
    print('Hello world!')


if __name__ == '__main__':
    app.plugins.manage()
