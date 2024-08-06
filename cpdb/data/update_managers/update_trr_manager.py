from trr.models import TRR
from django.contrib.gis.geos import Point
import pytz
from rest_framework import serializers
from .base import UpdateManagerBase


class TRRSerializer(serializers.ModelSerializer):
    class Meta:
        model = TRR
        fields = ['id', 'officer_id', 'beat', 'block', 'direction', 'street',
                  'location', 'trr_datetime', 'indoor_or_outdoor',
                  'lighting_condition', 'weather_condition', 'notify_OEMC',
                  'notify_district_sergeant', 'notify_OP_command', 'notify_DET_division',
                  'number_of_weapons_discharged', 'party_fired_first', 'location_recode',
                  'taser', 'total_number_of_shots', 'firearm_used', 'number_of_officers_using_firearm',
                  'officer_on_duty', 'officer_in_uniform', 'officer_injured', 'officer_rank',
                  'subject_id', 'subject_armed', 'subject_injured', 'subject_alleged_injury',
                  'subject_age', 'subject_birth_year', 'subject_gender', 'subject_race']


class UpdateTRRManager(UpdateManagerBase):
    def __init__(self, batch_size):
        super().__init__(table_name="csv_trr_main",
                         filename="data-updates/trrs/trr_main.csv",
                         Model=TRR,
                         Serializer=TRRSerializer,
                         batch_size=batch_size)

    def query_data(self):
        return f"""
                select distinct
                    replace(trr_id, '-', '')::int as id,
                    o.officer_id::float::int,
                    nullif(beat, '')::float::int as beat,
                    nullif(block, '') as block,
                    d.direction,
                    initcap(nullif(street, '')) as street,
                    initcap(nullif(location, '')) as location,
                    nullif(trr_datetime, '')::timestamp as trr_datetime,
                    initcap(nullif(indoor_or_outdoor, '')) as indoor_or_outdoor,
                    nullif(lighting_condition, '') as lighting_condition,
                    nullif(weather_condition, '') as weather_condition,
                    case
                        when lower(notify_oemc) in ('yes', 'y', 'true', '1') then true
                        when lower(notify_oemc) in ('no', 'n', 'false', '0') then false
                        else null
                    end as "notify_OEMC",
                    case
                        when lower(notify_district_sergeant) in ('yes', 'y', 'true', '1') then true
                        when lower(notify_district_sergeant) in ('no', 'n', 'false', '0') then false
                        else null
                    end as notify_district_sergeant,
                    case
                        when lower(notify_op_command) in ('yes', 'y', 'true', '1') then true
                        when lower(notify_op_command) in ('no', 'n', 'false', '0') then false
                        else null
                    end as "notify_OP_command",
                    case
                        when lower(notify_det_division) in ('yes', 'y', 'true', '1') then true
                        when lower(notify_det_division) in ('no', 'n', 'false', '0') then false
                        else null
                    end as "notify_DET_division",
                    nullif(number_of_weapons_discharged, '')::float::int
                        as number_of_weapons_discharged,
                    nullif(party_fired_first, '') as party_fired_first,
                    initcap(nullif(location_recode, '')) as location_recode,
                    case
                        when lower(taser) in ('yes', 'y', 'true', '1') then true
                        when lower(taser) in ('no', 'n', 'false', '0') then false
                        else null
                    end as taser,
                    nullif(total_number_of_shots, '')::float::int as total_number_of_shots,
                    case
                        when lower(firearm_used) in ('yes', 'y', 'true', '1') then true
                        when lower(firearm_used) in ('no', 'n', 'false', '0') then false
                        else null
                    end as firearm_used,
                    nullif(number_of_officers_using_firearm, '')::float::int
                        as number_of_officers_using_firearm,
                    nullif(longitude, '')::float as longitude,
                    nullif(latitude, '')::float as latitude,
                    nullif(officer_assigned_beat, '') as officer_assigned_beat,
                    nullif(officer_on_duty, '')::boolean as officer_on_duty,
                    nullif(officer_in_uniform, '')::boolean as officer_in_uniform,
                    nullif(officer_injured, '')::boolean as officer_injured,
                    initcap(nullif(officer_rank, '')) as officer_rank,
                    u.id as officer_unit_id,
                    du.id as officer_unit_detail_id,
                    nullif(subject_id, '')::float::int as subject_id,
                    case
                        when lower(subject_armed) in ('yes', 'y', 'true', '1') then true
                        when lower(subject_armed) in ('no', 'n', 'false', '0') then false
                        else null
                    end as subject_armed,
                    case
                        when lower(subject_injured) in ('yes', 'y', 'true', '1') then true
                        when lower(subject_injured) in ('no', 'n', 'false', '0') then false
                        else null
                    end as subject_injured,
                    case
                        when lower(subject_alleged_injury) in ('yes', 'y', 'true', '1') then true
                        when lower(subject_alleged_injury) in ('no', 'n', 'false', '0') then false
                        else null
                    end as subject_alleged_injury,
                    nullif(subject_age, '')::float::int as subject_age,
                    nullif(subject_birth_year, '')::float::int as subject_birth_year,
                    substring(nullif(subject_gender, ''), 1,1) as subject_gender,
                    initcap(nullif(subject_race, '')) as subject_race
                from {self.table_name} m
                left join (
                    select
                        'S' as dir, 'South' as direction
                    union all
                    select
                        'N' as dir, 'North' as direction
                    union all
                    select
                        'W' as dir, 'West' as direction
                    union all
                    select
                        'E' as dir, 'East' as direction
                ) d
                    on m.direction = d.dir
                left join csv_officer o
                    on o.uid = case
                        when m.uid != '' then m.uid::float::int
                        else null end
                left join data_policeunit u
                    on u.unit_name = lpad(officer_unit_id::float::int::text, 3, '0')
                    and u.active
                left join data_policeunit du
                    on du.unit_name = case when officer_unit_detail_id = 'REDACTED' then null
                                        else lpad(officer_unit_detail_id::float::int::text, 3, '0') end
                    and du.active
                limit {self.batch_size} offset {self.offset}"""

    def preprocess_batch(self, batch):
        eastern = pytz.utc

        for idx, row in enumerate(batch):
            batch[idx]['trr_datetime'] = eastern.localize(row['trr_datetime'],
                                                          is_dst=True) if row['trr_datetime'] else None

            longitude, latitude = batch[idx].pop('longitude'), batch[idx].pop('latitude')

            if longitude and latitude:
                batch[idx]['point'] = Point(float(longitude), float(latitude))
            else:
                batch[idx]['point'] = None

        return batch
