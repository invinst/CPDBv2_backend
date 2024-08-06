from data.models import Award
from rest_framework import serializers
from .base import UpdateManagerBase


class AwardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Award
        # TODO: figure out if we can add rank and last promotion date
        fields = ['award_type', 'current_status', 'start_date', 'end_date',
                  'request_date', 'ceremony_date', 'requester_full_name']


class UpdateAwardManager(UpdateManagerBase):
    def __init__(self, batch_size=100000):
        super().__init__(table_name='csv_awards',
                         filename="data-updates/awards/awards.csv",
                         Model=Award,
                         Serializer=AwardSerializer,
                         batch_size=batch_size)

    def query_data(self):
        return f"""
                select
                    officer_id::float::int,
                    initcap(award_type) as award_type,
                    initcap(current_award_status) as current_status,
                    award_start_date::date as start_date,
                    award_end_date::date as end_date,
                    award_request_date::date as request_date,
                    ceremony_date::date,
                    requester_full_name
                    -- award_id as tracking_no
                from {self.table_name} t
                join csv_final_profiles o
                    on o.uid::float::int = t.uid::float::int
                join data_officer d
                    on d.id = o.officer_id::float::int
                limit {self.batch_size} offset {self.offset}"""
