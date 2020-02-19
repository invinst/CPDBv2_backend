import time


def timing(func):  # pragma: no cover
    def return_func(*args, **kwargs):
        return timeit(lambda: func(*args, **kwargs))
    return return_func


def timeit(func, start_message=None):  # pragma: no cover
    if start_message:
        print(start_message)
    start_time = time.time()
    res = func()
    print(f'Finished on --- {time.time() - start_time} seconds ---')
    return res


def formatted_errors(errors):
    results = []
    for key, value in errors.items():
        if isinstance(value, dict):
            error_messages = []
            for items in value.values():
                error_messages.extend(items)
            results.append((key, error_messages))
        elif isinstance(value, list):
            results.append((key, value))
    return dict(results)
