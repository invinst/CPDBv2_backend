from trr.models import WeaponDischarge
from rest_framework import serializers
from .base import UpdateManagerBase


class WeaponDischargeSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeaponDischarge
        fields = ['weapon_type', 'weapon_type_description', 'firearm_make', 'firearm_model', 'firearm_barrel_length',
                  'firearm_caliber', 'total_number_of_shots', 'firearm_reloaded', 'handgun_worn_type',
                  'handgun_drawn_type', 'method_used_to_reload', 'sight_used', 'protective_cover_used',
                  'discharge_distance', 'object_struck_of_discharge', 'discharge_position']


class UpdateWeaponDischargeManager(UpdateManagerBase):
    def __init__(self, batch_size):
        super().__init__(table_name="csv_weapon_discharges",
                         filename="data-updates/trrs/trr_weapon_discharges.csv",
                         Model=WeaponDischarge,
                         Serializer=WeaponDischargeSerializer,
                         batch_size=batch_size*10)

    def query_data(self):
        return f"""
                select distinct
                    main.id as trr_id,
                    t.weapon_type,
                    t.weapon_type_description,
                    t.firearm_make,
                    t.firearm_model,
                    t.firearm_barrel_length,
                    t.firearm_caliber,
                    t.total_number_of_shots::float::int as total_number_of_shots,
                    lower(t.firearm_reloaded) in ('yes', 'y', '1.0', '1') as firearm_reloaded,
                    t.handgun_worn_type,
                    t.handgun_drawn_type,
                    t.method_used_to_reload,
                    lower(t.sight_used) in ('yes', 'y', '1.0', '1') as sight_used,
                    substring(t.protective_cover_used, 1, 32) as protective_cover_used,
                    t.discharge_distance,
                    case
                        when t.object_struck_of_discharge = 'NONE' then null
                        when t.object_struck_of_discharge = 'OTHER PERSON' then 'PERSON'
                        when t.object_struck_of_discharge = 'ANY OTHER COMBINATION' then 'UNKNOWN'
                        when t.object_struck_of_discharge = 'SUBJECT' then 'UNKNOWN'
                        else t.object_struck_of_discharge end as object_struck_of_discharge,
                    t.discharge_position
                from {self.table_name} t
                join trr_trr main
                    on main.id = replace(t.trr_id, '-', '')::int
                limit {self.batch_size} offset {self.offset}
                """
