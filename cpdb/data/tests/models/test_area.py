from django.test.testcases import TestCase, override_settings

from robber.expect import expect

from data.factories import AreaFactory, AllegationFactory, OfficerAllegationFactory, AllegationCategoryFactory, \
    OfficerFactory


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
                'category_name': 'category_1',
                'num_allegation': 5
            }, {
                'category_name': 'category_3',
                'num_allegation': 3
            }, {
                'category_name': 'category_2',
                'num_allegation': 2
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
                'fullname': 'A B',
                'num_allegation': 5
            }, {
                'fullname': 'E F',
                'num_allegation': 3
            }, {
                'fullname': 'C D',
                'num_allegation': 2
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
    def test_v1_url_default(self):
        area = AreaFactory.build(area_type='whatever', name='abc')
        expect(area.v1_url).to.eq('domain')
