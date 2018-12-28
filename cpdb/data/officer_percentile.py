from datetime import datetime

from django.contrib.gis.db import models
from django.db.models import F, Q, IntegerField, Func
from django.utils.timezone import now, timedelta

from tqdm import tqdm
import pytz

from data.models import Officer, Award
from data.constants import (
    ALLEGATION_MAX_DATETIME, ALLEGATION_MIN_DATETIME,
    INTERNAL_CIVILIAN_ALLEGATION_MAX_DATETIME, INTERNAL_CIVILIAN_ALLEGATION_MIN_DATETIME,
    TRR_MAX_DATETIME, TRR_MIN_DATETIME,
    PERCENTILE_GROUPS, PERCENTILE_ALLEGATION_GROUP, PERCENTILE_ALLEGATION_INTERNAL_CIVILIAN_GROUP, PERCENTILE_TRR_GROUP,
    PERCENTILE_HONORABLE_MENTION_GROUP
)
from data.utils.percentile import percentile, merge_metric
from data.utils.round import Round


def latest_year_percentile(percentile_groups=PERCENTILE_GROUPS):
    dates = [date for percentile_group in percentile_groups
             for date in PERCENTILE_MAP[percentile_group]['range']]
    min_year = min(dates).year
    max_year = max(dates).year

    resignation_dates = Officer.objects.filter(
        resignation_date__isnull=False
    ).values_list('resignation_date', flat=True).distinct()

    resignation_years = set([resignation_date.year for resignation_date in resignation_dates])
    calculating_years = [resignation_year for resignation_year in resignation_years
                         if min_year <= resignation_year <= max_year]
    percentile_officers = []

    for year in tqdm(calculating_years, 'calculate yearly percentiles'):
        yearly_percentile_officers = top_percentile(year, percentile_groups)
        percentile_officers += [officer for officer in yearly_percentile_officers
                                if officer.resignation_date and officer.resignation_date.year == year]

    current_year = now().year
    current_year_percentile_officers = top_percentile(current_year, percentile_groups)
    percentile_officers += [officer for officer in current_year_percentile_officers
                            if not officer.resignation_date or officer.resignation_date.year == current_year]

    return percentile_officers


def top_percentile(year=now().year, percentile_groups=PERCENTILE_GROUPS):
    """ This is calculate top percentile of top_percentile_value
    :return: list of (officer_id, percentile_value)
    # """
    if any(t not in PERCENTILE_GROUPS for t in percentile_groups):
        raise ValueError("percentile_group is invalid")
    computed_data = []
    for percentile_group in percentile_groups:
        percentile_types = PERCENTILE_MAP[percentile_group]['percentile_funcs'].keys()
        new_data = _compute_metric(year, percentile_group)
        computed_data = merge_metric(computed_data, new_data, percentile_types)
        for percentile_type in percentile_types:
            computed_data = percentile(computed_data, percentile_type=percentile_type, decimal_places=4)

    return computed_data


def _allegation_count_query(min_datetime, max_datetime):
    return models.Count(
        models.Case(
            models.When(
                Q(
                    officerallegation__allegation__incident_date__gte=min_datetime,
                    officerallegation__allegation__incident_date__lte=max_datetime
                ),
                then='officerallegation'
            ), output_field=models.CharField(),
        ), distinct=True
    )


def _allegation_civilian_count_query(min_datetime, max_datetime):
    return models.Count(
        models.Case(
            models.When(
                Q(
                    officerallegation__allegation__is_officer_complaint=False,
                    officerallegation__allegation__incident_date__gte=min_datetime,
                    officerallegation__allegation__incident_date__lte=max_datetime
                ),
                then='officerallegation'
            ), output_field=models.CharField(),
        ), distinct=True
    )


def _allegation_internal_count_query(min_datetime, max_datetime):
    return models.Count(
        models.Case(
            models.When(
                Q(
                    officerallegation__allegation__is_officer_complaint=True,
                    officerallegation__allegation__incident_date__gte=min_datetime,
                    officerallegation__allegation__incident_date__lte=max_datetime
                ),
                then='officerallegation'
            )
        ), distinct=True
    )


