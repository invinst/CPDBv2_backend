from django.test.testcases import TestCase, override_settings

from robber.expect import expect

from data.factories import (AreaFactory, AllegationFactory, OfficerAllegationFactory,
                            AllegationCategoryFactory, OfficerFactory, RacePopulationFactory)
from data.models import Area


class AreaTestCase(TestCase):
    def test_allegation_count(self):
        area = AreaFactory(area_type='community', name='abc')
        AllegationFactory.create_batch(2, areas=[area])
        expect(area.allegation_count).to.eq(2)

    def test_get_most_common_complaint(self):
        area = AreaFactory(area_type='community', name='abc')
        category1 = AllegationCategoryFactory(category='category_1')
        category2 = AllegationCategoryFactory(category='category_2')
        category3 = AllegationCategoryFactory(category='category_3')
        AllegationCategoryFactory.create_batch(2)

        OfficerAllegationFactory.create_batch(5, allegation_category=category1, allegation__areas=[area])
        OfficerAllegationFactory.create_batch(2, allegation_category=category2, allegation__areas=[area])
        OfficerAllegationFactory.create_batch(3, allegation_category=category3, allegation__areas=[area])

        expect(list(area.get_most_common_complaint())).to.eq([
            {
                'id': category1.id,
                'name': 'category_1',
                'count': 5
            }, {
                'id': category3.id,
                'name': 'category_3',
                'count': 3
            }, {
                'id': category2.id,
                'name': 'category_2',
                'count': 2
            }
        ])

    def test_get_officers_most_complaints(self):
        area = AreaFactory(area_type='community', name='abc')
        officer1 = OfficerFactory(first_name='A', last_name='B')
        officer2 = OfficerFactory(first_name='C', last_name='D')
        officer3 = OfficerFactory(first_name='E', last_name='F')
        OfficerFactory.create_batch(2)

        OfficerAllegationFactory.create_batch(5, officer=officer1, allegation__areas=[area])
        OfficerAllegationFactory.create_batch(2, officer=officer2, allegation__areas=[area])
        OfficerAllegationFactory.create_batch(3, officer=officer3, allegation__areas=[area])

        expect(list(area.get_officers_most_complaints())).to.eq([
            {
                'id': officer1.id,
                'name': 'A B',
                'count': 5
            }, {
                'id': officer3.id,
                'name': 'E F',
                'count': 3
            }, {
                'id': officer2.id,
                'name': 'C D',
                'count': 2
            }
        ])

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
    def test_v1_url_for_beat_area(self):
        area = AreaFactory.build(area_type='beat', name='abc')
        url = 'domain/url-mediator/session-builder?beat=abc'
        expect(area.v1_url).to.eq(url)

    @override_settings(V1_URL='domain')
    def test_v1_url_for_police_district_area(self):
        area = AreaFactory.build(area_type='police-districts', name='abc')
        url = 'domain/url-mediator/session-builder?police_district=abc'
        expect(area.v1_url).to.eq(url)

    @override_settings(V1_URL='domain')
    def test_v1_url_for_school_ground_area(self):
        area = AreaFactory.build(area_type='school-grounds', name='abc')
        url = 'domain/url-mediator/session-builder?school_ground=abc'
        expect(area.v1_url).to.eq(url)

    @override_settings(V1_URL='domain')
    def test_v1_url_for_ward_area(self):
        area = AreaFactory.build(area_type='wards', name='abc')
        url = 'domain/url-mediator/session-builder?ward=abc'
        expect(area.v1_url).to.eq(url)

    @override_settings(V1_URL='domain')
    def test_v1_url_default(self):
        area = AreaFactory.build(area_type='whatever', name='abc')
        expect(area.v1_url).to.eq('domain')


class AreaObjectManagerTestCase(TestCase):
    def test_with_allegation_per_capita(self):
        area = AreaFactory(area_type='police-district', name='abc')
        RacePopulationFactory(race='White', count=150, area=area)
        RacePopulationFactory(race='Black', count=50, area=area)
        AllegationFactory.create_batch(4, areas=[area])

        results = Area.objects.with_allegation_per_capita() \
            .values('id', 'complaint_count', 'population', 'allegation_per_capita')
        expect(list(results)).to.eq([{
            'id': area.id,
            'population': 200,
            'complaint_count': 4,
            'allegation_per_capita': 0.02
        }])
