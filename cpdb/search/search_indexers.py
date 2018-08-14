from tqdm import tqdm

from data.models import PoliceUnit, Area, Allegation, Salary
from data.utils.percentile import percentile
from search.doc_types import UnitDocType, AreaDocType, CrDocType, TRRDocType, RankDocType
from search.indices import autocompletes_alias
from search.serializers import RacePopulationSerializer
from trr.models import TRR


class BaseIndexer(object):
    doc_type_klass = None

    def __init__(self, index_name=None):
        self.index_name = index_name or autocompletes_alias.new_index_name

    def get_queryset(self):
        raise NotImplementedError

    def extract_datum(self, datum):
        raise NotImplementedError

    def extract_datum_with_id(self, datum):
        '''
        Ensure that the indexed document has the same ID as its corresponding database record.
        We can't do this to indexer classes where extract_datum() returns a list because
        multiple documents cannot share the same ID.
        '''
        extracted_data = self.extract_datum(datum)
        if not isinstance(extracted_data, list):
            extracted_data['meta'] = {'id': datum.pk}
        return extracted_data

    def save_doc(self, extracted_data, index=None):
        extracted_data['_index'] = self.index_name
        doc = self.doc_type_klass(**extracted_data)
        doc.save()

    def index_datum(self, datum):
        extracted_data = self.extract_datum_with_id(datum)
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


class UnitIndexer(BaseIndexer):
    doc_type_klass = UnitDocType

    def get_queryset(self):
        return PoliceUnit.objects.all()

    def extract_datum(self, datum):
        return {
            'name': datum.unit_name,
            'searchable_name': 'Unit {}'.format(datum.unit_name) if datum.unit_name else 'Unit',
            'description': datum.description,
            'url': datum.v1_url,
            'to': datum.v2_to,
            'active_member_count': datum.active_member_count,
            'member_count': datum.member_count,
        }


class AreaIndexer(BaseIndexer):
    doc_type_klass = AreaDocType
    _percentiles = {}

    def _compute_police_district_percentiles(self, query):
        scores = query.filter(area_type='police-districts').order_by('allegation_per_capita')
        return {
            district.id: district.percentile_allegation_per_capita
            for district in percentile(scores, key='allegation_per_capita')
        }

    def get_queryset(self):
        queryset = Area.objects.with_allegation_per_capita()
        self._percentiles = self._compute_police_district_percentiles(queryset)
        return queryset

    def _get_area_tag(self, area_type):
        return Area.SESSION_BUILDER_MAPPING.get(area_type, area_type).replace('_', ' ')

    def extract_datum(self, datum):
        tags = list(datum.tags)
        area_tag = self._get_area_tag(datum.area_type)
        if area_tag and area_tag not in tags:
            tags.append(area_tag)

        name = datum.name
        if datum.area_type == 'police-districts':
            name = datum.description if datum.description else datum.name

        officers_most_complaint = list(datum.get_officers_most_complaints())

        return {
            'name': name,
            'area_type': area_tag.replace(' ', '-'),
            'url': datum.v1_url,
            'tags': tags,
            'allegation_count': datum.allegation_count,
            'officers_most_complaint': officers_most_complaint,
            'most_common_complaint': list(datum.get_most_common_complaint()),
            'race_count': RacePopulationSerializer(
                datum.racepopulation_set.order_by('-count'),
                many=True).data,
            'median_income': datum.median_income,
            'alderman': datum.alderman,
            'allegation_percentile': self._percentiles.get(datum.id, None),
            'police_hq': datum.police_hq.name if datum.police_hq else None,
            'commander': {
                'id': datum.commander.id,
                'full_name': datum.commander.full_name,
                'allegation_count': datum.commander.allegation_count,
            } if datum.commander else None
        }


class IndexerManager(object):
    def __init__(self, indexers=None):
        self.indexers = indexers or []

    def _build_mapping(self):
        autocompletes_alias.write_index.close()
        for indexer in self.indexers:
            indexer.doc_type_klass.init(index=autocompletes_alias.new_index_name)
        autocompletes_alias.write_index.open()

    def _index_data(self):
        for indexer_klass in self.indexers:
            a = indexer_klass()
            a.index_data()

    def rebuild_index(self, migrate_doc_types=[]):
        with autocompletes_alias.indexing():
            self._build_mapping()
            autocompletes_alias.migrate(migrate_doc_types)
            self._index_data()


class CrIndexer(BaseIndexer):
    doc_type_klass = CrDocType

    def get_queryset(self):
        return Allegation.objects.all()

    def extract_datum(self, datum):
        return {
            'crid': datum.crid,
            'incident_date': datum.incident_date.strftime("%Y-%m-%d") if datum.incident_date else None,
            'to': datum.v2_to
        }


class TRRIndexer(BaseIndexer):
    doc_type_klass = TRRDocType

    def get_queryset(self):
        return TRR.objects.all()

    def extract_datum(self, datum):
        return {
            'id': datum.id,
            'trr_datetime': datum.trr_datetime.strftime("%Y-%m-%d") if datum.trr_datetime else None,
            'to': datum.v2_to
        }


class RankIndexer(BaseIndexer):
    doc_type_klass = RankDocType

    def get_queryset(self):
        return Salary.objects.rank_objects()

    def extract_datum(self, datum):
        return {
            'rank': datum.rank,
            'tags': ['rank']
        }
