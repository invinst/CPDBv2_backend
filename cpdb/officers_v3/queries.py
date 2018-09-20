from itertools import groupby
from operator import attrgetter, itemgetter

from django.db.models import Q, Subquery, OuterRef

from data.models import OfficerHistory, Salary, Officer
from officers_v3.seriallizers.respone_serialiers import (
    CRNewTimelineSerializer,
    JoinedNewTimelineSerializer,
    UnitChangeNewTimelineSerializer,
    RankChangeNewTimelineSerializer,
    AwardNewTimelineSerializer,
    TRRNewTimelineSerializer
)


class OfficerTimeline:
    def __init__(self, officer):
        self.officer = officer

    def unit_subqueries(self, outer_ref_field):
        return {
            'unit_name': Subquery(
                OfficerHistory.objects.filter(officer_id=self.officer.id).filter(
                    Q(effective_date__lte=OuterRef(outer_ref_field)) | Q(effective_date__isnull=True),
                    Q(end_date__gte=OuterRef(outer_ref_field)) | Q(end_date__isnull=True)
                ).values('unit__unit_name')[:1]
            ),
            'unit_description': Subquery(
                OfficerHistory.objects.filter(officer_id=self.officer.id).filter(
                    Q(effective_date__lte=OuterRef(outer_ref_field)) | Q(effective_date__isnull=True),
                    Q(end_date__gte=OuterRef(outer_ref_field)) | Q(end_date__isnull=True)
                ).values('unit__description')[:1]
            )
        }

    def rank_subquery(self, outer_ref_field):
        return {
            'rank_name': Subquery(
                Salary.objects.filter(officer_id=self.officer.id, spp_date__isnull=False).filter(
                    spp_date__lte=OuterRef(outer_ref_field),
                ).order_by('-year', '-spp_date').values('rank')[:1]
            )
        }

    @property
    def _cr_timeline(self):
        cr_timeline_queryset = self.officer.officerallegation_set.filter(
            start_date__isnull=False,
        ).select_related(
            'allegation', 'allegation_category'
        ).prefetch_related(
            'allegation__victims', 'allegation__attachment_files'
        ).annotate(
            **self.unit_subqueries('start_date')
        ).annotate(
            **self.rank_subquery('start_date')
        )

        return CRNewTimelineSerializer(cr_timeline_queryset, many=True).data

    @property
    def _unit_change_timeline(self):
        unit_change_timeline_queryset = self.officer.officerhistory_set.filter(
            effective_date__isnull=False,
        ).exclude(
            effective_date=self.officer.appointed_date
        ).order_by('effective_date').select_related('unit').annotate(
            **self.rank_subquery('effective_date')
        )

        return UnitChangeNewTimelineSerializer(
            unit_change_timeline_queryset,
            many=True
        ).data

    @property
    def _rank_change_timeline(self):
        salary_timeline_queryset = self.officer.salary_set.exclude(
            spp_date__isnull=True
        ).order_by('year').annotate(
            **self.unit_subqueries('spp_date')
        )
        salary_timeline = [
            salaries.next()
            for _, salaries in groupby(salary_timeline_queryset, key=attrgetter('rank'))
        ]

        return RankChangeNewTimelineSerializer(
            [salary for salary in salary_timeline if salary.spp_date != self.officer.appointed_date],
            many=True
        ).data

    @property
    def _join_timeline(self):
        if self.officer.appointed_date:
            joined_timeline_query = Officer.objects.filter(id=self.officer.id).annotate(
                **self.unit_subqueries('appointed_date')
            ).annotate(
                **self.rank_subquery('appointed_date')
            )[:1]
            return JoinedNewTimelineSerializer(joined_timeline_query, many=True).data
        else:
            return []

    @property
    def _award_timeline(self):
        award_timeline_queryset = self.officer.award_set.filter(
            Q(start_date__isnull=False),
            ~Q(award_type__contains='Honorable Mention'),
            ~Q(award_type__in=['Complimentary Letter', 'Department Commendation'])
        ).annotate(
            **self.unit_subqueries('start_date')
        ).annotate(
            **self.rank_subquery('start_date')
        )
        return AwardNewTimelineSerializer(award_timeline_queryset, many=True).data

    @property
    def _trr_timeline(self):
        trr_timeline_queryset = self.officer.trr_set.all().annotate(
            **self.unit_subqueries('trr_datetime')
        ).annotate(
            **self.rank_subquery('trr_datetime')
        )
        return TRRNewTimelineSerializer(trr_timeline_queryset, many=True).data

    def __iter__(self):
        timeline = self._cr_timeline + self._unit_change_timeline + self._rank_change_timeline + \
                   self._join_timeline + self._award_timeline + self._trr_timeline
        sorted_timeline = sorted(timeline, key=itemgetter('date_sort', 'priority_sort'), reverse=True)

        for item in sorted_timeline:
            for key in ['officer_id', 'date_sort', 'priority_sort']:
                item.pop(key, None)
        return iter(sorted_timeline)
