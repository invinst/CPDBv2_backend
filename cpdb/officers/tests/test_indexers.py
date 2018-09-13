from datetime import date, datetime

from django.test import SimpleTestCase, TestCase

from mock import Mock, patch
from robber import expect
import pytz

from data.factories import (
    OfficerFactory, AllegationFactory, OfficerAllegationFactory, AwardFactory,
    SalaryFactory
)
from officers.indexers import (
    JoinedNewTimelineEventIndexer,
    TRRNewTimelineEventIndexer,
    AwardNewTimelineEventIndexer,
    OfficerCoaccusalsIndexer,
    RankChangeNewTimelineEventIndexer,
)
from trr.factories import TRRFactory


class JoinedNewTimelineEventIndexerTestCase(SimpleTestCase):
    def test_get_queryset(self):
        officer = Mock()
        with patch('officers.indexers.Officer.objects.filter', return_value=[officer]):
            expect(JoinedNewTimelineEventIndexer().get_queryset()).to.eq([officer])

    def test_extract_datum(self):
        officer = Mock(
            id=123,
            appointed_date=date(2012, 1, 1),
            get_unit_by_date=Mock(return_value=Mock(
                unit_name='001',
                description='Unit_001',
            )),
            get_rank_by_date=Mock(return_value='Police Officer'),
        )
        expect(JoinedNewTimelineEventIndexer().extract_datum(officer)).to.eq({
            'officer_id': 123,
            'date_sort': date(2012, 1, 1),
            'priority_sort': 10,
            'date': '2012-01-01',
            'kind': 'JOINED',
            'unit_name': '001',
            'unit_description': 'Unit_001',
            'rank': 'Police Officer',
        })


class AwardNewTimelineEventIndexerTestCase(TestCase):
    def test_get_queryset(self):
        AwardFactory(award_type='Honorable Mention')
        AwardFactory(award_type='Honorable Mention Ribbon Award')
        AwardFactory(award_type="Superintendent'S Honorable Mention")
        AwardFactory(award_type='Special Honorable Mention')
        AwardFactory(award_type='Complimentary Letter')
        AwardFactory(award_type='Department Commendation')
        award1 = AwardFactory(award_type='Life Saving Award')
        award2 = AwardFactory(award_type='Award Of Appreciation')
        award3 = AwardFactory(award_type='Problem Solving Award')
        expect(set([
            obj.pk for obj in AwardNewTimelineEventIndexer().get_queryset()
        ])).to.eq(set([award1.id, award2.id, award3.id]))

    def test_extract_datum(self):
        award = Mock(
            officer_id=123,
            start_date=date(2010, 3, 4),
            award_type='Honorable Mention',
            officer=Mock(
                get_rank_by_date=Mock(return_value='Police Officer'),
                get_unit_by_date=Mock(return_value=Mock(
                    unit_name='001',
                    description='Unit_001',
                )),
            ),
        )
        expect(AwardNewTimelineEventIndexer().extract_datum(award)).to.eq({
            'officer_id': 123,
            'date_sort': date(2010, 3, 4),
            'priority_sort': 40,
            'date': '2010-03-04',
            'kind': 'AWARD',
            'award_type': 'Honorable Mention',
            'unit_name': '001',
            'unit_description': 'Unit_001',
            'rank': 'Police Officer',
        })


class TRRNewTimelineEventIndexerTestCase(TestCase):
    def test_get_queryset(self):
        trr = TRRFactory()
        TRRFactory(officer=None)

        expect([obj.id for obj in TRRNewTimelineEventIndexer().get_queryset()]).to.eq([trr.id])

    def test_extract_datum(self):
        trr = Mock(
            id=2,
            officer_id=123,
            trr_datetime=datetime(2010, 3, 4),
            firearm_used=False,
            taser=False,
            officer=Mock(
                get_rank_by_date=Mock(return_value='Police Officer'),
                get_unit_by_date=Mock(return_value=Mock(
                    unit_name='001',
                    description='Unit_001',
                )),
            ),
            point=Mock(
                x=34.5,
                y=67.8
            ),
        )

        expect(TRRNewTimelineEventIndexer().extract_datum(trr)).to.eq({
            'trr_id': 2,
            'officer_id': 123,
            'date_sort': date(2010, 3, 4),
            'priority_sort': 50,
            'date': '2010-03-04',
            'kind': 'FORCE',
            'taser': False,
            'firearm_used': False,
            'unit_name': '001',
            'unit_description': 'Unit_001',
            'rank': 'Police Officer',
            'point': {
                'lat': 67.8,
                'lon': 34.5
            },
        })


