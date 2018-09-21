from django.db import connection
from django.db.models import OuterRef, Subquery, Count
from django.db.models.functions import Lower
from tqdm import tqdm

from data.constants import (
    MAJOR_AWARDS, MIN_VISUAL_TOKEN_YEAR, MAX_VISUAL_TOKEN_YEAR,
    PERCENTILE_TRR_GROUP, PERCENTILE_ALLEGATION_INTERNAL_CIVILIAN_GROUP, PERCENTILE_ALLEGATION_GROUP
)

from data.models import (
    Officer, OfficerAllegation, Award,
    OfficerBadgeNumber, OfficerHistory, Salary,
    OfficerYearlyPercentile
)
from trr.models import TRR
from data import officer_percentile
from utils.bulk_db import build_bulk_update_sql


def cache_data():
    build_cached_yearly_percentiles()
    build_cached_percentiles()
    build_cached_columns()


def _allegation_count_subquery(**kwargs):
    return Subquery(
        OfficerAllegation.objects.filter(
            officer_id=OuterRef('id'),
            **kwargs
        ).values('officer_id').annotate(
            count=Count('allegation_id', distinct=True)
        ).values('count')[:1]
    )


def _award_count_subquery(**kwargs):
    return Subquery(
        Award.objects.filter(
            officer_id=OuterRef('id'),
            **kwargs
        ).values('officer_id').annotate(
            count=Count('id')
        ).values('count')[:1]
    )


def build_cached_columns():
    Officer.objects.update(
        allegation_count=_allegation_count_subquery(),
        sustained_count=_allegation_count_subquery(final_finding='SU'),
        unsustained_count=_allegation_count_subquery(final_finding='NS'),
        discipline_count=_allegation_count_subquery(disciplined=True),
        honorable_mention_count=_award_count_subquery(award_type__contains='Honorable Mention'),
        civilian_compliment_count=_award_count_subquery(award_type='Complimentary Letter'),
        major_award_count=Subquery(
            Award.objects.annotate(
                lower_award_type=Lower('award_type')
            ).filter(
                officer_id=OuterRef('id'),
                lower_award_type__in=MAJOR_AWARDS
            ).values('officer_id').annotate(
                count=Count('id')
            ).values('count')[:1]
        ),
        trr_count=Subquery(
            TRR.objects.filter(
                officer_id=OuterRef('id'),
            ).values('officer_id').annotate(
                count=Count('id')
            ).values('count')[:1]
        ),
        current_badge=Subquery(
            OfficerBadgeNumber.objects.filter(
                officer_id=OuterRef('id'),
                current=True
            ).values('star')[:1]
        ),
        last_unit=Subquery(
            OfficerHistory.objects.filter(
                officer_id=OuterRef('id'),
            ).order_by('-end_date').values('unit_id')[:1]
        ),
        current_salary=Subquery(
            Salary.objects.filter(
                officer_id=OuterRef('id'),
            ).order_by('-year').values('salary')[:1]
        )
    )

    count_columns = [
        'allegation_count',
        'sustained_count',
        'unsustained_count',
        'discipline_count',
        'honorable_mention_count',
        'civilian_compliment_count',
        'major_award_count',
        'trr_count',
    ]

    for column in count_columns:
        Officer.objects.filter(**{'{}__isnull'.format(column): True}).update(**{column: 0})


def build_cached_yearly_percentiles():
    percentile_groups = [
        PERCENTILE_ALLEGATION_GROUP,
        PERCENTILE_ALLEGATION_INTERNAL_CIVILIAN_GROUP,
        PERCENTILE_TRR_GROUP
    ]

    def _not_retired(officer):
        return not officer.resignation_date or officer.year <= officer.resignation_date.year

    results = []
    for yr in tqdm(range(MIN_VISUAL_TOKEN_YEAR, MAX_VISUAL_TOKEN_YEAR + 1), desc='Prepare percentile data'):
        officers = officer_percentile.top_percentile(yr, percentile_groups=percentile_groups)
        results.extend(filter(_not_retired, officers))

    cursor = connection.cursor()
    cursor.execute("TRUNCATE TABLE {}".format(OfficerYearlyPercentile._meta.db_table))

    OfficerYearlyPercentile.objects.bulk_create(
        OfficerYearlyPercentile(
            officer=result,
            year=result.year,
            percentile_trr=getattr(result, 'percentile_trr', None),
            percentile_allegation=getattr(result, 'percentile_allegation', None),
            percentile_allegation_civilian=getattr(result, 'percentile_allegation_civilian', None),
            percentile_allegation_internal=getattr(result, 'percentile_allegation_internal', None),
        ) for result in results
    )


def build_cached_percentiles():
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
