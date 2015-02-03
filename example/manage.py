from app import app


@app.manage.command('db')
def hello_world_command():
    print('Hello world!')


app.manage()
