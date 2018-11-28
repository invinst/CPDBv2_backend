from operator import itemgetter

from django.db.models import Q, Subquery, OuterRef
from django.db.models.functions import TruncDate

from data.models import OfficerHistory, Salary, Officer
from officers.serializers.response_serializers import (
    CRNewTimelineSerializer,
    JoinedNewTimelineSerializer,
    UnitChangeNewTimelineSerializer,
    RankChangeNewTimelineSerializer,
    AwardNewTimelineSerializer,
    TRRNewTimelineSerializer
)
from officers.serializers.response_mobile_serializers import (
    CRNewTimelineMobileSerializer,
    JoinedNewTimelineMobileSerializer,
    UnitChangeNewTimelineMobileSerializer,
    RankChangeNewTimelineMobileSerializer,
    AwardNewTimelineMobileSerializer,
    TRRNewTimelineMobileSerializer
)


class OfficerTimelineBaseQuery(object):
    cr_new_timeline_serializer = None
    unit_change_new_timeline_serializer = None
    rank_change_new_timeline_serializer = None
    joined_new_timeline_serializer = None
    award_new_timeline_serializer = None
    trr_new_timeline_serializer = None

    def __init__(self, officer):
        self.officer = officer

    def unit_subqueries(self, outer_ref_field):
        return {
            'unit_name': Subquery(
                OfficerHistory.objects.filter(officer_id=self.officer.id).filter(
                    Q(effective_date__lte=OuterRef(outer_ref_field)) | Q(effective_date__isnull=True),
                    Q(end_date__gte=OuterRef(outer_ref_field)) | Q(end_date__isnull=True)
                ).order_by('effective_date').values('unit__unit_name')[:1]
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
                Salary.objects.filter(
                    officer_id=self.officer.id,
                    rank_changed=True,
                    spp_date__lte=OuterRef(outer_ref_field),
                ).order_by('-year', '-spp_date').values('rank')[:1]
            )
        }

    @property
    def _cr_timeline(self):
        cr_timeline_queryset = self.officer.officerallegation_set.filter(
            allegation__incident_date__isnull=False,
        ).select_related(
            'allegation', 'allegation_category'
        ).prefetch_related(
            'allegation__victims', 'allegation__attachment_files'
        ).annotate(
            **self.unit_subqueries('allegation__incident_date')
        ).annotate(
            **self.rank_subquery('allegation__incident_date')
        )

        return self.cr_new_timeline_serializer(cr_timeline_queryset, many=True).data

    @property
    def _unit_change_timeline(self):
        unit_change_timeline_queryset = self.officer.officerhistory_set.filter(
            effective_date__isnull=False,
        ).exclude(
            effective_date=self.officer.appointed_date
        ).order_by('effective_date').select_related('unit').annotate(
            **self.rank_subquery('effective_date')
        )

        return self.unit_change_new_timeline_serializer(
            unit_change_timeline_queryset,
            many=True
        ).data

    @property
    def _rank_change_timeline(self):
        salary_timeline = self.officer.salary_set.filter(
            rank_changed=True
        ).exclude(
            spp_date=self.officer.appointed_date
        ).order_by('year').annotate(
            **self.unit_subqueries('spp_date')
        )

        return self.rank_change_new_timeline_serializer(
            salary_timeline, many=True
        ).data

    @property
    def _join_timeline(self):
        if self.officer.appointed_date:
            joined_timeline_query = Officer.objects.filter(id=self.officer.id).annotate(
                **self.unit_subqueries('appointed_date')
            ).annotate(
                **self.rank_subquery('appointed_date')
            )[:1]
            return self.joined_new_timeline_serializer(joined_timeline_query, many=True).data
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
        return self.award_new_timeline_serializer(award_timeline_queryset, many=True).data

    @property
    def _trr_timeline(self):
        trr_timeline_queryset = self.officer.trr_set.all().annotate(
            trr_date=TruncDate('trr_datetime')
        ).annotate(
            **self.unit_subqueries('trr_date')
        ).annotate(
            **self.rank_subquery('trr_date')
        )
        return self.trr_new_timeline_serializer(trr_timeline_queryset, many=True).data

    def execute(self):
        timeline = self._cr_timeline + self._unit_change_timeline + self._rank_change_timeline + \
                   self._join_timeline + self._award_timeline + self._trr_timeline
        sorted_timeline = sorted(timeline, key=itemgetter('date_sort', 'priority_sort'), reverse=True)

        for item in sorted_timeline:
            for key in ['date_sort', 'priority_sort']:
                item.pop(key, None)
        return sorted_timeline


class OfficerTimelineQuery(OfficerTimelineBaseQuery):
    cr_new_timeline_serializer = CRNewTimelineSerializer
    unit_change_new_timeline_serializer = UnitChangeNewTimelineSerializer
    rank_change_new_timeline_serializer = RankChangeNewTimelineSerializer
    joined_new_timeline_serializer = JoinedNewTimelineSerializer
    award_new_timeline_serializer = AwardNewTimelineSerializer
    trr_new_timeline_serializer = TRRNewTimelineSerializer


class OfficerTimelineMobileQuery(OfficerTimelineBaseQuery):
    cr_new_timeline_serializer = CRNewTimelineMobileSerializer
    unit_change_new_timeline_serializer = UnitChangeNewTimelineMobileSerializer
    rank_change_new_timeline_serializer = RankChangeNewTimelineMobileSerializer
    joined_new_timeline_serializer = JoinedNewTimelineMobileSerializer
    award_new_timeline_serializer = AwardNewTimelineMobileSerializer
    trr_new_timeline_serializer = TRRNewTimelineMobileSerializer
