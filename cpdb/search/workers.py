from elasticsearch_dsl.query import Q

from .doc_types import (
    UnitDocType, ReportDocType, AreaDocType, CrDocType,
    TRRDocType, RankDocType, ZipCodeDocType, SearchTermItemDocType
)
from officers.doc_types import OfficerInfoDocType


class Worker(object):
    doc_type_klass = None
    fields = []
    sort_order = []
    name = ''

    @property
    def _searcher(self):
        return self.doc_type_klass().search()

    def query(self, term, **kwargs):
        return self._searcher \
            .query('multi_match', query=term, operator='and', fields=self.fields) \
            .sort(*self.sort_order)

    def search(self, term, size=10, begin=0, **kwargs):
        return self.query(term, **kwargs)[begin:size].execute()

    def get_sample(self):
        query = self._searcher.query(
            'function_score',
            random_score={}
        ).query(
            'exists',
            field='tags'
        )
        return query[:1].execute()


class DateWorker(Worker):
    date_fields = []

    def query(self, term, **kwargs):
        dates = kwargs.get('dates', [])
        queries = [Q('terms',  **{date_field: dates}) for date_field in self.date_fields]
        return self._searcher.query(Q('bool', should=queries))


class ReportWorker(Worker):
    doc_type_klass = ReportDocType
    fields = ['excerpt', 'title', 'publication', 'author', 'tags']


class OfficerWorker(Worker):
    doc_type_klass = OfficerInfoDocType

    def query(self, term, **kwargs):
        _query = self._searcher.query(
            'function_score',
            query={
                'multi_match': {
                    'query': term,
                    'fields': ['badge', 'historic_badges', 'full_name', 'tags', '_id']
                }
            },
            functions=[
                {
                    'filter': {
                        'match': {
                            'tags': term
                        }
                    },
                    'script_score': {
                        'script': '_score + 60000'
                    }
                },
                {
                    'filter': {
                        'match': {
                            'full_name': {
                                'query': term,
                                'operator': 'and'
                            }
                        }
                    },
                    'script_score': {
                        'script': '_score + 500'
                    }
                },
                {
                    'filter': {
                        'match': {
                            'full_name': term
                        }
                    },
                    'script_score': {
                        'script': '_score + doc[\'allegation_count\'].value * 3'
                    }
                }
            ]
        )
        return _query


class UnitWorker(Worker):
    doc_type_klass = UnitDocType
    fields = ['name', 'long_name', 'description', 'tags']


class AreaWorker(Worker):
    doc_type_klass = AreaDocType
    area_type = None
    fields = ['name', 'tags']
    sort_order = ['-allegation_count', 'name.keyword', '_score']

    def query(self, term, **kwargs):
        filter = Q('term', area_type=self.area_type) if self.area_type else Q('match_all')
        q = Q('bool',
              must=[Q('multi_match', query=term, operator='and', fields=self.fields)],
              filter=filter)
        return self._searcher.query(q).sort(*self.sort_order)


class NeighborhoodsWorker(AreaWorker):
    area_type = 'neighborhood'


class CommunityWorker(AreaWorker):
    area_type = 'community'


class PoliceDistrictWorker(AreaWorker):
    area_type = 'police-district'


class SchoolGroundWorker(AreaWorker):
    area_type = 'school-ground'


class WardWorker(AreaWorker):
    area_type = 'ward'


class BeatWorker(AreaWorker):
    area_type = 'beat'


class UnitOfficerWorker(Worker):
    doc_type_klass = OfficerInfoDocType
    fields = ['long_unit_name', 'description']
    sort_order = ['-allegation_count']

    def query(self, term, **kwargs):
        return self._searcher.query('nested', path='historic_units', query=Q(
            'multi_match',
            operator='and',
            fields=[f'historic_units.{field}' for field in self.fields],
            query=term
        )).sort(*self.sort_order)


class RankWorker(Worker):
    doc_type_klass = RankDocType
    fields = ['rank', 'tags']
    sort_order = ['-active_officers_count']


class DateCRWorker(DateWorker):
    doc_type_klass = CrDocType
    date_fields = ['incident_date']


class CRWorker(Worker):
    doc_type_klass = CrDocType

    def query(self, term, **kwargs):
        return self._searcher\
            .query('multi_match', query=term, operator='and', fields=['crid', 'summary'])\
            .highlight('summary')


class DateTRRWorker(DateWorker):
    doc_type_klass = TRRDocType
    date_fields = ['trr_datetime']


class DateOfficerWorker(DateWorker):
    doc_type_klass = OfficerInfoDocType
    date_fields = ['cr_incident_dates', 'trr_datetimes']


class TRRWorker(Worker):
    doc_type_klass = TRRDocType
    fields = ['_id']


class ZipCodeWorker(Worker):
    doc_type_klass = ZipCodeDocType
    fields = ['zip_code', 'tags']


class SearchTermItemWorker(Worker):
    doc_type_klass = SearchTermItemDocType
    fields = ['name', 'category_name']
    sort_order = ['category_name']


class InvestigatorCRWorker(Worker):
    doc_type_klass = CrDocType
    fields = ['investigator_names']