class OfficerCoaccusalsIndexerTestCase(TestCase):
    def test_get_queryset(self):
        officer = OfficerFactory()
        expect(list(OfficerCoaccusalsIndexer().get_queryset())).to.eq([officer])

    def test_extract_datum(self):
        officer1 = OfficerFactory(appointed_date=date(2001, 1, 1))
        officer2 = OfficerFactory(
            first_name='Officer',
            last_name='456',
            race='White',
            gender='M',
            birth_year=1950,
            rank='Police Officer',
            appointed_date=date(2002, 1, 1),
            civilian_allegation_percentile=11.1111,
            internal_allegation_percentile=22.2222,
            trr_percentile=33.3333,
            complaint_percentile=44.4444,
        )
        officer3 = OfficerFactory(
            first_name='Officer',
            last_name='789',
            race='Black',
            gender='M',
            birth_year=1970,
            rank='Po As Detective',
            appointed_date=date(2003, 1, 1),
            civilian_allegation_percentile=55.5555,
            internal_allegation_percentile=66.6666,
            trr_percentile=77.7777,
            complaint_percentile=88.8888,
        )

        allegation1 = AllegationFactory(incident_date=datetime(2002, 1, 1, tzinfo=pytz.utc))
        allegation2 = AllegationFactory(incident_date=datetime(2003, 1, 1, tzinfo=pytz.utc))
        allegation3 = AllegationFactory(incident_date=datetime(2004, 1, 1, tzinfo=pytz.utc))
        allegation4 = AllegationFactory(incident_date=datetime(2005, 1, 1, tzinfo=pytz.utc))

        OfficerAllegationFactory(
            officer=officer2, allegation=allegation1, final_finding='SU', start_date=date(2003, 1, 1)
        )
        OfficerAllegationFactory(
            officer=officer3, allegation=allegation2, final_finding='SU', start_date=date(2004, 1, 1)
        )
        OfficerAllegationFactory(
            officer=officer3, allegation=allegation3, final_finding='NS', start_date=date(2005, 1, 1)
        )
        OfficerAllegationFactory(
            officer=officer1, allegation=allegation4, final_finding='NS', start_date=date(2006, 1, 1)
        )
        OfficerAllegationFactory(
            officer=officer2, allegation=allegation4, final_finding='NS', start_date=date(2006, 1, 1)
        )
        OfficerAllegationFactory(
            officer=officer3, allegation=allegation4, final_finding='NS', start_date=date(2006, 1, 1)
        )

        expect(dict(OfficerCoaccusalsIndexer().extract_datum(officer1))).to.eq({
            'id': officer1.id,
            'coaccusals': [{
                'id': officer2.id,
                'full_name': 'Officer 456',
                'allegation_count': 2,
                'sustained_count': 1,
                'complaint_percentile': 44.4444,
                'race': 'White',
                'gender': 'Male',
                'birth_year': 1950,
                'coaccusal_count': 1,
                'rank': 'Police Officer',
                'percentile_allegation_civilian': 11.1111,
                'percentile_allegation_internal': 22.2222,
                'percentile_trr': 33.3333,
            }, {
                'id': officer3.id,
                'full_name': 'Officer 789',
                'allegation_count': 3,
                'sustained_count': 1,
                'complaint_percentile': 88.8888,
                'race': 'Black',
                'gender': 'Male',
                'birth_year': 1970,
                'coaccusal_count': 1,
                'rank': 'Po As Detective',
                'percentile_allegation_civilian': 55.5555,
                'percentile_allegation_internal': 66.6666,
                'percentile_trr': 77.7777,
            }]
        })


class RankChangeNewTimelineEventIndexerTestCase(TestCase):
    def test_get_queryset(self):
        officer1 = OfficerFactory()
        officer2 = OfficerFactory()
        salary1 = SalaryFactory(
            officer=officer1, salary=5000, year=2005, rank='Police Officer', spp_date=date(2005, 1, 1),
            start_date=date(2005, 1, 1)
        )
        SalaryFactory(
            officer=officer1, salary=10000, year=2006, rank='Police Officer', spp_date=date(2005, 1, 1),
            start_date=date(2005, 1, 1)
        )
        salary2 = SalaryFactory(
            officer=officer1, salary=15000, year=2007, rank='Sergeant', spp_date=date(2007, 1, 1),
            start_date=date(2005, 1, 1)
        )
        salary3 = SalaryFactory(
            officer=officer2, salary=5000, year=2005, rank='Police Officer', spp_date=date(2005, 1, 1),
            start_date=date(2005, 1, 1)
        )
        salary4 = SalaryFactory(
            officer=officer2, salary=15000, year=2006, rank='Detective', spp_date=date(2006, 1, 1),
            start_date=date(2005, 1, 1)
        )
        SalaryFactory(
            officer=officer2, salary=20000, year=2007, rank='Detective', spp_date=date(2006, 1, 1),
            start_date=date(2005, 1, 1)
        )
        expect(RankChangeNewTimelineEventIndexer().get_queryset()).to.eq([salary1, salary2, salary3, salary4])

    def test_extract_datum(self):
        salary = Mock(
            officer_id=123,
            spp_date=date(2005, 1, 1),
            salary=10000,
            year=2015,
            rank='Police Officer',
            start_date=date(2010, 3, 4),
            officer=Mock(
                get_unit_by_date=Mock(return_value=Mock(
                    unit_name='001',
                    description='Unit_001',
                )),
            ),
        )
        expect(RankChangeNewTimelineEventIndexer().extract_datum(salary)).to.eq({
            'officer_id': 123,
            'date_sort': date(2005, 1, 1),
            'priority_sort': 25,
            'date': '2005-01-01',
            'kind': 'RANK_CHANGE',
            'unit_name': '001',
            'unit_description': 'Unit_001',
            'rank': 'Police Officer',
        })
