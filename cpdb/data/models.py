import os
from datetime import date, datetime
from itertools import groupby

from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField, JSONField
from django.core.exceptions import MultipleObjectsReturned
from django.db.models import F, Q, Value, Max, Case, When, IntegerField, DateTimeField, Count, Func
from django.db.models.functions import Concat, ExtractYear, Cast, Lower
from django.utils.text import slugify
from django.utils.timezone import now, timedelta

from data.constants import (
    ACTIVE_CHOICES, ACTIVE_UNKNOWN_CHOICE, CITIZEN_DEPTS, CITIZEN_CHOICE, LOCATION_CHOICES, AREA_CHOICES,
    LINE_AREA_CHOICES, OUTCOMES, FINDINGS, GENDER_DICT, FINDINGS_DICT, OUTCOMES_DICT,
    MEDIA_TYPE_CHOICES, MEDIA_TYPE_DOCUMENT, BACKGROUND_COLOR_SCHEME, PERCENTILE_ALLEGATION,
    DISCIPLINE_CODES, PERCENTILE_TYPES, MAJOR_AWARDS, PERCENTILE_TRR, PERCENTILE_HONORABLE_MENTION,
)
from data.utils.aggregation import get_num_range_case
from data.utils.calculations import percentile
from data.utils.interpolate import ScaleThreshold
from data.validators import validate_race
from data.utils.calculations import Round
from trr.models import TRR

AREA_CHOICES_DICT = dict(AREA_CHOICES)


class TaggableModel(models.Model):
    tags = ArrayField(models.CharField(null=True, max_length=20), default=[])

    class Meta:
        abstract = True


