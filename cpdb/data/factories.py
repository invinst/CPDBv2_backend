from django.contrib.gis.geos import MultiPolygon, Polygon, MultiLineString, LineString

import factory
from faker import Faker

from data.models import Area, Investigator, LineArea

fake = Faker()


class AreaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Area

    name = factory.LazyFunction(lambda: fake.word())
    area_type = 'school-grounds'
    polygon = factory.LazyFunction(lambda: MultiPolygon(Polygon((
        (87.940101, 42.023135),
        (87.523661, 42.023135),
        (87.523661, 41.644286),
        (87.940101, 41.644286),
        (87.940101, 42.023135)))))


class LineAreaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = LineArea

    name = factory.LazyFunction(lambda: fake.word())
    linearea_type = 'passageway'
    geom = factory.LazyFunction(lambda: MultiLineString(
        LineString(
            (-87.6543545842184386, 41.7741537537218477),
            (-87.6543453548284504, 41.7738192794681069)
        )
    ))


class InvestigatorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Investigator
        django_get_or_create = ('name',)

    name = factory.LazyFunction(lambda: fake.name())
    raw_name = factory.LazyAttribute(lambda o: o.name.upper())
    current_rank = factory.LazyFunction(lambda: fake.word())