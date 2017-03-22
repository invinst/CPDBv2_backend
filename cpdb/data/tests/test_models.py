from django.test.testcases import TestCase, SimpleTestCase, override_settings

from robber.expect import expect

from data.models import Officer, OfficerBadgeNumber, PoliceUnit
from data.factories import (
    OfficerFactory, OfficerBadgeNumberFactory, AreaFactory, OfficerHistoryFactory, PoliceUnitFactory, AllegationFactory,
    OfficerAllegationFactory, AllegationCategoryFactory, ComplainantFactory, AttachmentFileFactory, InvolvementFactory
)
from data.constants import MEDIA_TYPE_VIDEO, MEDIA_TYPE_AUDIO, MEDIA_TYPE_DOCUMENT


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
                'count': 1
            }
        ])

    def test_complainant_race_aggregation(self):
        officer = OfficerFactory()
        allegation = AllegationFactory()
        OfficerAllegationFactory(officer=officer, allegation=allegation)
        ComplainantFactory(allegation=allegation, race='White')
        ComplainantFactory(allegation=allegation, race='')

        expect(officer.complainant_race_aggregation).to.eq([
            {
                'name': 'White',
                'count': 1
            },
            {
                'name': None,
                'count': 1
            }
        ])

    def test_complainant_race_aggregation_no_complainant(self):
        officer = OfficerFactory()
        expect(officer.complainant_race_aggregation).to.eq([])

    def test_complainant_age_aggregation(self):
        officer = OfficerFactory()
        allegation = AllegationFactory()
        OfficerAllegationFactory(officer=officer, allegation=allegation)
        ComplainantFactory(allegation=allegation, age=18)

        expect(officer.complainant_age_aggregation).to.eq([
            {
                'name': '18',
                'count': 1
            }
        ])

    def test_complainant_age_aggregation_age_null(self):
        officer = OfficerFactory()
        allegation = AllegationFactory()
        OfficerAllegationFactory(officer=officer, allegation=allegation)
        ComplainantFactory(allegation=allegation, age=None)
        expect(officer.complainant_age_aggregation).to.eq([])

    def test_complainant_gender_aggregation(self):
        officer = OfficerFactory()
        allegation = AllegationFactory()
        OfficerAllegationFactory(officer=officer, allegation=allegation)
        ComplainantFactory(allegation=allegation, gender='F')
        ComplainantFactory(allegation=allegation, gender='')

        expect(officer.complainant_gender_aggregation).to.eq([
            {
                'name': 'Female',
                'count': 1
            },
            {
                'name': None,
                'count': 1
            }
        ])

    def test_complainant_gender_aggregation_no_complainant(self):
        officer = OfficerFactory()
        expect(officer.complainant_gender_aggregation).to.eq([])

    def test_abbr_name(self):
        officer = OfficerFactory(first_name='Michel', last_name='Foo')
        expect(officer.abbr_name).to.eq('M. Foo')


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

    def test_final_finding_display(self):
        officer_allegation = OfficerAllegationFactory(final_finding='?')
        expect(officer_allegation.final_finding_display).to.eq('Unknown')

        officer_allegation = OfficerAllegationFactory(final_finding='UN')
        expect(officer_allegation.final_finding_display).to.eq('Unfounded')

    def test_recc_finding_display(self):
        officer_allegation = OfficerAllegationFactory(recc_finding='?')
        expect(officer_allegation.recc_finding_display).to.eq('Unknown')

        officer_allegation = OfficerAllegationFactory(recc_finding='UN')
        expect(officer_allegation.recc_finding_display).to.eq('Unfounded')

    def test_final_outcome_display(self):
        officer_allegation = OfficerAllegationFactory(final_outcome='?')
        expect(officer_allegation.final_outcome_display).to.eq('Unknown')

        officer_allegation = OfficerAllegationFactory(final_outcome='100')
        expect(officer_allegation.final_outcome_display).to.eq('Reprimand')

    def test_recc_outcome_display(self):
        officer_allegation = OfficerAllegationFactory(recc_outcome='?')
        expect(officer_allegation.recc_outcome_display).to.eq('Unknown')

        officer_allegation = OfficerAllegationFactory(recc_outcome='100')
        expect(officer_allegation.recc_outcome_display).to.eq('Reprimand')


class OfficerHistoryTestCase(TestCase):
    def test_unit_name(self):
        history = OfficerHistoryFactory(unit=PoliceUnitFactory(unit_name='abc'))
        expect(history.unit_name).to.eq('abc')


class AllegationTestCase(TestCase):
    def test_address(self):
        allegation = AllegationFactory(add1=3000, add2='Michigan Ave', city='Chicago IL')
        expect(allegation.address).to.eq('3000 Michigan Ave, Chicago IL')

    def test_officer_allegations(self):
        allegation = AllegationFactory()
        OfficerAllegationFactory(id=1, allegation=allegation, officer=OfficerFactory())
        expect(allegation.officer_allegations.count()).to.eq(1)
        expect(allegation.officer_allegations[0].id).to.eq(1)

    def test_complainants(self):
        allegation = AllegationFactory()
        ComplainantFactory(id=1, allegation=allegation)
        expect(allegation.complainants.count()).to.eq(1)
        expect(allegation.complainants[0].id).to.eq(1)

    def test_videos(self):
        allegation = AllegationFactory()
        AttachmentFileFactory(id=1, allegation=allegation, file_type=MEDIA_TYPE_VIDEO)
        expect(allegation.videos.count()).to.eq(1)
        expect(allegation.videos[0].id).to.eq(1)

    def test_audios(self):
        allegation = AllegationFactory()
        AttachmentFileFactory(id=1, allegation=allegation, file_type=MEDIA_TYPE_AUDIO)
        expect(allegation.audios.count()).to.eq(1)
        expect(allegation.audios[0].id).to.eq(1)

    def test_documents(self):
        allegation = AllegationFactory()
        AttachmentFileFactory(id=1, allegation=allegation, file_type=MEDIA_TYPE_DOCUMENT)
        expect(allegation.documents.count()).to.eq(1)
        expect(allegation.documents[0].id).to.eq(1)


class ComplainantTestCase(TestCase):
    def test_gender_display(self):
        expect(ComplainantFactory(gender='M').gender_display).to.equal('Male')
        expect(ComplainantFactory(gender='F').gender_display).to.equal('Female')
        expect(ComplainantFactory(gender='X').gender_display).to.equal('X')
        expect(ComplainantFactory(gender='?').gender_display).to.equal('?')


class InvolvementTestCase(TestCase):
    def test_gender_display(self):
        expect(InvolvementFactory(gender='M').gender_display).to.equal('Male')
        expect(InvolvementFactory(gender='F').gender_display).to.equal('Female')
        expect(InvolvementFactory(gender='X').gender_display).to.equal('X')
        expect(InvolvementFactory(gender='?').gender_display).to.equal('?')