def _trr_count_query(min_datetime, max_datetime):
    return models.Count(
        models.Case(
            models.When(
                Q(trr__trr_datetime__date__gte=min_datetime, trr__trr_datetime__date__lte=max_datetime),
                then='trr'
            ), output_field=models.CharField(),
        ), distinct=True
    )


def _honorable_mention_count_query(_, max_datetime):
    return models.Count(
        models.Case(
            models.When(
                award__start_date__lte=max_datetime.date(),
                award__award_type='Honorable Mention',
                then='award'
            ), output_field=models.CharField(),
        ), distinct=True
    )


def _to_datetime(date):
    return datetime(year=date.year, month=date.month, day=date.day, tzinfo=pytz.utc)


def _get_award_dataset_range():
    award_date = Award.objects.aggregate(
        models.Min('start_date'),
        models.Max('start_date'),
    ).values()
    award_datetimes = [_to_datetime(x) for x in award_date if x is not None]
    if not award_datetimes:
        return []

    return min(award_datetimes), max(award_datetimes)


def create_percentile_map():
    return {
        PERCENTILE_ALLEGATION_GROUP: {
            'percentile_funcs': {
                'allegation': _allegation_count_query,
            },
            'range': (ALLEGATION_MIN_DATETIME, ALLEGATION_MAX_DATETIME)
        },
        PERCENTILE_ALLEGATION_INTERNAL_CIVILIAN_GROUP: {
            'percentile_funcs': {
                'allegation_civilian': _allegation_civilian_count_query,
                'allegation_internal': _allegation_internal_count_query
            },
            'range': (INTERNAL_CIVILIAN_ALLEGATION_MIN_DATETIME, INTERNAL_CIVILIAN_ALLEGATION_MAX_DATETIME)
        },
        PERCENTILE_TRR_GROUP: {
            'percentile_funcs': {
                'trr': _trr_count_query,
            },
            'range': (TRR_MIN_DATETIME, TRR_MAX_DATETIME)
        },
        PERCENTILE_HONORABLE_MENTION_GROUP: {
            'percentile_funcs': {
                'honorable_mention': _honorable_mention_count_query,
            },
            'range': _get_award_dataset_range()
        }
    }


PERCENTILE_MAP = create_percentile_map()


def _compute_metric(year_end, percentile_group):
    data_range = PERCENTILE_MAP[percentile_group]['range']
    if not data_range:
        return Officer.objects.none()

    min_datetime, max_datetime = data_range
    if year_end:
        max_datetime = min(max_datetime, datetime(year_end, 12, 31, tzinfo=pytz.utc))
    if min_datetime + timedelta(days=365) > max_datetime:
        return Officer.objects.none()

    query = _officer_service_year(min_datetime.date(), max_datetime.date())
    query = query.annotate(year=models.Value(year_end, output_field=IntegerField()))

    func_map = PERCENTILE_MAP[percentile_group]['percentile_funcs']
    for metric, func in func_map.items():
        num_key = f'num_{metric}'
        metric_key = f'metric_{metric}'

        query = query.annotate(**{num_key: func(min_datetime, max_datetime)})
        query = query.annotate(**{
            metric_key: models.ExpressionWrapper(
                Round(F(num_key) / F('service_year')),
                output_field=models.FloatField()
            )
        })
    return query


def _officer_service_year(min_date, max_date):
    query = Officer.objects.filter(appointed_date__isnull=False)
    query = query.annotate(
        end_date=models.Case(
            models.When(
                Q(resignation_date__isnull=False, resignation_date__lt=max_date),
                then='resignation_date'),
            default=models.Value(max_date),
            output_field=models.DateField()),
        start_date=models.Case(
            models.When(appointed_date__lt=min_date, then=models.Value(min_date)),
            default='appointed_date',
            output_field=models.DateField()),
    )
    # filter-out officer has service time smaller than 1 year
    query = query.filter(end_date__gte=F('start_date') + timedelta(days=365))

    return query.annotate(
        officer_id=F('id'),
        service_year=(
            Func(
                F('end_date') - F('start_date'),
                template="ROUND(CAST(%(function)s('day', %(expressions)s) / 365.0 as numeric), 4)",
                function='DATE_PART',
                output_field=models.FloatField()
            )  # in order to easy to test and calculate, we only get 4 decimal points
        )
    )
