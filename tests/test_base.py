def test_imports():
    import muffin

    assert hasattr(muffin, "Request")
    assert hasattr(muffin, "Response")
    assert hasattr(muffin, "ResponseError")
    assert hasattr(muffin, "ResponseFile")
    assert hasattr(muffin, "ResponseHTML")
    assert hasattr(muffin, "ResponseJSON")
    assert hasattr(muffin, "ResponseRedirect")
    assert hasattr(muffin, "ResponseStream")
    assert hasattr(muffin, "ResponseText")
    assert hasattr(muffin, "ASGINotFoundError")
    assert hasattr(muffin, "ASGIInvalidMethodError")
    assert hasattr(muffin, "TestClient")
