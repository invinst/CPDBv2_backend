from django.db import connection
from django.db.models import OuterRef, Subquery, Count
from tqdm import tqdm

from data.models import Officer, OfficerAllegation
from data import officer_percentile
from utils.bulk_db import build_bulk_update_sql


def cache_data():
    build_percentile_cached_data()
    build_count_cached_data()


def build_count_cached_data():
    Officer.objects.update(
        allegation_count=Subquery(
            OfficerAllegation.objects.filter(
                officer_id=OuterRef('id')
            ).values('officer_id').annotate(
                allegation_count=Count('allegation_id', distinct=True)
            ).values('allegation_count')[:1]
        ),
        sustained_count=Subquery(
            OfficerAllegation.objects.filter(
                officer_id=OuterRef('id'),
                final_finding='SU'
            ).values('officer_id').annotate(
                sustained_count=Count('allegation_id', distinct=True)
            ).values('sustained_count')[:1]
        )
    )


def build_percentile_cached_data():
    percentile_values = officer_percentile.latest_year_percentile()

    if percentile_values:
        Officer.objects.all().update(
            complaint_percentile=None,
            civilian_allegation_percentile=None,
            internal_allegation_percentile=None,
            trr_percentile=None,
            honorable_mention_percentile=None,
        )

        data = [{
            'id': officer.officer_id,
            'complaint_percentile': getattr(officer, 'percentile_allegation', None),
            'civilian_allegation_percentile': getattr(officer, 'percentile_allegation_civilian', None),
            'internal_allegation_percentile': getattr(officer, 'percentile_allegation_internal', None),
            'trr_percentile': getattr(officer, 'percentile_trr', None),
            'honorable_mention_percentile': getattr(officer, 'percentile_honorable_mention', None),
        } for officer in percentile_values]

        update_fields = [
            'complaint_percentile',
            'civilian_allegation_percentile',
            'internal_allegation_percentile',
            'trr_percentile',
            'honorable_mention_percentile'
        ]

        cursor = connection.cursor()

        batch_size = 100
        for i in tqdm(range(0, len(data), batch_size)):
            batch_data = data[i:i + batch_size]
            update_command = build_bulk_update_sql(Officer._meta.db_table, 'id', update_fields, batch_data)
            cursor.execute(update_command)
