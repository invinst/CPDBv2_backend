from django.db import models
from django.db.models.functions import Concat
from django.contrib.postgres.aggregates import ArrayAgg

from tqdm import tqdm
from elasticsearch.helpers import bulk

from es_index import es_client
from data.models import PoliceUnit, Area, Allegation, Salary, OfficerAllegation, Officer, AttachmentFile
from search_terms.models import SearchTermItem
from trr.models import TRR, ActionResponse
from lawsuit.models import Lawsuit
from data.utils.percentile import percentile
from search.doc_types import (
    UnitDocType, AreaDocType, CrDocType, TRRDocType,
    RankDocType, ZipCodeDocType, SearchTermItemDocType, LawsuitDocType
)
from search.indices import autocompletes_alias
from search.indexer_serializers import (
    RacePopulationSerializer, OfficerMostComplaintsSerializer, VictimSerializer,
    CoaccusedSerializer, AttachmentFileSerializer, TRROfficerSerializer
)
from search.utils import chicago_zip_codes


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
        return Area.objects.all().prefetch_related('tags')

    def _get_area_tag(self, area_type):
        return Area.SESSION_BUILDER_MAPPING.get(area_type, area_type).replace('_', ' ')

    def extract_datum(self, datum):
        tags = [tag.name for tag in datum.tags.all()]
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
    def __init__(self, indexers=None, migrate_doc_types=None):
        self.indexers = indexers or []
        self.migrate_doc_types = migrate_doc_types or []

    def _build_mapping(self):
        autocompletes_alias.write_index.close()
        for indexer in self.indexers:
            indexer.doc_type_klass.init(index=autocompletes_alias.new_index_name)
        for migrate_doc_type in self.migrate_doc_types:
            migrate_doc_type.init(index=autocompletes_alias.new_index_name)
        autocompletes_alias.write_index.open()

    def _index_data(self):
        for indexer_klass in self.indexers:
            a = indexer_klass()
            bulk(es_client, a.docs())

    def rebuild_index(self):
        with autocompletes_alias.indexing():
            self._build_mapping()
            autocompletes_alias.migrate([doc_type._doc_type.name for doc_type in self.migrate_doc_types])
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
            .values(
                'allegation_category__category',
                'allegation_category__allegation_name',
                'allegation_category_id',
                'allegation_id'
            )
        for obj in queryset:
            self.officerallegation_dict.setdefault(obj['allegation_id'], []).append(obj)

    def get_queryset(self):
        return Allegation.objects.all().annotate(
            investigator_names=ArrayAgg(
                models.Case(
                    models.When(investigatorallegation__investigator__officer_id__isnull=False, then=Concat(
                        'investigatorallegation__investigator__officer__first_name', models.Value(' '),
                        'investigatorallegation__investigator__officer__last_name'
                    )),
                    default=Concat(
                        'investigatorallegation__investigator__first_name', models.Value(' '),
                        'investigatorallegation__investigator__last_name'
                    )
                )
            )
        )

    def extract_datum(self, datum):
        officer_allegations = datum.officer_allegations.filter(
            officer__isnull=False
        ).prefetch_related('officer').order_by('-officer__allegation_count')
        attachment_files = AttachmentFile.objects.for_allegation().showing().filter(
            owner_id=datum.crid
        ).exclude(
            text_content=''
        )

        return {
            'crid': datum.crid,
            'category': getattr(datum.most_common_category, 'category', '') or 'Unknown',
            'sub_category': getattr(datum.most_common_category, 'allegation_name', '') or 'Unknown',
            'incident_date': datum.incident_date.strftime('%Y-%m-%d') if datum.incident_date else None,
            'summary': datum.summary,
            'to': f'/complaint/{datum.crid}/',
            'investigator_names': datum.investigator_names,
            'address': datum.address,
            'victims': VictimSerializer(datum.victims, many=True).data,
            'coaccused': CoaccusedSerializer(
                [officer_allegation.officer for officer_allegation in officer_allegations], many=True
            ).data,
            'attachment_files': AttachmentFileSerializer(attachment_files, many=True).data,
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
        return TRR.objects.all().select_related('officer')

    def extract_datum(self, datum):
        return {
            'id': datum.id,
            'trr_datetime': datum.trr_datetime.strftime('%Y-%m-%d') if datum.trr_datetime else None,
            'force_type': self.top_forcetype_dict.get(datum.id, None),
            'to': datum.v2_to,
            'category': datum.force_category,
            'address': ' '.join(filter(None, [datum.block, datum.street])),
            'officer': TRROfficerSerializer(datum.officer).data if datum.officer else None
        }


class LawsuitIndexer(BaseIndexer):
    doc_type_klass = LawsuitDocType

    def get_queryset(self):
        return Lawsuit.objects.all()

    def extract_datum(self, datum):
        return {
            'id': datum.id,
            'case_no': datum.case_no,
            'primary_cause': datum.primary_cause,
            'summary': datum.summary,
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


class SearchTermItemIndexer(BaseIndexer):
    doc_type_klass = SearchTermItemDocType

    def get_queryset(self):
        return SearchTermItem.objects.prefetch_related('category')

    def extract_datum(self, datum):
        return {
            'slug': datum.slug,
            'name': datum.name,
            'category_name': datum.category.name if datum.category else None,
            'description': datum.description,
            'call_to_action_type': datum.call_to_action_type,
            'link': datum.link,
        }
