import asyncio

import pytest

import muffin


@pytest.mark.async
def test_local(loop):
    l1 = muffin.local(loop)
    l2 = muffin.local(loop)
    assert l1 is l2

    log, fut1, fut2 = [], asyncio.Future(), asyncio.Future()

    @asyncio.coroutine
    def coro1():
        l1.value = 'task1'
        yield from fut1
        log.append(l1.value)
        fut2.set_result(True)

    @asyncio.coroutine
    def coro2():
        l1.value = 'task2'
        fut1.set_result(True)
        yield from fut2
        log.append(l1.value)

    yield from asyncio.wait([coro1(), coro2()])
    assert log == ['task1', 'task2']


def test_slocal():
    from muffin.utils import local, slocal
    loop = asyncio.get_event_loop()
    local = local(loop=loop)
    with pytest.raises(RuntimeError):
        local.test = 1

    sl = slocal(loop=loop)
    sl.test = 1
    assert sl.test == 1

    sl2 = slocal(loop=loop)
    assert sl is sl2


def test_struct():
    from muffin.utils import Struct, LStruct

    data = Struct({'test': 42})
    assert data.test == 42

    data.test = 21
    assert data.test == 21

    settings = LStruct({'option': 'value'})
    assert settings.option == 'value'

    settings.option2 = 'value2'
    settings.lock()
    settings.lock()

    with pytest.raises(RuntimeError):
        settings.test = 42


def test_generate_password_hash_default():
    from muffin.utils import generate_password_hash, check_password_hash

    password = '#secret$'
    password_hash = generate_password_hash(password, digestmod='sha1', salt_length=8)

    assert password_hash.startswith('sha1')
    assert len(password_hash.split('$')[1]) == 8
    assert len(password_hash.split('$')[2]) == 40
    assert check_password_hash(password, password_hash)


def test_generate_password_hash_sha256():
    from muffin.utils import generate_password_hash, check_password_hash

    password = '#secret$'
    password_hash = generate_password_hash(password, digestmod='sha256', salt_length=20)

    assert password_hash.startswith('sha256')
    assert len(password_hash.split('$')[1]) == 20
    assert len(password_hash.split('$')[2]) == 64
    assert check_password_hash(password, password_hash)

#  pylama:ignore=E0237
