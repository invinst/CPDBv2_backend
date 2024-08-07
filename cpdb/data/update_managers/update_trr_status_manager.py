from trr.models import TRRStatus
import pytz
from rest_framework import serializers
from .base import UpdateManagerBase


class TRRStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = TRRStatus
        fields = ['rank', 'star', 'status', 'age', 'status_datetime']


class UpdateTRRStatusManager(UpdateManagerBase):
    def __init__(self, batch_size):
        super().__init__(table_name="csv_trr_statuses",
                         filename="data-updates/trrs/trr_statuses.csv",
                         Model=TRRStatus,
                         Serializer=TRRStatusSerializer,
                         batch_size=batch_size)

    def query_data(self):
        return f"""
                select distinct
                    replace(trr_id, '-', '')::int as trr_id,
                    initcap(rank) as rank,
                    star::float::int as star,
                    status,
                    age,
                    (status_date::date || ' ' || status_time)::Timestamp as status_datetime
                from {self.table_name} t
                join trr_trr trr on trr.id = replace(t.trr_id, '-', '')::int
                limit {self.batch_size} offset {self.offset}
                """

    def preprocess_batch(self, batch):
        tz = pytz.timezone('America/Chicago')

        for idx, row in enumerate(batch):
            if row['status_datetime'] and row['status_datetime'] != ' ':
                batch[idx]['status_datetime'] = tz.localize(row['status_datetime'])
            else:
                batch[idx]['status_datetime'] = None

        return batch