class PoliceUnit(TaggableModel):
    unit_name = models.CharField(max_length=5)
    description = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.unit_name

    @property
    def v2_to(self):
        return '/unit/%s/' % self.unit_name

    @property
    def v1_url(self):
        return '{domain}/url-mediator/session-builder?unit={unit_name}'.format(
            domain=settings.V1_URL, unit_name=self.unit_name
        )

    @property
    def member_count(self):
        return Officer.objects.filter(officerhistory__unit=self).distinct().count()

    @property
    def active_member_count(self):
        return Officer.objects.filter(
            officerhistory__unit=self, officerhistory__end_date__isnull=True
        ).distinct().count()

    @property
    def member_race_aggregation(self):
        query_set = Officer.objects.filter(officerhistory__unit=self).distinct().annotate(
            name=models.Case(
                models.When(race__isnull=True, then=models.Value('Unknown')),
                models.When(race__in=['n/a', 'n/a ', 'nan', ''], then=models.Value('Unknown')),
                default='race',
                output_field=models.CharField()
            )
        ).values('name').annotate(
            count=models.Count('id', distinct=True)
        )

        return list(query_set)

    @property
    def member_age_aggregation(self):
        query_set = Officer.objects.filter(officerhistory__unit=self).distinct().annotate(
            member_age=models.Case(
                models.When(birth_year__isnull=True, then=None),
                default=now().year - F('birth_year'),
                output_field=models.IntegerField()
            )
        ).annotate(
            name=get_num_range_case('member_age', [0, 20, 30, 40, 50])
        ).values('name').annotate(
            count=models.Count('id', distinct=True)
        )

        return list(query_set)

    @property
    def member_gender_aggregation(self):
        query_set = Officer.objects.filter(officerhistory__unit=self).distinct().annotate(
            member_gender=models.Case(
                models.When(gender='', then=models.Value('Unknown')),
                models.When(gender__isnull=True, then=models.Value('Unknown')),
                default='gender',
                output_field=models.CharField()
            )
        ).values('member_gender').annotate(
            count=models.Count('id', distinct=True)
        )

        return [
            {
                'name': GENDER_DICT.get(obj['member_gender'], 'Unknown'),
                'count': obj['count']
            }
            for obj in query_set if obj['count'] > 0
        ]

    @property
    def complaint_count(self):
        return OfficerAllegation.objects.filter(
            officer__officerhistory__unit=self
        ).order_by('allegation').distinct('allegation').count()

    @property
    def sustained_count(self):
        return OfficerAllegation.objects.filter(
            officer__officerhistory__unit=self, final_finding='SU'
        ).order_by('allegation').distinct('allegation').count()

    @property
    def complaint_category_aggregation(self):
        query_set = OfficerAllegation.objects.filter(officer__officerhistory__unit=self).distinct().annotate(
            name=models.Case(
                models.When(allegation_category__category__isnull=True, then=models.Value('Unknown')),
                default='allegation_category__category',
                output_field=models.CharField()
            )).values('name').annotate(
            count=models.Count('allegation__id', distinct=True),
            sustained_count=models.Sum(
                models.Case(
                    models.When(final_finding='SU', then=1),
                    default=0,
                    output_field=models.IntegerField()
                )
            )
        )
        return list(query_set)

    @property
    def complainant_race_aggregation(self):
        query_set = Complainant.objects.filter(
            allegation__officerallegation__officer__officerhistory__unit=self
        ).distinct().annotate(
            name=models.Case(
                models.When(race__isnull=True, then=models.Value('Unknown')),
                models.When(race__in=['n/a', 'n/a ', 'nan', ''], then=models.Value('Unknown')),
                default='race',
                output_field=models.CharField()
            )
        ).values('name').annotate(
            count=models.Count('id', distinct=True)
        )

        sustained_count_query_set = Complainant.objects.filter(
            allegation__officerallegation__officer__officerhistory__unit=self,
            allegation__officerallegation__final_finding='SU'
        ).distinct().annotate(
            name=models.Case(
                models.When(race__isnull=True, then=models.Value('Unknown')),
                models.When(race__in=['n/a', 'n/a ', 'nan', ''], then=models.Value('Unknown')),
                default='race',
                output_field=models.CharField()
            )
        ).values('name').annotate(
            sustained_count=models.Count('id', distinct=True)
        )

        sustained_count_results = {
            obj['name']: obj['sustained_count'] for obj in sustained_count_query_set
        }

        return [
            {
                'name': obj['name'],
                'count': obj['count'],
                'sustained_count': sustained_count_results.get(obj['name'], 0)
            }
            for obj in query_set if obj['count'] > 0
        ]

    @property
    def complainant_age_aggregation(self):
        query_set = Complainant.objects.filter(
            allegation__officerallegation__officer__officerhistory__unit=self
        ).distinct().annotate(
            name=get_num_range_case('age', [0, 20, 30, 40, 50])
        ).values('name').annotate(
            count=models.Count('id', distinct=True)
        )

        sustained_count_query_set = Complainant.objects.filter(
            allegation__officerallegation__officer__officerhistory__unit=self,
            allegation__officerallegation__final_finding='SU'
        ).distinct().annotate(
            name=get_num_range_case('age', [0, 20, 30, 40, 50])
        ).values('name').annotate(
            sustained_count=models.Count('id', distinct=True)
        )

        sustained_count_results = {
            obj['name']: obj['sustained_count'] for obj in sustained_count_query_set
        }

        return [
            {
                'name': obj['name'],
                'count': obj['count'],
                'sustained_count': sustained_count_results.get(obj['name'], 0)
            }
            for obj in query_set if obj['count'] > 0
        ]

    @property
    def complainant_gender_aggregation(self):
        query_set = Complainant.objects.filter(
            allegation__officerallegation__officer__officerhistory__unit=self
        ).distinct().annotate(
            complainant_gender=models.Case(
                models.When(gender='', then=models.Value('Unknown')),
                default='gender',
                output_field=models.CharField()
            )
        ).values('complainant_gender').annotate(
            count=models.Count('id', distinct=True)
        )

        sustained_count_query_set = Complainant.objects.filter(
            allegation__officerallegation__officer__officerhistory__unit=self,
            allegation__officerallegation__final_finding='SU'
        ).distinct().annotate(
            complainant_gender=models.Case(
                models.When(gender='', then=models.Value('Unknown')),
                default='gender',
                output_field=models.CharField()
            )
        ).values('complainant_gender').annotate(
            sustained_count=models.Count('id', distinct=True)
        )

        sustained_count_results = {
            obj['complainant_gender']: obj['sustained_count'] for obj in sustained_count_query_set
        }

        return [
            {
                'name': GENDER_DICT.get(obj['complainant_gender'], 'Unknown'),
                'count': obj['count'],
                'sustained_count': sustained_count_results.get(obj['complainant_gender'], 0)
            }
            for obj in query_set if obj['count'] > 0
        ]


