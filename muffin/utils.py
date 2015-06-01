import hmac
import hashlib
import random
import asyncio


SALT_CHARS = 'bcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'


class MuffinException(Exception):

    """ Implement a Muffin's exception. """

    pass


def abcoroutine(func):
    """ Mark function/method as coroutine.

    Used with Meta classes.

    """
    func._abcoroutine = True
    return func


def to_coroutine(func):
    """ Ensure that the function is coroutine.

    If not convert to coroutine.

    """
    if not asyncio.iscoroutinefunction(func):
        func = asyncio.coroutine(func)
    return func


def create_signature(secret, value, digestmod='sha1', encoding='utf-8'):
    """ Create HMAC Signature from secret for value. """
    if isinstance(secret, str):
        secret = secret.encode(encoding)

    if isinstance(value, str):
        value = value.encode(encoding)

    if isinstance(digestmod, str):
        digestmod = getattr(hashlib, digestmod, hashlib.sha1)

    hm = hmac.new(secret, digestmod=hashlib.sha1)
    hm.update(value)
    return hm.hexdigest()


def check_signature(signature, *args, **kwargs):
    """ Check for the signature is correct. """
    return hmac.compare_digest(signature, create_signature(*args, **kwargs))


def generate_password_hash(password, digestmod='sha1', salt_length=8):
    """ Hash a password with given method and salt length. """

    salt = ''.join(random.sample(SALT_CHARS, salt_length))
    signature = create_signature(salt, password, digestmod=digestmod)
    return '$'.join((digestmod, salt, signature))


def check_password_hash(password, pwhash):
    if pwhash.count('$') < 2:
        return False
    digestmod, salt, signature = pwhash.split('$', 2)
    return check_signature(signature, salt, password, digestmod=digestmod)


class Structure(dict):

    """ `Attribute` dictionary. """

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError("Attribute '%s' doesn't exists. " % name)

    def __setattr__(self, name, value):
        self[name] = value
