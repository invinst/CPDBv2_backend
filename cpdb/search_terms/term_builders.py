import urllib

from django.conf import settings

from data.models import Area, Officer, PoliceUnit
from data import constants as data_constants


_term_builders = dict()


def _register_term_builder(klass):
    _term_builders[klass.slug] = klass
    return klass


def get_term_builders(key):
    return _term_builders[key]


class AreaTermBuilder:
    @classmethod
    def build_terms(cls):
        return [
            {
                'name': area.name,
                'link': '%s/url-mediator/session-builder?%s' % (
                    settings.V1_URL,
                    urllib.urlencode({cls.query_key: area.name})
                )
            }
            for area in Area.objects.filter(area_type=cls.slug)
        ]


@_register_term_builder
class PoliceDistrictsTermBuilder(AreaTermBuilder):
    slug = data_constants.POLICE_DISTRICTS_AREA_CHOICE
    query_key = 'police_district'


@_register_term_builder
class CommunitiesTermBuilder(AreaTermBuilder):
    slug = data_constants.COMMUNITY_AREA_CHOICE
    query_key = 'community'


@_register_term_builder
class NeighborhoodsTermBuilder(AreaTermBuilder):
    slug = data_constants.NEIGHBORHOODS_AREA_CHOICE
    query_key = 'neighborhood'


@_register_term_builder
class PoliceBeatTermBuilder(AreaTermBuilder):
    slug = data_constants.POLICE_BEATS_AREA_CHOICE
    query_key = 'beat'


@_register_term_builder
class SchoolGroundsTermBuilder(AreaTermBuilder):
    slug = data_constants.SCHOOL_GROUNDS_AREA_CHOICE
    query_key = 'school_ground'


@_register_term_builder
class WardsTermBuilder(AreaTermBuilder):
    slug = data_constants.WARDS_AREA_CHOICE
    query_key = 'ward'


@_register_term_builder
class OfficerRankTermBuilder:
    slug = 'officer-rank'

    @classmethod
    def build_terms(cls):
        return [
            {
                'name': rank,
                'link': '%s/url-mediator/session-builder?%s' % (
                    settings.V1_URL,
                    urllib.urlencode({'officer__rank': rank})
                )
            }
            for rank in Officer.objects.values_list('rank', flat=True).distinct()
        ]


@_register_term_builder
class PoliceUnitTermBuilder:
    slug = 'officer-unit'

    @classmethod
    def build_terms(cls):
        return [
            {
                'name': description,
                'link': '%s/url-mediator/session-builder?%s' % (
                    settings.V1_URL,
                    urllib.urlencode({'officer__unit': unit_name})
                )
            }
            for (unit_name, description) in PoliceUnit.objects.values_list('unit_name', 'description')
        ]
