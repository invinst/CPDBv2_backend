import os
from datetime import datetime
from itertools import groupby

from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField, JSONField
from django.core.exceptions import MultipleObjectsReturned
from django.db.models import F
from django.db.models import Q
from django.db.models.functions import ExtractYear
from django.utils.text import slugify

from data.constants import (
    ACTIVE_CHOICES, ACTIVE_UNKNOWN_CHOICE, CITIZEN_DEPTS, CITIZEN_CHOICE, LOCATION_CHOICES, AREA_CHOICES,
    LINE_AREA_CHOICES, OUTCOMES, FINDINGS, GENDER_DICT, FINDINGS_DICT, OUTCOMES_DICT,
    MEDIA_TYPE_CHOICES, MEDIA_TYPE_DOCUMENT, BACKGROUND_COLOR_SCHEME,
    DISCIPLINE_CODES
)
from data.utils.aggregation import get_num_range_case
from data.utils.interpolate import ScaleThreshold

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
                default=datetime.now().year - F('birth_year'),
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
    suffix_name = models.CharField(max_length=5, null=True)
    gender = models.CharField(max_length=1, blank=True)
    race = models.CharField(max_length=50, blank=True)
    appointed_date = models.DateField(null=True)
    resignation_date = models.DateField(null=True)
    rank = models.CharField(max_length=100, blank=True)
    birth_year = models.IntegerField(null=True)
    active = models.CharField(choices=ACTIVE_CHOICES, max_length=10, default=ACTIVE_UNKNOWN_CHOICE)

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        return '%s %s' % (self.first_name, self.last_name,)

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
    def v1_url(self):
        return '{domain}/officer/{slug}/{pk}'.format(domain=settings.V1_URL, slug=slugify(self.full_name), pk=self.pk)

    @property
    def last_unit(self):
        try:
            return OfficerHistory.objects.filter(officer=self.pk).order_by('-end_date')[0].unit.unit_name
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


class Area(TaggableModel):
    name = models.CharField(max_length=100)
    area_type = models.CharField(max_length=30, choices=AREA_CHOICES)
    polygon = models.MultiPolygonField(srid=4326, null=True)

    @property
    def v1_url(self):
        if self.area_type == 'neighborhoods':
            return '{domain}/url-mediator/session-builder?neighborhood={name}'.format(domain=settings.V1_URL,
                                                                                      name=self.name)

        if self.area_type == 'community':
            return '{domain}/url-mediator/session-builder?community={name}'.format(domain=settings.V1_URL,
                                                                                   name=self.name)

        return settings.V1_URL


class LineArea(models.Model):
    name = models.CharField(max_length=100)
    linearea_type = models.CharField(max_length=30, choices=LINE_AREA_CHOICES)
    geom = models.MultiLineStringField(srid=4326, blank=True)


class Investigator(models.Model):
    raw_name = models.CharField(max_length=160)
    name = models.CharField(max_length=160, blank=True)
    current_rank = models.CharField(max_length=50, blank=True)
    unit = models.ForeignKey(PoliceUnit, null=True)


class Allegation(models.Model):
    crid = models.CharField(max_length=30, blank=True)
    summary = models.TextField(blank=True)
    location = models.CharField(
        max_length=20, blank=True, choices=LOCATION_CHOICES)
    add1 = models.IntegerField(null=True)
    add2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)
    incident_date = models.DateTimeField(null=True)
    investigator = models.ForeignKey(Investigator, null=True)
    areas = models.ManyToManyField(Area)
    line_areas = models.ManyToManyField(LineArea)
    point = models.PointField(srid=4326, null=True)
    beat = models.ForeignKey(Area, null=True, related_name='beats')
    source = models.CharField(blank=True, max_length=20)

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
    def videos(self):
        # Due to the privacy issue with the data that was posted on the IPRA / COPA data portal
        # We need to hide all videos
        return self.attachment_files.none()

    @property
    def audios(self):
        # Due to the privacy issue with the data that was posted on the IPRA / COPA data portal
        # We need to hide all audios
        return self.attachment_files.none()

    @property
    def documents(self):
        # Due to the privacy issue with the data that was posted on the IPRA / COPA data portal
        # We need to hide those documents
        ipra_query = Q(original_url__icontains='ipra')
        copa_query = Q(original_url__icontains='copa')
        tag_query = Q(tag__in=['TRR', 'OBR'])
        type_query = Q(file_type=MEDIA_TYPE_DOCUMENT)
        return self.attachment_files.filter(type_query & ~(tag_query & (ipra_query | copa_query)))


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


class PoliceWitness(models.Model):
    allegation = models.ForeignKey(Allegation, null=True)
    gender = models.CharField(max_length=1, blank=True)
    race = models.CharField(max_length=50, blank=True)
    officer = models.ForeignKey(Officer, null=True)


class Complainant(models.Model):
    allegation = models.ForeignKey(Allegation, null=True)
    gender = models.CharField(max_length=1, blank=True)
    race = models.CharField(max_length=50, blank=True)
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
    race = models.CharField(max_length=50, null=True)
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

    class Meta:
        unique_together = (('allegation', 'original_url'),)


class Award(models.Model):
    officer = models.ForeignKey(Officer)
    award_type = models.CharField(max_length=255)
    incident_start_date = models.DateField(null=True)
    incident_end_date = models.DateField(null=True)
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
    race = models.CharField(max_length=50, blank=True)
    age = models.IntegerField(null=True)


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
