import muffin


app = muffin.Application('example', CONFIG='config.debug')


@app.view('/')
def hello(request):
    return (yield from app.jade.render('index.jade'))


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


@app.view('/db-async')
def db_async(request):
    from models import Test
    results = yield from app.peewee.query(Test.select())
    return [t.data for t in results]


@app.manage.command
def hello_world():
    print('Hello world!')


if __name__ == '__main__':
    app.manage()