class Officer(TaggableModel):
    first_name = models.CharField(max_length=255, db_index=True)
    last_name = models.CharField(max_length=255, db_index=True)
    middle_initial = models.CharField(max_length=5, null=True)
    middle_initial2 = models.CharField(max_length=5, null=True)
    suffix_name = models.CharField(max_length=5, null=True)
    gender = models.CharField(max_length=1, blank=True)
    race = models.CharField(max_length=50, default='Unknown', validators=[validate_race])
    appointed_date = models.DateField(null=True)
    resignation_date = models.DateField(null=True)
    rank = models.CharField(max_length=100, blank=True)
    birth_year = models.IntegerField(null=True)
    active = models.CharField(choices=ACTIVE_CHOICES, max_length=10, default=ACTIVE_UNKNOWN_CHOICE)

    complaint_percentile = models.DecimalField(max_digits=6, decimal_places=3, null=True)

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        return '%s %s' % (self.first_name, self.last_name,)

    @property
    def historic_badges(self):
        # old not current badge
        return self.officerbadgenumber_set.exclude(current=True).values_list('star', flat=True)

    @property
    def historic_units(self):
        return [o.unit for o in self.officerhistory_set.all().order_by('-effective_date')]

    @property
    def trr_count(self):
        return self.trr_set.count()

    @property
    def current_badge(self):
        try:
            return self.officerbadgenumber_set.get(current=True).star
        except (OfficerBadgeNumber.DoesNotExist, MultipleObjectsReturned):
            return ''

    @property
    def gender_display(self):
        try:
            return GENDER_DICT[self.gender]
        except KeyError:
            return self.gender

    @property
    def allegation_count(self):
        return self.officerallegation_set.all().distinct().count()

    @property
    def sustained_count(self):
        return self.officerallegation_set.filter(final_finding='SU').distinct().count()

    @property
    def honorable_mention_count(self):
        return self.award_set.filter(award_type__contains='Honorable Mention').distinct().count()

    @property
    def civilian_compliment_count(self):
        return self.award_set.filter(award_type='Complimentary Letter').distinct().count()

    @property
    def v1_url(self):
        return '{domain}/officer/{slug}/{pk}'.format(domain=settings.V1_URL, slug=slugify(self.full_name), pk=self.pk)

    @property
    def last_unit(self):
        try:
            return OfficerHistory.objects.filter(officer=self.pk).order_by('-end_date')[0].unit
        except IndexError:
            return None

    @property
    def current_age(self):
        return datetime.now().year - self.birth_year

    @staticmethod
    def get_dataset_range():
        allegation_date = Allegation.objects.aggregate(
            models.Min('incident_date'),
            models.Max('incident_date'),
            models.Min('officerallegation__start_date'),
            models.Max('officerallegation__start_date'),
            models.Max('officerallegation__end_date'),
        ).values()
        trr_date = TRR.objects.aggregate(
            models.Min('trr_datetime'),
            models.Max('trr_datetime')
        ).values()
        all_date = allegation_date[:]
        all_date.extend(trr_date)
        all_date = [x.date() if hasattr(x, 'date') else x for x in all_date
                    if x is not None]
        if not all_date:
            return []
        return [min(all_date), max(all_date)]

    @staticmethod
    def get_award_dataset_range():
        award_date = Award.objects.aggregate(
            models.Min('start_date'),
            models.Max('start_date'),
        ).values()
        award_date = [x.date() if hasattr(x, 'date') else x for x in award_date if x is not None]
        if not award_date:
            return []
        return [min(award_date), max(award_date)]

    @staticmethod
    def _annotate_officer_working_range(query, dataset_min_date, dataset_max_date):
        query = query.annotate(
            end_date=models.Case(
                models.When(resignation_date__isnull=True, then=models.Value(dataset_max_date)),
                default='resignation_date',
                output_field=models.DateField()),
            start_date=models.Case(
                models.When(appointed_date__lt=dataset_min_date, then=models.Value(dataset_min_date)),
                default='appointed_date',
                output_field=models.DateField()),
        )
        # filter-out officer has service time smaller than 1 year
        query = query.filter(end_date__gt=F('start_date') + timedelta(days=365))
        return query.annotate(
            service_year=(
                Func(
                    F('end_date') - F('start_date'),
                    template="ROUND(CAST(%(function)s('day', %(expressions)s) / 365.0 as numeric), 4)",
                    function='DATE_PART',
                    output_field=models.FloatField()
                )  # in order to easy to test and calculate, we only get 4 decimal points
            )
        )

    @staticmethod
    def _annotate_num_complaint_n_trr(query, dataset_max_date):
        return query.annotate(
            officer_id=F('id'),
            year=models.Value(dataset_max_date.year, output_field=IntegerField()),
            num_allegation=models.Count(
                models.Case(
                    models.When(
                        officerallegation__start_date__lte=dataset_max_date,
                        then='officerallegation'
                    ), output_field=models.CharField(),
                ), distinct=True
            ),
            num_allegation_internal=models.Count(
                models.Case(
                    models.When(
                        Q(officerallegation__allegation__is_officer_complaint=True) &
                        Q(officerallegation__start_date__lte=dataset_max_date),
                        then='officerallegation'
                    )
                ), distinct=True
            ),
            num_trr=models.Count(
                models.Case(
                    models.When(
                        trr__trr_datetime__date__lte=dataset_max_date,
                        then='trr'
                    ), output_field=models.CharField(),
                ), distinct=True
            ),
        )

    @staticmethod
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

    @staticmethod
    def compute_metric_percentile(year_end=now().year):
        dataset_range = Officer.get_dataset_range()
        if not dataset_range:
            return []
        [dataset_min_date, dataset_max_date] = dataset_range

        if year_end:
            dataset_max_date = min(dataset_max_date, date(year_end, 12, 31))

        # STEP 1: compute the service time of all officers
        query = Officer.objects.filter(appointed_date__isnull=False)
        query = Officer._annotate_officer_working_range(query, dataset_min_date, dataset_max_date)

        # STEP 2: count the allegation (internal/civil) and TRR
        query = Officer._annotate_num_complaint_n_trr(query, dataset_max_date)

        # STEP 3: calculate the metric
        query = query.annotate(
            metric_allegation=models.ExpressionWrapper(
                Round(F('num_allegation') / F('service_year')),
                output_field=models.FloatField()),
            metric_allegation_internal=models.ExpressionWrapper(
                Round(F('num_allegation_internal') / F('service_year')),
                output_field=models.FloatField()),
            metric_allegation_civilian=models.ExpressionWrapper(
                Round((F('num_allegation') - F('num_allegation_internal')) / F('service_year')),
                output_field=models.FloatField()),
            metric_trr=models.ExpressionWrapper(
                Round(F('num_trr') / F('service_year')),
                output_field=models.FloatField())
        ).order_by(PERCENTILE_ALLEGATION, PERCENTILE_TRR, 'officer_id')

        return query

    @staticmethod
    def top_complaint_officers(top_percentile_value, year=now().year, percentile_types=PERCENTILE_TYPES):
        """ This is calculate top percentile of top_percentile_value
        :return: list of (officer_id, percentile_value)
        """
        computed_data = list(Officer.compute_metric_percentile(year))

        if any(t not in PERCENTILE_TYPES for t in percentile_types):
            raise ValueError("percentile_type is invalid")

        for percentile_type in percentile_types:
            computed_data = percentile(
                computed_data,
                100.0 - top_percentile_value,
                key=percentile_type,
                decimal_places=4)
        return computed_data

    @staticmethod
    def compute_honorable_mention_metric(year_end=now().year):
        dataset_range = Officer.get_award_dataset_range()
        if not dataset_range:
            return []
        [dataset_min_date, dataset_max_date] = dataset_range

        if year_end:
            dataset_max_date = min(dataset_max_date, date(year_end, 12, 31))

        # STEP 1: compute the service time of all officers
        query = Officer.objects.filter(appointed_date__isnull=False)
        query = Officer._annotate_officer_working_range(query, dataset_min_date, dataset_max_date)

        # STEP 2: count the allegation (internal/civil), TRR and major award
        query = Officer._annotate_honorable_mention(query, dataset_max_date)

        # STEP 3: calculate the metric
        query = query.annotate(
            metric_honorable_mention=models.ExpressionWrapper(
                Round(F('num_honorable_mention') / F('service_year')),
                output_field=models.FloatField()),
        ).order_by(PERCENTILE_HONORABLE_MENTION, 'id')

        return query

    @staticmethod
    def annotate_honorable_mention_percentile_officers():
        officer_metrics = list(Officer.compute_honorable_mention_metric())
        officer_metrics_with_honorable_mention_percentile = percentile(
            officer_metrics,
            key=PERCENTILE_HONORABLE_MENTION,
            decimal_places=4
        )
        return officer_metrics_with_honorable_mention_percentile

    @property
    def v2_to(self):
        return '/officer/%d/' % self.pk

    def get_absolute_url(self):
        return '/officer/%d/' % self.pk

    @property
    def abbr_name(self):
        return '%s. %s' % (self.first_name[0].upper(), self.last_name)

    @property
    def discipline_count(self):
        return self.officerallegation_set.filter(final_outcome__in=DISCIPLINE_CODES).count()

    @property
    def visual_token_background_color(self):
        cr_scale = ScaleThreshold(domain=[1, 5, 10, 25, 40], target_range=range(6))

        cr_threshold = cr_scale.interpolate(self.allegation_count)

        return BACKGROUND_COLOR_SCHEME['{cr_threshold}0'.format(
            cr_threshold=cr_threshold
        )]

    @property
    def visual_token_png_url(self):
        return 'https://{account_name}.blob.core.windows.net/visual-token/officer_{id}.png'.format(
            account_name=settings.VISUAL_TOKEN_STORAGEACCOUNTNAME, id=self.id
        )

    @property
    def visual_token_png_path(self):
        file_name = 'officer_{id}.png'.format(
            account_name=settings.VISUAL_TOKEN_STORAGEACCOUNTNAME, id=self.id
        )
        return os.path.join(settings.VISUAL_TOKEN_SOCIAL_MEDIA_FOLDER, file_name)

    def get_unit_by_date(self, query_date):
        try:
            officer_history = self.officerhistory_set.filter(
                Q(effective_date__lte=query_date) | Q(effective_date__isnull=True),
                Q(end_date__gte=query_date) | Q(end_date__isnull=True)
            )[0]
            return officer_history.unit

        except IndexError:
            return None

    @staticmethod
    def _group_and_sort_aggregations(data, key_name='name'):
        """
        Helper to group by name, aggregate count & sustained_counts.
        Also makes sure 'Unknown' group is always the last item.
        """
        groups = []
        unknown_group = None
        for k, g in groupby(data, lambda x: x[key_name]):
            group = {'name': k, 'count': 0, 'sustained_count': 0, 'items': []}
            unknown_year = None
            for item in g:
                if item['year']:
                    group['items'].append(item)
                    group['count'] += item['count']
                    group['sustained_count'] += item['sustained_count']
                else:
                    unknown_year = item
            if unknown_year:
                group['count'] += item['count']
                group['sustained_count'] += item['sustained_count']
            if k != 'Unknown':
                groups.append(group)
            else:
                unknown_group = group

        if unknown_group is not None:
            groups.append(unknown_group)
        return groups

    @property
    def complaint_category_aggregation(self):
        query = self.officerallegation_set.all()
        query = query.annotate(
            name=models.Case(
                models.When(
                    allegation_category__category__isnull=True, then=models.Value('Unknown')),
                default='allegation_category__category',
                output_field=models.CharField()),
            year=ExtractYear('start_date'))
        query = query.values('name', 'year').order_by('name', 'year').annotate(
            count=models.Count('name'),
            sustained_count=models.Sum(models.Case(
                models.When(final_finding='SU', then=1), default=models.Value(0),
                output_field=models.IntegerField())))

        return Officer._group_and_sort_aggregations(list(query))

    @property
    def complainant_race_aggregation(self):
        query = self.officerallegation_set.all()
        query = query.annotate(
            name=models.Case(
                models.When(allegation__complainant__isnull=True, then=models.Value('Unknown')),
                models.When(allegation__complainant__race__in=['n/a', 'n/a ', 'nan', ''], then=models.Value('Unknown')),
                default='allegation__complainant__race',
                output_field=models.CharField()
            ),
            year=ExtractYear('start_date'),
        )
        query = query.values('name', 'year').order_by('name', 'year').annotate(
            count=models.Count('name'),
            sustained_count=models.Sum(
                models.Case(
                    models.When(final_finding='SU', then=1),
                    default=models.Value(0),
                    output_field=models.IntegerField()
                )
            )
        )
        return Officer._group_and_sort_aggregations(list(query))

    @property
    def complainant_age_aggregation(self):
        query = self.officerallegation_set.all()
        query = query.annotate(
            name=get_num_range_case('allegation__complainant__age', [0, 20, 30, 40, 50]),
            year=ExtractYear('start_date')
        )
        query = query.values('name', 'year').order_by('name', 'year').annotate(
            count=models.Count('name'),
            sustained_count=models.Sum(
                models.Case(
                    models.When(final_finding='SU', then=1),
                    default=models.Value(0),
                    output_field=models.IntegerField()
                )
            )
        )
        return Officer._group_and_sort_aggregations(list(query))

    @property
    def complainant_gender_aggregation(self):

        query = self.officerallegation_set.all()
        query = query.values('allegation__complainant__gender').annotate(
            complainant_gender=models.Case(
                models.When(allegation__complainant__gender='', then=models.Value('Unknown')),
                models.When(allegation__complainant__isnull=True, then=models.Value('Unknown')),
                default='allegation__complainant__gender',
                output_field=models.CharField()
            ),
            year=ExtractYear('start_date')
        )
        query = query.values('complainant_gender', 'year').order_by('complainant_gender', 'year').annotate(
            count=models.Count('complainant_gender'),
            sustained_count=models.Sum(
                models.Case(
                    models.When(final_finding='SU', then=1),
                    default=models.Value(0),
                    output_field=models.IntegerField()
                )
            )
        )

        data = [
            {
                'name': GENDER_DICT.get(obj['complainant_gender'], 'Unknown'),
                'sustained_count': obj['sustained_count'],
                'count': obj['count'],
                'year': obj['year']
            }
            for obj in query if obj['count'] > 0
        ]
        return Officer._group_and_sort_aggregations(data)

    @property
    def total_complaints_aggregation(self):
        query = self.officerallegation_set.filter(start_date__isnull=False)
        query = query.annotate(year=ExtractYear('start_date'))
        query = query.values('year').order_by('year').annotate(
            count=models.Count('id'),
            sustained_count=models.Sum(
                models.Case(
                    models.When(final_finding='SU', then=1),
                    default=models.Value(0),
                    output_field=models.IntegerField()
                )
            )
        )
        aggregate_count = 0
        aggregate_sustained_count = 0
        results = list(query)
        for item in results:
            aggregate_count += item['count']
            aggregate_sustained_count += item['sustained_count']
        return results

    @property
    def major_award_count(self):
        return self.award_set.annotate(
            lower_award_type=Lower('award_type')
        ).filter(
            lower_award_type__in=MAJOR_AWARDS
        ).count()

    @property
    def coaccusals(self):
        return Officer.objects.filter(
            officerallegation__allegation__officerallegation__officer=self
        ).distinct().exclude(id=self.id).annotate(coaccusal_count=Count('id')).order_by('-coaccusal_count')

    @property
    def current_salary(self):
        current_salary_object = self.salary_set.all().order_by('-year').first()
        return current_salary_object.salary if current_salary_object else None


