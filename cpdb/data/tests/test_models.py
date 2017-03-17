from django.test.testcases import TestCase, SimpleTestCase, override_settings

from robber.expect import expect

from data.models import Officer, OfficerBadgeNumber, PoliceUnit
from data.factories import (
    OfficerFactory, OfficerBadgeNumberFactory, AreaFactory, OfficerHistoryFactory, PoliceUnitFactory,
    AllegationFactory, OfficerAllegationFactory, AllegationCategoryFactory, ComplainantFactory
)


class OfficerTestCase(TestCase):
    def test_str(self):
        self.assertEqual(str(Officer(first_name='Daniel', last_name='Abate')), 'Daniel Abate')

    @override_settings(V1_URL='domain')
    def test_v1_url(self):
        first = 'first'
        last = 'last'
        url = 'domain/officer/first-last/1'
        expect(Officer(first_name=first, last_name=last, pk=1).v1_url).to.eq(url)

    def test_v2_to(self):
        expect(Officer(pk=1).v2_to).to.eq('/officer/1/')

    def test_current_badge_not_found(self):
        officer = OfficerFactory()
        expect(officer.current_badge).to.equal('')
        OfficerBadgeNumberFactory(officer=officer, current=False)
        expect(officer.current_badge).to.equal('')

    def test_current_badge(self):
        officer = OfficerFactory()
        OfficerBadgeNumberFactory(officer=officer, star='123', current=True)
        expect(officer.current_badge).to.eq('123')

    def test_gender_display(self):
        expect(OfficerFactory(gender='M').gender_display).to.equal('Male')
        expect(OfficerFactory(gender='F').gender_display).to.equal('Female')
        expect(OfficerFactory(gender='X').gender_display).to.equal('X')

    def test_gender_display_keyerror(self):
        expect(OfficerFactory(gender='').gender_display).to.equal('')

    def test_last_unit(self):
        officer = OfficerFactory()
        expect(officer.last_unit).to.equal(None)
        OfficerHistoryFactory(officer=officer, unit=PoliceUnitFactory(unit_name='CAND'))
        expect(officer.last_unit).to.eq('CAND')

    def test_complaint_category_aggregation(self):
        officer = OfficerFactory()
        allegation = AllegationFactory()
        allegation_category = AllegationCategoryFactory(category='Use of Force')
        OfficerAllegationFactory(officer=officer, allegation=allegation, allegation_category=allegation_category)

        expect(officer.complaint_category_aggregation).to.eq([
            {
                'name': 'Use of Force',
                'count': 1,
                'sustained_count': 0
            }
        ])

    def test_complainant_race_aggregation(self):
        officer = OfficerFactory()
        allegation1 = AllegationFactory()
        allegation2 = AllegationFactory()
        OfficerAllegationFactory(officer=officer, allegation=allegation1, final_finding='SU')
        OfficerAllegationFactory(officer=officer, allegation=allegation2)
        ComplainantFactory(allegation=allegation1, race='White')
        ComplainantFactory(allegation=allegation2, race='')

        expect(officer.complainant_race_aggregation).to.eq([
            {
                'name': 'White',
                'count': 1,
                'sustained_count': 1
            },
            {
                'name': 'Unknown',
                'count': 1,
                'sustained_count': 0
            }
        ])

    def test_complainant_race_aggregation_no_complainant(self):
        officer = OfficerFactory()
        expect(officer.complainant_race_aggregation).to.eq([])

    def test_complainant_age_aggregation(self):
        officer = OfficerFactory()
        allegation1 = AllegationFactory()
        allegation2 = AllegationFactory()
        OfficerAllegationFactory(officer=officer, allegation=allegation1, final_finding='SU')
        OfficerAllegationFactory(officer=officer, allegation=allegation2)
        ComplainantFactory(allegation=allegation1, age=23)
        ComplainantFactory(allegation=allegation2, age=None)

        expect(officer.complainant_age_aggregation).to.eq([
            {
                'name': 'Unknown',
                'count': 1,
                'sustained_count': 0
            },
            {
                'name': '21-30',
                'count': 1,
                'sustained_count': 1
            }
        ])

    def test_complainant_gender_aggregation(self):
        officer = OfficerFactory()
        allegation1 = AllegationFactory()
        allegation2 = AllegationFactory()
        OfficerAllegationFactory(officer=officer, allegation=allegation1, final_finding='SU')
        OfficerAllegationFactory(officer=officer, allegation=allegation2)
        ComplainantFactory(allegation=allegation1, gender='F')
        ComplainantFactory(allegation=allegation2, gender='')

        expect(officer.complainant_gender_aggregation).to.eq([
            {
                'name': 'Female',
                'count': 1,
                'sustained_count': 1
            },
            {
                'name': 'Unknown',
                'count': 1,
                'sustained_count': 0
            }
        ])

    def test_complainant_gender_aggregation_no_complainant(self):
        officer = OfficerFactory()
        expect(officer.complainant_gender_aggregation).to.eq([])


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


class OfficerAllegationTestCase(TestCase):
    def test_crid(self):
        allegation = AllegationFactory(crid='123456')
        officer_allegation = OfficerAllegationFactory(allegation=allegation)
        expect(officer_allegation.crid).to.eq('123456')

    def test_category(self):
        officer_allegation = OfficerAllegationFactory()
        expect(officer_allegation.category).to.eq(None)

        allegation_category = AllegationCategoryFactory(category='category')
        officer_allegation = OfficerAllegationFactory(allegation_category=allegation_category)
        expect(officer_allegation.category).to.eq('category')

    def test_subcategory(self):
        officer_allegation = OfficerAllegationFactory()
        expect(officer_allegation.subcategory).to.eq(None)

        allegation_category = AllegationCategoryFactory(allegation_name='subcategory')
        officer_allegation = OfficerAllegationFactory(allegation_category=allegation_category)
        expect(officer_allegation.subcategory).to.eq('subcategory')

    def test_coaccused_count(self):
        allegation = AllegationFactory()
        officer_allegation = OfficerAllegationFactory(allegation=allegation)
        OfficerAllegationFactory.create_batch(5, allegation=allegation)

        expect(officer_allegation.coaccused_count).to.eq(6)

    def test_finding(self):
        officer_allegation = OfficerAllegationFactory()
        expect(officer_allegation.finding).to.eq('Unknown')

        officer_allegation = OfficerAllegationFactory(final_finding='UN')
        expect(officer_allegation.finding).to.eq('Unfounded')


class OfficerHistoryTestCase(TestCase):
    def test_unit_name(self):
        history = OfficerHistoryFactory(unit=PoliceUnitFactory(unit_name='abc'))
        expect(history.unit_name).to.eq('abc')
