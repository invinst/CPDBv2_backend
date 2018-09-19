import cPickle
import timeit
from operator import itemgetter

from mock import Mock


from officers_v3.views import OfficersV3ViewSet
from officers.views import OfficersViewSet
from data.models import Officer

from benchmark.utils import drop_null_empty, drop_keys, diff


def officer_ids():
    return [o.id for o in Officer.objects.all()]


# OFFICER PAGE ===================================
def benchmark_summary():
    try:
        print('OfficersV3ViewSet')
        officers_running_times = [
            (
                officer_id,
                timeit.timeit(lambda: OfficersViewSet().summary(None, officer_id), number=1),
                timeit.timeit(lambda: OfficersV3ViewSet().summary(None, officer_id), number=1),
            )
            for officer_id in officer_ids()
        ]
        officers_running_times.sort(key=lambda x: x[1], reverse=True)
        cPickle.dump(officers_running_times, open('files/officers_running_times.p', 'wb'))
    except:
        pass


# HTTP OFFICER PAGE ===================================
def benchmark_http_summary():
    try:
        print('api/v2/officers-v3')
        http_officers_running_times = [
            (
                officer_id,
                timeit.timeit(
                    "h.request('http://localhost:8000/api/v2/officers/{}/summary/')".format(officer_id),
                    "from httplib2 import Http; h=Http()", number=1),
                timeit.timeit(
                    "h.request('http://localhost:8000/api/v2/officers-v3/{}/summary/')".format(officer_id),
                    "from httplib2 import Http; h=Http()", number=1),
            )
            for officer_id in officer_ids()
        ]
        http_officers_running_times.sort(key=lambda x: x[1], reverse=True)
        cPickle.dump(http_officers_running_times, open('files/http_officers_running_times.p', 'wb'))
    except:
        pass


# TIMELINE PAGE ===================================
def benchmark_timeline():
    try:
        print('OfficersV3ViewSet - Timeline')
        timeline_running_times = [
            (
                officer_id,
                timeit.timeit(lambda: OfficersViewSet().new_timeline_items(None, officer_id), number=1),
                timeit.timeit(lambda: OfficersV3ViewSet().new_timeline_items(None, officer_id), number=1),
            )
            for officer_id in officer_ids()
        ]
        timeline_running_times.sort(key=lambda x: x[1], reverse=True)
        cPickle.dump(timeline_running_times, open('files/timeline_running_times.p', 'wb'))
    except:
        pass


# HTTP TIMELINE PAGE ===================================
def benchmark_http_timeline():
    try:
        print('api/v2/officers-v3/id/new-timeline-items')
        http_timeline_running_times = [
            (
                officer_id,
                timeit.timeit(
                    "h.request('http://localhost:8000/api/v2/officers/{}/new-timeline-items/')".format(officer_id),
                    "from httplib2 import Http; h=Http()", number=1),
                timeit.timeit(
                    "h.request('http://localhost:8000/api/v2/officers-v3/{}/new-timeline-items/')".format(officer_id),
                    "from httplib2 import Http; h=Http()", number=1),
            )
            for officer_id in officer_ids()
        ]
        http_timeline_running_times.sort(key=lambda x: x[1], reverse=True)
        cPickle.dump(http_timeline_running_times, open('files/http_timeline_running_times.p', 'wb'))
    except:
        pass


# cPickle ===================================
def load_cpickle_running_times():
    return cPickle.load(open('running_times.p', 'rb'))


def load_cpickle_http_running_times():
    return cPickle.load(open('http_running_times.p', 'rb'))


def load_cpickle_officers_running_times():
    return cPickle.load(open('officers_running_times.p', 'rb'))


def load_cpickle_http_officers_running_times():
    return cPickle.load(open('http_officers_running_times.p', 'rb'))


# COMPARE OFFICER SUMMARY DATA ===================================
def compare_officer_summary(officer_id):
    data_1 = OfficersViewSet().summary(None, officer_id).data
    data_2 = OfficersV3ViewSet().summary(None, officer_id).data
    return drop_keys(data_1, ['has_visual_token', 'complaint_records']) == drop_null_empty(data_2)


def diff_officer_summary(officer_id):
    data_1 = OfficersViewSet().summary(None, officer_id).data
    data_1 = drop_keys(data_1, ['has_visual_token', 'complaint_records'])

    data_2 = OfficersV3ViewSet().summary(None, officer_id).data
    drop_null_empty(data_2)

    diff(data_1, data_2)


def compare_officers_summary():
    return filter(
        lambda (_, equal): not equal,
        [(officer_id, compare_officer_summary(officer_id)) for officer_id in officer_ids()]
    )


# COMPARE OFFICER TIMELINE DATA ===================================
priority_mapping = {
    'RANK_CHANGE': 25,
    'UNIT_CHANGE': 20,
    'JOINED': 10,
    'CR': 30,
    'AWARD': 40,
    'FORCE': 50
}


def timeline_sort_key(item):
    return (
        item['date'],
        priority_mapping.get(item['kind'], 0),
        item.get('award_type', ''),
        item.get('crid', '')
    )


def sort_relationship(data):
    data = sorted(
        data,
        key=timeline_sort_key,
        reverse=True
    )
    for item in data:
        if item['kind'] == 'CR' and 'attachments' in item:
            item['attachments'] = sorted(item['attachments'], key=itemgetter('url'))
    return data


def get_officer_timelines(officer_id):
    data_1 = OfficersViewSet().new_timeline_items(None, officer_id).data
    for data in data_1:
        drop_keys(data, ['has_visual_token', 'rank', 'unit_name', 'unit_description'])
    drop_null_empty(data_1)
    data_1 = sort_relationship(data_1)

    data_2 = list(OfficersV3ViewSet().new_timeline_items(None, officer_id).data)
    for data in data_2:
        drop_keys(data, ['rank', 'unit_name', 'unit_description'])
    drop_null_empty(data_2)
    data_2 = sort_relationship(data_2)

    return data_1, data_2


def compare_officer_timeline(officer_id):
    data_1, data_2 = get_officer_timelines(officer_id)
    return data_1 == data_2


def diff_officer_timeline(officer_id):
    data_1, data_2 = get_officer_timelines(officer_id)
    diff(data_1, data_2)


def compare_officers_timeline():
    return filter(
            lambda (_, equal): not equal,
            [(officer_id, compare_officer_timeline(officer_id)) for officer_id in officer_ids()]
        )


# COMPARE OFFICER TOP OFFICERS DATA ===================================
def compare_top_officers():
    request = Mock(GET={})
    assert(
        OfficersViewSet().top_officers_by_allegation(request).data ==
        OfficersV3ViewSet().top_officers_by_allegation(request).data
    )


def diff_top_officers():
    request = Mock(GET={})
    for o1, o2 in zip(
        OfficersViewSet().top_officers_by_allegation(request).data,
        OfficersV3ViewSet().top_officers_by_allegation(request).data
    ):
        diff(o1, o2)
