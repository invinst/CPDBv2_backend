import base64
import hashlib
import hmac


def get_hash_token(key, msg):
    try:
        msg = msg.encode('utf-8')
    except AttributeError:
        pass
    hash_digest = hmac.new(
        key.encode('utf-8'),
        msg=msg,
        digestmod=hashlib.sha256
    ).digest()

    return f'sha256={base64.b64encode(hash_digest).decode()}'
