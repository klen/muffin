async def test_app_imported(app):
    assert app.cfg.name == 'muffin'
    assert app.state == 'started'
