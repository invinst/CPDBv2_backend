import uuid
from time import time


per_run_uuid = str(uuid.uuid4())


def timing_validate(message):
    def real_decorator(func):
        def wrapper(*args, **kwargs):
            print(message)
            start_time = time()
            return_value = func(*args, **kwargs)
            print(f'Done in {time() - start_time}')
            return return_value
        return wrapper
    return real_decorator