class OfficerBadgeNumber(models.Model):
    officer = models.ForeignKey(Officer, null=True)
    star = models.CharField(max_length=10)
    current = models.BooleanField(default=False)

    def __str__(self):
        return '%s - %s' % (self.officer, self.star)


class OfficerHistory(models.Model):
    officer = models.ForeignKey(Officer, null=True)
    unit = models.ForeignKey(PoliceUnit, null=True)
    effective_date = models.DateField(null=True)
    end_date = models.DateField(null=True)

    @property
    def unit_name(self):
        return self.unit.unit_name

    @property
    def unit_description(self):
        return self.unit.description


class AreaObjectManager(models.Manager):
    def with_allegation_per_capita(self):
        racepopulation = RacePopulation.objects.filter(area=models.OuterRef('pk')).values('area')
        population = racepopulation.annotate(s=models.Sum('count')).values('s')
        query = Area.objects.annotate(
            population=models.Subquery(population),
            complaint_count=Count('allegation', distinct=True))
        query = query.annotate(
            allegation_per_capita=models.ExpressionWrapper(
                Cast(F('complaint_count'), models.FloatField()) / F('population'),
                output_field=models.FloatField()))
        return query


class Area(TaggableModel):
    SESSION_BUILDER_MAPPING = {
        'neighborhoods': 'neighborhood',
        'community': 'community',
        'school-grounds': 'school_ground',
        'wards': 'ward',
        'police-districts': 'police_district',
        'beat': 'beat',
    }

    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255, null=True, blank=True, help_text="Another name for area")
    area_type = models.CharField(max_length=30, choices=AREA_CHOICES)
    polygon = models.MultiPolygonField(srid=4326, null=True)
    median_income = models.CharField(max_length=100, null=True)
    commander = models.ForeignKey(Officer, null=True)
    alderman = models.CharField(max_length=255, null=True, help_text="Alderman of Ward")
    police_hq = models.ForeignKey(
        'data.Area',
        null=True,
        help_text="This beat contains police-district HQ"
    )

    objects = AreaObjectManager()

    def get_most_common_complaint(self):
        query = OfficerAllegation.objects.filter(allegation__areas__in=[self])
        query = query.values('allegation_category__category').annotate(
            id=F('allegation_category__id'),
            name=F('allegation_category__category'),
            count=Count('allegation', distinct=True)
        )
        query = query.order_by('-count')[:3]
        return query.values('id', 'name', 'count')

    def get_officers_most_complaints(self):
        query = OfficerAllegation.objects.filter(allegation__areas__in=[self])
        query = query.values('officer').annotate(
            id=F('officer__id'),
            name=Concat('officer__first_name', Value(' '), 'officer__last_name'),
            count=Count('allegation', distinct=True)
        )
        query = query.order_by('-count')[:3]
        return query.values('id', 'name', 'count')

    @property
    def allegation_count(self):
        return self.allegation_set.distinct().count()

    @property
    def v1_url(self):
        base_url = '{domain}/url-mediator/session-builder'.format(domain=settings.V1_URL)

        if self.area_type not in self.SESSION_BUILDER_MAPPING:
            return settings.V1_URL
        return '{base_url}?{keyword}={name}'.format(
            base_url=base_url,
            keyword=self.SESSION_BUILDER_MAPPING[self.area_type],
            name=self.name
        )


