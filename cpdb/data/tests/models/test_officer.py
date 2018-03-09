from datetime import date, timedelta
from django.test.testcases import TestCase, override_settings
from robber.expect import expect

from data.models import Officer
from data.factories import (
    OfficerFactory, OfficerBadgeNumberFactory, OfficerHistoryFactory, PoliceUnitFactory,
    OfficerAllegationFactory, AwardFactory
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

    def test_honorable_mention_count(self):
        officer = OfficerFactory()
        AwardFactory(officer=officer, award_type='Other')
        AwardFactory(officer=officer, award_type='Complimentary Letter')
        AwardFactory(officer=officer, award_type='Complimentary Letter')
        AwardFactory(officer=officer, award_type='Honorable Mention')
        AwardFactory(officer=officer, award_type='ABC Honorable Mention')

        expect(officer.honorable_mention_count).to.eq(2)

    def test_civilian_compliment_count(self):
        officer = OfficerFactory()
        AwardFactory(officer=officer, award_type='Other')
        AwardFactory(officer=officer, award_type='Complimentary Letter')
        AwardFactory(officer=officer, award_type='Complimentary Letter')
        AwardFactory(officer=officer, award_type='Honorable Mention')
        AwardFactory(officer=officer, award_type='ABC Honorable Mention')

        expect(officer.civilian_compliment_count).to.eq(2)

    def test_last_unit(self):
        officer = OfficerFactory()
        expect(officer.last_unit).to.equal(None)
        OfficerHistoryFactory(officer=officer, unit=PoliceUnitFactory(unit_name='CAND'))
        expect(officer.last_unit).to.eq('CAND')

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

    def test_top_complaint_officers(self):
        officer1 = OfficerFactory(id=1, appointed_date=date.today() - timedelta(days=60))
        OfficerAllegationFactory.create_batch(1, officer=officer1)
        officer2 = OfficerFactory(id=2, appointed_date=date(1980, 1, 1))
        OfficerAllegationFactory.create_batch(1, officer=officer2)
        officer3 = OfficerFactory(id=3, appointed_date=date(1980, 1, 1))
        OfficerAllegationFactory.create_batch(2, officer=officer3)

        results = Officer.top_complaint_officers(100)
        expect(results).to.eq([
            (2, 0.0),
            (3, 50.0)
        ])

        officer4 = OfficerFactory(id=4, appointed_date=date(1980, 1, 1))
        OfficerAllegationFactory.create_batch(3, officer=officer4)
        officer5 = OfficerFactory(id=5, appointed_date=date(1980, 1, 1))
        OfficerAllegationFactory.create_batch(4, officer=officer5)
        results = Officer.top_complaint_officers(25)
        expect(results).to.eq([
            (5, 75.0)
        ])

    @override_settings(VISUAL_TOKEN_STORAGEACCOUNTNAME='cpdbdev')
    def test_visual_token_png_url(self):
        officer = OfficerFactory(id=90)
        expect(officer.visual_token_png_url).to.eq('https://cpdbdev.blob.core.windows.net/visual-token/officer_90.png')

    @override_settings(VISUAL_TOKEN_SOCIAL_MEDIA_FOLDER='media_folder')
    def test_visual_token_png_path(self):
        officer = OfficerFactory(id=90)
        expect(officer.visual_token_png_path).to.eq('media_folder/officer_90.png')
