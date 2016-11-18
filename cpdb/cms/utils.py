import uuid

seen_keys = {}


def generate_draft_block_key():
    key = None

    while key is None or key in seen_keys:
        key = str(uuid.uuid4())[:5]

    seen_keys[key] = True
    return key
