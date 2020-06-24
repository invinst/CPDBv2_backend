from django.db.models import Count, Q, F

from data.models import Allegation, OfficerAllegation, Complainant
from trr.models import ActionResponse


class BaseSummaryQuery(object):
    def __init__(self, pinboard):
        self.pinboard = pinboard

    def _calculate_percentage(self, data):
        total_count = sum([item['count'] for item in data])
        result = [{**item, 'percentage': round(item['count'] / total_count, 2)} for item in data]
        for item in result:
            del item['count']
        return result

    def query(self):
        raise NotImplementedError


class ComplaintSummaryQuery(BaseSummaryQuery):
    def query(self):
        return OfficerAllegation.objects.filter(
            officer_id__in=self.pinboard.all_officer_ids
        ).annotate(
            category=F('allegation_category__category')
        ).values(
            'category'
        ).annotate(
            count=Count('id', distinct=True)
        ).order_by('-count')


class TrrSummaryQuery(BaseSummaryQuery):
    def query(self):
        return ActionResponse.objects.filter(
            Q(trr_id__in=self.pinboard.trr_ids) | Q(trr__officer_id__in=self.pinboard.all_officer_ids)
        ).values(
            'force_type'
        ).annotate(
            count=Count('id', distinct=True)
        ).order_by('-count')


class OfficersSummaryQuery(BaseSummaryQuery):
    def query(self):
        race_count = self.pinboard.all_officers.values('race').annotate(count=Count('id')).order_by('-count')
        gender_count = self.pinboard.all_officers.values('gender').annotate(count=Count('id')).order_by('-count')
        return {
            'race': self._calculate_percentage(race_count),
            'gender': self._calculate_percentage(gender_count)
        }


class ComplainantsSummaryQuery(BaseSummaryQuery):
    def all_allegation_ids(self):
        return Allegation.objects.filter(
            Q(crid__in=self.pinboard.crids) |
            Q(officerallegation__officer_id__in=list(self.pinboard.all_officer_ids))
        ).distinct().values_list('crid', flat=True)

    def query(self):
        all_complainants = Complainant.objects.filter(allegation_id__in=self.all_allegation_ids())
        race_count = all_complainants.values('race').annotate(count=Count('id')).order_by('-count')
        gender_count = all_complainants.values('gender').annotate(count=Count('id')).order_by('-count')
        return {
            'race': self._calculate_percentage(race_count),
            'gender': self._calculate_percentage(gender_count)
        }
