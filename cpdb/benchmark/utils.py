def stats(running_times):
    max_time = max(running_times)
    min_time = min(running_times)
    avg_time = sum(running_times) / len(running_times)
    return max_time, min_time, avg_time


def drop_null_empty(object):
    if isinstance(object, dict):
        for key in object.keys():
            drop_null_empty(object[key])
            value = object[key]
            if value is None or value == [] or value == {}:
                object.pop(key, None)

    elif isinstance(object, list):
        for item in object:
            drop_null_empty(item)
    return object


def drop_keys(data, keys):
    for key in keys:
        data.pop(key, None)
    return data


def diff_dict(dict_1, dict_2):
    keys1 = set(dict_1.keys())
    keys2 = set(dict_2.keys())

    keys_a = keys1 - keys2
    keys_b = keys2 - keys1
    if keys_a:
        print('dict_1 - dict_2', keys_a)
    if keys_b:
        print('dict_2 - dict_1', keys_b)

    for key in list(keys1.union(keys2)):
        value_1 = dict_1.get(key, None)
        value_2 = dict_2.get(key, None)
        if value_1 != value_2:
            print(key, value_1, value_2)


def diff(data_1, data_2):
    if isinstance(data_1, list):
        if isinstance(data_2, list) and len(data_1) == len(data_2):
            for idx, (dict_1, dict_2) in enumerate(zip(data_1, data_2)):
                print 'compare item[{}]'.format(idx)
                diff(dict_1, dict_2)
        else:
            print('array-1', data_1)
            print('#===============')
            print('array-2', data_2)
            print('#===============')
    elif isinstance(data_1, dict):
        diff_dict(data_1, data_2)
