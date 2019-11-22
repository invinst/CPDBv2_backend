from data.models import Officer, Allegation
from trr.models import TRR


class BaseModelQuery(object):
    query_field = None

    def __init__(self, ids):
        self.ids = ids

    def queryset(self):
        raise NotImplementedError

    def query(self):
        return self.queryset().filter(**{f'{self.query_field}__in': self.ids})


class OfficerQuery(BaseModelQuery):
    query_field = 'id'

    def queryset(self):
        return Officer.objects


class CrQuery(BaseModelQuery):
    query_field = 'crid'

    def queryset(self):
        return Allegation.objects


class TrrQuery(BaseModelQuery):
    query_field = 'id'

    def queryset(self):
        return TRR.objects
