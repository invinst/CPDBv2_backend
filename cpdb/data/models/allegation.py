from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField
from django_bulk_update.manager import BulkUpdateManager

from data.constants import GENDER_DICT, MEDIA_TYPE_DOCUMENT, MEDIA_IPRA_COPA_HIDING_TAGS
from data.utils.aggregation import get_num_range_case
from .common import TimeStampsModel


class Allegation(TimeStampsModel):
    crid = models.CharField(max_length=30, primary_key=True)
    summary = models.TextField(blank=True)
    location = models.CharField(max_length=64, blank=True)
    add1 = models.CharField(max_length=16, blank=True)
    add2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)
    incident_date = models.DateTimeField(null=True)
    areas = models.ManyToManyField('data.Area')
    line_areas = models.ManyToManyField('data.LineArea')
    point = models.PointField(srid=4326, null=True)
    beat = models.ForeignKey('data.Area', on_delete=models.SET_NULL, null=True, related_name='beats')
    source = models.CharField(blank=True, max_length=20)
    is_officer_complaint = models.BooleanField(default=False)
    old_complaint_address = models.CharField(max_length=255, null=True)
    police_witnesses = models.ManyToManyField('data.Officer', through='PoliceWitness')
    subjects = ArrayField(models.CharField(max_length=255), default=list)

    # CACHED COLUMNS
    most_common_category = models.ForeignKey('data.AllegationCategory', on_delete=models.SET_NULL, null=True)
    first_start_date = models.DateField(null=True)
    first_end_date = models.DateField(null=True)
    coaccused_count = models.IntegerField(default=0, null=True)

    objects = BulkUpdateManager()

    @property
    def category_names(self):
        query = self.officer_allegations.annotate(
            name=models.Case(
                models.When(allegation_category__isnull=True, then=models.Value('Unknown')),
                default='allegation_category__category',
                output_field=models.CharField()))
        query = query.values('name').distinct()
        results = sorted([result['name'] for result in query])
        return results if results else ['Unknown']

    @property
    def address(self):
        if self.old_complaint_address:
            return self.old_complaint_address
        result = ''
        add1 = self.add1.strip()
        add2 = self.add2.strip()
        city = self.city.strip()
        if add1:
            result = add1
        if add2:
            result = ' '.join(filter(None, [result, add2]))
        if city:
            result = ', '.join(filter(None, [result, city]))
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
        results = sorted([result['name'] for result in query])
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
    def documents(self):
        return self.attachment_files.filter(file_type=MEDIA_TYPE_DOCUMENT)

    @property
    def filtered_attachment_files(self):
        # Due to the privacy issue with the data that was posted on the IPRA / COPA data portal
        # We need to hide those documents
        return self.attachment_files.exclude(tag__in=MEDIA_IPRA_COPA_HIDING_TAGS)

    @property
    def v2_to(self):
        if self.officerallegation_set.count() == 0:
            return f'/complaint/{self.crid}/'

        officer_allegations = self.officerallegation_set.filter(officer__isnull=False)

        if officer_allegations.count() == 0:
            return f'/complaint/{self.crid}/'

        return f'/complaint/{self.crid}/{officer_allegations.first().officer.pk}/'
