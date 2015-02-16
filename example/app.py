import muffin


app = muffin.Application('example', CONFIG='config.debug')


@app.view('/')
def hello(request):
    return (yield from app.plugins.jade.render(
        'index.jade', user=request.session.get('user', 'anonimous')))


@app.view('/login')
def login(request):
    request.session['user'] = request.GET.get('user', 'anonimous')
    return "Logged as %s" % request.session['user']


@app.view('/db-sync')
def db_sync(request):
    from models import Test
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
    from models import Test
    results = yield from app.peewee.query(Test.select())
    return [t.data for t in results]


@app.plugins.manage.command
def hello_world():
    print('Hello world!')


if __name__ == '__main__':
    app.plugins.manage()
