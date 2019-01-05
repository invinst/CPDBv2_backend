from django.apps import apps
from django.conf import settings
from django.contrib.gis.db import models
from django.db.models import F, Value, Count
from django.db.models.functions import Concat, Cast

from data.constants import AREA_CHOICES
from data.utils.getters import get_officers_most_complaints_from_query
from .common import TaggableModel, TimeStampsModel


class Area(TimeStampsModel, TaggableModel):
    SESSION_BUILDER_MAPPING = {
        'neighborhoods': 'neighborhood',
        'community': 'community',
        'school-grounds': 'school_ground',
        'wards': 'ward',
        'police-districts': 'police_district',
        'beat': 'beat',
    }

    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255, null=True, blank=True, help_text='Another name for area')
    area_type = models.CharField(max_length=30, choices=AREA_CHOICES)
    polygon = models.MultiPolygonField(srid=4326, null=True)
    median_income = models.CharField(max_length=100, null=True)
    commander = models.ForeignKey('data.Officer', on_delete=models.SET_NULL, null=True)
    alderman = models.CharField(max_length=255, null=True, help_text='Alderman of Ward')
    police_hq = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        help_text='This beat contains police-district HQ'
    )

    @classmethod
    def police_districts_with_allegation_per_capita(cls):
        RacePopulation = apps.get_app_config('data').get_model('RacePopulation')
        racepopulation = RacePopulation.objects.filter(area=models.OuterRef('pk')).values('area')
        population = racepopulation.annotate(s=models.Sum('count')).values('s')
        return cls.objects.filter(area_type='police-districts').annotate(
            population=models.Subquery(population),
            complaint_count=Count('allegation', distinct=True)
        ).filter(population__isnull=False).annotate(
            allegation_per_capita=models.ExpressionWrapper(
                Cast(F('complaint_count'), models.FloatField()) / F('population'),
                output_field=models.FloatField()
            )
        )

    def get_most_common_complaint(self):
        OfficerAllegation = apps.get_app_config('data').get_model('OfficerAllegation')
        query = OfficerAllegation.objects.filter(allegation__areas__in=[self])
        query = query.values('allegation_category__category').annotate(
            id=F('allegation_category__id'),
            name=F('allegation_category__category'),
            count=Count('allegation', distinct=True)
        )
        query = query.order_by('-count')[:3]
        return query.values('id', 'name', 'count')

    def get_officers_most_complaints(self):
        OfficerAllegation = apps.get_app_config('data').get_model('OfficerAllegation')
        query = OfficerAllegation.objects.filter(allegation__areas__in=[self])
        return get_officers_most_complaints_from_query(query)

    @property
    def allegation_count(self):
        return self.allegation_set.distinct().count()

    @property
    def v1_url(self):
        base_url = f'{settings.V1_URL}/url-mediator/session-builder'

        if self.area_type not in self.SESSION_BUILDER_MAPPING:
            return settings.V1_URL
        return f'{base_url}?{self.SESSION_BUILDER_MAPPING[self.area_type]}={self.name}'
