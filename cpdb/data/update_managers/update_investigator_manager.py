from django.db import transaction
from django.db import connection
from data.models import Allegation, Investigator, InvestigatorAllegation, PoliceUnit
from rest_framework import serializers
from .base import UpdateManagerBase


class InvestigatorSerializer(serializers.ModelSerializer):
    class Meta:
        race = serializers.CharField(max_length=50, initial='Unknown')

        model = Investigator
        fields = ['first_name', 'last_name', 'middle_initial', 'suffix_name', 'appointed_date']


class InvestigatorAllegationSerializer(serializers.ModelSerializer):

    class Meta:
        model = InvestigatorAllegation
        fields = ['current_star', 'current_rank', 'investigator_type', 'current_unit_id']


class UpdateInvestigatorManager(UpdateManagerBase):
    def __init__(self, batch_size):
        super().__init__(table_name='csv_investigators',
                         filename='data-updates/complaints/investigators.csv',
                         Model=Investigator,
                         Serializer=InvestigatorSerializer,
                         batch_size=batch_size)

    def query_data(self):
        return ""

    # TODO: change this to use the new query_data method/base class
    @transaction.atomic
    def update_data(self, update_holding_table):
        table_name = self.table_name

        self.update_holding_table()

        cursor = connection.cursor()
        cursor.execute(f"select count(*) from {table_name}")
        row_count = cursor.fetchone()[0]

        print("Deleting existing investigator data")
        Investigator.objects.all().delete()

        print("Querying police unit data to link investigators")
        police_units = PoliceUnit.objects.all()
        police_unit_dict = {police_unit.unit_name: police_unit for police_unit in police_units}

        print("Querying allegations to link to investigators")
        allegations = Allegation.objects.all()
        allegation_dict = {allegation.crid: allegation for allegation in allegations}

        print(f"Total rows to insert: {row_count}")
        batch_size = 100000
        offset = 0

        self.created_investigators = {}  # store by id to not insert dupes

        print("Deduplicating investigators on all columns")
        cursor.execute(f"""
                       drop table if exists temp_investigators;

                       create table temp_investigators as (
                            select distinct
                                a.crid,
                                rank() over (
                                    order by
                                        first_name,
                                        last_name,
                                        middle_initial,
                                        suffix_name,
                                        appointed_date
                                    desc) as id,
                                initcap(first_name) as first_name,
                                initcap(last_name) as last_name,
                                nullif(middle_initial, '') as middle_initial,
                                nullif(suffix_name, '') as suffix_name,
                                appointed_date::date as appointed_date,
                                current_star,
                                current_rank,
                                investigator_type,
                                investigating_agency,
                                lpad(current_unit::float::int::text, 3, '0') as unit_name
                            from {table_name} t
                            join data_allegation a
                                on a.crid = replace(t.cr_id, '-', '')
                            where
                                first_name is not null
                                and last_name is not null
                        );""")

        while offset < row_count:
            cursor.execute(f"select * from temp_investigators limit {batch_size} offset {offset}")
            self.columns = [col[0] for col in cursor.description]

            print(f"Processing batch {offset} to {offset + batch_size}")
            self.process_batch(batch=cursor.fetchall(),
                               police_unit_dict=police_unit_dict,
                               allegation_dict=allegation_dict)

            offset += batch_size

    def process_batch(self, batch, police_unit_dict, allegation_dict):
        investigators = []
        investigator_allegations = []

        investigator_fields = set([field.name for field in Investigator._meta.get_fields()])
        investigator_allegation_fields = set([field.name for field in InvestigatorAllegation._meta.get_fields()])

        # first create investigators, then create investigator_allegations using created investigators
        for data in batch:
            row = dict(zip(self.columns, data))

            if row['id'] not in self.created_investigators:
                investigator_dict = {key: value for key, value in row.items()
                                     if key in investigator_fields}

                self.created_investigators[row['id']] = Investigator(**investigator_dict)
                investigators.append(investigator_dict)

        for data in batch:
            row = dict(zip(self.columns, data))

            row['allegation'] = allegation_dict.get(row['crid'])
            row['investigator'] = self.created_investigators.get(row['id'])
            row['current_unit'] = police_unit_dict.get(row['unit_name'])

            investigator_allegations.append({key: value for key, value in row.items()
                                             if (key in investigator_allegation_fields) and
                                             (key != 'id')})

        investigator_serializer = InvestigatorSerializer(data=investigator_allegations, many=True)

        if investigator_serializer.is_valid(raise_exception=True):
            Investigator.objects.bulk_create([Investigator(**investigator)
                                              for investigator in investigators])

        investigator_allegation_serializer = InvestigatorAllegationSerializer(data=investigator_allegations, many=True)

        if investigator_allegation_serializer.is_valid(raise_exception=True):
            InvestigatorAllegation.objects.bulk_create([InvestigatorAllegation(**investigator_allegation)
                                                        for investigator_allegation in investigator_allegations])
