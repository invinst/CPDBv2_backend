from datetime import datetime

from django.test.testcases import TestCase
from django.core.validators import ValidationError

import pytz
from robber.expect import expect

from data.factories import (
    AttachmentRequestFactory, AllegationFactory, InvestigatorAllegationFactory,
    InvestigatorFactory, OfficerBadgeNumberFactory, OfficerFactory)
from data.models import AttachmentRequest


class AttachmentRequestTestCase(TestCase):
    def test_default_status(self):
        attachment_request = AttachmentRequestFactory()
        expect(attachment_request.status).to.be.false()

    def test_str(self):
        attachment_request = AttachmentRequestFactory.build(
            allegation=AllegationFactory(crid='1111'),
            email='foo@bar.com'
        )
        expect(str(attachment_request)).to.eq('foo@bar.com - 1111')

    def test_crid(self):
        attachment_request = AttachmentRequestFactory.build(
            allegation=AllegationFactory(crid='1111'),
        )
        expect(attachment_request.crid).to.eq('1111')

    def test_email_validation(self):
        expect(lambda: AttachmentRequestFactory(email='foo')).to.throw(ValidationError)

    def test_unique_allegation_and_email(self):
        allegation = AllegationFactory()
        email = 'foo@bar.com'
        AttachmentRequestFactory(email=email, allegation=allegation)

        expect(lambda: AttachmentRequestFactory(email=email, allegation=allegation)).to.throw(ValidationError)
        expect(len(AttachmentRequest.objects.all())).to.eq(1)

    def test_investigator_names(self):
        allegation = AllegationFactory()
        investigator = InvestigatorFactory(first_name='Jerome', last_name='Finnigan')
        InvestigatorAllegationFactory(allegation=allegation, investigator=investigator)
        attachment_request = AttachmentRequestFactory(allegation=allegation)
        expect(attachment_request.investigator_names()).to.eq('Jerome Finnigan')


class AttachmentRequestManager(TestCase):
    def test_annotate_investigated_by_cpd(self):
        allegation_1 = AllegationFactory(crid='001', incident_date=datetime(2005, 12, 31, tzinfo=pytz.utc))
        allegation_2 = AllegationFactory(crid='002', incident_date=datetime(2007, 12, 31, tzinfo=pytz.utc))
        allegation_3 = AllegationFactory(crid='003', incident_date=datetime(2007, 12, 31, tzinfo=pytz.utc))
        allegation_4 = AllegationFactory(crid='004', incident_date=datetime(2007, 12, 31, tzinfo=pytz.utc))
        allegation_5 = AllegationFactory(crid='005', incident_date=datetime(2007, 12, 31, tzinfo=pytz.utc))
        allegation_6 = AllegationFactory(crid='006', incident_date=datetime(2007, 12, 31, tzinfo=pytz.utc))

        attachment_request_1 = AttachmentRequestFactory(allegation=allegation_1)
        attachment_request_2 = AttachmentRequestFactory(allegation=allegation_2)
        attachment_request_3 = AttachmentRequestFactory(allegation=allegation_3)
        attachment_request_4 = AttachmentRequestFactory(allegation=allegation_4)
        attachment_request_5 = AttachmentRequestFactory(allegation=allegation_5)
        attachment_request_6 = AttachmentRequestFactory(allegation=allegation_6)

        officer_1 = OfficerFactory()
        officer_2 = OfficerFactory()

        OfficerBadgeNumberFactory(officer=officer_2, star='12345')

        investigator_1 = InvestigatorFactory(officer=officer_1)
        investigator_2 = InvestigatorFactory(officer=officer_2)

        InvestigatorAllegationFactory(allegation=allegation_3, current_star='123456')
        InvestigatorAllegationFactory(allegation=allegation_5, current_star=None, investigator=investigator_1)
        InvestigatorAllegationFactory(allegation=allegation_6, current_star=None, investigator=investigator_2)

        expected_results = {
            attachment_request_1.id: True,
            attachment_request_2.id: False,
            attachment_request_3.id: True,
            attachment_request_4.id: False,
            attachment_request_5.id: False,
            attachment_request_6.id: True,
        }

        for attachment_request in AttachmentRequest.objects.annotate_investigated_by_cpd():
            expect(attachment_request.investigated_by_cpd).to.be.eq(expected_results[attachment_request.id])
