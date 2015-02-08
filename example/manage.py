from app import app


@app.manage.command
def hello_world():
    print('Hello world!')


app.manage()
