from datetime import datetime

from django.test.testcases import TestCase
from django.contrib.gis.geos.collections import MultiPolygon, Polygon, MultiLineString, LineString, Point

import pytz
from freezegun import freeze_time

from data.models import Allegation, Area, LineArea
from data.factories import AreaFactory, InvestigatorFactory, LineAreaFactory, InvestigatorAllegationFactory
from data_versioning.models import Changelog, LOG_TYPE_CREATE, LOG_TYPE_UPDATE, LOG_TYPE_DELETE
from data_versioning.changekeepers import PostgreSQLChangeKeeper


class PostgreSQLChangeKeeperTestCase(TestCase):
    changekeeper = PostgreSQLChangeKeeper()

    def __init__(self, *args, **kwargs):
        super(PostgreSQLChangeKeeperTestCase, self).__init__(*args, **kwargs)
        self.maxDiff = None

    def test_create(self):
        area1 = AreaFactory(name='abc')
        area2 = AreaFactory(name='edf')
        allegation_obj = {
            'crid': '123456',
            'incident_date': datetime(1987, 6, 5, 4, 3, 2, tzinfo=pytz.utc),
            'areas': [area1],
            ''
            'beat': area2
        }
        change_source = {
            'name': 'FOIA',
            'azure_blob_storage_id': 'abc123xyz'
        }
        self.assertEqual(Allegation.objects.all().count(), 0)
        with freeze_time('2012-01-14 12:21:34', tz_offset=0):
            self.changekeeper.create(Allegation, source=change_source, content=allegation_obj)
        self.assertEqual(Allegation.objects.all().count(), 1)
        allegation = Allegation.objects.first()
        self.assertEqual(allegation.crid, '123456')
        allegation.areas.get(name='abc')
        self.assertEqual(allegation.beat.name, 'edf')
        self.assertEqual(allegation.incident_date, datetime(1987, 6, 5, 4, 3, 2, tzinfo=pytz.utc))

        self.assertEqual(Changelog.objects.all().count(), 1)
        changelog = Changelog.objects.all()[0]
        self.assertEqual(changelog.created, datetime(2012, 1, 14, 12, 21, 34, tzinfo=pytz.utc))
        self.assertEqual(changelog.object_pk, allegation.pk)
        self.assertEqual(changelog.target_model, 'data.allegation')
        self.assertEqual(changelog.log_type, LOG_TYPE_CREATE)
        self.assertEqual(dict(changelog.content.items()), {
            'crid': '123456',
            'incident_date': '1987-06-05T04:03:02+00:00',
            'areas': [area1.pk],
            'beat': area2.pk
        })
        self.assertEqual(dict(changelog.source.items()), change_source)

    def test_create_with_multipolygon(self):
        self.changekeeper.create(Area, source=dict(), content={
            'polygon': MultiPolygon([Polygon([
                Point(-87.6472903440513420, 41.9777476245163967),
                Point(-87.6488601283914619, 41.9770421499063531),
                Point(-87.6489575350607453, 41.9769610907360757),
                Point(-87.6472903440513420, 41.9777476245163967)
            ])])
        })
        changelog = Changelog.objects.first()
        self.assertEqual(changelog.content['polygon'], (
            'SRID=4326;MULTIPOLYGON (((-87.64729034405134 41.9777476245164, '
            '-87.64886012839146 41.97704214990635, -87.64895753506075 41.97696109073608, '
            '-87.64729034405134 41.9777476245164)))'))

    def test_create_with_multilinestring(self):
        self.changekeeper.create(LineArea, source=dict(), content={
            'geom': MultiLineString([LineString([Point(1, 2), Point(2, 3)])])
            })
        changelog = Changelog.objects.first()
        self.assertEqual(
            changelog.content['geom'],
            'SRID=4326;MULTILINESTRING ((1 2, 2 3))'
        )

    def test_create_with_point(self):
        self.changekeeper.create(Allegation, source=dict(), content={'point': Point(4, 5)})
        changelog = Changelog.objects.first()
        self.assertEqual(
            changelog.content['point'],
            'SRID=4326;POINT (4 5)'
        )

    def test_update(self):
        areas = AreaFactory.create_batch(4)

        allegation = Allegation.objects.create(
            crid='123456',
            incident_date=None,
            beat=areas[1])
        allegation.areas.set([areas[0]])

        change_obj = {
            'incident_date': datetime(2000, 1, 1, 0, 0, 0, tzinfo=pytz.utc),
            'areas': [areas[2]],
            'beat': areas[3]
        }

        self.changekeeper.update(allegation, source=dict(), content=change_obj)

        allegation = Allegation.objects.get(pk=allegation.pk)
        self.assertEqual(allegation.incident_date, datetime(2000, 1, 1, 0, 0, 0, tzinfo=pytz.utc))
        self.assertEqual([area.pk for area in allegation.areas.all()], [areas[2].pk])
        self.assertEqual(allegation.beat, areas[3])

        changelog = Changelog.objects.get()
        self.assertEqual(changelog.target_model, 'data.allegation')
        self.assertEqual(changelog.log_type, LOG_TYPE_UPDATE)
        self.assertEqual(changelog.object_pk, allegation.pk)
        self.assertEqual(dict(changelog.content.items()), {
            'pk': allegation.pk,
            'incident_date': [None, '2000-01-01T00:00:00+00:00'],
            'areas': [[areas[0].pk], [areas[2].pk]],
            'beat': [areas[1].pk, areas[3].pk]
        })

    def test_delete(self):
        areas = AreaFactory.create_batch(3)
        investigator = InvestigatorFactory()
        line_area = LineAreaFactory()
        with freeze_time('2012-01-14 12:21:34', tz_offset=0):
            allegation = Allegation.objects.create(
                crid='456123',
                add1='103',
                beat=areas[0],
                city='abc',
                add2='def',
                location='01',
                point=Point(0, 0),
                source='IPRA',
                summary='lorem ipsum',
                is_officer_complaint=False,
                incident_date=datetime(2000, 1, 1, tzinfo=pytz.utc)
            )

            InvestigatorAllegationFactory(investigator=investigator, allegation=allegation)
            allegation.line_areas.add(line_area)
            allegation.areas.add(*areas[1:])
            allegation.save()

        old_pk = allegation.pk

        self.changekeeper.delete(allegation, source=dict())

        self.assertEqual(Allegation.objects.filter(pk=allegation.pk).count(), 0)

        changelog = Changelog.objects.get()
        self.assertEqual(changelog.target_model, 'data.allegation')
        self.assertEqual(changelog.log_type, LOG_TYPE_DELETE)
        self.assertEqual(changelog.object_pk, old_pk)
        self.assertEqual(dict(changelog.content.items()), {
            'id': old_pk,
            'crid': '456123',
            'add1': '103',
            'beat': areas[0].pk,
            'areas': [area.pk for area in areas[1:]],
            'city': 'abc',
            'line_areas': [line_area.pk],
            'add2': 'def',
            'location': '01',
            'point': 'SRID=4326;POINT (0 0)',
            'source': 'IPRA',
            'summary': 'lorem ipsum',
            'incident_date': '2000-01-01T00:00:00Z',
            'is_officer_complaint': False,
        })
