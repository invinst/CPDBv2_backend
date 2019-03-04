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
