import asyncio

import pytest


async def test_async():

    async def TRUE():
        return True

    result = await TRUE()
    assert result


async def test_client(client):
    response = await client.get('/')
    assert response.status == 200

    body = await response.text()
    assert body == 'OK'
