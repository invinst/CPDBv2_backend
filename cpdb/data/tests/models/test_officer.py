import json
from datetime import date, datetime

import botocore
import pytz
from django.test.testcases import TestCase, override_settings
from freezegun import freeze_time
from mock import patch
from robber.expect import expect

from data.constants import ACTIVE_YES_CHOICE, ACTIVE_NO_CHOICE
from data.factories import (
    OfficerFactory, OfficerBadgeNumberFactory, OfficerHistoryFactory, PoliceUnitFactory,
    OfficerAllegationFactory, AllegationFactory, ComplainantFactory, AllegationCategoryFactory, SalaryFactory,
    AttachmentFileFactory, InvestigatorFactory, InvestigatorAllegationFactory,
)
from data.models import Officer


class OfficerTestCase(TestCase):
    def test_str(self):
        self.assertEqual(str(Officer(first_name='Daniel', last_name='Abate')), 'Daniel Abate')

    @override_settings(V1_URL='domain')
    def test_v1_url(self):
        first = 'first'
        last = 'last'
        url = 'domain/officer/first-last/1'
        expect(Officer(first_name=first, last_name=last, pk=1).v1_url).to.eq(url)

    def test_v2_to(self):
        officer = OfficerFactory(id=1, first_name='Jerome', last_name='Finnigan')
        expect(officer.v2_to).to.eq('/officer/1/jerome-finnigan/')

    def test_get_absolute_url(self):
        officer = OfficerFactory(id=1, first_name='Jerome', last_name='Finnigan')
        expect(officer.get_absolute_url()).to.eq('/officer/1/jerome-finnigan/')

    @freeze_time('2017-01-14 12:00:01', tz_offset=0)
    def test_current_age(self):
        expect(OfficerFactory(birth_year=1968).current_age).to.eq(49)

    def test_historic_units(self):
        officer = OfficerFactory()
        unithistory1 = OfficerHistoryFactory(officer=officer, unit__unit_name='1',
                                             unit__description='Unit 1', effective_date=date(2000, 1, 1))
        unithistory2 = OfficerHistoryFactory(officer=officer, unit__unit_name='2',
                                             unit__description='Unit 2', effective_date=date(2000, 1, 2))
        expect(officer.historic_units).to.eq([unithistory2.unit, unithistory1.unit])

    def test_historic_badges(self):
        officer = OfficerFactory()
        expect(officer.historic_badges).to.be.empty()
        OfficerBadgeNumberFactory(officer=officer, star='000', current=True)
        OfficerBadgeNumberFactory(officer=officer, star='123', current=False)
        OfficerBadgeNumberFactory(officer=officer, star='456', current=False)
        expect(list(officer.historic_badges)).to.eq(['123', '456'])

    def test_gender_display(self):
        expect(OfficerFactory(gender='M').gender_display).to.equal('Male')
        expect(OfficerFactory(gender='F').gender_display).to.equal('Female')
        expect(OfficerFactory(gender='X').gender_display).to.equal('X')

    def test_gender_display_keyerror(self):
        expect(OfficerFactory(gender='').gender_display).to.equal('')

    def test_abbr_name(self):
        officer = OfficerFactory(first_name='Michel', last_name='Foo')
        expect(officer.abbr_name).to.eq('M. Foo')

    def test_visual_token_background_color(self):
        crs_colors = [
            (0, '#f5f4f4'),
            (3, '#edf0fa'),
            (7, '#d4e2f4'),
            (20, '#c6d4ec'),
            (30, '#aec9e8'),
            (45, '#90b1f5')
        ]
        for cr_count, color in crs_colors:
            officer = OfficerFactory(allegation_count=cr_count)
            expect(officer.visual_token_background_color).to.eq(color)

    def test_get_unit_by_date(self):
        officer = OfficerFactory()
        unit_100 = PoliceUnitFactory()
        unit_101 = PoliceUnitFactory()
        OfficerHistoryFactory(
            officer=officer,
            unit=unit_100,
            effective_date=date(2000, 1, 1),
            end_date=date(2005, 12, 31),
        )
        OfficerHistoryFactory(
            officer=officer,
            unit=unit_101,
            effective_date=date(2006, 1, 1),
            end_date=date(2010, 12, 31),
        )
        expect(officer.get_unit_by_date(date(1999, 1, 1))).to.be.none()
        expect(officer.get_unit_by_date(date(2001, 1, 1))).to.eq(unit_100)
        expect(officer.get_unit_by_date(date(2007, 1, 1))).to.eq(unit_101)
        expect(officer.get_unit_by_date(date(2011, 1, 1))).to.be.none()

    def test_complaint_category_aggregation(self):
        officer = OfficerFactory()

        allegation_category = AllegationCategoryFactory(category='Use of Force')
        OfficerAllegationFactory(
            officer=officer,
            allegation=AllegationFactory(),
            allegation_category=allegation_category,
            start_date=None,
            final_finding='NS'
        )
        OfficerAllegationFactory(
            officer=officer,
            allegation=AllegationFactory(),
            allegation_category=allegation_category,
            start_date=date(
                2010, 1, 1),
            final_finding='NS'
        )
        OfficerAllegationFactory(
            officer=officer,
            allegation=AllegationFactory(),
            allegation_category=allegation_category,
            start_date=date(
                2011, 1, 1),
            final_finding='SU'
        )

        expect(officer.complaint_category_aggregation).to.eq([
            {
                'name': 'Use of Force',
                'count': 3,
                'sustained_count': 1,
                'items': [
                    {
                        'year': 2010,
                        'count': 1,
                        'sustained_count': 0,
                        'name': 'Use of Force'
                    }, {
                        'year': 2011,
                        'count': 1,
                        'sustained_count': 1,
                        'name': 'Use of Force'
                    }
                ]
            }
        ])

    def test_complainant_race_aggregation(self):
        officer = OfficerFactory()

        allegation1 = AllegationFactory()
        allegation2 = AllegationFactory()
        allegation3 = AllegationFactory()
        OfficerAllegationFactory(
            officer=officer, allegation=allegation1, start_date=date(2010, 1, 1), final_finding='SU'
        )
        OfficerAllegationFactory(
            officer=officer, allegation=allegation2, start_date=date(2011, 1, 1), final_finding='NS'
        )
        OfficerAllegationFactory(
            officer=officer, allegation=allegation3, start_date=None, final_finding='NS'
        )
        ComplainantFactory(allegation=allegation1, race='White')
        ComplainantFactory(allegation=allegation2, race='')
        ComplainantFactory(allegation=allegation3, race='White')

        expect(officer.complainant_race_aggregation).to.eq([
            {
                'name': 'White',
                'count': 2,
                'sustained_count': 1,
                'items': [
                    {
                        'year': 2010,
                        'count': 1,
                        'sustained_count': 1,
                        'name': 'White'
                    }
                ]
            },
            {
                'name': 'Unknown',
                'count': 1,
                'sustained_count': 0,
                'items': [
                    {
                        'year': 2011,
                        'count': 1,
                        'sustained_count': 0,
                        'name': 'Unknown'
                    }
                ]
            }
        ])

    def test_complainant_race_aggregation_no_complainant(self):
        officer = OfficerFactory()
        expect(officer.complainant_race_aggregation).to.eq([])

    def test_complainant_age_aggregation(self):
        officer = OfficerFactory()

        allegation1 = AllegationFactory()
        allegation2 = AllegationFactory()
        OfficerAllegationFactory(
            officer=officer, allegation=allegation1, start_date=date(2010, 1, 1), final_finding='SU'
        )
        OfficerAllegationFactory(
            officer=officer, allegation=allegation2, start_date=date(2011, 1, 1), final_finding='NS'
        )
        ComplainantFactory(allegation=allegation1, age=23)
        ComplainantFactory(allegation=allegation2, age=None)

        expect(officer.complainant_age_aggregation).to.eq([
            {
                'name': '21-30',
                'count': 1,
                'sustained_count': 1,
                'items': [
                    {
                        'year': 2010,
                        'count': 1,
                        'sustained_count': 1,
                        'name': '21-30'
                    }
                ]
            },
            {
                'name': 'Unknown',
                'count': 1,
                'sustained_count': 0,
                'items': [
                    {
                        'year': 2011,
                        'count': 1,
                        'sustained_count': 0,
                        'name': 'Unknown'
                    }
                ]
            }
        ])

    def test_complainant_gender_aggregation(self):
        officer = OfficerFactory()
        allegation1 = AllegationFactory()
        allegation2 = AllegationFactory()
        OfficerAllegationFactory(
            officer=officer, allegation=allegation1, start_date=date(2010, 1, 1), final_finding='SU'
        )
        OfficerAllegationFactory(
            officer=officer, allegation=allegation2, start_date=date(2011, 1, 1), final_finding='NS'
        )
        ComplainantFactory(allegation=allegation1, gender='F')
        ComplainantFactory(allegation=allegation2, gender='')
        expect(officer.complainant_gender_aggregation).to.eq([
            {
                'name': 'Female',
                'count': 1,
                'sustained_count': 1,
                'items': [
                    {
                        'year': 2010,
                        'count': 1,
                        'sustained_count': 1,
                        'name': 'Female'
                    }
                ]
            },
            {
                'name': 'Unknown',
                'count': 1,
                'sustained_count': 0,
                'items': [
                    {
                        'year': 2011,
                        'count': 1,
                        'sustained_count': 0,
                        'name': 'Unknown'
                    }
                ]
            }
        ])

    def test_complainant_gender_aggregation_no_complainant(self):
        officer = OfficerFactory()
        expect(officer.complainant_gender_aggregation).to.eq([])

    def test_coaccusals(self):
        officer0 = OfficerFactory()
        officer1 = OfficerFactory()
        officer2 = OfficerFactory()
        allegation0 = AllegationFactory()
        allegation1 = AllegationFactory()
        allegation2 = AllegationFactory()
        OfficerAllegationFactory(officer=officer0, allegation=allegation0)
        OfficerAllegationFactory(officer=officer0, allegation=allegation1)
        OfficerAllegationFactory(officer=officer0, allegation=allegation2)
        OfficerAllegationFactory(officer=officer1, allegation=allegation0)
        OfficerAllegationFactory(officer=officer1, allegation=allegation1)
        OfficerAllegationFactory(officer=officer2, allegation=allegation2)

        coaccusals = list(officer0.coaccusals)
        expect(coaccusals).to.have.length(2)
        expect(coaccusals).to.contain(officer1)
        expect(coaccusals).to.contain(officer2)

        expect(coaccusals[coaccusals.index(officer1)].coaccusal_count).to.eq(2)
        expect(coaccusals[coaccusals.index(officer2)].coaccusal_count).to.eq(1)

    def test_rank_histories(self):
        officer = OfficerFactory()
        SalaryFactory(
            officer=officer, salary=5000, year=2005, rank='Police Officer', spp_date=date(2005, 1, 1),
            start_date=date(2005, 1, 1)
        )
        SalaryFactory(
            officer=officer, salary=10000, year=2006, rank='Police Officer', spp_date=date(2005, 1, 1),
            start_date=date(2005, 1, 1)
        )
        SalaryFactory(
            officer=officer, salary=10000, year=2006, rank='Police Officer', spp_date=None,
            start_date=date(2005, 1, 1)
        )
        SalaryFactory(
            officer=officer, salary=15000, year=2007, rank='Police Officer', spp_date=date(2005, 1, 1),
            start_date=date(2005, 1, 1)
        )
        SalaryFactory(
            officer=officer, salary=20000, year=2008, rank='Sergeant', spp_date=date(2008, 1, 1),
            start_date=date(2005, 1, 1)
        )
        SalaryFactory(
            officer=officer, salary=25000, year=2009, rank='Sergeant', spp_date=date(2008, 1, 1),
            start_date=date(2005, 1, 1)
        )
        expect(officer.rank_histories).to.eq([{
            'date': date(2005, 1, 1),
            'rank': 'Police Officer'
        }, {
            'date': date(2008, 1, 1),
            'rank': 'Sergeant'
        }])

    def test_rank_histories_with_no_salary(self):
        officer = OfficerFactory()
        expect(officer.rank_histories).to.eq([])

    def test_get_rank_by_date(self):
        officer = OfficerFactory()
        SalaryFactory(
            officer=officer, salary=5000, year=2005, rank='Police Officer', spp_date=date(2005, 1, 1),
            start_date=date(2005, 1, 1)
        )
        SalaryFactory(
            officer=officer, salary=10000, year=2006, rank='Police Officer', spp_date=date(2005, 1, 1),
            start_date=date(2005, 1, 1)
        )
        SalaryFactory(
            officer=officer, salary=15000, year=2007, rank='Police Officer', spp_date=date(2005, 1, 1),
            start_date=date(2005, 1, 1)
        )
        SalaryFactory(
            officer=officer, salary=20000, year=2008, rank='Sergeant', spp_date=date(2008, 1, 1),
            start_date=date(2005, 1, 1)
        )
        SalaryFactory(
            officer=officer, salary=25000, year=2009, rank='Sergeant', spp_date=date(2008, 1, 1),
            start_date=date(2005, 1, 1)
        )
        expect(officer.get_rank_by_date(None)).to.eq(None)
        expect(officer.get_rank_by_date(date(2007, 1, 1))).to.eq('Police Officer')
        expect(officer.get_rank_by_date(datetime(2007, 1, 1, tzinfo=pytz.utc))).to.eq('Police Officer')
        expect(officer.get_rank_by_date(date(2005, 1, 1))).to.eq('Police Officer')
        expect(officer.get_rank_by_date(date(2009, 1, 1))).to.eq('Sergeant')
        expect(officer.get_rank_by_date(date(2004, 1, 1))).to.be.none()

    def test_get_rank_by_date_with_empty_rank_histories(self):
        officer = OfficerFactory()
        expect(officer.get_rank_by_date(date(2007, 1, 1))).to.be.none()

    def test_get_active_officers(self):
        officer = OfficerFactory(rank='Officer', active=ACTIVE_YES_CHOICE)
        OfficerFactory(rank='Officer', active=ACTIVE_YES_CHOICE)
        OfficerFactory(rank='Officer', active=ACTIVE_NO_CHOICE)
        OfficerFactory(rank='Senior Police Officer')
        OfficerFactory(rank='')
        SalaryFactory(rank='Police Officer', officer=officer)

        expect(Officer.get_active_officers(rank='Officer')).to.have.length(2)
        expect(Officer.get_active_officers(rank='Police Officer')).to.have.length(0)

    def test_get_officers_most_complaints(self):
        officer123 = OfficerFactory(
            id=123,
            rank='Officer',
            first_name='Jerome',
            last_name='Finnigan',
            allegation_count=2,
        )
        officer456 = OfficerFactory(
            id=456,
            rank='Officer',
            first_name='Ellis',
            last_name='Skol',
            allegation_count=1,
        )
        OfficerFactory(
            id=789,
            rank='Senior Police Officer',
            first_name='Raymond',
            last_name='Piwinicki',
            allegation_count=0,
        )

        expect(list(Officer.get_officers_most_complaints(rank='Officer'))).to.eq([
            officer123, officer456
        ])

    def test_allegation_attachments(self):
        allegation = AllegationFactory(crid='123')
        attachment_1 = AttachmentFileFactory(
            allegation=allegation, source_type='DOCUMENTCLOUD')
        attachment_2 = AttachmentFileFactory(
            allegation=allegation, source_type='PORTAL_COPA_DOCUMENTCLOUD')
        AttachmentFileFactory(
            allegation=allegation, source_type='PORTAL_COPA_DOCUMENTCLOUD', show=False)
        AttachmentFileFactory(allegation=allegation, source_type='COPA')
        allegation_456 = AllegationFactory(crid='456')
        AttachmentFileFactory(
            allegation=allegation_456, source_type='DOCUMENTCLOUD')
        AttachmentFileFactory(
            allegation=allegation_456, source_type='PORTAL_COPA_DOCUMENTCLOUD')
        AttachmentFileFactory(
            allegation=allegation_456, source_type='PORTAL_COPA_DOCUMENTCLOUD', show=False)

        officer = OfficerFactory(id=1)
        OfficerAllegationFactory(officer=officer, allegation=allegation)

        expect({attachment.id for attachment in officer.allegation_attachments}).to.eq({
            attachment_1.id, attachment_2.id
        })

    def test_investigator_attachments(self):
        allegation = AllegationFactory(crid='123')
        allegation_456 = AllegationFactory(crid='456')
        attachment_1 = AttachmentFileFactory(allegation=allegation, source_type='DOCUMENTCLOUD')
        attachment_2 = AttachmentFileFactory(allegation=allegation, source_type='PORTAL_COPA_DOCUMENTCLOUD')
        AttachmentFileFactory(allegation=allegation, source_type='PORTAL_COPA_DOCUMENTCLOUD', show=False)
        AttachmentFileFactory(allegation=allegation, source_type='COPA')
        AttachmentFileFactory(allegation=allegation, source_type='COPA', show=False)
        AttachmentFileFactory(allegation=allegation_456, source_type='DOCUMENTCLOUD')
        AttachmentFileFactory(allegation=allegation_456, source_type='PORTAL_COPA_DOCUMENTCLOUD')
        AttachmentFileFactory(allegation=allegation_456, source_type='PORTAL_COPA_DOCUMENTCLOUD', show=False)

        investigator = InvestigatorFactory(officer=OfficerFactory(id=1))
        InvestigatorAllegationFactory(allegation=allegation, investigator=investigator)

        expect({attachment.id for attachment in investigator.officer.investigator_attachments}).to.eq({
            attachment_1.id, attachment_2.id
        })

    @override_settings(S3_BUCKET_ZIP_DIRECTORY='zip')
    def test_get_zip_filename(self):
        officer = OfficerFactory(id=1, first_name='Jerome', last_name='Finnigan')
        expect(officer.get_zip_filename(with_docs=False)).to.eq('zip/Jerome_Finnigan.zip')
        expect(officer.get_zip_filename(with_docs=True)).to.eq('zip_with_docs/Jerome_Finnigan_with_docs.zip')

    @override_settings(S3_BUCKET_ZIP_DIRECTORY='zip', S3_BUCKET_OFFICER_CONTENT='officer_content_bucket')
    @patch('data.models.officer.aws')
    def test_check_zip_file_exist(self, aws_mock):
        aws_mock.s3.get_object.return_value = {}
        officer = OfficerFactory(id=1, first_name='Jerome', last_name='Finnigan')

        expect(officer.check_zip_file_exist(with_docs=False)).to.be.true()
        expect(aws_mock.s3.get_object).to.be.called_with(
            Bucket='officer_content_bucket',
            Key='zip/Jerome_Finnigan.zip'
        )

        expect(officer.check_zip_file_exist(with_docs=True)).to.be.true()
        expect(aws_mock.s3.get_object).to.be.called_with(
            Bucket='officer_content_bucket',
            Key='zip_with_docs/Jerome_Finnigan_with_docs.zip'
        )

    @override_settings(S3_BUCKET_ZIP_DIRECTORY='zip', S3_BUCKET_OFFICER_CONTENT='officer_content_bucket')
    @patch('data.models.officer.aws')
    def test_check_zip_file_exist_return_false(self, aws_mock):
        exception = botocore.exceptions.ClientError(
            error_response={'Error': {'Code': 'NoSuchKey'}},
            operation_name='get_object'
        )
        aws_mock.s3.get_object.side_effect = exception
        officer = OfficerFactory(first_name='Jerome', last_name='Finnigan')

        expect(officer.check_zip_file_exist(with_docs=False)).to.be.false()
        expect(officer.check_zip_file_exist(with_docs=True)).to.be.false()

    @override_settings(S3_BUCKET_ZIP_DIRECTORY='zip', S3_BUCKET_OFFICER_CONTENT='officer_content_bucket')
    @patch('data.models.officer.aws')
    def test_check_zip_file_exist_raise_exception(self, aws_mock):
        client_exception = botocore.exceptions.ClientError(
            error_response={'Error': {'Code': 'NoSuchBucket'}},
            operation_name='get_object'
        )
        other_exception = Exception('some other exception')

        aws_mock.s3.get_object.side_effect = [client_exception, other_exception]
        officer = OfficerFactory(first_name='Jerome', last_name='Finnigan')

        expect(lambda: officer.check_zip_file_exist(with_docs=False)).to.throw(botocore.exceptions.ClientError)
        expect(lambda: officer.check_zip_file_exist(with_docs=True)).to.throw(Exception)

    @override_settings(
        S3_BUCKET_OFFICER_CONTENT='officer_content_bucket',
        S3_BUCKET_ZIP_DIRECTORY='zip',
        S3_BUCKET_XLSX_DIRECTORY='xlsx',
        S3_BUCKET_PDF_DIRECTORY='pdf',
        LAMBDA_FUNCTION_CREATE_OFFICER_ZIP_FILE='createOfficerZipFileTest'
    )
    @patch('data.models.officer.aws')
    def test_invoke_create_zip(self, aws_mock):
        exception = botocore.exceptions.ClientError(
            error_response={'Error': {'Code': 'NoSuchKey'}},
            operation_name='get_object'
        )
        aws_mock.s3.get_object.side_effect = exception

        allegation = AllegationFactory(crid='1')
        allegation_456 = AllegationFactory(crid='456')
        AttachmentFileFactory(
            allegation=allegation,
            source_type='DOCUMENTCLOUD',
            external_id='ABC',
            title='allegation 1 attachment'
        )
        AttachmentFileFactory(allegation=allegation, source_type='COPA')
        AttachmentFileFactory(allegation=allegation_456, source_type='DOCUMENTCLOUD')
        AttachmentFileFactory(allegation=allegation_456, source_type='PORTAL_COPA_DOCUMENTCLOUD')

        officer = OfficerFactory(id=1, first_name='Jerome', last_name='Finnigan')
        OfficerAllegationFactory(officer=officer, allegation=allegation)

        allegation_2 = AllegationFactory(crid='2')
        allegation_789 = AllegationFactory(crid='789')
        AttachmentFileFactory(
            allegation=allegation_2,
            source_type='DOCUMENTCLOUD',
            external_id='XYZ',
            title='allegation 2 attachment'
        )
        AttachmentFileFactory(allegation=allegation_2, source_type='COPA')
        AttachmentFileFactory(allegation=allegation_789, source_type='DOCUMENTCLOUD')
        AttachmentFileFactory(allegation=allegation_789, source_type='PORTAL_COPA_DOCUMENTCLOUD')

        investigator = InvestigatorFactory(officer=officer)
        InvestigatorAllegationFactory(allegation=allegation_2, investigator=investigator)

        officer.invoke_create_zip(with_docs=True)

        expect(aws_mock.s3.get_object).to.be.called_with(
            Bucket='officer_content_bucket',
            Key='zip_with_docs/Jerome_Finnigan_with_docs.zip'
        )
        _, kwargs = aws_mock.lambda_client.invoke_async.call_args
        expect(kwargs['FunctionName']).to.eq('createOfficerZipFileTest')
        expect(json.loads(kwargs['InvokeArgs'])).to.eq({
            'key': 'zip_with_docs/Jerome_Finnigan_with_docs.zip',
            'bucket': 'officer_content_bucket',
            'file_map': {
                'xlsx/1/accused.xlsx': 'accused.xlsx',
                'xlsx/1/use_of_force.xlsx': 'use_of_force.xlsx',
                'xlsx/1/investigator.xlsx': 'investigator.xlsx',
                'xlsx/1/documents.xlsx': 'documents.xlsx',
                'pdf/ABC': f'documents/allegation 1 attachment.pdf',
                'pdf/XYZ': f'investigators/allegation 2 attachment.pdf'
            }
        })

    @override_settings(
        S3_BUCKET_OFFICER_CONTENT='officer_content_bucket',
        S3_BUCKET_ZIP_DIRECTORY='zip',
        S3_BUCKET_XLSX_DIRECTORY='xlsx',
        S3_BUCKET_PDF_DIRECTORY='pdf',
        LAMBDA_FUNCTION_CREATE_OFFICER_ZIP_FILE='createOfficerZipFileTest'
    )
    @patch('data.models.officer.aws')
    def test_invoke_create_zip_without_docs(self, aws_mock):
        exception = botocore.exceptions.ClientError(
            error_response={'Error': {'Code': 'NoSuchKey'}},
            operation_name='get_object'
        )
        aws_mock.s3.get_object.side_effect = exception

        allegation = AllegationFactory(crid='1')
        allegation_456 = AllegationFactory(crid='456')
        AttachmentFileFactory(
            allegation=allegation,
            source_type='DOCUMENTCLOUD',
            external_id='ABC',
            title='allegation 1 attachment'
        )
        AttachmentFileFactory(allegation=allegation, source_type='COPA')
        AttachmentFileFactory(allegation=allegation_456, source_type='DOCUMENTCLOUD')
        AttachmentFileFactory(allegation=allegation_456, source_type='PORTAL_COPA_DOCUMENTCLOUD')

        officer = OfficerFactory(id=1, first_name='Jerome', last_name='Finnigan')
        OfficerAllegationFactory(officer=officer, allegation=allegation)

        allegation_2 = AllegationFactory(crid='2')
        allegation_789 = AllegationFactory(crid='789')
        AttachmentFileFactory(
            allegation=allegation_2,
            source_type='DOCUMENTCLOUD',
            external_id='XYZ',
            title='allegation 2 attachment'
        )
        AttachmentFileFactory(allegation=allegation_2, source_type='COPA')
        AttachmentFileFactory(allegation=allegation_789, source_type='DOCUMENTCLOUD')
        AttachmentFileFactory(allegation=allegation_789, source_type='PORTAL_COPA_DOCUMENTCLOUD')

        investigator = InvestigatorFactory(officer=officer)
        InvestigatorAllegationFactory(allegation=allegation_2, investigator=investigator)

        officer.invoke_create_zip(with_docs=False)

        expect(aws_mock.s3.get_object).to.be.called_with(
            Bucket='officer_content_bucket',
            Key='zip/Jerome_Finnigan.zip'
        )

        _, kwargs = aws_mock.lambda_client.invoke_async.call_args
        expect(kwargs['FunctionName']).to.eq('createOfficerZipFileTest')
        expect(json.loads(kwargs['InvokeArgs'])).to.eq({
            'key': 'zip/Jerome_Finnigan.zip',
            'bucket': 'officer_content_bucket',
            'file_map': {
                'xlsx/1/accused.xlsx': 'accused.xlsx',
                'xlsx/1/use_of_force.xlsx': 'use_of_force.xlsx',
                'xlsx/1/investigator.xlsx': 'investigator.xlsx',
                'xlsx/1/documents.xlsx': 'documents.xlsx'
            }
        })

    @override_settings(S3_BUCKET_ZIP_DIRECTORY='zip', S3_BUCKET_OFFICER_CONTENT='officer_content_bucket')
    @patch('data.models.officer.aws')
    def test_generate_presigned_zip_url(self, aws_mock):
        aws_mock.s3.generate_presigned_url.return_value = 'presigned_url'

        officer = OfficerFactory(id=1, first_name='Jerome', last_name='Finnigan')

        expect(officer.generate_presigned_zip_url(with_docs=True)).to.eq('presigned_url')
        expect(aws_mock.s3.generate_presigned_url).to.be.called_with(
            ClientMethod='get_object',
            Params={
                'Bucket': 'officer_content_bucket',
                'Key': 'zip_with_docs/Jerome_Finnigan_with_docs.zip',
            }
        )

    @override_settings(S3_BUCKET_ZIP_DIRECTORY='zip', S3_BUCKET_OFFICER_CONTENT='officer_content_bucket')
    @patch('data.models.officer.aws')
    def test_generate_presigned_zip_url_without_docs(self, aws_mock):
        aws_mock.s3.generate_presigned_url.return_value = 'presigned_url'

        officer = OfficerFactory(first_name='Jerome', last_name='Finnigan')

        expect(officer.generate_presigned_zip_url(with_docs=False)).to.eq('presigned_url')
        expect(aws_mock.s3.generate_presigned_url).to.be.called_with(
            ClientMethod='get_object',
            Params={
                'Bucket': 'officer_content_bucket',
                'Key': 'zip/Jerome_Finnigan.zip',
            }
        )
