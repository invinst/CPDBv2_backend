from datetime import date, datetime
from decimal import Decimal
from operator import itemgetter

from django.test import TestCase, override_settings

from mock import Mock, patch
from robber import expect
import pytz

from data.factories import (
    OfficerFactory, OfficerAllegationFactory, OfficerHistoryFactory, AllegationFactory,
    AwardFactory, SalaryFactory, OfficerBadgeNumberFactory, ComplainantFactory
)
from officers.indexers import OfficersIndexer
from trr.factories import TRRFactory


class OfficersIndexerTestCase(TestCase):
    def setUp(self):
        self.maxDiff = None

    def extract_data(self):
        indexer = OfficersIndexer()
        return [indexer.extract_datum(obj) for obj in indexer.get_queryset()]

    @override_settings(V1_URL='http://test.com')
    @patch(
        'officers.indexers.officers_indexer.officer_percentile.top_percentile',
        Mock(return_value=[])
    )
    def test_extract_info(self):
        officer = OfficerFactory(
            id=123,
            first_name='Alex',
            last_name='Mack',
            rank='5',
            race='White',
            gender='M',
            appointed_date=date(2017, 2, 27),
            resignation_date=date(2017, 12, 27),
            active='Yes',
            birth_year=1910,
            complaint_percentile=99.8,
            honorable_mention_percentile=98,
            tags=['Jason VanDyke']
        )
        TRRFactory(officer=officer, trr_datetime=datetime(2002, 9, 29, tzinfo=pytz.utc))
        SalaryFactory(officer=officer, salary=9000)
        AwardFactory(
            officer=officer,
            award_type='Honorable Mention'
        )
        AwardFactory(
            officer=officer,
            award_type='Complimentary Letter'
        )
        AwardFactory(
            officer=officer,
            award_type='Honored Police Star'
        )
        AwardFactory(
            officer=officer,
            award_type='Lambert Tree'
        )
        OfficerHistoryFactory(
            officer=officer,
            unit__id=1001,
            unit__unit_name='001',
            unit__description='Hyde Park D',
            effective_date=date(2010, 1, 1),
            end_date=date(2011, 1, 1)
        )
        OfficerHistoryFactory(
            officer=officer,
            unit__id=1002,
            unit__unit_name='002',
            unit__description='Tactical',
            effective_date=date(2011, 1, 2)
        )
        OfficerBadgeNumberFactory(
            officer=officer,
            star='123456',
            current=True
        )
        OfficerBadgeNumberFactory(
            officer=officer,
            star='123',
            current=False
        )
        OfficerBadgeNumberFactory(
            officer=officer,
            star='456',
            current=False
        )

        allegation = AllegationFactory(incident_date=datetime(2000, 4, 26, tzinfo=pytz.utc))
        OfficerAllegationFactory(
            officer=officer,
            final_finding='SU',
            start_date=date(2000, 1, 1),
            allegation_category__category='Illegal Search',
            allegation=allegation,
            disciplined=True
        )
        ComplainantFactory(
            allegation=allegation,
            race='White',
            age=18,
            gender='M'
        )

        rows = self.extract_data()
        expect(rows).to.have.length(1)
        expect(rows[0]).to.eq({
            'id': 123,
            'full_name': 'Alex Mack',
            'unit': {
                'id': 1002,
                'unit_name': '002',
                'description': 'Tactical',
                'long_unit_name': 'Unit 002'
            },
            'rank': '5',
            'race': 'White',
            'badge': '123456',
            'badge_keyword': '123456',
            'historic_badges': ['123', '456'],
            'historic_badges_keyword': ['123', '456'],
            'historic_units': [
                {
                    'id': 1002,
                    'unit_name': '002',
                    'description': 'Tactical',
                    'long_unit_name': 'Unit 002',
                }, {
                    'id': 1001,
                    'unit_name': '001',
                    'description': 'Hyde Park D',
                    'long_unit_name': 'Unit 001',
                }
            ],
            'gender': 'Male',
            'date_of_appt': '2017-02-27',
            'date_of_resignation': '2017-12-27',
            'active': 'Active',
            'birth_year': 1910,
            'complaint_records': {
                'count': 1,
                'sustained_count': 1,
                'items': [{'year': 2000, 'count': 1, 'sustained_count': 1}],
                'facets': [
                    {
                        'name': 'category',
                        'entries': [{'name': 'Illegal Search', 'count': 1, 'sustained_count': 1, 'items': [
                            {'year': 2000, 'name': 'Illegal Search', 'count': 1, 'sustained_count': 1}
                        ]}]
                    },
                    {
                        'name': 'complainant race',
                        'entries': [{'name': 'White', 'count': 1, 'sustained_count': 1, 'items': [
                            {'year': 2000, 'name': 'White', 'count': 1, 'sustained_count': 1}
                        ]}]
                    },
                    {
                        'name': 'complainant age',
                        'entries': [{'name': '<20', 'count': 1, 'sustained_count': 1, 'items': [
                            {'year': 2000, 'name': '<20', 'count': 1, 'sustained_count': 1}
                        ]}]
                    },
                    {
                        'name': 'complainant gender',
                        'entries': [{'name': 'Male', 'count': 1, 'sustained_count': 1, 'items': [
                            {'year': 2000, 'name': 'Male', 'count': 1, 'sustained_count': 1}
                        ]}]
                    }
                ]
            },
            'allegation_count': 1,
            'complaint_percentile': Decimal('99.8'),
            'honorable_mention_count': 1,
            'honorable_mention_percentile': 98,
            'has_visual_token': False,
            'sustained_count': 1,
            'discipline_count': 1,
            'civilian_compliment_count': 1,
            'trr_count': 1,
            'major_award_count': 2,
            'tags': ['Jason VanDyke'],
            'to': '/officer/123/alex-mack/',
            'url': 'http://test.com/officer/alex-mack/123',
            'current_salary': 9000,
            'unsustained_count': 0,
            'coaccusals': [],
            'current_allegation_percentile': None,
            'percentiles': [],
            'cr_incident_dates': ['2000-04-26'],
            'trr_datetimes': ['2002-09-29'],
            'internal_allegation_percentile': None,
            'trr_percentile': None,
            'civilian_allegation_percentile': None,
        })

    def test_has_visual_token(self):
        OfficerFactory(
            civilian_allegation_percentile=10,
            internal_allegation_percentile=11,
            trr_percentile=12)
        rows = self.extract_data()
        expect(rows).to.have.length(1)
        expect(rows[0]['has_visual_token']).to.be.true()

    def test_has_visual_token_false(self):
        OfficerFactory(
            civilian_allegation_percentile=None,
            internal_allegation_percentile=11,
            trr_percentile=12)
        OfficerFactory(
            civilian_allegation_percentile=10,
            internal_allegation_percentile=None,
            trr_percentile=12)
        OfficerFactory(
            civilian_allegation_percentile=10,
            internal_allegation_percentile=11,
            trr_percentile=None)
        OfficerFactory(
            civilian_allegation_percentile=None,
            internal_allegation_percentile=None,
            trr_percentile=None)
        rows = self.extract_data()
        expect([row['has_visual_token'] for row in rows]).to.eq([False] * 4)

    def test_extract_info_complaint_record_null_category(self):
        officer = OfficerFactory()
        OfficerAllegationFactory(
            officer=officer,
            allegation_category=None,
            final_finding='SU',
            start_date=date(2000, 1, 2)
        )
        OfficerAllegationFactory(
            officer=officer,
            allegation_category__category='Illegal Search',
            final_finding='NS',
            start_date=None
        )

        rows = self.extract_data()

        expect(rows).to.have.length(1)
        first_facets = rows[0]['complaint_records']['facets'][0]
        first_facets['entries'] = sorted(first_facets['entries'], key=itemgetter('name'))

        expect(first_facets).to.eq({
            'name': 'category',
            'entries': [
                {'name': 'Illegal Search', 'count': 1, 'sustained_count': 0, 'items': [
                    {'year': None, 'name': 'Illegal Search', 'count': 1, 'sustained_count': 0}
                ]},
                {'name': 'Unknown', 'count': 1, 'sustained_count': 1, 'items': [
                    {'year': 2000, 'name': 'Unknown', 'count': 1, 'sustained_count': 1}
                ]},
            ]
        })

    def test_extract_info_complaint_record_null_complainant(self):
        officer = OfficerFactory()
        OfficerAllegationFactory(
            officer=officer,
            final_finding='UN',
            start_date=date(2000, 1, 2)
        )
        allegation = AllegationFactory()
        ComplainantFactory(
            allegation=allegation,
            race='White',
            gender='M',
            age=21)
        OfficerAllegationFactory(
            officer=officer,
            allegation=allegation,
            final_finding='UN',
            start_date=None
        )

        rows = self.extract_data()

        expect(rows).to.have.length(1)
        expect(rows[0]['complaint_records']['facets'][1:]).to.eq([
            {
                'name': 'complainant race',
                'entries': [
                    {'name': 'Unknown', 'count': 1, 'sustained_count': 0, 'items': [
                        {'year': 2000, 'name': 'Unknown', 'count': 1, 'sustained_count': 0}
                    ]},
                    {'name': 'White', 'count': 1, 'sustained_count': 0, 'items': [
                        {'year': None, 'name': 'White', 'count': 1, 'sustained_count': 0}
                    ]}
                ]
            },
            {
                'name': 'complainant age',
                'entries': [
                    {'name': 'Unknown', 'count': 1, 'sustained_count': 0, 'items': [
                        {'year': 2000, 'name': 'Unknown', 'count': 1, 'sustained_count': 0}
                    ]},
                    {'name': '20-30', 'count': 1, 'sustained_count': 0, 'items': [
                        {'year': None, 'name': '20-30', 'count': 1, 'sustained_count': 0}
                    ]}
                ]
            },
            {
                'name': 'complainant gender',
                'entries': [
                    {'name': 'Unknown', 'count': 1, 'sustained_count': 0, 'items': [
                        {'year': 2000, 'name': 'Unknown', 'count': 1, 'sustained_count': 0}
                    ]},
                    {'name': 'Male', 'count': 1, 'sustained_count': 0, 'items': [
                        {'year': None, 'name': 'Male', 'count': 1, 'sustained_count': 0}
                    ]}
                ]
            }
        ])

    def test_extract_info_complaint_record_complainant_empty_gender(self):
        allegation = AllegationFactory()
        ComplainantFactory(
            allegation=allegation,
            gender='')
        OfficerAllegationFactory(
            final_finding='UN',
            start_date=date(2000, 1, 2),
            allegation=allegation
        )

        rows = self.extract_data()

        expect(rows).to.have.length(1)
        expect(rows[0]['complaint_records']['facets'][3]).to.eq({
            'name': 'complainant gender',
            'entries': [{'name': 'Unknown', 'count': 1, 'sustained_count': 0, 'items': [
                {'year': 2000, 'name': 'Unknown', 'count': 1, 'sustained_count': 0}
            ]}]
        })

    def test_extract_info_complaint_record_complainant_unknown_race(self):
        allegation = AllegationFactory()
        ComplainantFactory(
            allegation=allegation,
            race='')
        OfficerAllegationFactory(
            final_finding='UN',
            start_date=date(2000, 1, 2),
            allegation=allegation
        )

        rows = self.extract_data()

        expect(rows).to.have.length(1)
        expect(rows[0]['complaint_records']['facets'][1]).to.eq({
            'name': 'complainant race',
            'entries': [{'name': 'Unknown', 'count': 1, 'sustained_count': 0, 'items': [
                {'year': 2000, 'name': 'Unknown', 'count': 1, 'sustained_count': 0}
            ]}]
        })

    def test_extract_info_complaint_record_complainant_null_age(self):
        allegation = AllegationFactory()
        ComplainantFactory(
            allegation=allegation,
            age=None)
        OfficerAllegationFactory(
            final_finding='UN',
            start_date=date(2000, 1, 2),
            allegation=allegation
        )

        rows = self.extract_data()

        expect(rows).to.have.length(1)
        expect(rows[0]['complaint_records']['facets'][2]).to.eq({
            'name': 'complainant age',
            'entries': [{'name': 'Unknown', 'count': 1, 'sustained_count': 0, 'items': [
                {'year': 2000, 'name': 'Unknown', 'count': 1, 'sustained_count': 0}
            ]}]
        })

    def test_extract_info_coaccusals(self):
        officer = OfficerFactory(id=1101)
        other_officer = OfficerFactory(id=1102)
        allegation1 = AllegationFactory()
        OfficerAllegationFactory(officer=officer, allegation=allegation1)
        OfficerAllegationFactory(officer=other_officer, allegation=allegation1)
        allegation2 = AllegationFactory()
        OfficerAllegationFactory(officer=officer, allegation=allegation2)
        OfficerAllegationFactory(officer=other_officer, allegation=allegation2)

        rows = sorted(self.extract_data(), key=itemgetter('id'))

        expect(rows).to.have.length(2)
        expect(rows[0]['coaccusals']).to.eq([
            {
                'id': 1102,
                'coaccusal_count': 2
            }
        ])
        expect(rows[1]['coaccusals']).to.eq([
            {
                'id': 1101,
                'coaccusal_count': 2
            }
        ])

    # @override_settings(ALLEGATION_MIN='1988-01-01')
    # @override_settings(ALLEGATION_MAX='2016-07-01')
    # @override_settings(INTERNAL_CIVILIAN_ALLEGATION_MIN='2000-01-01')
    # @override_settings(INTERNAL_CIVILIAN_ALLEGATION_MAX='2016-07-01')
    # @override_settings(TRR_MIN='2004-01-08')
    # @override_settings(TRR_MAX='2016-04-12')
    # def test_extract_datum_percentiles(self):
    #     officer1 = OfficerFactory(id=1, appointed_date=date(2013, 1, 1))
    #     officer2 = OfficerFactory(id=2, appointed_date=date(2015, 3, 14))
    #     OfficerFactory(id=3, appointed_date=date(2014, 3, 1), resignation_date=date(2015, 4, 14))

    #     OfficerAllegationFactory(
    #         officer=officer1,
    #         allegation__incident_date=datetime(2015, 1, 1, tzinfo=pytz.utc),
    #         start_date=date(2015, 1, 1),
    #         allegation__is_officer_complaint=False)
    #     OfficerAllegationFactory(
    #         officer=officer1,
    #         start_date=date(2015, 1, 1),
    #         allegation__incident_date=datetime(2015, 1, 1, tzinfo=pytz.utc),
    #         allegation__is_officer_complaint=False)
    #     OfficerAllegationFactory(
    #         officer=officer1,
    #         start_date=date(2016, 1, 22),
    #         allegation__incident_date=datetime(2016, 1, 1, tzinfo=pytz.utc),
    #         allegation__is_officer_complaint=False)
    #     OfficerAllegationFactory.create_batch(
    #         2,
    #         officer=officer2,
    #         start_date=date(2017, 10, 19),
    #         allegation__incident_date=datetime(2016, 1, 16, tzinfo=pytz.utc),
    #         allegation__is_officer_complaint=False
    #     )
    #     OfficerAllegationFactory(
    #         officer=officer2,
    #         start_date=date(2017, 10, 19),
    #         allegation__incident_date=datetime(2016, 3, 15, tzinfo=pytz.utc),
    #         allegation__is_officer_complaint=True
    #     )
    #     OfficerAllegationFactory(
    #         officer=officer2,
    #         start_date=date(2017, 10, 19),
    #         allegation__incident_date=datetime(2017, 3, 15, tzinfo=pytz.utc),
    #         allegation__is_officer_complaint=True
    #     )
    #     TRRFactory(
    #         officer=officer1,
    #         trr_datetime=datetime(2017, 3, 15, tzinfo=pytz.utc),
    #     )
    #     TRRFactory(
    #         officer=officer1,
    #         trr_datetime=datetime(2016, 3, 15, tzinfo=pytz.utc),
    #     )
    #     rows = sorted(self.extract_data(), key=itemgetter('id'))
    #     expect(rows).to.have.length(3)
    #     expect(rows[0]['current_allegation_percentile']).to.eq('33.3333')
    #     expect(rows[0]['percentiles']).to.eq([
    #         {
    #             'id': 1,
    #             'year': 2014,
    #             'percentile_allegation': '0.0000',
    #             'percentile_allegation_civilian': '0.0000',
    #             'percentile_allegation_internal': '0.0000',
    #             'percentile_trr': '0.0000'
    #         },
    #         {
    #             'id': 1,
    #             'year': 2015,
    #             'percentile_allegation': '50.0000',
    #             'percentile_allegation_civilian': '50.0000',
    #             'percentile_allegation_internal': '0.0000',
    #             'percentile_trr': '0.0000'
    #         },
    #         {
    #             'id': 1,
    #             'year': 2016,
    #             'percentile_allegation': '33.3333',
    #             'percentile_allegation_civilian': '33.3333',
    #             'percentile_allegation_internal': '0.0000',
    #             'percentile_trr': '66.6667'
    #         }
    #     ])
    #     expect(rows[1]['current_allegation_percentile']).to.eq('66.6667')
    #     expect(rows[1]['percentiles']).to.eq([
    #         {
    #             'id': 2,
    #             'year': 2016,
    #             'percentile_allegation': '66.6667',
    #             'percentile_allegation_civilian': '66.6667',
    #             'percentile_allegation_internal': '66.6667',
    #             'percentile_trr': '0.0000'
    #         }
    #     ])
    #     expect(rows[2]['current_allegation_percentile']).to.eq('0.0000')
    #     expect(rows[2]['percentiles']).to.eq([
    #         {
    #             'id': 3,
    #             'year': 2015,
    #             'percentile_allegation': '0.0000',
    #             'percentile_allegation_civilian': '0.0000',
    #             'percentile_allegation_internal': '0.0000',
    #             'percentile_trr': '0.0000'
    #         }
    #     ])

    # @patch('officers.indexers.officers_indexer.MIN_VISUAL_TOKEN_YEAR', 2016)
    # @patch('officers.indexers.officers_indexer.MAX_VISUAL_TOKEN_YEAR', 2016)
    # @patch(
    #     'officers.indexers.officers_indexer.officer_percentile.top_percentile',
    #     Mock(return_value=[Mock(
    #         spec=[
    #             'id',
    #             'year',
    #             'resignation_date',
    #             'percentile_allegation',
    #             'percentile_allegation_civilian',
    #             'percentile_allegation_internal'],
    #         id=123,
    #         year=2016,
    #         resignation_date=date(2017, 3, 4),
    #         percentile_allegation=23.4543,
    #         percentile_allegation_civilian=54.2342,
    #         percentile_allegation_internal=54.3432
    #     )])
    # )
    def test_extract_datum_percentiles_missing_value(self):
        OfficerFactory(id=123)
        rows = self.extract_data()

        expect(rows).to.have.length(1)
        expect(rows[0]['percentiles']).to.eq([
            {
                'id': 123,
                'year': 2016,
                'percentile_allegation': '23.4543',
                'percentile_allegation_civilian': '54.2342',
                'percentile_allegation_internal': '54.3432'
            }
        ])
