import json
from datetime import datetime
from itertools import groupby

import botocore
from django.apps import apps
from django.conf import settings
from django.contrib.gis.db import models
from django.db.models import Q, Count
from django.db.models.functions import ExtractYear
from django.utils import timezone
from django.utils.text import slugify
from django_bulk_update.manager import BulkUpdateManager

from data.constants import (
    ACTIVE_CHOICES,
    ACTIVE_UNKNOWN_CHOICE,
    GENDER_DICT,
    BACKGROUND_COLOR_SCHEME,
    ACTIVE_YES_CHOICE,
)
from shared.aws import aws
from xlsx.constants import XLSX_FILE_NAMES
from .common import TaggableModel
from data.utils.aggregation import get_num_range_case
from data.utils.interpolate import ScaleThreshold
from data.validators import validate_race
from .common import TimeStampsModel


class Officer(TimeStampsModel, TaggableModel):
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

    # CACHED COLUMNS
    complaint_percentile = models.DecimalField(max_digits=6, decimal_places=4, null=True)
    civilian_allegation_percentile = models.DecimalField(max_digits=6, decimal_places=4, null=True)
    internal_allegation_percentile = models.DecimalField(max_digits=6, decimal_places=4, null=True)
    trr_percentile = models.DecimalField(max_digits=6, decimal_places=4, null=True)
    honorable_mention_percentile = models.DecimalField(max_digits=6, decimal_places=4, null=True)
    allegation_count = models.IntegerField(default=0, null=True)
    sustained_count = models.IntegerField(default=0, null=True)
    honorable_mention_count = models.IntegerField(default=0, null=True)
    unsustained_count = models.IntegerField(default=0, null=True)
    discipline_count = models.IntegerField(default=0, null=True)
    civilian_compliment_count = models.IntegerField(default=0, null=True)
    trr_count = models.IntegerField(default=0, null=True)
    major_award_count = models.IntegerField(default=0, null=True)
    current_badge = models.CharField(max_length=10, null=True)
    last_unit = models.ForeignKey('data.PoliceUnit', on_delete=models.SET_NULL, null=True)
    current_salary = models.PositiveIntegerField(null=True)
    has_unique_name = models.BooleanField(default=False)

    objects = BulkUpdateManager()

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def historic_badges(self):
        # old not current badge
        return self.officerbadgenumber_set.exclude(current=True).values_list('star', flat=True)

    @property
    def historic_units(self):
        return [o.unit for o in self.officerhistory_set.all().select_related('unit').order_by('-effective_date')]

    @property
    def gender_display(self):
        try:
            return GENDER_DICT[self.gender]
        except KeyError:
            return self.gender

    @property
    def v1_url(self):
        return f'{settings.V1_URL}/officer/{slugify(self.full_name)}/{self.pk}'

    @property
    def current_age(self):
        return timezone.localtime(timezone.now()).year - self.birth_year

    @property
    def v2_to(self):
        return f'/officer/{self.pk}/{slugify(self.full_name)}/'

    def get_absolute_url(self):
        return f'/officer/{self.pk}/'

    @property
    def abbr_name(self):
        return f'{self.first_name[0].upper()}. {self.last_name}'

    @property
    def visual_token_background_color(self):
        cr_scale = ScaleThreshold(domain=[1, 5, 10, 25, 40], target_range=range(6))

        cr_threshold = cr_scale.interpolate(self.allegation_count)

        return BACKGROUND_COLOR_SCHEME[f'{cr_threshold}0']

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
    def coaccusals(self):
        return Officer.objects.filter(
            officerallegation__allegation__officerallegation__officer=self
        ).distinct().exclude(id=self.id).annotate(coaccusal_count=Count('id')).order_by('-coaccusal_count')

    @property
    def rank_histories(self):
        salaries = self.salary_set.exclude(spp_date__isnull=True).order_by('year')
        try:
            first_salary = salaries[0]
        except IndexError:
            return []
        current_rank = first_salary.rank
        rank_histories = [{'date': first_salary.spp_date, 'rank': first_salary.rank}]
        for salary in salaries:
            if salary.rank != current_rank:
                rank_histories.append({'date': salary.spp_date, 'rank': salary.rank})
                current_rank = salary.rank
        return rank_histories

    def get_rank_by_date(self, query_date):
        if query_date is None:
            return None

        if type(query_date) is datetime:
            query_date = query_date.date()
        rank_histories = self.rank_histories

        try:
            first_history = rank_histories[0]
        except IndexError:
            return None

        last_history = rank_histories[len(rank_histories)-1]
        if query_date < first_history['date']:
            return None
        if query_date >= last_history['date']:
            return last_history['rank']
        for i in range(len(rank_histories)):
            if query_date < rank_histories[i]['date']:
                return rank_histories[i-1]['rank']
            if query_date == rank_histories[i]['date']:
                return rank_histories[i]['rank']

    @classmethod
    def get_active_officers(cls, rank):
        return cls.objects.filter(rank=rank, active=ACTIVE_YES_CHOICE)

    @classmethod
    def get_officers_most_complaints(cls, rank):
        return cls.objects.filter(rank=rank).exclude(allegation_count=0).order_by('-allegation_count')[:3]

    @property
    def allegation_attachments(self):
        AttachmentFile = apps.get_app_config('data').get_model('AttachmentFile')
        return AttachmentFile.objects.filter(
            allegation__officerallegation__officer=self,
            source_type__in=['DOCUMENTCLOUD', 'COPA_DOCUMENTCLOUD']
        ).distinct('id')

    @property
    def investigator_attachments(self):
        AttachmentFile = apps.get_app_config('data').get_model('AttachmentFile')
        return AttachmentFile.objects.filter(
            allegation__investigatorallegation__investigator__officer=self,
            source_type__in=['DOCUMENTCLOUD', 'COPA_DOCUMENTCLOUD']
        ).distinct('id')

    def get_zip_filename(self, with_docs):
        if with_docs:
            return f'{settings.S3_BUCKET_ZIP_DIRECTORY}_with_docs/Officer_{self.id}_with_docs.zip'
        return f'{settings.S3_BUCKET_ZIP_DIRECTORY}/Officer_{self.id}.zip'

    def check_zip_file_exist(self, with_docs):
        try:
            aws.s3.get_object(
                Bucket=settings.S3_BUCKET_OFFICER_CONTENT,
                Key=self.get_zip_filename(with_docs)
            )
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                return False
            raise e
        else:
            return True

    def invoke_create_zip(self, with_docs):
        if not self.check_zip_file_exist(with_docs):
            zip_key = self.get_zip_filename(with_docs=with_docs)
            if with_docs:
                allegation_attachments_map = {
                    f'{settings.S3_BUCKET_PDF_DIRECTORY}/{attachment.external_id}':
                        f'documents/{attachment.title}.pdf'
                    for attachment in self.allegation_attachments
                }
                investigator_attachments_dict = {
                    f'{settings.S3_BUCKET_PDF_DIRECTORY}/{attachment.external_id}':
                        f'investigators/{attachment.title}.pdf'
                    for attachment in self.investigator_attachments
                }
            else:
                allegation_attachments_map = {}
                investigator_attachments_dict = {}

            xlsx_map = {
                f'{settings.S3_BUCKET_XLSX_DIRECTORY}/{self.id}/{file_name}': file_name
                for file_name in XLSX_FILE_NAMES
            }

            aws.lambda_client.invoke_async(
                FunctionName='createOfficerZipFile',
                InvokeArgs=json.dumps(
                    {
                        'key': zip_key,
                        'bucket': settings.S3_BUCKET_OFFICER_CONTENT,
                        'file_map': {**xlsx_map, **allegation_attachments_map, **investigator_attachments_dict}
                    }
                )
            )

    def generate_presigned_zip_url(self, with_docs):
        zip_key = self.get_zip_filename(with_docs=with_docs)
        return aws.s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': settings.S3_BUCKET_OFFICER_CONTENT,
                'Key': zip_key,
            }
        )
