import re
from random import sample

from django.contrib.gis.db import models
from django.db.models import Q, Count, Prefetch, Value, IntegerField, F

from sortedm2m.fields import SortedManyToManyField

from data.constants import MEDIA_TYPE_DOCUMENT
from data.models import Officer, AttachmentFile, OfficerAllegation, Allegation
from data.models.common import TimeStampsModel
from pinboard.fields import HexField
from pinboard.constants import PINBOARD_TITLE_DUPLICATE_PATTERN


class AllegationManager(models.Manager):
    def get_complaints_in_pinboard(self, pinboard_id):
        return self.filter(pinboard=pinboard_id).prefetch_related(
            Prefetch(
                'officerallegation_set',
                queryset=OfficerAllegation.objects.select_related('allegation_category').prefetch_related('officer'),
                to_attr='officer_allegations')
            )


class ProxyAllegation(Allegation):
    objects = AllegationManager()

    class Meta:
        proxy = True


class Pinboard(TimeStampsModel):
    id = HexField(hex_length=8, primary_key=True)
    title = models.CharField(max_length=255, default='', blank=True)
    officers = SortedManyToManyField('data.Officer')
    allegations = SortedManyToManyField('data.Allegation')
    trrs = SortedManyToManyField('trr.TRR')
    description = models.TextField(default='', blank=True)
    source_pinboard = models.ForeignKey(
        'pinboard.Pinboard', on_delete=models.SET_NULL, null=True, related_name='child_pinboards'
    )

    def __str__(self):
        return f'{self.id} - {self.title}' if self.title else self.id

    @property
    def is_empty(self):
        return not any([self.officers.exists(), self.allegations.exists(), self.trrs.exists()])

    @property
    def example_pinboards(self):
        if self.is_empty:
            return ExamplePinboard.random(2)
        else:
            return None

    @property
    def all_officers(self):
        allegation_ids = self.allegations.all().values_list('crid', flat=True)
        trr_ids = self.trrs.all().values_list('id', flat=True)
        return Officer.objects.filter(
            Q(officerallegation__allegation_id__in=allegation_ids) |
            Q(trr__id__in=trr_ids) |
            Q(pinboard__id=self.id)
        ).order_by('first_name', 'last_name').distinct()

    def clone(self, is_duplicated=False):
        new_pinboard = Pinboard()
        if is_duplicated:
            match = re.match(PINBOARD_TITLE_DUPLICATE_PATTERN, self.title)
            if match:
                copy_suffix = int(match.group(2)) + 1 if match.group(2) else 2
                new_pinboard.title = f'{match.group(1)} copy {copy_suffix}'
            else:
                new_pinboard.title = f'{self.title} copy'
        else:
            new_pinboard.title = self.title
        new_pinboard.description = self.description
        new_pinboard.source_pinboard = self
        new_pinboard.save()

        new_pinboard.officers.set(self.officers.all())
        new_pinboard.allegations.set(self.allegations.all())
        new_pinboard.trrs.set(self.trrs.all())

        return new_pinboard

    @property
    def officer_ids(self):
        return self.officers.values_list('id', flat=True)

    @property
    def crids(self):
        return self.allegations.values_list('crid', flat=True)

    @property
    def trr_ids(self):
        return self.trrs.values_list('id', flat=True)

    def relevant_documents_query(self, **kwargs):
        return AttachmentFile.showing.filter(
            file_type=MEDIA_TYPE_DOCUMENT,
            **kwargs
        ).only(
            'id',
            'preview_image_url',
            'url',
            'allegation',
        ).select_related(
            'allegation',
            'allegation__most_common_category',
        ).prefetch_related(
            Prefetch(
                'allegation__officerallegation_set',
                queryset=OfficerAllegation.objects.select_related('officer').order_by('-officer__allegation_count'),
                to_attr='prefetched_officer_allegations'
            ),
            'allegation__victims'
        )

    @property
    def relevant_documents(self):
        officer_ids = self.officers.all().values_list('id', flat=True)
        crids = self.allegations.all().values_list('crid', flat=True)
        via_allegation = self.relevant_documents_query(allegation__in=crids)
        via_officer = self.relevant_documents_query(allegation__officerallegation__officer__in=officer_ids)

        return via_allegation.union(
            via_officer,
        ).distinct().order_by('-allegation__incident_date')

    @property
    def relevant_coaccusals(self):
        officer_ids = self.officers.all().values_list('id', flat=True)
        crids = self.allegations.all().values_list('crid', flat=True)
        trr_officer_ids = self.trrs.all().values_list('officer_id', flat=True).distinct()

        columns = [
            'id',
            'rank',
            'first_name',
            'last_name',
            'appointed_date',
            'resignation_date',
            'current_badge',
            'gender',
            'birth_year',
            'race',
            'rank',
            'trr_percentile',
            'complaint_percentile',
            'civilian_allegation_percentile',
            'internal_allegation_percentile',
            'allegation_count',
            'sustained_count',
            'discipline_count',
            'trr_count',
            'major_award_count',
            'honorable_mention_count',
            'honorable_mention_percentile',
            'last_unit_id',
            'civilian_compliment_count'
        ]

        related_renamed_columns = (
            ('unit_id', 'last_unit__id'),
            ('unit_name', 'last_unit__unit_name'),
            ('unit_description', 'last_unit__description')
        )

        content_columns = columns + [col[1] for col in related_renamed_columns]
        officer_qs = Officer.objects.annotate(**{
            annotated_column: F(column) for annotated_column, column in related_renamed_columns
        })

        via_officer = officer_qs.filter(
            officerallegation__allegation__officerallegation__officer_id__in=officer_ids
        ).exclude(id__in=officer_ids).only(*content_columns).annotate(
            sub_coaccusal_count=Count('officerallegation', distinct=True)
        )

        via_allegation = officer_qs.filter(
            officerallegation__allegation__in=crids
        ).exclude(id__in=officer_ids).only(*content_columns).annotate(
            sub_coaccusal_count=Count('officerallegation', distinct=True)
        )

        via_trr = officer_qs.filter(
            id__in=trr_officer_ids
        ).exclude(id__in=officer_ids).only(*content_columns).annotate(
            sub_coaccusal_count=Value(1, output_field=IntegerField())
        )
        sub_query = via_officer.union(via_allegation, all=True).union(via_trr, all=True)

        select_columns = ', '.join(
            [f'"{col}"' for col in columns] +
            [f'"{col[0]}"' for col in related_renamed_columns]
        )

        raw_query = f'''
            WITH cte AS ({sub_query.query})
            SELECT {select_columns},
                SUM("sub_coaccusal_count") "coaccusal_count"
            FROM cte
            GROUP BY {select_columns}
            ORDER BY "coaccusal_count" DESC
        '''
        query = Officer.objects.raw(raw_query)
        return query

    def relevant_complaints_query(self, **kwargs):
        crids = self.allegations.all().values_list('crid', flat=True)
        return Allegation.objects.filter(**kwargs).exclude(crid__in=crids).only(
            'crid',
            'incident_date',
            'most_common_category',
            'point',
            'old_complaint_address',
            'add1',
            'add2',
            'city'
        ).select_related(
            'most_common_category',
        ).prefetch_related(
            Prefetch(
                'officerallegation_set',
                queryset=OfficerAllegation.objects.select_related(
                    'officer'
                ).order_by(
                    '-officer__allegation_count'
                ),
                to_attr='prefetched_officer_allegations'
            ),
            'victims'
        )

    def relevant_complaints_count_query(self, **kwargs):
        crids = self.allegations.all().values_list('crid', flat=True)
        return Allegation.objects.filter(**kwargs).exclude(crid__in=crids).only('crid')

    @property
    def relevant_complaints_count(self):
        officer_ids = self.officers.all().values_list('id', flat=True)
        via_officer = self.relevant_complaints_count_query(
            officerallegation__officer__in=officer_ids
        )
        via_investigator = self.relevant_complaints_count_query(
            investigatorallegation__investigator__officer__in=officer_ids
        )
        via_police_witness = self.relevant_complaints_count_query(
            police_witnesses__in=officer_ids
        )
        return via_officer.union(via_investigator, via_police_witness).distinct().count

    @property
    def relevant_complaints(self):
        officer_ids = self.officers.all().values_list('id', flat=True)
        via_officer = self.relevant_complaints_query(
            officerallegation__officer__in=officer_ids
        )
        via_investigator = self.relevant_complaints_query(
            investigatorallegation__investigator__officer__in=officer_ids
        )
        via_police_witness = self.relevant_complaints_query(
            police_witnesses__in=officer_ids
        )
        query = via_officer.union(via_investigator, via_police_witness).distinct().order_by('-incident_date')
        # LimitOffsetPagination need count and we optimize it with a more simple query
        setattr(query, 'count', self.relevant_complaints_count)
        return query


class ExamplePinboard(TimeStampsModel):
    pinboard = models.OneToOneField(Pinboard, primary_key=True, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.pinboard)

    @classmethod
    def random(cls, n):
        return sample(list(cls.objects.all()), min(cls.objects.count(), n))
