def test_user(mixer):
    user = mixer.blend('example.models.User')
    user.set_password('pass')
    assert not user.check_password('wrong')
    assert user.check_password('pass')
