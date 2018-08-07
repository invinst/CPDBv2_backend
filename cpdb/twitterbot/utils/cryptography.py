import base64
import hashlib
import hmac


def get_hash_token(key, msg):
    hash_digest = hmac\
        .new(
            bytes(key).encode('utf-8'),
            msg=bytes(msg).encode('utf-8'),
            digestmod=hashlib.sha256
        )\
        .digest()

    return 'sha256=%s' % base64.b64encode(hash_digest)
