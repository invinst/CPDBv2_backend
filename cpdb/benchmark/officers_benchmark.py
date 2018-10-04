import cPickle
import timeit
import csv
from operator import itemgetter

from mock import Mock


from old_officers.views import OldOfficersViewSet
from officers.views import OfficersViewSet
from data.models import Officer

from benchmark.utils import drop_null_empty, drop_keys, diff


def officer_ids():
    return [o.id for o in Officer.objects.all()]


# OFFICER PAGE ===================================
def benchmark_summary():
    print('OfficersViewSet')
    officers_running_times = [
        (
            officer_id,
            timeit.timeit(lambda: OldOfficersViewSet().summary(None, officer_id), number=1),
            timeit.timeit(lambda: OfficersViewSet().summary(None, officer_id), number=1),
        )
        for officer_id in officer_ids()
    ]
    officers_running_times.sort(key=lambda x: x[1], reverse=True)
    cPickle.dump(officers_running_times, open('files/officers_running_times.p', 'wb'))


# HTTP OFFICER PAGE ===================================
def benchmark_http_summary(server_host):
    print('api/v2/officers/id/summary')
    http_officers_running_times = [
        (
            officer_id,
            timeit.timeit(
                "h.request('{}/api/v2/old/officers/{}/summary/')".format(server_host, officer_id),
                "from httplib2 import Http; h=Http()", number=1),
            timeit.timeit(
                "h.request('{}/api/v2/officers/{}/summary/')".format(server_host, officer_id),
                "from httplib2 import Http; h=Http()", number=1),
        )
        for officer_id in officer_ids()
    ]
    http_officers_running_times.sort(key=lambda x: x[1], reverse=True)
    cPickle.dump(http_officers_running_times, open('files/http_officers_running_times.p', 'wb'))


# TIMELINE PAGE ===================================
def benchmark_timeline():
    print('OfficersViewSet - Timeline')
    timeline_running_times = [
        (
            officer_id,
            timeit.timeit(lambda: OldOfficersViewSet().new_timeline_items(None, officer_id), number=1),
            timeit.timeit(lambda: OfficersViewSet().new_timeline_items(None, officer_id), number=1),
        )
        for officer_id in officer_ids()
    ]
    timeline_running_times.sort(key=lambda x: x[1], reverse=True)
    cPickle.dump(timeline_running_times, open('files/timeline_running_times.p', 'wb'))


# HTTP TIMELINE PAGE ===================================
def benchmark_http_timeline(server_host):
    print('api/v2/officers/id/new-timeline-items')
    http_timeline_running_times = [
        (
            officer_id,
            timeit.timeit(
                "h.request('{}/api/v2/old/officers/{}/new-timeline-items/')".format(server_host, officer_id),
                "from httplib2 import Http; h=Http()", number=1),
            timeit.timeit(
                "h.request('{}/api/v2/officers/{}/new-timeline-items/')".format(server_host, officer_id),
                "from httplib2 import Http; h=Http()", number=1),
        )
        for officer_id in officer_ids()
    ]
    http_timeline_running_times.sort(key=lambda x: x[1], reverse=True)
    cPickle.dump(http_timeline_running_times, open('files/http_timeline_running_times.p', 'wb'))


# cPickle ===================================
def load_cpickle_running_times():
    return cPickle.load(open('files/officers_running_times.p', 'rb'))


def load_cpickle_http_running_times():
    return cPickle.load(open('files/http_officers_running_times.p', 'rb'))


def load_cpickle_officers_running_times():
    return cPickle.load(open('files/timeline_running_times.p', 'rb'))


def load_cpickle_http_officers_running_times():
    return cPickle.load(open('files/http_timeline_running_times.p', 'rb'))


def to_csv(name):
    with open('files/{}.csv'.format(name), 'wb') as csvfile:
        spamwriter = csv.writer(csvfile)
        spamwriter.writerow(['ID', 'ES Time', 'Postgres Time'])
        for page in cPickle.load(open('files/{}.p'.format(name), 'rb')):
            spamwriter.writerow(page)


# COMPARE OFFICER SUMMARY DATA ===================================
def compare_officer_summary(officer_id):
    data_1 = OldOfficersViewSet().summary(None, officer_id).data
    data_2 = OfficersViewSet().summary(None, officer_id).data
    return drop_keys(data_1, ['has_visual_token', 'complaint_records']) == drop_null_empty(data_2)


def diff_officer_summary(officer_id):
    data_1 = OldOfficersViewSet().summary(None, officer_id).data
    data_1 = drop_keys(data_1, ['has_visual_token', 'complaint_records'])

    data_2 = OfficersViewSet().summary(None, officer_id).data
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
        item.get('crid', ''),
        item.get('trr_id', ''),
        item.get('rank', ''),
        item.get('unit_name', ''),
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


def remove_wrong_rank_change(timeline_items):
    if timeline_items:
        reversed_timeline_items = list(reversed(timeline_items))
        wrong_rank_change_index = None
        joined_item = None
        for index, item in enumerate(reversed_timeline_items):
            if item['kind'] == 'JOINED':
                joined_item = item
                continue
            if joined_item and item['kind'] == 'RANK_CHANGE':
                first_rank_change_item = item
                if joined_item.get('rank', None) == first_rank_change_item.get('rank', None):
                    wrong_rank_change_index = index
                break
        if wrong_rank_change_index is not None:
            del reversed_timeline_items[wrong_rank_change_index]
            return list(reversed(reversed_timeline_items))
    return timeline_items


def remove_unit_in_rank_change(timeline_items):
    for item in timeline_items:
        if item['kind'] == 'RANK_CHANGE':
            item['unit_name'] = ''
            item['unit_description'] = ''
    return timeline_items


def remove_rank_in_unit_change(timeline_items):
    for item in timeline_items:
        if item['kind'] == 'UNIT_CHANGE':
            item['rank'] = ''
    return timeline_items


def remove_rank_unit_if_need(timeline_items):
    return remove_unit_in_rank_change(remove_rank_in_unit_change(timeline_items))


def get_officer_timelines(officer_id):
    data_1 = OldOfficersViewSet().new_timeline_items(None, officer_id).data
    for data in data_1:
        drop_keys(data, ['has_visual_token'])
    drop_null_empty(data_1)
    data_1 = remove_rank_unit_if_need(remove_wrong_rank_change(sort_relationship(data_1)))

    data_2 = list(OfficersViewSet().new_timeline_items(None, officer_id).data)
    drop_null_empty(data_2)
    data_2 = remove_rank_unit_if_need(sort_relationship(data_2))

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
        OldOfficersViewSet().top_officers_by_allegation(request).data ==
        OfficersViewSet().top_officers_by_allegation(request).data
    )


def diff_top_officers():
    request = Mock(GET={})
    for o1, o2 in zip(
        OldOfficersViewSet().top_officers_by_allegation(request).data,
        OfficersViewSet().top_officers_by_allegation(request).data
    ):
        diff(o1, o2)
