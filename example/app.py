import muffin


app = muffin.Application()

from models import Test


@app.view('/')
def hello(request):
    return (yield from app.jade.render('index.jade'))


@app.view('/db-sync')
def db_sync(request):
    return [t.data for t in Test.select()]


@app.view('/db-async')
def db_async(request):
    results = yield from app.peewee.query(Test.select())
    return [t.data for t in results]


@app.view('/json')
def json(request):
    return {'json': 'here'}


@app.view('/404')
def raise404(request):
    raise muffin.HTTPNotFound
