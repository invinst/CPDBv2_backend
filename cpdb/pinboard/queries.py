from django.db.models import Count, Q, F

from data.models import Allegation, OfficerAllegation, Complainant
from trr.models import ActionResponse


DISPLAYED_RACES = ['Black', 'White', 'Hispanic']
DISPLAYED_GENDERS = ['M', 'F']


class BaseSummaryQuery(object):
    def __init__(self, pinboard):
        self.pinboard = pinboard

    def _calculate_percentage(self, data):
        total_count = sum([item['count'] for item in data])
        result = [{**item, 'percentage': round(item['count'] / total_count, 2)} for item in data]
        for item in result:
            del item['count']
        return result

    def _group_race_data(self, data):
        return self._group_geographic_data(data, DISPLAYED_RACES, 'Other', 'race')

    def _group_gender_data(self, data):
        return self._group_geographic_data(data, DISPLAYED_GENDERS, 'Unknown', 'gender')

    def _group_geographic_data(self, data, display_names, other_name, name_key):
        if not data:
            return []
        all_item_names = display_names + [other_name]
        result = {name: 0 for name in all_item_names}
        for item in data:
            if not item[name_key] in display_names:
                result[other_name] += item['count']
            else:
                result[item[name_key]] += item['count']
        return [{name_key: name, 'count': result[name]} for name in all_item_names]

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
        race_count = self.pinboard.all_officers.values('race').annotate(count=Count('id'))
        gender_count = self.pinboard.all_officers.values('gender').annotate(count=Count('id')).order_by('-count')
        return {
            'race': self._calculate_percentage(self._group_race_data(race_count)),
            'gender': self._calculate_percentage(self._group_gender_data(gender_count))
        }


class ComplainantsSummaryQuery(BaseSummaryQuery):
    def all_allegation_ids(self):
        return Allegation.objects.filter(
            Q(crid__in=self.pinboard.crids) |
            Q(officerallegation__officer_id__in=list(self.pinboard.all_officer_ids))
        ).distinct().values_list('crid', flat=True)

    def query(self):
        all_complainants = Complainant.objects.filter(allegation_id__in=self.all_allegation_ids())
        race_count = all_complainants.values('race').annotate(count=Count('id'))
        gender_count = all_complainants.values('gender').annotate(count=Count('id')).order_by('-count')
        return {
            'race': self._calculate_percentage(self._group_race_data(race_count)),
            'gender': self._calculate_percentage(self._group_gender_data(gender_count))
        }
