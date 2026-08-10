from pathlib import Path

import muffin


async def test_static_folders(tmp_path):
    # Create a static file under tmp_path
    static_dir = tmp_path / "static"
    static_dir.mkdir()
    (static_dir / "data.txt").write_text("hello static")

    app = muffin.Application(
        static_folders=[str(static_dir)],
        static_url_prefix="/assets",
    )
    assert app.cfg.STATIC_FOLDERS
    assert app.cfg.STATIC_URL_PREFIX == "/assets"

    @app.route("/")
    async def index(request):
        return "OK"

    client = muffin.TestClient(app)
    res = await client.get("/")
    assert res.status_code == 200

    res = await client.get("/assets/data.txt")
    assert res.status_code == 200
    assert await res.text() == "hello static"
