from datetime import datetime

from django.test.testcases import TestCase
from django.contrib.admin.sites import AdminSite
from django.test.client import RequestFactory

from robber.expect import expect
import pytz

from data.admin import AttachmentFileAdmin, max_tag_count
from data.factories import AllegationFactory, AttachmentFileFactory, TagFactory
from data.models import AttachmentFile


class AttachmentFileAdminTestCase(TestCase):
    def setUp(self):
        self.attachment_file_admin = AttachmentFileAdmin(AttachmentFile, AdminSite())
        self.request = RequestFactory()
        allegation_1 = AllegationFactory(incident_date=datetime(2005, 12, 31, tzinfo=pytz.utc))
        allegation_2 = AllegationFactory(incident_date=datetime(2007, 12, 31, tzinfo=pytz.utc))
        tag_1 = TagFactory(id=1, name='Tactical')
        tag_2 = TagFactory(id=2, name='Complaint')
        tag_3 = TagFactory(id=3, name='Taser')
        self.attachment_file_1 = AttachmentFileFactory(allegation=allegation_1)
        self.attachment_file_2 = AttachmentFileFactory(allegation=allegation_2)
        self.attachment_file_1.tags.set([tag_1, tag_2, tag_3])
        self.attachment_file_2.tags.set([tag_3])

    def test_get_queryset(self):
        expect(list(self.attachment_file_admin.get_queryset(self.request))).to.eq(
            [self.attachment_file_1, self.attachment_file_2]
        )

    def test_get_list_display(self):
        expect(list(self.attachment_file_admin.get_list_display(self.request))).to.eq(
            ['id', 'title', 'source_type', 'updated_at', 'tag_0', 'tag_1', 'tag_2']
        )

    def test_max_tag_count(self):
        expect(max_tag_count()).to.eq(3)

    def test_create_tag_fields(self):
        tag_0_func = self.attachment_file_admin.tag_0
        expect(str(tag_0_func(self.attachment_file_1))).to.eq('<a href=/admin/data/tag/1/change/>Tactical</a>')
        expect(str(tag_0_func(self.attachment_file_2))).to.eq('<a href=/admin/data/tag/3/change/>Taser</a>')
        expect(tag_0_func.allow_tags).to.be.true()
        expect(tag_0_func.short_description).to.eq('Tag 0')

        tag_1_func = self.attachment_file_admin.tag_1
        expect(str(tag_1_func(self.attachment_file_1))).to.eq('<a href=/admin/data/tag/2/change/>Complaint</a>')
        expect(str(tag_1_func(self.attachment_file_2))).to.eq('')
        expect(tag_1_func.allow_tags).to.be.true()
        expect(tag_1_func.short_description).to.eq('Tag 1')

        tag_2_func = self.attachment_file_admin.tag_2
        expect(str(tag_2_func(self.attachment_file_1))).to.eq('<a href=/admin/data/tag/3/change/>Taser</a>')
        expect(str(tag_2_func(self.attachment_file_2))).to.eq('')
        expect(tag_2_func.allow_tags).to.be.true()
        expect(tag_2_func.short_description).to.eq('Tag 2')
