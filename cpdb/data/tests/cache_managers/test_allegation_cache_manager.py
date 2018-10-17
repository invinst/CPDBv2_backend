from datetime import date

from django.test.testcases import TestCase

from robber import expect

from data.cache_managers import allegation_cache_manager
from data.factories import (
    AllegationFactory,
    OfficerAllegationFactory,
    AllegationCategoryFactory
)


class AllegationCacheManagerTestCase(TestCase):
    def test_coaccused_count(self):
        allegation_1 = AllegationFactory()
        allegation_2 = AllegationFactory()
        OfficerAllegationFactory.create_batch(6, allegation=allegation_1)
        allegation_cache_manager.cache_data()
        allegation_1.refresh_from_db()
        allegation_2.refresh_from_db()

        expect(allegation_1.coaccused_count).to.eq(6)
        expect(allegation_2.coaccused_count).to.eq(0)

    def test_most_common_category(self):
        allegation = AllegationFactory()
        category1, category2 = AllegationCategoryFactory.create_batch(2)

        OfficerAllegationFactory(allegation=allegation, allegation_category=category2)
        OfficerAllegationFactory.create_batch(2, allegation=allegation, allegation_category=category1)
        OfficerAllegationFactory.create_batch(3, allegation=allegation, allegation_category=None)
        allegation_cache_manager.cache_data()
        allegation.refresh_from_db()

        expect(allegation.most_common_category).to.eq(category1)

    def test_first_start_date(self):
        allegation = AllegationFactory()
        first_start_date = date(2003, 3, 20)
        OfficerAllegationFactory(allegation=allegation, start_date=None)
        OfficerAllegationFactory(allegation=allegation, start_date=first_start_date)
        allegation_cache_manager.cache_data()
        allegation.refresh_from_db()

        expect(allegation.first_start_date).to.eq(first_start_date)

    def test_first_end_date(self):
        allegation = AllegationFactory()
        first_end_date = date(2003, 3, 20)
        OfficerAllegationFactory(allegation=allegation, end_date=None)
        OfficerAllegationFactory(allegation=allegation, end_date=first_end_date)
        allegation_cache_manager.cache_data()
        allegation.refresh_from_db()

        expect(allegation.first_end_date).to.eq(first_end_date)