class RacePopulation(models.Model):
    race = models.CharField(max_length=255)
    count = models.PositiveIntegerField()
    area = models.ForeignKey(Area)


class LineArea(models.Model):
    name = models.CharField(max_length=100)
    linearea_type = models.CharField(max_length=30, choices=LINE_AREA_CHOICES)
    geom = models.MultiLineStringField(srid=4326, blank=True)


class Investigator(models.Model):
    first_name = models.CharField(max_length=255, db_index=True, null=True)
    last_name = models.CharField(max_length=255, db_index=True, null=True)
    middle_initial = models.CharField(max_length=5, null=True)
    suffix_name = models.CharField(max_length=5, null=True)
    appointed_date = models.DateField(null=True)
    officer = models.ForeignKey(Officer, null=True)

    @property
    def num_cases(self):
        return self.investigatorallegation_set.all().count()

    @property
    def full_name(self):
        return '%s %s' % (self.first_name, self.last_name,)

    @property
    def abbr_name(self):
        return '%s. %s' % (self.first_name[0].upper(), self.last_name)


class Allegation(models.Model):
    crid = models.CharField(max_length=30, blank=True)
    summary = models.TextField(blank=True)
    location = models.CharField(
        max_length=20, blank=True, choices=LOCATION_CHOICES)
    add1 = models.IntegerField(null=True)
    add2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)
    incident_date = models.DateTimeField(null=True)
    areas = models.ManyToManyField(Area)
    line_areas = models.ManyToManyField(LineArea)
    point = models.PointField(srid=4326, null=True)
    beat = models.ForeignKey(Area, null=True, related_name='beats')
    source = models.CharField(blank=True, max_length=20)
    is_officer_complaint = models.BooleanField(default=False)

    @property
    def category_names(self):
        query = self.officer_allegations.annotate(
            name=models.Case(
                models.When(allegation_category__isnull=True, then=models.Value('Unknown')),
                default='allegation_category__category',
                output_field=models.CharField()))
        query = query.values('name').distinct()
        results = [result['name'] for result in query]
        return results if results else ['Unknown']

    @property
    def address(self):
        result = ''
        if self.add1 is not None:
            result = str(self.add1)
        if self.add2 != '':
            result = ' '.join(filter(None, [result, self.add2]))
        if self.city:
            result = ', '.join(filter(None, [result, self.city]))
        return result

    @property
    def officer_allegations(self):
        return self.officerallegation_set.all()

    @property
    def complainants(self):
        return self.complainant_set.all()

    @property
    def victims(self):
        return self.victim_set.all()

    @property
    def complainant_races(self):
        query = self.complainant_set.annotate(
            name=models.Case(
                models.When(race__in=['n/a', 'n/a ', 'nan', ''], then=models.Value('Unknown')),
                default='race',
                output_field=models.CharField()))
        query = query.values('name').distinct()
        results = [result['name'] for result in query]
        return results if results else ['Unknown']

    @property
    def complainant_age_groups(self):
        results = self.complainant_set.annotate(name=get_num_range_case('age', [0, 20, 30, 40, 50]))
        results = results.values('name').distinct()
        results = [result['name'] for result in results]
        return results if results else ['Unknown']

    @property
    def complainant_genders(self):
        query = self.complainant_set.annotate(
            name=models.Case(
                models.When(gender='', then=models.Value('Unknown')),
                default='gender',
                output_field=models.CharField()))
        query = query.values('name').distinct()
        results = [GENDER_DICT.get(result['name'], 'Unknown') for result in query]
        return results if results else ['Unknown']

    @property
    def first_start_date(self):
        try:
            return self.officerallegation_set.filter(start_date__isnull=False)\
                .values_list('start_date', flat=True)[0]
        except IndexError:
            return None

    @property
    def first_end_date(self):
        try:
            return self.officerallegation_set.filter(end_date__isnull=False)\
                .values_list('end_date', flat=True)[0]
        except IndexError:
            return None

    def get_newest_added_document(self):
        return self.attachment_files.filter(file_type=MEDIA_TYPE_DOCUMENT)\
            .exclude(created_at__isnull=True).latest('created_at')

    @property
    def documents(self):
        return self.attachment_files.filter(file_type=MEDIA_TYPE_DOCUMENT)

    @staticmethod
    def get_cr_with_new_documents(limit):
        start_datetime = now() - timedelta(weeks=24)
        query = Allegation.objects.all()
        type_query = Q(attachment_files__file_type=MEDIA_TYPE_DOCUMENT)

        # get 40 allegations which has newest documents
        query = query.annotate(
            new_document_added=Max(
                Case(
                    When(type_query, then='attachment_files__created_at'),
                    output_field=DateTimeField()
                )
            )
        )
        query = query.filter(
            new_document_added__gte=start_datetime,
            new_document_added__isnull=False
        ).order_by('-new_document_added')[:limit]

        # count number of recent documents for each above allegation
        query = query.annotate(
            num_recent_documents=Count(
                Case(
                    When(
                        type_query & Q(attachment_files__created_at__gte=start_datetime),
                        then=1),
                    output_field=IntegerField(),
                )
            )
        )
        return query

    @property
    def v2_to(self):
        if self.officerallegation_set.count() == 0:
            return '/complaint/%s/' % self.crid

        officer_allegations = self.officerallegation_set.filter(officer__isnull=False)

        if officer_allegations.count() == 0:
            return '/complaint/%s/' % self.crid

        return '/complaint/%s/%s/' % (self.crid, officer_allegations.first().officer.pk)


