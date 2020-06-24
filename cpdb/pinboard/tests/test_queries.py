from django.test import TestCase

from robber.expect import expect

from pinboard.queries import ComplaintSummaryQuery, TrrSummaryQuery, OfficersSummaryQuery, ComplainantsSummaryQuery
from pinboard.factories import PinboardFactory
from trr.factories import TRRFactory, ActionResponseFactory
from data.factories import (
    OfficerFactory,
    AllegationFactory,
    AllegationCategoryFactory,
    OfficerAllegationFactory,
    ComplainantFactory,
)


class ComplaintSummaryQueryTestCase(TestCase):
    def test_query(self):
        allegation_officer1, allegation_officer2 = OfficerFactory.create_batch(2)
        trr_officer1, trr_officer2 = OfficerFactory.create_batch(2)
        pinboard_officer1, pinboard_officer2 = OfficerFactory.create_batch(2)
        other_officer = OfficerFactory()

        pinboard_allegation1, pinboard_allegation2 = AllegationFactory.create_batch(2)
        allegation1, allegation2, allegation3, allegation4 = AllegationFactory.create_batch(4)

        trr1 = TRRFactory(officer=trr_officer1)
        trr2 = TRRFactory(officer=trr_officer2)

        allegation_category1 = AllegationCategoryFactory(category='Operation/Personnel Violations', )
        allegation_category2 = AllegationCategoryFactory(category='Illegal Search', )
        allegation_category3 = AllegationCategoryFactory(category='Verbal Abuse', )

        OfficerAllegationFactory(
            allegation=pinboard_allegation1,
            officer=allegation_officer1,
            allegation_category=allegation_category1
        )
        OfficerAllegationFactory(
            allegation=pinboard_allegation2,
            officer=allegation_officer1,
            allegation_category=allegation_category2
        )
        OfficerAllegationFactory(
            allegation=pinboard_allegation1,
            officer=allegation_officer2,
            allegation_category=allegation_category3
        )
        OfficerAllegationFactory(
            allegation=pinboard_allegation2,
            officer=allegation_officer2,
            allegation_category=allegation_category3
        )
        OfficerAllegationFactory(
            allegation=allegation3,
            officer=trr_officer1,
            allegation_category=None
        )
        OfficerAllegationFactory(
            allegation=allegation4,
            officer=trr_officer1,
            allegation_category=allegation_category1
        )
        OfficerAllegationFactory(
            allegation=pinboard_allegation1,
            officer=trr_officer1,
            allegation_category=None
        )
        OfficerAllegationFactory(
            allegation=pinboard_allegation2,
            officer=trr_officer2,
            allegation_category=None
        )
        OfficerAllegationFactory(
            allegation=pinboard_allegation2,
            officer=trr_officer2,
            allegation_category=allegation_category1
        )
        OfficerAllegationFactory(
            allegation=allegation1,
            officer=pinboard_officer1,
            allegation_category=None
        )
        OfficerAllegationFactory(
            allegation=allegation2,
            officer=pinboard_officer1,
            allegation_category=allegation_category2
        )
        OfficerAllegationFactory(
            allegation=allegation1,
            officer=other_officer,
            allegation_category=allegation_category2
        )

        pinboard = PinboardFactory(
            trrs=(trr1, trr2),
            allegations=(pinboard_allegation1, pinboard_allegation2),
            officers=(pinboard_officer1, pinboard_officer2)
        )
        expect(list(ComplaintSummaryQuery(pinboard).query())).to.eq([
            {'category': None, 'count': 4},
            {'category': 'Operation/Personnel Violations', 'count': 3},
            {'category': 'Illegal Search', 'count': 2},
            {'category': 'Verbal Abuse', 'count': 2}
        ])


class TrrSummaryQueryQueryTestCase(TestCase):
    def test_query(self):
        allegation_officer1 = OfficerFactory()
        allegation_officer2 = OfficerFactory()
        trr_officer_1 = OfficerFactory()
        trr_officer_2 = OfficerFactory()
        pinboard_officer1 = OfficerFactory()
        pinboard_officer2 = OfficerFactory()
        other_officer = OfficerFactory()

        pinboard_allegation = AllegationFactory()
        OfficerAllegationFactory(allegation=pinboard_allegation, officer=allegation_officer1)
        OfficerAllegationFactory(allegation=pinboard_allegation, officer=allegation_officer2)

        pinboard_trr1 = TRRFactory(officer=trr_officer_1)
        pinboard_trr2 = TRRFactory(officer=trr_officer_2)
        trr1 = TRRFactory(officer=allegation_officer1)
        trr2 = TRRFactory(officer=allegation_officer2)
        trr3 = TRRFactory(officer=allegation_officer2)
        trr4 = TRRFactory(officer=allegation_officer2)
        trr5 = TRRFactory(officer=pinboard_officer1)
        TRRFactory(officer=pinboard_officer2)
        other_trr1 = TRRFactory(officer=other_officer)
        other_trr2 = TRRFactory(officer=other_officer)

        ActionResponseFactory(trr=pinboard_trr1, force_type=None)
        ActionResponseFactory(trr=pinboard_trr2, force_type='Verbal Commands')
        ActionResponseFactory(trr=trr1, force_type='Physical Force - Stunning')
        ActionResponseFactory(trr=trr1, force_type=None)
        ActionResponseFactory(trr=trr2, force_type='Physical Force - Stunning')
        ActionResponseFactory(trr=trr3, force_type='Verbal Commands')
        ActionResponseFactory(trr=trr4, force_type='Physical Force - Stunning')
        ActionResponseFactory(trr=trr5, force_type='Physical Force - Stunning')
        ActionResponseFactory(trr=other_trr1, force_type='Taser')
        ActionResponseFactory(trr=other_trr2, force_type='Chemical')

        pinboard = PinboardFactory(
            trrs=(pinboard_trr1, pinboard_trr2),
            allegations=(pinboard_allegation,),
            officers=(pinboard_officer1, pinboard_officer2)
        )
        expect(list(TrrSummaryQuery(pinboard).query())).to.eq([
            {'force_type': 'Physical Force - Stunning', 'count': 4},
            {'force_type': 'Verbal Commands', 'count': 2},
            {'force_type': None, 'count': 2}
        ])


