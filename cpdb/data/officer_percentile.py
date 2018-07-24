from datetime import date, datetime
import pytz

from django.contrib.gis.db import models
from django.db.models import F, Q, IntegerField, Func
from django.utils.timezone import now, timedelta

from data.models import Officer, Award
from data.constants import (
    PERCENTILE_HONORABLE_MENTION,
    ALLEGATION_MAX_DATETIME, ALLEGATION_MIN_DATETIME,
    INTERNAL_CIVILIAN_ALLEGATION_MAX_DATETIME, INTERNAL_CIVILIAN_ALLEGATION_MIN_DATETIME,
    TRR_MAX_DATETIME, TRR_MIN_DATETIME,
    PERCENTILE_GROUPS, PERCENTILE_ALLEGATION_GROUP, PERCENTILE_ALLEGATION_INTERNAL_CIVILIAN_GROUP, PERCENTILE_TRR_GROUP
)
from data.utils.percentile import percentile, merge_metric
from data.utils.round import Round


def top_allegation_percentile(year=now().year):
    return top_percentile(year, percentile_groups=[PERCENTILE_ALLEGATION_GROUP])


def top_visual_token_percentile(year=now().year):
    visual_token_percentile_groups = [
        PERCENTILE_ALLEGATION_INTERNAL_CIVILIAN_GROUP,
        PERCENTILE_TRR_GROUP
    ]
    return top_percentile(year, percentile_groups=visual_token_percentile_groups)


def top_percentile(year=now().year, percentile_groups=PERCENTILE_GROUPS):
    """ This is calculate top percentile of top_percentile_value
    :return: list of (officer_id, percentile_value)
    # """
    if any(t not in PERCENTILE_GROUPS for t in percentile_groups):
        raise ValueError("percentile_type is invalid")

    computed_data = []
    for percentile_group in percentile_groups:
        percentile_types = PERCENTILE_MAP[percentile_group]['percentile_funcs'].keys()
        new_data = _compute_metric(year, percentile_group)
        computed_data = merge_metric(computed_data, new_data, percentile_types)
        for percentile_type in percentile_types:
            computed_data = percentile(computed_data, percentile_type=percentile_type, decimal_places=4)

    return computed_data


def annotate_honorable_mention_percentile_officers():
    officer_metrics = list(_compute_honorable_mention_metric())
    officer_metrics_with_honorable_mention_percentile = percentile(
        officer_metrics,
        percentile_type=PERCENTILE_HONORABLE_MENTION,
        decimal_places=4
    )
    return officer_metrics_with_honorable_mention_percentile


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
        }
    }


PERCENTILE_MAP = create_percentile_map()


def _compute_metric(year_end, percentile_group):
    min_datetime, max_datetime = PERCENTILE_MAP[percentile_group]['range']
    if year_end:
        max_datetime = min(max_datetime, datetime(year_end, 12, 31, tzinfo=pytz.utc))
    if min_datetime + timedelta(days=365) > max_datetime:
        return Officer.objects.none()

    query = _officer_service_year(min_datetime.date(), max_datetime.date())
    query = query.annotate(year=models.Value(year_end, output_field=IntegerField()))

    func_map = PERCENTILE_MAP[percentile_group]['percentile_funcs']
    for metric, func in func_map.iteritems():
        num_key = 'num_{}'.format(metric)
        metric_key = 'metric_{}'.format(metric)

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


def _compute_honorable_mention_metric(year_end=now().year):
    dataset_range = _get_award_dataset_range()
    if not dataset_range:
        return []
    [dataset_min_date, dataset_max_date] = dataset_range

    if year_end:
        dataset_max_date = min(dataset_max_date, date(year_end, 12, 31))

    if dataset_min_date + timedelta(days=365) > dataset_max_date:
        return []

    # STEP 1: compute the service time of all officers
    query = _officer_service_year(dataset_min_date, dataset_max_date)

    # STEP 2: count the allegation (internal/civil), TRR and major award
    query = _annotate_honorable_mention(query, dataset_max_date)

    # STEP 3: calculate the metric
    query = query.annotate(
        metric_honorable_mention=models.ExpressionWrapper(
            Round(F('num_honorable_mention') / F('service_year')),
            output_field=models.FloatField()),
    ).order_by('metric_honorable_mention', 'id')

    return query


def _get_award_dataset_range():
    award_date = Award.objects.aggregate(
        models.Min('start_date'),
        models.Max('start_date'),
    ).values()
    award_date = [x.date() if hasattr(x, 'date') else x for x in award_date if x is not None]
    if not award_date:
        return []
    return [min(award_date), max(award_date)]


def _annotate_honorable_mention(query, dataset_max_date):
    return query.annotate(
        num_honorable_mention=models.Count(
            models.Case(
                models.When(
                    award__start_date__lte=dataset_max_date,
                    award__award_type='Honorable Mention',
                    then='award'
                ), output_field=models.CharField(),
            ), distinct=True
        )
    )
