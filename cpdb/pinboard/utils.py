import uuid


def generate_hex_from_uuid(length):
    if length % 2 != 0:
        raise ValueError(f'length must be an even number, got {length}')
    return uuid.uuid4().bytes[0:(length // 2)].hex().lstrip("0x").zfill(length)


def int_to_zero_padded_hex(x, length):
    if x < 0 or x >= 16**length:
        raise ValueError(f'x must be within [0, 16**{length}], got {x}')
    return hex(x).lstrip("0x").zfill(length)


def zero_padded_hex_to_int(x):
    return int(x, 16)