class OfficersSummaryQueryTestCase(TestCase):
    def test_query(self):
        allegation_officer1 = OfficerFactory(race='White', gender='M')
        allegation_officer2 = OfficerFactory(race='Hispanic', gender='F')
        trr_officer_1 = OfficerFactory(race='Black', gender='M')
        trr_officer_2 = OfficerFactory(race='', gender='M')
        pinboard_officer1 = OfficerFactory(race='White', gender='X')
        pinboard_officer2 = OfficerFactory(race='Black', gender='')
        OfficerFactory(race='White', gender='')
        OfficerFactory(race='Black', gender='')

        pinboard_allegation = AllegationFactory()
        OfficerAllegationFactory(allegation=pinboard_allegation, officer=allegation_officer1)
        OfficerAllegationFactory(allegation=pinboard_allegation, officer=allegation_officer2)

        pinboard_trr1 = TRRFactory(officer=trr_officer_1)
        pinboard_trr2 = TRRFactory(officer=trr_officer_2)

        pinboard = PinboardFactory(
            trrs=(pinboard_trr1, pinboard_trr2),
            allegations=(pinboard_allegation,),
            officers=(pinboard_officer1, pinboard_officer2)
        )
        query_results = dict(OfficersSummaryQuery(pinboard).query())
        expect(list(query_results['race'])).to.eq([
            {'race': 'Black', 'percentage': 0.33},
            {'race': 'White', 'percentage': 0.33},
            {'race': '', 'percentage': 0.17},
            {'race': 'Hispanic', 'percentage': 0.17}
        ])
        expect(list(query_results['gender'])).to.eq([
            {'gender': 'M', 'percentage': 0.5},
            {'gender': '', 'percentage': 0.17},
            {'gender': 'F', 'percentage': 0.17},
            {'gender': 'X', 'percentage': 0.17}
        ])


class ComplainantsSummaryQueryTestCase(TestCase):
    def test_query(self):
        trr_officer_1 = OfficerFactory()
        trr_officer_2 = OfficerFactory()
        pinboard_officer = OfficerFactory()
        other_officer = OfficerFactory()

        pinboard_allegation = AllegationFactory()
        allegation1 = AllegationFactory()
        allegation2 = AllegationFactory()
        allegation3 = AllegationFactory()
        allegation4 = AllegationFactory()
        other_allegation = AllegationFactory()

        OfficerAllegationFactory(allegation=pinboard_allegation, officer=other_officer)
        OfficerAllegationFactory(allegation=allegation1, officer=trr_officer_1)
        OfficerAllegationFactory(allegation=allegation2, officer=trr_officer_2)
        OfficerAllegationFactory(allegation=allegation3, officer=trr_officer_2)
        OfficerAllegationFactory(allegation=allegation4, officer=pinboard_officer)

        ComplainantFactory(allegation=pinboard_allegation, gender='M', race='White')
        ComplainantFactory(allegation=pinboard_allegation, gender='F', race='Black')
        ComplainantFactory(allegation=allegation1, gender='X', race='Black')
        ComplainantFactory(allegation=allegation1, gender='', race='')
        ComplainantFactory(allegation=allegation3, gender='F', race='Hispanic')
        ComplainantFactory(allegation=allegation4, gender='M', race='White')
        ComplainantFactory(allegation=other_allegation, gender='M', race='')
        ComplainantFactory(allegation=other_allegation, gender='F', race='Black')

        pinboard_trr1 = TRRFactory(officer=trr_officer_1)
        pinboard_trr2 = TRRFactory(officer=trr_officer_2)

        pinboard = PinboardFactory(
            trrs=(pinboard_trr1, pinboard_trr2),
            allegations=(pinboard_allegation,),
            officers=(pinboard_officer,)
        )
        query_results = dict(ComplainantsSummaryQuery(pinboard).query())
        expect(list(query_results['race'])).to.eq([
            {'race': 'White', 'percentage': 0.33},
            {'race': 'Black', 'percentage': 0.33},
            {'race': 'Hispanic', 'percentage': 0.17},
            {'race': '', 'percentage': 0.17}
        ])
        expect(list(query_results['gender'])).to.eq([
            {'gender': 'F', 'percentage': 0.33},
            {'gender': 'M', 'percentage': 0.33},
            {'gender': 'X', 'percentage': 0.17},
            {'gender': '', 'percentage': 0.17}
        ])