class InvestigatorAllegation(models.Model):
    investigator = models.ForeignKey(Investigator)
    allegation = models.ForeignKey(Allegation)
    current_star = models.CharField(max_length=10, null=True)
    current_rank = models.CharField(max_length=100, null=True)
    current_unit = models.ForeignKey(PoliceUnit, null=True)


class AllegationCategory(models.Model):
    category_code = models.CharField(max_length=255)
    category = models.CharField(max_length=255, blank=True)
    allegation_name = models.CharField(max_length=255, blank=True)
    on_duty = models.BooleanField(default=False)
    citizen_dept = models.CharField(max_length=50, default=CITIZEN_CHOICE, choices=CITIZEN_DEPTS)


class OfficerAllegation(models.Model):
    allegation = models.ForeignKey(Allegation, null=True)
    allegation_category = models.ForeignKey(AllegationCategory, to_field='id', null=True)
    officer = models.ForeignKey(Officer, null=True)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    officer_age = models.IntegerField(null=True)

    recc_finding = models.CharField(
        choices=FINDINGS, max_length=2, blank=True)
    recc_outcome = models.CharField(
        choices=OUTCOMES, max_length=3, blank=True)
    final_finding = models.CharField(
        choices=FINDINGS, max_length=2, blank=True)
    final_outcome = models.CharField(
        choices=OUTCOMES, max_length=3, blank=True)
    final_outcome_class = models.CharField(max_length=20, blank=True)

    @property
    def crid(self):
        return self.allegation.crid

    @property
    def category(self):
        try:
            return self.allegation_category.category
        except AttributeError:
            return None

    @property
    def subcategory(self):
        try:
            return self.allegation_category.allegation_name
        except AttributeError:
            return None

    @property
    def coaccused_count(self):
        return OfficerAllegation.objects.filter(allegation=self.allegation).distinct().count()

    @property
    def final_finding_display(self):
        try:
            return FINDINGS_DICT[self.final_finding]
        except KeyError:
            return 'Unknown'

    @property
    def recc_finding_display(self):
        try:
            return FINDINGS_DICT[self.recc_finding]
        except KeyError:
            return 'Unknown'

    @property
    def final_outcome_display(self):
        try:
            return OUTCOMES_DICT[self.final_outcome]
        except KeyError:
            return 'Unknown'

    @property
    def recc_outcome_display(self):
        try:
            return OUTCOMES_DICT[self.recc_outcome]
        except KeyError:
            return 'Unknown'

    @property
    def documents(self):
        return self.allegation.documents

    @property
    def attachments(self):
        return self.allegation.attachment_files.all()


