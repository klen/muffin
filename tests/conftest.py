import pytest
import uvloop

import muffin


@pytest.fixture(
    params=[
        pytest.param(("asyncio"), id="asyncio"),
        pytest.param(("asyncio", {"loop_factory": uvloop.new_event_loop}), id="asyncio+uvloop"),
        "trio",
        "curio",
    ],
    scope="session",
)
def aiolib(request):
    return request.param
