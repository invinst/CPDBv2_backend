from data.models import Officer, OfficerBadgeNumber
from rest_framework import serializers
from .base import UpdateManagerBase


class OfficerSerializer(serializers.ModelSerializer):
    class Meta:
        race = serializers.CharField(max_length=50, initial='Unknown')

        model = Officer
        fields = ['first_name', 'last_name', 'middle_initial', 'middle_initial2', 'suffix_name',
                  'gender', 'race', 'appointed_date', 'resignation_date', 'active', 'birth_year',
                  'rank']


class UpdateOfficerManager(UpdateManagerBase):
    def __init__(self, batch_size=10000):
        super().__init__(table_name='csv_final_profiles',
                         filename="data-updates/officers/final-profiles.csv",
                         Model=Officer,
                         Serializer=OfficerSerializer,
                         batch_size=batch_size)

    def query_data(self):
        return f"""select distinct
                officer_id::float::int as id,
                initcap(trim(first_name)) as first_name,
                initcap(trim(last_name)) as last_name,
                nullif(trim(middle_initial), '') as middle_initial,
                nullif(trim(middle_initial2), '') as middle_initial2,
                nullif(trim(suffix_name), '') as suffix_name,
                substring(nullif(trim(gender), ''), 1, 1) as gender,
                initcap(nullif(trim(race), '')) as race,
                nullif(appointed_date, '')::date as appointed_date,
                nullif(resignation_date, '')::date as resignation_date,
                coalesce(trim(current_rank), '') as rank,
                nullif(birth_year, '')::float::int as birth_year,
                case when current_status = '1.0' then 'Yes'
                    when current_status = '0.0' then 'No'
                    else 'Unknown' end as active,
                nullif(current_star, '')::float::int as current_badge,
                u.id as last_unit_id
        from {self.table_name} t
        left join data_policeunit u
            on u.unit_name = lpad(t.current_unit::float::int::text, 3, '0')
            and u.active
        limit {self.batch_size} offset {self.offset}"""

    def preprocess_batch(self, batch):
        # create badge numbers for this batch of officers
        badge_numbers = []
        for idx, row in enumerate(batch):
            batch[idx] = {key: value for key, value in row.items() if value}

            if row['current_badge']:
                badge_numbers.append({'star': row['current_badge'],
                                      'officer_id': row['id'],
                                      'current': True})

        OfficerBadgeNumber.objects.bulk_create([OfficerBadgeNumber(**badge)
                                                for badge in badge_numbers])

        return batch
