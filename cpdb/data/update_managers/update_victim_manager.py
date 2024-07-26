from data.models import Victim
from rest_framework import serializers
from .base import UpdateManagerBase


class VictimSerializer(serializers.ModelSerializer):
    race = serializers.CharField(max_length=50, initial='Unknown')

    class Meta:
        model = Victim
        fields = ['gender', 'race', 'age', 'birth_year']


class UpdateVictimManager(UpdateManagerBase):
    def __init__(self, batch_size=10000):
        super().__init__(table_name="csv_victims",
                         filename="data-updates/complaints/victims.csv",
                         Model=Victim,
                         Serializer=VictimSerializer,
                         batch_size=batch_size)

    def query_data(self):
        return f"""select
                a.crid as allegation_id,
                coalesce(substring(nullif(gender, ''), 1, 1), '') as gender,
                coalesce(initcap(nullif(race, '')), 'Unknown') as race,
                age::float::int as age,
                nullif(birth_year, '')::float::int as birth_year
            from {self.table_name} t
            join data_allegation a
                on a.crid = replace(t.cr_id, '-', '')
            limit {self.batch_size} offset {self.offset}"""
