from trr.models import SubjectWeapon
from rest_framework import serializers
from .base import UpdateManagerBase


class SubjectWeaponSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectWeapon
        fields = ['weapon_type', 'firearm_caliber', 'weapon_description']


class UpdateSubjectWeaponManager(UpdateManagerBase):
    def __init__(self, batch_size):
        super().__init__(table_name='csv_trr_subject_weapons',
                         filename='data-updates/trrs/trr_subject_weapons.csv',
                         Model=SubjectWeapon,
                         Serializer=SubjectWeaponSerializer,
                         batch_size=batch_size)

    def query_data(self):
        return f"""
                select distinct
                    trr.id as trr_id,
                    weapon_type,
                    firearm_caliber,
                    nullif(trim(weapon_description), '') as weapon_description
                from {self.table_name} t
                join trr_trr trr
                    on trr.id = replace(t.trr_id, '-', '')::int
                limit {self.batch_size} offset {self.offset}"""
