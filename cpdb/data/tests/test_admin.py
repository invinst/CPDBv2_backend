from datetime import datetime

from django.test.testcases import TestCase
from django.contrib.admin.sites import AdminSite
from django.test.client import RequestFactory


from robber.expect import expect
import pytz

from data.admin import AttachmentRequestAdmin
from data.factories import AllegationFactory, AttachmentRequestFactory
from data.models import AttachmentRequest


class AttachmentRequestAdminTestCase(TestCase):
    def setUp(self):
        self.attachment_admin = AttachmentRequestAdmin(AttachmentRequest, AdminSite())
        self.request = RequestFactory()

    def test_get_queryset(self):
        allegation_1 = AllegationFactory(incident_date=datetime(2005, 12, 31, tzinfo=pytz.utc))
        allegation_2 = AllegationFactory(incident_date=datetime(2007, 12, 31, tzinfo=pytz.utc))

        attachment_request_1 = AttachmentRequestFactory(allegation=allegation_1)
        attachment_request_2 = AttachmentRequestFactory(allegation=allegation_2)

        expect(list(self.attachment_admin.get_queryset(self.request))).to.eq(
            [attachment_request_1, attachment_request_2]
        )

    def test_investigated_by_cpd(self):
        allegation_1 = AllegationFactory(incident_date=datetime(2005, 12, 31, tzinfo=pytz.utc))
        allegation_2 = AllegationFactory(incident_date=datetime(2007, 12, 31, tzinfo=pytz.utc))

        AttachmentRequestFactory(allegation=allegation_1)
        AttachmentRequestFactory(allegation=allegation_2)

        investigated_by_cpd_1 = self.attachment_admin.get_queryset(self.request)[0]
        investigated_by_cpd_2 = self.attachment_admin.get_queryset(self.request)[1]
        expect(self.attachment_admin.investigated_by_cpd(investigated_by_cpd_1)).to.be.true()
        expect(self.attachment_admin.investigated_by_cpd(investigated_by_cpd_2)).to.be.false()
