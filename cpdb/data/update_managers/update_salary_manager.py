from data.models import Salary
from rest_framework import serializers
from .base import UpdateManagerBase


class SalarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Salary
        fields = ['pay_grade', 'rank', 'salary', 'employee_status',
                  'org_hire_date', 'spp_date', 'start_date',
                  'age_at_hire', 'year']


class UpdateSalaryManager(UpdateManagerBase):
    def __init__(self, batch_size=100000):
        super().__init__(table_name='csv_salaries',
                         filename="data-updates/salaries/salaries.csv",
                         Model=Salary,
                         Serializer=SalarySerializer,
                         batch_size=batch_size)

    def query_data(self):
        return f"""
                select
                    o.officer_id::float::int as officer_id,
                    t.pay_grade,
                    initcap(t.rank) as rank,
                    t.salary::float::int,
                    t.employee_status,
                    t.org_hire_date::date,
                    t.spp_date::date,
                    t.start_date::date,
                    t.age_at_hire::float::int,
                    t.year::float::int
            from {self.table_name} t
            join csv_final_profiles o
                on t.UID::float::int = o.uid::float::int
            join data_officer d
                on d.id = o.officer_id::float::int
            where
                pay_grade is not null
            limit {self.batch_size} offset {self.offset}"""
