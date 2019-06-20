from random import sample

from django.contrib.gis.db import models
from django.db.models import Q, Count, Prefetch, Value, IntegerField

from sortedm2m.fields import SortedManyToManyField

from data.models import Officer, AttachmentFile, OfficerAllegation, Allegation
from data.models.common import TimeStampsModel
from pinboard.fields import HexField


class Pinboard(TimeStampsModel):
    id = HexField(hex_length=8, primary_key=True)
    title = models.CharField(max_length=255, default='', blank=True)
    officers = SortedManyToManyField('data.Officer')
    allegations = SortedManyToManyField('data.Allegation')
    trrs = SortedManyToManyField('trr.TRR')
    description = models.TextField(default='', blank=True)

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

    def clone(self):
        new_pinboard = Pinboard()
        new_pinboard.title = self.title
        new_pinboard.description = self.description
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
                to_attr='prefetch_officer_allegations'
            )
        )

    @property
    def relevant_documents(self):
        officer_ids = self.officers.all().values_list('id', flat=True)
        crids = self.allegations.all().values_list('crid', flat=True)
        via_allegation = self.relevant_documents_query(allegation__in=crids)
        via_officer = self.relevant_documents_query(allegation__officerallegation__officer__in=officer_ids)
        via_investigator = self.relevant_documents_query(
            allegation__investigatorallegation__investigator__officer__in=officer_ids
        )
        via_police_witnesses = self.relevant_documents_query(allegation__police_witnesses__in=officer_ids)

        return via_allegation.union(
            via_officer,
            via_investigator,
            via_police_witnesses
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
            'trr_percentile',
            'complaint_percentile',
            'civilian_allegation_percentile',
            'internal_allegation_percentile',
            'resignation_date'
        ]
        via_officer = Officer.objects.filter(
            officerallegation__allegation__officerallegation__officer_id__in=officer_ids
        ).exclude(id__in=officer_ids).only(*columns).annotate(
            sub_coaccusal_count=Count('officerallegation', distinct=True)
        )
        via_allegation = Officer.objects.filter(
            officerallegation__allegation__in=crids
        ).exclude(id__in=officer_ids).only(*columns).annotate(
            sub_coaccusal_count=Count('officerallegation', distinct=True)
        )
        via_trr = Officer.objects.filter(
            id__in=trr_officer_ids
        ).exclude(id__in=officer_ids).only(*columns).annotate(
            sub_coaccusal_count=Value(1, output_field=IntegerField())
        )
        sub_query = via_officer.union(via_allegation, all=True).union(via_trr, all=True)

        select_columns = ', '.join([f'"{col}"' for col in columns])
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
            'point'
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
                to_attr='prefetch_officer_allegations'
            )
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
