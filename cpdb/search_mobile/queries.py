from data.models import Allegation

from search.queries import OfficerQuery, CrQuery, TrrQuery, LawsuitQuery


class OfficerMobileQuery(OfficerQuery):
    pass


class CrMobileQuery(CrQuery):
    def queryset(self):
        return Allegation.objects.select_related('most_common_category')


class TrrMobileQuery(TrrQuery):
    pass


class LawsuitMobileQuery(LawsuitQuery):
    pass
