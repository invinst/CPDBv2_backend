from trr.models import ActionResponse
from rest_framework import serializers
from .base import UpdateManagerBase


class ActionResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActionResponse
        fields = ['person', 'resistance_type', 'action', 'other_description', 'member_action',
                  'force_type', 'action_sub_category', 'action_category', 'resistance_level']


class UpdateActionResponseManager(UpdateManagerBase):
    def __init__(self, batch_size):
        super().__init__(table_name="csv_trr_actions_responses",
                         filename="data-updates/trrs/trr_actions_responses.csv",
                         Model=ActionResponse,
                         Serializer=ActionResponseSerializer,
                         batch_size=batch_size*10)

    def query_data(self):
        return f"""
                select distinct
                    trr.id as trr_id,
                    initcap(person) as person,
                    initcap(nullif(resistance_type, '')) as resistance_type,
                    initcap(action) as action,
                    initcap(nullif(trim(other_description), '')) as other_description,
                    initcap(member_action) as member_action,
                    initcap(nullif(force_type, '')) as force_type,
                    substring(action_sub_category, 1, 3) as action_sub_category,
                    substring(action_category, 1, 1) as action_category,
                    resistance_level
                from {self.table_name} t
                join trr_trr trr on trr.id = replace(t.trr_id, '-', '')::int
                limit {self.batch_size} offset {self.offset}
                """
