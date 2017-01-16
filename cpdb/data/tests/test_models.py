from django.test.testcases import TestCase, SimpleTestCase, override_settings

from robber.expect import expect

from data.models import Officer, OfficerBadgeNumber, PoliceUnit
from data.factories import OfficerFactory, OfficerBadgeNumberFactory, AreaFactory


class OfficerTestCase(TestCase):
    def test_str(self):
        self.assertEqual(str(Officer(first_name='Daniel', last_name='Abate')), 'Daniel Abate')

    @override_settings(V1_URL='domain')
    def test_v1_url(self):
        first = 'first'
        last = 'last'
        url = 'domain/officer/first-last/1'
        expect(Officer(first_name=first, last_name=last, pk=1).v1_url).to.eq(url)

    def test_current_badge_not_found(self):
        officer = OfficerFactory()
        expect(officer.current_badge).to.equal('')
        OfficerBadgeNumberFactory(officer=officer, current=False)
        expect(officer.current_badge).to.equal('')

    def test_current_badge(self):
        officer = OfficerFactory()
        OfficerBadgeNumberFactory(officer=officer, star='123', current=True)
        expect(officer.current_badge).to.eq('123')


class OfficerBadgeNumberTestCase(SimpleTestCase):
    def test_str(self):
        officer = Officer(first_name='Jeffery', last_name='Aaron')
        expect(
            str(OfficerBadgeNumber(officer=officer, star='123456'))
        ).to.eq('Jeffery Aaron - 123456')


class PoliceUnitTestCase(SimpleTestCase):
    def test_str(self):
        self.assertEqual(str(PoliceUnit(unit_name='lorem')), 'lorem')

    @override_settings(V1_URL='domain')
    def test_v1_url(self):
        unit = 'unit'
        url = 'domain/url-mediator/session-builder?unit=unit'
        expect(PoliceUnit(unit_name=unit).v1_url).to.eq(url)


class AreaTestCase(SimpleTestCase):
    @override_settings(V1_URL='domain')
    def test_v1_url_for_community_area(self):
        area = AreaFactory.build(area_type='community', name='abc')
        url = 'domain/url-mediator/session-builder?community=abc'
        expect(area.v1_url).to.eq(url)

    @override_settings(V1_URL='domain')
    def test_v1_url_for_neighborhoods_area(self):
        area = AreaFactory.build(area_type='neighborhoods', name='abc')
        url = 'domain/url-mediator/session-builder?neighborhood=abc'
        expect(area.v1_url).to.eq(url)

    @override_settings(V1_URL='domain')
    def test_v1_url_default(self):
        area = AreaFactory.build(area_type='whatever', name='abc')
        expect(area.v1_url).to.eq('domain')
