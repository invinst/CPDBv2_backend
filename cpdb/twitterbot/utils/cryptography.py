import base64
import hashlib
import hmac


def get_hash_token(key, msg):
    hash_digest = hmac\
        .new(key, msg=msg, digestmod=hashlib.sha256)\
        .digest()

    return 'sha256=%s' % base64.b64encode(hash_digest)
