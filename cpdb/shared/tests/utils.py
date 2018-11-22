from mock import Mock
from robber import expect


def create_object(dict_object):
    m = Mock(spec=dict_object.keys(), **dict_object)
    if 'name' in dict_object:
        m.configure_mock(name=dict_object['name'])
    return m


def validate_object(obj, data):
    for key, value in data.iteritems():
        expect(getattr(obj, key, None)).to.eq(value)


def diff_dict(dict_1, dict_2):
    keys1 = set(dict_1.keys())
    keys2 = set(dict_2.keys())

    keys_a = keys1 - keys2
    keys_b = keys2 - keys1
    if keys_a:
        print('=== dict_1 - dict_2', keys_a)
    if keys_b:
        print('=== dict_2 - dict_1', keys_b)

    for key in list(keys1.union(keys2)):
        value_1 = dict_1.get(key, None)
        value_2 = dict_2.get(key, None)
        if value_1 != value_2:
            print(key, value_1, value_2)


def diff(data_1, data_2):
    if isinstance(data_1, list) and isinstance(data_2, list):
        len_1 = len(data_1)
        len_2 = len(data_2)
        if len_1 != len_2:
            print('=== Different length', len_1, len_2)
            if len_1 > len_2:
                print(data_1[len_2:])
            else:
                print(data_2[len_1:])
        for idx, (dict_1, dict_2) in enumerate(zip(data_1, data_2)):
            print('compare item[{}]'.format(idx))
            diff(dict_1, dict_2)
    elif isinstance(data_1, dict) and isinstance(data_2, dict):
        diff_dict(data_1, data_2)
    else:
        print('=== Data type miss-match', type(data_1), type(data_2))
