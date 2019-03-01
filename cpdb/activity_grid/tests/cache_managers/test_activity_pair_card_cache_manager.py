from django.test.testcases import TestCase

from robber import expect

from activity_grid.factories import ActivityPairCardFactory
from activity_grid.cache_managers import activity_pair_card_cache_manager
from data.factories import OfficerFactory, AllegationFactory, OfficerAllegationFactory


class ActivityPairCardCacheManagerTestCase(TestCase):
    def test_cache_data(self):
        officer_1 = OfficerFactory()
        officer_2 = OfficerFactory()

        allegation_1 = AllegationFactory()
        allegation_2 = AllegationFactory()
        OfficerAllegationFactory(allegation=allegation_1, officer=officer_1)
        OfficerAllegationFactory(allegation=allegation_1, officer=officer_2)
        OfficerAllegationFactory(allegation=allegation_2, officer=officer_1)
        OfficerAllegationFactory(allegation=allegation_2, officer=officer_2)
        OfficerAllegationFactory(officer=officer_1)
        OfficerAllegationFactory(officer=officer_2)

        pair_card = ActivityPairCardFactory(
            officer1=officer_1,
            officer2=officer_2
        )
        activity_pair_card_cache_manager.cache_data()

        pair_card.refresh_from_db()
        expect(pair_card.coaccusal_count).to.eq(2)
