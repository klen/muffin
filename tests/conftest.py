import pytest

import muffin


@pytest.fixture(
    params=[
        pytest.param(("asyncio", {"use_uvloop": False}), id="asyncio"),
        pytest.param(("asyncio", {"use_uvloop": True}), id="asyncio+uvloop"),
        "trio",
        "curio",
    ],
    scope="session",
)
def aiolib(request):
    return request.param
