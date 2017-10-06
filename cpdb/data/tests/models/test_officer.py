from django.test.testcases import TestCase, override_settings

from robber.expect import expect

from data.models import Officer
from data.factories import (
    OfficerFactory, OfficerBadgeNumberFactory, OfficerHistoryFactory, PoliceUnitFactory, AllegationFactory,
    OfficerAllegationFactory, AllegationCategoryFactory, ComplainantFactory
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

    def test_get_absolute_url(self):
        expect(Officer(pk=1).get_absolute_url()).to.eq('/officer/1/')

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

    def test_abbr_name(self):
        officer = OfficerFactory(first_name='Michel', last_name='Foo')
        expect(officer.abbr_name).to.eq('M. Foo')

    def test_discipline_count(self):
        officer = OfficerFactory()
        OfficerAllegationFactory(officer=officer, final_outcome='100')
        OfficerAllegationFactory(officer=officer, final_outcome='600')
        OfficerAllegationFactory(officer=officer, final_outcome='')
        expect(officer.discipline_count).to.eq(1)

    def test_visual_token_background_color(self):
        crs_colors = [
            (0, '#f5f4f4'),
            (3, '#edf0fa'),
            (7, '#d4e2f4'),
            (20, '#c6d4ec'),
            (30, '#aec9e8'),
            (45, '#90b1f5')
        ]
        for cr, color in crs_colors:
            officer = OfficerFactory()
            OfficerAllegationFactory.create_batch(cr, officer=officer)
            expect(officer.visual_token_background_color).to.eq(color)

    def test_visual_token_png_url(self):
        officer = OfficerFactory(id=90)
        expect(officer.visual_token_png_url).to.eq('https://cpdbdev.blob.core.windows.net/visual-token/officer_90.png')

    @override_settings(VISUAL_TOKEN_SOCIAL_MEDIA_FOLDER='media_folder')
    def test_visual_token_png_path(self):
        officer = OfficerFactory(id=90)
        expect(officer.visual_token_png_path).to.eq('media_folder/officer_90.png')
