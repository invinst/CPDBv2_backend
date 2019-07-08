from django.test.testcases import TestCase
from django.contrib.admin.sites import AdminSite
from django.test.client import RequestFactory

from robber.expect import expect

from pinboard.admin import PinboardAdmin
from pinboard.factories import PinboardFactory
from pinboard.models import Pinboard


class PinboardAdminTestCase(TestCase):
    def setUp(self):
        self.attachment_admin = PinboardAdmin(Pinboard, AdminSite())
        self.request = RequestFactory()

    def test_get_queryset(self):
        PinboardFactory(id='66ef1560', title='', description='')
        PinboardFactory(id='66ff1560', title='', description='')
        PinboardFactory(id='67ef1560', title='', description='')
        PinboardFactory(id='67ff1560', title='66 officers', description='')
        PinboardFactory(id='67af1560', title='Repeater', description='66 officers')

        queryset, use_distinct = self.attachment_admin.get_search_results(self.request, None, None)
        expect({pinboard.id for pinboard in queryset}).to.eq({
            '66ef1560', '66ff1560', '67ef1560', '67ff1560', '67af1560'
        })
        expect(use_distinct).to.be.true()

    def test_get_queryset_with_search_term(self):
        PinboardFactory(id='66ef1560', title='', description='')
        PinboardFactory(id='66ff1560', title='', description='')
        PinboardFactory(id='67ef1560', title='', description='')
        PinboardFactory(id='67ff1560', title='66 officers', description='')
        PinboardFactory(id='67af1560', title='Repeater', description='66 officers')

        queryset, use_distinct = self.attachment_admin.get_search_results(self.request, None, '66')
        expect({pinboard.id for pinboard in queryset}).to.eq({'66ef1560', '66ff1560', '67ff1560'})
        expect(use_distinct).to.be.true()

    def test_get_queryset_with_non_hex_search_term(self):
        PinboardFactory(id='66ef1560', title='', description='')
        PinboardFactory(id='66ff1560', title='', description='')
        PinboardFactory(id='67ef1560', title='', description='')
        PinboardFactory(id='67ff1560', title='66 officers', description='')
        PinboardFactory(id='67af1560', title='Repeater', description='66 officers')
        PinboardFactory(id='67bf1560', title='', description='66 officers')

        queryset, use_distinct = self.attachment_admin.get_search_results(self.request, None, 'er')
        expect({pinboard.id for pinboard in queryset}).to.eq({'67ff1560', '67af1560'})
        expect(use_distinct).to.be.true()
