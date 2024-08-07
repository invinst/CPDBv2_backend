from data.models import Complainant
from rest_framework import serializers
from .base import UpdateManagerBase


class ComplainantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complainant
        fields = ['gender', 'race', 'age', 'birth_year']


class UpdateComplainantManager(UpdateManagerBase):
    def __init__(self, batch_size=10000):
        super().__init__(table_name='csv_complainants',
                         filename="data-updates/complaints/complainants.csv",
                         Model=Complainant,
                         Serializer=ComplainantSerializer,
                         batch_size=batch_size)

    def query_data(self):
        return f"""
                select
                    replace(cr_id, '-', '') as allegation_id,
                    substring(gender, 1, 1) as gender,
                    nullif(initcap(trim(race)), '') as race,
                    age::float::int as age,
                    nullif(nullif(nullif(nullif(nullif(birth_year, '19MS'),
                    '19MX'), '19FS'),'19FX'), '')::float::int as birth_year
                from {self.table_name} t
                join data_allegation a
                    on a.crid = replace(t.cr_id, '-', '')
                limit {self.batch_size} offset {self.offset}"""

    def preprocess_batch(self, batch):
        batch = [{key: value for key, value in row.items() if value}
                 for row in batch]

        return batch