class PoliceWitness(models.Model):
    allegation = models.ForeignKey(Allegation, null=True)
    officer = models.ForeignKey(Officer, null=True)


class Complainant(models.Model):
    allegation = models.ForeignKey(Allegation, null=True)
    gender = models.CharField(max_length=1, blank=True)
    race = models.CharField(max_length=50, default='Unknown', validators=[validate_race])
    age = models.IntegerField(null=True)

    @property
    def gender_display(self):
        try:
            return GENDER_DICT[self.gender]
        except KeyError:
            return self.gender


class OfficerAlias(models.Model):
    old_officer_id = models.IntegerField()
    new_officer = models.ForeignKey(Officer)

    class Meta:
        unique_together = ('old_officer_id', 'new_officer')


class Involvement(models.Model):
    allegation = models.ForeignKey(Allegation)
    officer = models.ForeignKey(Officer, null=True)
    full_name = models.CharField(max_length=50)
    involved_type = models.CharField(max_length=25)
    gender = models.CharField(max_length=1, null=True)
    race = models.CharField(max_length=50, default='Unknown', validators=[validate_race])
    age = models.IntegerField(null=True)

    @property
    def gender_display(self):
        try:
            return GENDER_DICT[self.gender]
        except KeyError:
            return self.gender


class AttachmentFile(models.Model):
    file_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES, db_index=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    url = models.CharField(max_length=255, db_index=True)
    additional_info = JSONField()
    tag = models.CharField(max_length=50)
    original_url = models.CharField(max_length=255, db_index=True)
    allegation = models.ForeignKey(Allegation, related_name='attachment_files')

    # Document cloud information
    preview_image_url = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(null=True)
    last_updated = models.DateTimeField(null=True)

    class Meta:
        unique_together = (('allegation', 'original_url'),)


