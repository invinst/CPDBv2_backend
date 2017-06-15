from datetime import datetime

from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField, JSONField
from django.core.exceptions import MultipleObjectsReturned
from django.conf import settings
from django.utils.text import slugify
from django.db.models import F

from data.constants import (
    ACTIVE_CHOICES, ACTIVE_UNKNOWN_CHOICE, CITIZEN_DEPTS, CITIZEN_CHOICE, LOCATION_CHOICES, AREA_CHOICES,
    LINE_AREA_CHOICES, AGENCY_CHOICES, OUTCOMES, FINDINGS, GENDER_DICT, FINDINGS_DICT, OUTCOMES_DICT,
    MEDIA_TYPE_CHOICES, MEDIA_TYPE_VIDEO, MEDIA_TYPE_DOCUMENT, MEDIA_TYPE_AUDIO)
from data.utils.aggregation import get_num_range_case


AREA_CHOICES_DICT = dict(AREA_CHOICES)


class PoliceUnit(models.Model):
    unit_name = models.CharField(max_length=5)
    description = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.unit_name

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
                models.When(race__in=['n/a', 'n/a ', ''], then=models.Value('Unknown')),
                default='race',
                output_field=models.CharField()
            )
        ).values('name').annotate(
            count=models.Count('name')
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
            count=models.Count('name')
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
            count=models.Count('member_gender')
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
        return OfficerAllegation.objects.filter(officer__officerhistory__unit=self).distinct().count()

    @property
    def sustained_count(self):
        return OfficerAllegation.objects.filter(
            officer__officerhistory__unit=self, final_finding='SU'
        ).distinct().count()

    @property
    def complaint_category_aggregation(self):
        query_set = OfficerAllegation.objects.filter(officer__officerhistory__unit=self).distinct().annotate(
            name=models.Case(
                models.When(allegation_category__category__isnull=True, then=models.Value('Unknown')),
                default='allegation_category__category',
                output_field=models.CharField()
            )).values('name').annotate(
                count=models.Count('name'),
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
        query_set = OfficerAllegation.objects.filter(officer__officerhistory__unit=self).distinct().annotate(
            name=models.Case(
                models.When(allegation__complainant__race__isnull=True, then=models.Value('Unknown')),
                models.When(allegation__complainant__race__in=['n/a', 'n/a ', ''], then=models.Value('Unknown')),
                default='allegation__complainant__race',
                output_field=models.CharField()
            )
        ).values('name').annotate(
            count=models.Count('name'),
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
    def complainant_age_aggregation(self):
        query_set = OfficerAllegation.objects.filter(officer__officerhistory__unit=self).distinct().annotate(
            name=get_num_range_case('allegation__complainant__age', [0, 20, 30, 40, 50])
        ).values('name').annotate(
            count=models.Count('name'),
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
    def complainant_gender_aggregation(self):
        query_set = OfficerAllegation.objects.filter(officer__officerhistory__unit=self).distinct().annotate(
            complainant_gender=models.Case(
                models.When(allegation__complainant__gender='', then=models.Value('Unknown')),
                models.When(allegation__complainant__isnull=True, then=models.Value('Unknown')),
                default='allegation__complainant__gender',
                output_field=models.CharField()
            )
        ).values('complainant_gender').annotate(
            count=models.Count('complainant_gender'),
            sustained_count=models.Sum(
                models.Case(
                    models.When(final_finding='SU', then=1),
                    default=0,
                    output_field=models.IntegerField()
                )
            )
        )

        return [
            {
                'name': GENDER_DICT.get(obj['complainant_gender'], 'Unknown'),
                'count': obj['count'],
                'sustained_count': obj['sustained_count']
            }
            for obj in query_set if obj['count'] > 0
        ]


class Officer(models.Model):
    first_name = models.CharField(
        max_length=255, null=True, db_index=True, blank=True)
    last_name = models.CharField(
        max_length=255, null=True, db_index=True, blank=True)
    gender = models.CharField(max_length=1, blank=True)
    race = models.CharField(max_length=50, blank=True)
    appointed_date = models.DateField(null=True)
    rank = models.CharField(max_length=100, blank=True)
    birth_year = models.IntegerField(null=True)
    active = models.CharField(choices=ACTIVE_CHOICES, max_length=10, default=ACTIVE_UNKNOWN_CHOICE)
    tags = ArrayField(models.CharField(null=True, max_length=20), default=[])

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

    @property
    def complaint_category_aggregation(self):
        return list(
            self.officerallegation_set
                .annotate(
                    name=models.Case(
                        models.When(allegation_category__category__isnull=True, then=models.Value('Unknown')),
                        default='allegation_category__category',
                        output_field=models.CharField()))
                .values('name')
                .annotate(
                    count=models.Count('name'),
                    sustained_count=models.Sum(models.Case(
                        models.When(final_finding='SU', then=1), default=models.Value(0),
                        output_field=models.IntegerField()))))

    @property
    def complainant_race_aggregation(self):
        return list(
            self.officerallegation_set
                .annotate(name=models.Case(
                    models.When(allegation__complainant__isnull=True, then=models.Value('Unknown')),
                    models.When(allegation__complainant__race__in=['n/a', 'n/a ', ''], then=models.Value('Unknown')),
                    default='allegation__complainant__race',
                    output_field=models.CharField()))
                .values('name')
                .annotate(
                    count=models.Count('name'),
                    sustained_count=models.Sum(models.Case(
                        models.When(final_finding='SU', then=1), default=models.Value(0),
                        output_field=models.IntegerField()))))

    @property
    def complainant_age_aggregation(self):
        return list(
            self.officerallegation_set
                .annotate(name=get_num_range_case('allegation__complainant__age', [0, 20, 30, 40, 50]))
                .values('name')
                .annotate(
                    count=models.Count('name'),
                    sustained_count=models.Sum(models.Case(
                        models.When(final_finding='SU', then=1), default=models.Value(0),
                        output_field=models.IntegerField()))))

    @property
    def complainant_gender_aggregation(self):
        aggregation = self.officerallegation_set.values('allegation__complainant__gender') \
            .annotate(complainant_gender=models.Case(
                    models.When(allegation__complainant__gender='', then=models.Value('Unknown')),
                    models.When(allegation__complainant__isnull=True, then=models.Value('Unknown')),
                    default='allegation__complainant__gender',
                    output_field=models.CharField()
                )) \
            .values('complainant_gender') \
            .annotate(count=models.Count('complainant_gender'), sustained_count=models.Sum(models.Case(
                    models.When(final_finding='SU', then=1), default=models.Value(0),
                    output_field=models.IntegerField())))

        return [
            {
                'name': GENDER_DICT.get(obj['complainant_gender'], 'Unknown'),
                'sustained_count': obj['sustained_count'],
                'count': obj['count']
            }
            for obj in aggregation if obj['count'] > 0
        ]

    @property
    def v2_to(self):
        return '/officer/%d/' % self.pk

    @property
    def abbr_name(self):
        return '%s. %s' % (self.first_name[0].upper(), self.last_name)


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


class Area(models.Model):
    name = models.CharField(max_length=100)
    area_type = models.CharField(max_length=30, choices=AREA_CHOICES)
    polygon = models.MultiPolygonField(srid=4326, null=True)
    objects = models.GeoManager()

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
    objects = models.GeoManager()


class Investigator(models.Model):
    raw_name = models.CharField(max_length=160)
    name = models.CharField(max_length=160)
    current_rank = models.CharField(max_length=50, blank=True)
    current_report = models.CharField(max_length=4, blank=True)
    unit = models.ForeignKey(PoliceUnit, null=True)
    agency = models.CharField(choices=AGENCY_CHOICES, max_length=10)


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
    def videos(self):
        return self.attachment_files.filter(file_type=MEDIA_TYPE_VIDEO)

    @property
    def audios(self):
        return self.attachment_files.filter(file_type=MEDIA_TYPE_AUDIO)

    @property
    def documents(self):
        return self.attachment_files.filter(file_type=MEDIA_TYPE_DOCUMENT)


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
