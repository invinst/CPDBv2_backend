from tqdm import tqdm

from cms.models import FAQPage, ReportPage
from data.models import Officer, PoliceUnit, Area, OfficerAllegation, OfficerHistory
from search.doc_types import (
        FAQDocType, ReportDocType, OfficerDocType,
        UnitDocType, NeighborhoodsDocType, CommunityDocType,
        CoAccusedOfficerDocType, UnitOfficerDocType)
from .indices import autocompletes


def extract_text_from_value(value):
    return '\n'.join([block['text'] for block in value['blocks']])


class BaseIndexer(object):
    doc_type_klass = None

    def get_queryset(self):
        raise NotImplementedError

    def extract_datum(self, datum):
        raise NotImplementedError

    def save_doc(self, extracted_data):
        doc = self.doc_type_klass(**extracted_data)
        doc.save()

    def index_datum(self, datum):
        extracted_data = self.extract_datum(datum)
        if isinstance(extracted_data, list):
            [self.save_doc(entry) for entry in extracted_data]
        else:
            self.save_doc(extracted_data)

    def index_data(self):
        for datum in tqdm(
                self.get_queryset(),
                desc='Indexing {doc_type_name}'.format(
                    doc_type_name=self.doc_type_klass._doc_type.name)):
                self.index_datum(datum)


class FAQIndexer(BaseIndexer):
    doc_type_klass = FAQDocType

    def get_queryset(self):
        return FAQPage.objects.all()

    def extract_datum(self, datum):
        fields = datum.fields

        return {
            'question': extract_text_from_value(fields['question_value']),
            'answer': extract_text_from_value(fields['answer_value'])
        }


class ReportIndexer(BaseIndexer):
    doc_type_klass = ReportDocType

    def get_queryset(self):
        return ReportPage.objects.all()

    def extract_datum(self, datum):
        fields = datum.fields

        return {
            'publication': fields['publication_value'],
            'author': fields['author_value'],
            'excerpt': extract_text_from_value(fields['excerpt_value']),
            'title': extract_text_from_value(fields['title_value'])
        }


class CoAccusedOfficerIndexer(BaseIndexer):
    doc_type_klass = CoAccusedOfficerDocType

    def get_queryset(self):
        return Officer.objects.all()

    def extract_datum(self, datum):
        pks = datum.officerallegation_set.values_list('allegation__pk', flat=True)
        involved_pks = OfficerAllegation.objects.filter(allegation__pk__in=pks).exclude(officer=datum)\
            .values_list('officer__pk', flat=True)
        officers = Officer.objects.filter(pk__in=involved_pks)

        return [{
            'full_name': officer.full_name,
            'badge': officer.current_badge,
            'url': officer.v1_url,
            'co_accused_officer': {
                'full_name': datum.full_name,
                'badge': datum.current_badge
            }
        } for officer in officers]


class OfficerIndexer(BaseIndexer):
    doc_type_klass = OfficerDocType

    def get_queryset(self):
        return Officer.objects.all()

    def extract_datum(self, datum):
        return {
            'full_name': datum.full_name,
            'badge': datum.current_badge,
            'url': datum.v1_url
        }


class UnitIndexer(BaseIndexer):
    doc_type_klass = UnitDocType

    def get_queryset(self):
        return PoliceUnit.objects.all()

    def extract_datum(self, datum):
        return {
            'name': datum.unit_name,
            'url': datum.v1_url
        }


class UnitOfficerIndexer(BaseIndexer):
    doc_type_klass = UnitOfficerDocType

    def get_queryset(self):
        return OfficerHistory.objects.all()

    def extract_datum(self, datum):
        return {
            'full_name': datum.officer.full_name,
            'badge': datum.officer.current_badge,
            'url': datum.officer.v1_url,
            'allegation_count': datum.officer.officerallegation_set.count(),
            'unit_name': datum.unit.unit_name
        }


class AreaTypeIndexer(BaseIndexer):
    doc_type_klass = None
    area_type = None

    def get_queryset(self):
        return Area.objects.filter(area_type=self.area_type)

    def extract_datum(self, datum):
        return {
            'name': datum.name,
            'url': datum.v1_url
        }


class NeighborhoodsIndexer(AreaTypeIndexer):
    doc_type_klass = NeighborhoodsDocType
    area_type = 'neighborhoods'


class CommunityIndexer(AreaTypeIndexer):
    doc_type_klass = CommunityDocType
    area_type = 'community'


class IndexerManager(object):
    def __init__(self, indexers=None):
        self.indexers = indexers or []

    def _build_mapping(self):
        autocompletes.delete(ignore=404)
        autocompletes.create()

    def _index_data(self):
        for indexer_klass in self.indexers:
            indexer_klass().index_data()

    def rebuild_index(self):
        self._build_mapping()
        self._index_data()
