import logging
from data.models import OfficerAllegation, OfficerAllegationFinding, AllegationCategory
from rest_framework import serializers
from django.db import connection
from .base import UpdateManagerBase
from itertools import groupby
import operator

logger = logging.getLogger(__name__)


# TODO: add missing categories
class OfficerAllegationSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfficerAllegation
        fields = ['start_date', 'end_date', 'recc_finding', 'recc_outcome', 'final_finding', 'final_outcome',
                  'disciplined']


class OfficerAllegationFindingSerializer(serializers.ModelSerializer):
    final_finding = serializers.CharField(max_length=2, initial='ZZ')
    recc_finding = serializers.CharField(max_length=2, initial='ZZ')

    class Meta:
        model = OfficerAllegationFinding
        fields = ['recc_finding', 'final_finding']


class UpdateOfficerAllegationManager(UpdateManagerBase):
    def __init__(self, batch_size=10000):
        super().__init__(table_name='csv_complaints_accused',
                         filename="data-updates/complaints/complaints-accused.csv",
                         Model=OfficerAllegation,
                         Serializer=OfficerAllegationSerializer,
                         batch_size=batch_size)

    def query_data(self):
        return f"""
                select
                    a.crid as allegation_id,
                    coalesce(substring(nullif(trim(final_finding), ''), 1, 2), 'ZZ') as final_finding,
                    coalesce(nullif(final_outcome, ''), 'Unknown') as final_outcome,
                    coalesce(substring(nullif(trim(recc_finding), ''), 1, 2),
                        substring(nullif(final_finding, ''), 1, 2), 'ZZ') as recc_finding,
                    coalesce(nullif(recc_outcome, ''), 'Unknown') as recc_outcome,
                        case when disciplined = 'True' then true else false
                    end as disciplined,
                    c.id as allegation_category_id,
                    coalesce(t.complaint_code, a.crid) as category_code,
                    nullif(trim(t.category_tier_1), '') as category,
                    concat_ws('/', nullif(trim(t.category_tier_2), ''), nullif(trim(t.category_tier_3), ''),
                        nullif(trim(t.category_tier_4), '')) as allegation_name,
                    a.first_start_date as start_date,
                    a.first_end_date as end_date,
                    o.officer_id::float::int as officer_id
                from {self.table_name} t
                join csv_final_profiles o
                    on o.uid::float::int = t.uid::float::int
                join data_allegation a
                    on a.crid = replace(t.cr_id, '-', '')
                left join (
                    select distinct
                        id,
                        category_code
                    from
                    data_allegationcategory
                ) c
                    on (case when nullif(t.category_tier_1, '') is null then
                        trim(t.complaint_code) else 'no match' end) = c.category_code
                order by
                    crid, officer_id
                limit {self.batch_size} offset {self.offset}"""

    def process_batch(self, batch):
        # batch = [{key: value for key, value in row.items() if value}
        #          for row in batch]

        grouped_allegations = {}
        officer_allegation_keys = ['allegation_id', 'officer_id', 'final_outcome', 'recc_outcome',
                                   'disciplined', 'start_date', 'end_date']

        group_key = operator.itemgetter('allegation_id', 'officer_id')
        grouped_allegations = {key: list(allegation_group) for key, allegation_group in groupby(batch, key=group_key)}

        new_categories = self.add_or_get_categories(grouped_allegations)

        # allegation_group has all findings grouped by key, first entry is enough for officer_alleagtion
        officer_allegations = [{k: v for k, v in allegation_group[0].items()
                                if k in officer_allegation_keys} for allegation_group in grouped_allegations.values()]
        OfficerAllegation.objects.bulk_create([OfficerAllegation(**oa) for oa in officer_allegations])

        # requery for inserted id
        inserted_officer_allegation = OfficerAllegation.objects.filter(
            officer_id__in=[oa['officer_id'] for oa in officer_allegations],
            allegation_id__in=[oa['allegation_id'] for oa in officer_allegations]).all()

        officer_allegation_ids = {(oa.allegation_id, oa.officer_id): oa.id for oa in inserted_officer_allegation}

        try:
            findings = [
                {
                    "officer_allegation_id": officer_allegation_ids[(key[0], key[1])],
                    "final_finding": finding['final_finding'],
                    "recc_finding": finding['recc_finding'],
                    "allegation_category_id": (
                        new_categories[(
                            finding['category_code'],
                            finding['category'],
                            finding['allegation_name'],
                        )]
                        if finding['category']
                        else finding['allegation_category_id']
                    ),
                }
                for key, allegation_group in grouped_allegations.items()
                for finding in allegation_group
            ]
        except KeyError:
            print(list(grouped_allegations.values())[0])
            raise

        OfficerAllegationFinding.objects.bulk_create([OfficerAllegationFinding(**f) for f in findings])

    def add_or_get_categories(self, grouped_allegations):
        category_ids = {}

        new_format_rows = [row for group in grouped_allegations.values() for row in group if row.get('category')]

        if new_format_rows:
            for category_code, category, allegation_name in set(
                (row['category_code'], row['category'], row['allegation_name']) for row in new_format_rows
            ):
                obj, _ = AllegationCategory.objects.get_or_create(
                    category_code=category_code,
                    category=category,
                    allegation_name=allegation_name,
                    defaults={
                        "on_duty": True,
                        "citizen_dept": 'dept',
                    }
                )

                category_ids[(category_code, category, allegation_name)] = obj.id

        return category_ids

    def delete_existing_data(self):
        cursor = connection.cursor()

        cursor.execute("delete from data_officerallegation")

    def update_holding_table(self):
        updated_table = super().update_holding_table()

        cursor = connection.cursor()
        cursor.execute("create index if not exists idx_csv_final_profiles_uid_int "
                       "on csv_final_profiles((uid::float::int));")
        cursor.execute("create index if not exists idx_csv_complaints_accused_uid_int "
                       "on csv_complaints_accused((uid::float::int));")

        return updated_table
