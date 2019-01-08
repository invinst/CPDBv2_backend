from tqdm import tqdm
from elasticsearch.helpers import bulk

from es_index import es_client
from data.models import PoliceUnit, Area, Allegation, Salary, OfficerAllegation, Officer
from data.utils.percentile import percentile
from search.doc_types import UnitDocType, AreaDocType, CrDocType, TRRDocType, RankDocType, ZipCodeDocType
from search.indices import autocompletes_alias
from search.serializers import RacePopulationSerializer, OfficerMostComplaintsSerializer
from search.utils import chicago_zip_codes
from trr.models import TRR, ActionResponse


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
        if not isinstance(extracted_data, list) and hasattr(datum, 'pk'):
            extracted_data['meta'] = {'id': datum.pk}
        return extracted_data

    def _prepare_doc(self, extracted_data, index=None):
        extracted_data['_index'] = self.index_name
        return self.doc_type_klass(**extracted_data).to_dict(include_meta=True)

    def docs(self):
        for datum in tqdm(
                self.get_queryset(),
                desc=f'Indexing {self.doc_type_klass._doc_type.name}'):
            extracted_data = self.extract_datum_with_id(datum)
            if isinstance(extracted_data, list):
                for entry in extracted_data:
                    yield self._prepare_doc(entry)
            else:
                yield self._prepare_doc(extracted_data)


class UnitIndexer(BaseIndexer):
    doc_type_klass = UnitDocType

    def get_queryset(self):
        return PoliceUnit.objects.all()

    def extract_datum(self, datum):
        return {
            'name': datum.unit_name,
            'long_name': f'Unit {datum.unit_name}' if datum.unit_name else 'Unit',
            'description': datum.description,
            'url': datum.v1_url,
            'to': datum.v2_to,
            'active_member_count': datum.active_member_count,
            'member_count': datum.member_count,
        }


class AreaIndexer(BaseIndexer):
    doc_type_klass = AreaDocType
    _percentiles = {}

    def _compute_police_district_percentiles(self):
        scores = Area.police_districts_with_allegation_per_capita()
        return {
            district.id: district.percentile_allegation_per_capita
            for district in percentile(scores, key='allegation_per_capita')
        }

    def get_queryset(self):
        self._percentiles = self._compute_police_district_percentiles()
        return Area.objects.all()

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

        officers_most_complaint = OfficerMostComplaintsSerializer(
            list(datum.get_officers_most_complaints()),
            many=True
        ).data

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
            bulk(es_client, a.docs())

    def rebuild_index(self, migrate_doc_types=[]):
        with autocompletes_alias.indexing():
            self._build_mapping()
            autocompletes_alias.migrate(migrate_doc_types)
            self._index_data()


class CrIndexer(BaseIndexer):
    doc_type_klass = CrDocType

    def __init__(self, *args, **kwargs):
        super(CrIndexer, self).__init__(*args, **kwargs)
        self.populate_officerallegation_dict()

    def populate_officerallegation_dict(self):
        self.officerallegation_dict = dict()
        queryset = OfficerAllegation.objects.filter(allegation_category__isnull=False)\
            .select_related('allegation_category')\
            .values('allegation_category__category', 'allegation_category_id', 'allegation_id')
        for obj in queryset:
            self.officerallegation_dict.setdefault(obj['allegation_id'], []).append(obj)

    def get_most_common_category(self, id):
        category_count = dict()
        for officerallegation_obj in self.officerallegation_dict.get(id, []):
            category_obj = category_count.setdefault(officerallegation_obj['allegation_category_id'], {
                'category': officerallegation_obj['allegation_category__category'],
                'count': 0
            })
            category_obj['count'] += 1

        try:
            result = max(category_count.values(), key=lambda obj: obj['count'])
            return result['category']
        except ValueError:
            return None

    def get_queryset(self):
        return Allegation.objects.all()

    def extract_datum(self, datum):
        return {
            'crid': datum.crid,
            'category': self.get_most_common_category(datum.crid),
            'incident_date': datum.incident_date.strftime('%Y-%m-%d') if datum.incident_date else None,
            'to': f'/complaint/{datum.crid}/'
        }


class TRRIndexer(BaseIndexer):
    doc_type_klass = TRRDocType

    def __init__(self, *args, **kwargs):
        super(TRRIndexer, self).__init__(*args, **kwargs)
        self._populate_top_forcetype_dict()

    def _populate_top_forcetype_dict(self):
        self.top_forcetype_dict = dict()
        queryset = ActionResponse.objects\
            .filter(person='Member Action')\
            .order_by('-action_sub_category', 'force_type')

        for obj in queryset:
            if obj.trr_id not in self.top_forcetype_dict:
                self.top_forcetype_dict[obj.trr_id] = obj.force_type

    def get_queryset(self):
        return TRR.objects.all()

    def extract_datum(self, datum):
        return {
            'id': datum.id,
            'trr_datetime': datum.trr_datetime.strftime('%Y-%m-%d') if datum.trr_datetime else None,
            'force_type': self.top_forcetype_dict.get(datum.id, None),
            'to': datum.v2_to
        }


class RankIndexer(BaseIndexer):
    doc_type_klass = RankDocType

    def get_queryset(self):
        return Salary.objects.ranks

    def extract_datum(self, datum):
        return {
            'rank': datum,
            'tags': ['rank'],
            'active_officers_count': Officer.get_active_officers(datum).count(),
            'officers_most_complaints': OfficerMostComplaintsSerializer(
                Officer.get_officers_most_complaints(datum),
                many=True
            ).data
        }


class ZipCodeIndexer(BaseIndexer):
    doc_type_klass = ZipCodeDocType

    def get_queryset(self):
        return chicago_zip_codes()

    def extract_datum(self, datum):
        return {
            'id': datum.pk,
            'zip_code': datum.zip_code,
            'url': datum.url,
            'tags': ['zip code'],
        }
