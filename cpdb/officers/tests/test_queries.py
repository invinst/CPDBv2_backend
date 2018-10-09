import pytz
from datetime import date, datetime
from operator import attrgetter

from django.test import TestCase

from mock import patch, Mock, PropertyMock
from robber import expect

from data.factories import (
    OfficerFactory, OfficerAllegationFactory, PoliceUnitFactory, OfficerHistoryFactory, SalaryFactory,
    AwardFactory)
from officers.queries import OfficerTimelineQuery
from trr.factories import TRRFactory


class OfficerTimelineQueryTestCase(TestCase):
    @patch(
        'officers.queries.CRNewTimelineSerializer',
        return_value=Mock(data=[{'id': 1}, {'id': 2}])
    )
    def test_cr_timeline(self, cr_new_timeline_serializer_mock):
        officer = OfficerFactory(id=123)
        OfficerAllegationFactory(id=1, officer=officer, start_date=date(2002, 2, 3))
        OfficerAllegationFactory(id=2, officer=officer, start_date=date(2003, 1, 5))
        OfficerAllegationFactory(id=3, officer=officer, start_date=None)

        unit_1 = PoliceUnitFactory(unit_name='001', description='District 001')
        unit_2 = PoliceUnitFactory(unit_name='002', description='District 002')
        OfficerHistoryFactory(
            officer=officer, unit=unit_1, effective_date=date(2002, 1, 3), end_date=date(2003, 1, 2)
        )
        OfficerHistoryFactory(
            officer=officer, unit=unit_2, effective_date=date(2003, 1, 3), end_date=date(2018, 1, 3)
        )
        SalaryFactory(
            year=2001, rank='Police Officer', officer=officer, rank_changed=True, spp_date=date(2001, 5, 3)
        )
        SalaryFactory(
            year=2002, rank='Senior Police Officer', officer=officer, rank_changed=True, spp_date=date(2002, 5, 3)
        )

        other_officer = OfficerFactory(id=456)
        OfficerAllegationFactory(id=4, officer=other_officer, start_date=date(2003, 1, 5))

        expect(OfficerTimelineQuery(officer)._cr_timeline).to.eq([{'id': 1}, {'id': 2}])

        cr_timeline_queryset_arg = cr_new_timeline_serializer_mock.call_args[0][0]
        officer_allegation_1_arg, officer_allegation_2_arg = sorted(cr_timeline_queryset_arg, key=attrgetter('id'))

        expect(officer_allegation_1_arg.id).to.eq(1)
        expect(officer_allegation_1_arg.unit_name).to.eq('001')
        expect(officer_allegation_1_arg.unit_description).to.eq('District 001')
        expect(officer_allegation_1_arg.rank_name).to.eq('Police Officer')

        expect(officer_allegation_2_arg.id).to.eq(2)
        expect(officer_allegation_2_arg.unit_name).to.eq('002')
        expect(officer_allegation_2_arg.unit_description).to.eq('District 002')
        expect(officer_allegation_2_arg.rank_name).to.eq('Senior Police Officer')

    @patch(
        'officers.queries.UnitChangeNewTimelineSerializer',
        return_value=Mock(data=[{'id': 1}, {'id': 2}])
    )
    def test_unit_change_timeline(self, unit_change_new_timeline_serializer_mock):
        officer = OfficerFactory(id=123, appointed_date=date(2001, 2, 3))
        officer_history_1 = OfficerHistoryFactory(
            officer=officer, effective_date=date(2002, 1, 3), end_date=date(2002, 1, 3)
        )
        officer_history_2 = OfficerHistoryFactory(
            officer=officer, effective_date=date(2003, 1, 3), end_date=date(2018, 1, 3)
        )
        OfficerHistoryFactory(
            officer=officer, effective_date=None, end_date=date(2018, 1, 3)
        )
        OfficerHistoryFactory(
            officer=officer, effective_date=None, end_date=date(2001, 2, 3)
        )
        SalaryFactory(
            year=2001, rank='Police Officer', officer=officer, rank_changed=True, spp_date=date(2001, 5, 3)
        )
        SalaryFactory(
            year=2002, rank='Senior Police Officer', officer=officer, rank_changed=True, spp_date=date(2002, 5, 3)
        )

        other_officer = OfficerFactory(id=456)
        OfficerHistoryFactory(
            officer=other_officer, effective_date=date(2002, 1, 3), end_date=date(2002, 1, 3)
        )

        expect(OfficerTimelineQuery(officer)._unit_change_timeline).to.eq([{'id': 1}, {'id': 2}])

        unit_change_timeline_queryset_arg = unit_change_new_timeline_serializer_mock.call_args[0][0]
        officer_allegation_1_arg, officer_allegation_2_arg = unit_change_timeline_queryset_arg

        expect(officer_allegation_1_arg.id).to.eq(officer_history_1.id)
        expect(officer_allegation_1_arg.rank_name).to.eq('Police Officer')

        expect(officer_allegation_2_arg.id).to.eq(officer_history_2.id)
        expect(officer_allegation_2_arg.rank_name).to.eq('Senior Police Officer')

    @patch(
        'officers.queries.RankChangeNewTimelineSerializer',
        return_value=Mock(data=[{'id': 1}, {'id': 2}])
    )
    def test_rank_change_timeline(self, rank_change_new_timeline_serializer_mock):
        officer = OfficerFactory(id=123, appointed_date=date(2001, 2, 3))

        salary_1 = SalaryFactory(
            year=2001, rank='Police Officer', officer=officer, rank_changed=True, spp_date=date(2001, 5, 3)
        )
        salary_2 = SalaryFactory(
            year=2002, rank='Senior Police Officer', officer=officer, rank_changed=True, spp_date=date(2002, 5, 3)
        )
        SalaryFactory(
            year=2001, rank='Junior Police Officer', officer=officer, rank_changed=True, spp_date=date(2001, 2, 3)
        )
        SalaryFactory(
            year=2003, rank='Senior Police Officer', officer=officer, rank_changed=False, spp_date=date(2003, 5, 3)
        )

        unit_1 = PoliceUnitFactory(unit_name='001', description='District 001')
        unit_2 = PoliceUnitFactory(unit_name='002', description='District 002')
        OfficerHistoryFactory(
            officer=officer, unit=unit_1, effective_date=date(2001, 1, 3), end_date=date(2002, 1, 2)
        )
        OfficerHistoryFactory(
            officer=officer, unit=unit_2, effective_date=date(2002, 1, 3), end_date=date(2018, 1, 3)
        )

        other_officer = OfficerFactory(id=456)
        SalaryFactory(
            year=2001, rank='Police Officer', officer=other_officer, rank_changed=True, spp_date=date(2001, 5, 3)
        )

        expect(OfficerTimelineQuery(officer)._rank_change_timeline).to.eq([{'id': 1}, {'id': 2}])

        rank_change_timeline_queryset_arg = rank_change_new_timeline_serializer_mock.call_args[0][0]

        salary_1_arg, salary_2_arg = rank_change_timeline_queryset_arg

        expect(salary_1_arg.id).to.eq(salary_1.id)
        expect(salary_1_arg.unit_name).to.eq('001')
        expect(salary_1_arg.unit_description).to.eq('District 001')

        expect(salary_2_arg.id).to.eq(salary_2.id)
        expect(salary_2_arg.unit_name).to.eq('002')
        expect(salary_2_arg.unit_description).to.eq('District 002')

    @patch(
        'officers.queries.RankChangeNewTimelineSerializer',
        return_value=Mock(data=[{'id': 1}])
    )
    def test_rank_change_timeline_no_officer_appointed_date(self, rank_change_new_timeline_serializer_mock):
        officer = OfficerFactory(id=123, appointed_date=None)

        salary = SalaryFactory(
            year=2001, rank='Police Officer', officer=officer, rank_changed=True, spp_date=date(2001, 5, 3)
        )

        expect(OfficerTimelineQuery(officer)._rank_change_timeline).to.eq([{'id': 1}])

        rank_change_timeline_queryset_arg = rank_change_new_timeline_serializer_mock.call_args[0][0]

        salary_arg, = rank_change_timeline_queryset_arg
        expect(salary_arg.id).to.eq(salary.id)

    @patch(
        'officers.queries.JoinedNewTimelineSerializer',
        return_value=Mock(data=[{'id': 1}])
    )
    def test_join_timeline(self, join_new_timeline_serializer_mock):
        officer = OfficerFactory(id=123, appointed_date=date(2001, 2, 3))

        SalaryFactory(
            year=2001, rank='Police Officer', officer=officer, rank_changed=True, spp_date=date(2001, 2, 3)
        )

        unit = PoliceUnitFactory(unit_name='001', description='District 001')
        OfficerHistoryFactory(
            officer=officer, unit=unit, effective_date=date(2001, 1, 3), end_date=date(2001, 2, 3)
        )

        expect(OfficerTimelineQuery(officer)._join_timeline).to.eq([{'id': 1}])

        join_timeline_queryset_arg = join_new_timeline_serializer_mock.call_args[0][0]
        officer_arg, = join_timeline_queryset_arg

        expect(officer_arg.id).to.eq(officer.id)
        expect(officer_arg.unit_name).to.eq('001')
        expect(officer_arg.unit_description).to.eq('District 001')
        expect(officer_arg.rank_name).to.eq('Police Officer')

    def test_join_timeline_no_officer_appointed_date(self):
        officer = OfficerFactory(id=123, appointed_date=None)

        expect(OfficerTimelineQuery(officer)._join_timeline).to.eq([])

    @patch(
        'officers.queries.AwardNewTimelineSerializer',
        return_value=Mock(data=[{'id': 1}, {'id': 2}])
    )
    def test_award_timeline(self, award_new_timeline_serializer_mock):
        officer = OfficerFactory(id=123, appointed_date=date(2001, 2, 3))

        award_1 = AwardFactory(officer=officer, start_date=date(2002, 1, 3), award_type='Honored Police Star')
        award_2 = AwardFactory(officer=officer, start_date=date(2003, 1, 5), award_type='Life Saving Award')
        AwardFactory(officer=officer, start_date=date(2007, 2, 3), award_type='Complimentary Letter')
        AwardFactory(officer=officer, start_date=date(2008, 2, 3), award_type='Department Commendation')
        AwardFactory(officer=officer, start_date=date(2011, 2, 3), award_type='Citizen Honorable Mention')
        AwardFactory(officer=officer, start_date=None, award_type='Life Saving')

        unit_1 = PoliceUnitFactory(unit_name='001', description='District 001')
        unit_2 = PoliceUnitFactory(unit_name='002', description='District 002')
        OfficerHistoryFactory(
            officer=officer, unit=unit_1, effective_date=date(2002, 1, 3), end_date=date(2003, 1, 2)
        )
        OfficerHistoryFactory(
            officer=officer, unit=unit_2, effective_date=date(2003, 1, 3), end_date=date(2018, 1, 3)
        )
        SalaryFactory(
            year=2001, rank='Police Officer', officer=officer, rank_changed=True, spp_date=date(2001, 5, 3)
        )
        SalaryFactory(
            year=2002, rank='Senior Police Officer', officer=officer, rank_changed=True, spp_date=date(2002, 5, 3)
        )

        expect(OfficerTimelineQuery(officer)._award_timeline).to.eq([{'id': 1}, {'id': 2}])

        award_timeline_queryset_arg = award_new_timeline_serializer_mock.call_args[0][0]
        award_1_arg, award_2_arg = sorted(award_timeline_queryset_arg, key=attrgetter('id'))

        expect(award_1_arg.id).to.eq(award_1.id)
        expect(award_1_arg.unit_name).to.eq('001')
        expect(award_1_arg.unit_description).to.eq('District 001')
        expect(award_1_arg.rank_name).to.eq('Police Officer')

        expect(award_2_arg.id).to.eq(award_2.id)
        expect(award_2_arg.unit_name).to.eq('002')
        expect(award_2_arg.unit_description).to.eq('District 002')
        expect(award_2_arg.rank_name).to.eq('Senior Police Officer')

    @patch(
        'officers.queries.TRRNewTimelineSerializer',
        return_value=Mock(data=[{'id': 1}, {'id': 2}])
    )
    def test_trr_timeline(self, trr_new_timeline_serializer_mock):
        officer = OfficerFactory(id=123, appointed_date=date(2001, 2, 3))

        trr_1 = TRRFactory(officer=officer, trr_datetime=datetime(2002, 1, 4, tzinfo=pytz.utc))
        trr_2 = TRRFactory(officer=officer, trr_datetime=datetime(2003, 1, 5, tzinfo=pytz.utc))

        unit_1 = PoliceUnitFactory(unit_name='001', description='District 001')
        unit_2 = PoliceUnitFactory(unit_name='002', description='District 002')
        OfficerHistoryFactory(
            officer=officer, unit=unit_1, effective_date=date(2002, 1, 3), end_date=date(2003, 1, 2)
        )
        OfficerHistoryFactory(
            officer=officer, unit=unit_2, effective_date=date(2003, 1, 3), end_date=date(2018, 1, 3)
        )
        SalaryFactory(
            year=2001, rank='Police Officer', officer=officer, rank_changed=True, spp_date=date(2001, 5, 3)
        )
        SalaryFactory(
            year=2002, rank='Senior Police Officer', officer=officer, rank_changed=True, spp_date=date(2002, 5, 3)
        )

        expect(OfficerTimelineQuery(officer)._trr_timeline).to.eq([{'id': 1}, {'id': 2}])

        trr_timeline_queryset_arg = trr_new_timeline_serializer_mock.call_args[0][0]
        trr_1_arg, trr_2_arg = sorted(trr_timeline_queryset_arg, key=attrgetter('id'))

        expect(trr_1_arg.id).to.eq(trr_1.id)
        expect(trr_1_arg.unit_name).to.eq('001')
        expect(trr_1_arg.unit_description).to.eq('District 001')
        expect(trr_1_arg.rank_name).to.eq('Police Officer')

        expect(trr_2_arg.id).to.eq(trr_2.id)
        expect(trr_2_arg.unit_name).to.eq('002')
        expect(trr_2_arg.unit_description).to.eq('District 002')
        expect(trr_2_arg.rank_name).to.eq('Senior Police Officer')

    @patch(
        'officers.queries.OfficerTimelineQuery._cr_timeline',
        new_callable=PropertyMock,
        return_value=[
            {'id': 1, 'date_sort': date(2000, 1, 1), 'priority_sort': 30},
            {'id': 2, 'date_sort': date(2001, 1, 2), 'priority_sort': 30},
        ]
    )
    @patch(
        'officers.queries.OfficerTimelineQuery._unit_change_timeline',
        new_callable=PropertyMock,
        return_value=[
            {'id': 3, 'date_sort': date(2000, 1, 2), 'priority_sort': 20},
            {'id': 4, 'date_sort': date(2001, 1, 2), 'priority_sort': 20},
        ]
    )
    @patch(
        'officers.queries.OfficerTimelineQuery._rank_change_timeline',
        new_callable=PropertyMock,
        return_value=[
            {'id': 5, 'date_sort': date(2000, 1, 3), 'priority_sort': 25},
            {'id': 6, 'date_sort': date(2001, 1, 2), 'priority_sort': 25},
        ]
    )
    @patch(
        'officers.queries.OfficerTimelineQuery._join_timeline',
        new_callable=PropertyMock,
        return_value=[
            {'id': 7, 'date_sort': date(2000, 1, 1), 'priority_sort': 10},
        ]
    )
    @patch(
        'officers.queries.OfficerTimelineQuery._award_timeline',
        new_callable=PropertyMock,
        return_value=[
            {'id': 8, 'date_sort': date(2000, 1, 4), 'priority_sort': 40},
            {'id': 9, 'date_sort': date(2001, 1, 2), 'priority_sort': 40},
        ]
    )
    @patch(
        'officers.queries.OfficerTimelineQuery._trr_timeline',
        new_callable=PropertyMock,
        return_value=[
            {'id': 10, 'date_sort': date(2000, 1, 4), 'priority_sort': 50},
            {'id': 11, 'date_sort': date(2001, 1, 2), 'priority_sort': 50},
        ]
    )
    def test_execute(self, _trr, _award, _join, _rank, _unit, _cr):
        sorted_timeline = OfficerTimelineQuery(None).execute()
        sorted_timeline_ids = [item['id'] for item in sorted_timeline]
        expect(sorted_timeline_ids).to.eq([11, 9, 2, 6, 4, 10, 8, 5, 3, 1, 7])
