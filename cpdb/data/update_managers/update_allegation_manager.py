from data.models import Allegation
from django.db import connection
from django.contrib.gis.geos import Point
import pytz
from rest_framework import serializers
from .base import UpdateManagerBase


class AllegationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Allegation
        # exclude crid and beat specifically as these result in database calls
        # assume crid is valid, manually check if beat exists with a single query
        fields = ['incident_date', 'point', 'location', 'first_start_date', 'first_end_date',
                  'add1', 'add2', 'city', 'is_officer_complaint']


class UpdateAllegationManager(UpdateManagerBase):
    def __init__(self, batch_size=100000):
        super().__init__(table_name='csv_complaints_complaints',
                         filename="data-updates/complaints/complaints-complaints.csv",
                         Model=Allegation,
                         Serializer=AllegationSerializer,
                         batch_size=batch_size)

    def query_data(self):
        return f"""
                select
                    replace(cr_id, '-', '') as crid,
                    nullif(complaint_date, '')::date as first_start_date,
                    nullif(closed_date, '')::date as first_end_date,
                    coalesce(initcap(add1), '') as add1,
                    concat_ws(' ', nullif(street_direction, ''),
                            initcap(nullif(street_name, ''))) as add2,
                    concat_ws(' ', initcap(nullif(city, '')),
                            nullif(state, ''), nullif(zip, '')) as city,
                    nullif(old_complaint_address, '') as old_complaint_address,
                    a.id as beat_id,
                    coalesce(initcap(location), '') as location,
                    nullif(latitude, 'nan') as latitude,
                    nullif(longitude, 'nan') as longitude,
                    case
                        when nullif(incident_date, '') is not null
                        then (nullif(incident_date, '') || ' ' ||
                            coalesce(nullif(incident_time, ''), '00:00:00'))::timestamp
                        else null
                        end as incident_date,
                    case when
                        complainant_type = 'CPD EMPLOYEE' then True
                        else False end as is_officer_complaint
                from {self.table_name} t
                left join (
                    select distinct on (name) *
                    from data_area
                    order by name, id
                ) a
                    on lpad(replace(t.beat, '.0', ''), 4, '0') = a.name::varchar
                    and a.area_type = 'beat'
                where
                    cr_id != ''
                limit {self.batch_size} offset {self.offset}"""

    def preprocess_batch(self, batch):
        for idx, row in enumerate(batch):
            latitude, longitude = batch[idx].pop('latitude'), batch[idx].pop('longitude')

            if latitude and longitude:
                batch[idx]['point'] = Point(float(longitude), float(latitude))
            else:
                batch[idx]['point'] = None

            tz = pytz.timezone("America/Chicago")

            batch[idx]['incident_date'] = tz.localize(row['incident_date'], is_dst=True) \
                if row['incident_date'] else None

        return batch

    def delete_existing_data(self):
        cursor = connection.cursor()

        # have to delete all referencing columns
        cursor.execute("delete from data_officerallegation")
        cursor.execute("delete from data_investigatorallegation")
        cursor.execute("delete from data_policewitness")
        cursor.execute("delete from data_victim")
        cursor.execute("delete from data_complainant")
        cursor.execute("delete from data_allegation_areas")
        cursor.execute("delete from data_allegation")