class Award(models.Model):
    officer = models.ForeignKey(Officer)
    award_type = models.CharField(max_length=255)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    current_status = models.CharField(max_length=20)
    request_date = models.DateField()
    rank = models.CharField(max_length=100, blank=True)
    last_promotion_date = models.DateField(null=True)
    requester_full_name = models.CharField(max_length=255, null=True)
    ceremony_date = models.DateField(null=True)
    tracking_no = models.CharField(max_length=255, null=True)


class Victim(models.Model):
    allegation = models.ForeignKey(Allegation)
    gender = models.CharField(max_length=1, blank=True)
    race = models.CharField(max_length=50, default='Unknown', validators=[validate_race])
    age = models.IntegerField(null=True)

    @property
    def gender_display(self):
        try:
            return GENDER_DICT[self.gender]
        except KeyError:
            return self.gender


class AttachmentRequest(models.Model):
    allegation = models.ForeignKey(Allegation)
    email = models.EmailField(max_length=255)
    status = models.BooleanField(default=False)

    class Meta:
        unique_together = (('allegation', 'email'),)

    def __str__(self):
        return '%s - %s' % (self.email, self.allegation.crid)

    def save(self, *args, **kwargs):
        self.full_clean()
        super(AttachmentRequest, self).save(*args, **kwargs)


class Salary(models.Model):
    pay_grade = models.CharField(max_length=16)
    rank = models.CharField(max_length=64, null=True)
    salary = models.PositiveIntegerField()
    employee_status = models.CharField(max_length=32)
    org_hire_date = models.DateField(null=True)
    spp_date = models.DateField(null=True)
    start_date = models.DateField(null=True)
    year = models.PositiveSmallIntegerField()
    age_at_hire = models.PositiveSmallIntegerField(null=True)
    officer = models.ForeignKey(Officer)
