from datetime import datetime
from mock import patch

from django.test.testcases import TestCase
from django.contrib.admin.sites import AdminSite
from django.test.client import RequestFactory

from robber.expect import expect
import pytz

from data.admin import AttachmentFileAdmin, standardize_field_name, TagListFilter
from data.factories import AllegationFactory, AttachmentFileFactory
from data.models import AttachmentFile


class AttachmentFileAdminTestCase(TestCase):
    def setUp(self):
        self.attachment_file_admin = AttachmentFileAdmin(AttachmentFile, AdminSite())
        self.request = RequestFactory()
        allegation_1 = AllegationFactory(incident_date=datetime(2005, 12, 31, tzinfo=pytz.utc))
        allegation_2 = AllegationFactory(incident_date=datetime(2007, 12, 31, tzinfo=pytz.utc))
        self.attachment_file_1 = AttachmentFileFactory(allegation=allegation_1)
        self.attachment_file_2 = AttachmentFileFactory(allegation=allegation_2)
        self.attachment_file_1.tags.set('Tactical', 'Complaint', 'Taser')
        self.attachment_file_2.tags.set('Taser')

    def test_get_queryset(self):
        expect(list(self.attachment_file_admin.get_queryset(self.request))).to.eq(
            [self.attachment_file_1, self.attachment_file_2]
        )

    def test_get_list_display(self):
        expect(list(self.attachment_file_admin.get_list_display(self.request))).to.eq(
            ['id', 'title', 'source_type', 'updated_at', 'complaint', 'tactical', 'taser']
        )

    def test_standardize_field_name(self):
        expect(standardize_field_name('This is a field name')).to.eq('this_is_a_field_name')

    def test_create_tag_fields(self):
        self.attachment_file_admin.get_list_display(self.request)

        tactical_func = self.attachment_file_admin.tactical
        expect(tactical_func(self.attachment_file_1)).to.be.true()
        expect(tactical_func(self.attachment_file_2)).to.be.false()
        expect(tactical_func.allow_tags).to.be.true()
        expect(tactical_func.short_description).to.eq('tactical')
        expect(tactical_func.boolean).to.be.true()

        complaint_func = self.attachment_file_admin.complaint
        expect(complaint_func(self.attachment_file_1)).to.be.true()
        expect(complaint_func(self.attachment_file_2)).to.be.false()
        expect(tactical_func.allow_tags).to.be.true()
        expect(tactical_func.short_description).to.eq('tactical')
        expect(tactical_func.boolean).to.be.true()

        taser_func = self.attachment_file_admin.taser
        expect(taser_func(self.attachment_file_1)).to.be.true()
        expect(taser_func(self.attachment_file_2)).to.be.true()
        expect(tactical_func.allow_tags).to.be.true()
        expect(tactical_func.short_description).to.eq('tactical')
        expect(tactical_func.boolean).to.be.true()


class TagListFilterTestCase(TestCase):
    def setUp(self):
        self.attachment_file_admin = AttachmentFileAdmin(AttachmentFile, AdminSite())
        self.request = RequestFactory()
        allegation_1 = AllegationFactory(incident_date=datetime(2005, 12, 31, tzinfo=pytz.utc))
        allegation_2 = AllegationFactory(incident_date=datetime(2007, 12, 31, tzinfo=pytz.utc))
        self.attachment_file_1 = AttachmentFileFactory(allegation=allegation_1)
        self.attachment_file_2 = AttachmentFileFactory(allegation=allegation_2)
        self.attachment_file_3 = AttachmentFileFactory(allegation=allegation_2)
        self.attachment_file_1.tags.set('Tactical', 'Complaint', 'Taser')
        self.attachment_file_2.tags.set('Taser')

    def test_lookups(self):
        tag_list_filter = TagListFilter(
            request=self.request,
            model_admin=self.attachment_file_admin,
            model=AttachmentFile,
            params='Tag'
        )
        tactical_tag = AttachmentFile.tags.all().get(name='Tactical')
        complaint_tag = AttachmentFile.tags.all().get(name='Complaint')
        taser_tag = AttachmentFile.tags.all().get(name='Taser')
        expect(tag_list_filter.lookups(self.request, self.attachment_file_admin)).to.eq(
            [['tagged', 'Tagged'], [complaint_tag, complaint_tag], [tactical_tag, tactical_tag], [taser_tag, taser_tag]]
        )

    @patch('data.admin.attachment_file_admin.TagListFilter.value', return_value='')
    def test_queryset(self, mock_value):
        tag_list_filter = TagListFilter(
            request=self.request,
            model_admin=self.attachment_file_admin,
            model=AttachmentFile,
            params='Tag'
        )
        queryset = AttachmentFile.objects.all()

        expect(list(tag_list_filter.queryset(self.request, queryset))).to.eq(
            [self.attachment_file_1, self.attachment_file_2, self.attachment_file_3]
        )

    @patch('data.admin.attachment_file_admin.TagListFilter.value', return_value='tagged')
    def test_queryset_with_tagged_filter(self, mock_value):
        tag_list_filter = TagListFilter(
            request=self.request,
            model_admin=self.attachment_file_admin,
            model=AttachmentFile,
            params='Tag'
        )
        queryset = AttachmentFile.objects.all()

        expect(list(tag_list_filter.queryset(self.request, queryset))).to.eq(
            [self.attachment_file_1, self.attachment_file_2]
        )

    @patch('data.admin.attachment_file_admin.TagListFilter.value', return_value='Complaint')
    def test_queryset_with_tag_name_filter(self, mock_value):
        tag_list_filter = TagListFilter(
            request=self.request,
            model_admin=self.attachment_file_admin,
            model=AttachmentFile,
            params='Tag'
        )
        queryset = AttachmentFile.objects.all()

        expect(list(tag_list_filter.queryset(self.request, queryset))).to.eq([self.attachment_file_1])
