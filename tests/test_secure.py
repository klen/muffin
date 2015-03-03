from muffin import secure


def test_signature():
    assert secure.create_signature('secret', 'message')


def test_password_hash():
    pwhash = secure.generate_password_hash('pass')
    assert pwhash

    assert not secure.check_password_hash('wrong', pwhash)
    assert secure.check_password_hash('pass', pwhash)
