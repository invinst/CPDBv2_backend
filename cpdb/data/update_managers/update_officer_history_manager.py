from data.models import OfficerHistory
from rest_framework import serializers
from .base import UpdateManagerBase


class OfficerHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = OfficerHistory
        fields = ['effective_date', 'end_date']


class UpdateOfficerHistoryManager(UpdateManagerBase):
    def __init__(self, batch_size):
        super().__init__(table_name="csv_unit_history",
                         filename="data-updates/unit_history/unit_history.csv",
                         Model=OfficerHistory,
                         Serializer=OfficerHistorySerializer,
                         batch_size=batch_size*10)

    def query_data(self):
        return f"""
                select
                    oo.id as officer_id,
                    t.unit_start_date::date as effective_date,
                    t.unit_end_date::date as end_date,
                    pu.id as unit_id
                from {self.table_name} t
                join csv_final_profiles o
                    on t.uid::float::int = o.uid::float::int
                join data_officer oo
                    on oo.id = o.officer_id::float::int
                left join data_policeunit pu
                    on lpad(t.unit::float::int::text, 3, '0') = pu.unit_name
                limit {self.batch_size} offset {self.offset}"""
