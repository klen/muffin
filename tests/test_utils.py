from muffin import utils


def test_signature():
    assert utils.create_signature('secret', 'message')


def test_password_hash():
    pwhash = utils.generate_password_hash('pass')
    assert pwhash

    assert not utils.check_password_hash('wrong', pwhash)
    assert utils.check_password_hash('pass', pwhash)
