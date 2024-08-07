import logging
from data.models import OfficerAllegation
from rest_framework import serializers
from .base import UpdateManagerBase

logger = logging.getLogger(__name__)


# TODO: add missing categories
class OfficerAllegationSerializer(serializers.ModelSerializer):
    final_finding = serializers.CharField(max_length=2, initial='ZZ')
    recc_finding = serializers.CharField(max_length=2, initial='ZZ')

    class Meta:
        model = OfficerAllegation
        fields = ['start_date', 'end_date', 'recc_finding', 'recc_outcome', 'final_finding', 'final_outcome',
                  'disciplined']


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
                    replace(a.cr_id, '-', '') as allegation_id,
                    coalesce(substring(nullif(trim(final_finding), ''), 1, 2), 'ZZ') as final_finding,
                    final_outcome as final_outcome,
                    coalesce(substring(nullif(trim(recc_finding), ''), 1, 2), 'ZZ') as recc_finding,
                    recc_outcome as recc_outcome,
                        case when disciplined = 'True' then true else false
                    end as disciplined,
                    c.id as allegation_category_id,
                    nullif(a.complaint_date, '')::date as start_date,
                    nullif(a.closed_date, '')::date as end_date,
                    o.officer_id::float::int as officer_id
                from {self.table_name} t
                join csv_final_profiles o
                    on o.uid::float::int = t.uid::float::int
                join csv_complaints_complaints a
                    on a.cr_id = t.cr_id
                left join data_allegationcategory c
                    on c.category_code = trim(t.complaint_code)
                limit {self.batch_size} offset {self.offset}"""

    def preprocess_batch(self, batch):
        batch = [{key: value for key, value in row.items() if value}
                 for row in batch]

        return batch
