from cr_v3.views import CRV3ViewSet
from cr.views import CRViewSet
from data.models import Allegation
import timeit
import cPickle
from operator import itemgetter
from benchmark.utils import drop_null_empty, diff


def crids():
    return [a.crid for a in Allegation.objects.all()]


# CR PAGE ===================================
def benchmark_cr():
    try:
        print('CRV3ViewSet')
        cr_running_times = [
            (
                crid,
                timeit.timeit(lambda: CRViewSet().retrieve(None, crid), number=1),
                timeit.timeit(lambda: CRV3ViewSet().retrieve(None, crid), number=1),
            )
            for crid in crids()
        ]
        cr_running_times.sort(key=lambda x: x[1], reverse=True)
        cPickle.dump(cr_running_times, open('files/cr_running_times.p', 'wb'))
    except:
        pass


def benchmark_http_cr():
    try:
        print('api/v2/cr-v3')
        http_cr_running_times = [
            (
                crid,
                timeit.timeit(
                    "h.request('http://localhost:8000/api/v2/cr-v3/{}/')".format(crid),
                    "from httplib2 import Http; h=Http()", number=1),
                timeit.timeit(
                    "h.request('http://localhost:8000/api/v2/cr/{}/')".format(crid),
                    "from httplib2 import Http; h=Http()", number=1),
            )
            for crid in crids()
        ]
        http_cr_running_times.sort(key=lambda x: x[1], reverse=True)
        cPickle.dump(http_cr_running_times, open('files/http_cr_running_times.p', 'wb'))
    except:
        pass


# COMPARE CR DATA ===================================
def sort_cr_data(data):
    data['coaccused'] = sorted(data['coaccused'], key=itemgetter('id'))
    data['complainants'] = sorted(data['complainants'], key=itemgetter('gender', 'race', 'age'))
    data['victims'] = sorted(data['victims'], key=itemgetter('gender', 'race', 'age'))
    data['involvements'] = sorted(data['involvements'], key=itemgetter('full_name', 'involved_type'))
    data['attachments'] = sorted(data['attachments'], key=itemgetter('url'))
    return data


def compare_cr(crid):
    print "\r" + crid,
    data_1 = CRViewSet().retrieve(None, crid).data
    data_2 = CRV3ViewSet().retrieve(None, crid).data
    return drop_null_empty(sort_cr_data(data_1)) == drop_null_empty(sort_cr_data(data_2))


def cr_miss_keys(crid):
    data_1 = sort_cr_data(CRViewSet().retrieve(None, crid).data)
    drop_null_empty(data_1)

    data_2 = sort_cr_data(CRV3ViewSet().retrieve(None, crid).data)
    drop_null_empty(data_2)
    diff(data_1, data_2)


def compare_crs():
    assert(filter(lambda (_, equal): not equal, [(crid, compare_cr(crid)) for crid in crids()]) == [])


# COMPARE COMPLAIN SUMMARIES DATA ===================================
def compare_complain_summaries():
    assert(CRViewSet().complaint_summaries(None).data == CRV3ViewSet().complaint_summaries(None).data)
