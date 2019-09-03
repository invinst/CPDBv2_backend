from django.test.testcases import TestCase
from django.contrib.admin.sites import AdminSite
from django.test.client import RequestFactory

from robber.expect import expect

from activity_log.admin import DocumentTagsAnalyze, DocumentTagsAnalyzeAdmin
from activity_log.factories import ActivityLogFactory
from authentication.factories import AdminUserFactory
from activity_log.constants import ADD_TAG_TO_DOCUMENT, REMOVE_TAG_FROM_DOCUMENT
from data.factories import AttachmentFileFactory


class DocumentTagsAnalyzeAdminTestCase(TestCase):
    def setUp(self):
        self.document_tags_analyze_admin = DocumentTagsAnalyzeAdmin(DocumentTagsAnalyze, AdminSite())
        self.request = RequestFactory()
        self.admin_user = AdminUserFactory(id=1, username='admin user')
        self.attachment = AttachmentFileFactory(
            id=1,
            tags=['tag3']
        )
        ActivityLogFactory(
            modified_object=self.attachment,
            action_type=ADD_TAG_TO_DOCUMENT,
            user=self.admin_user,
            data='tag1'
        )
        ActivityLogFactory(
            modified_object=self.attachment,
            action_type=ADD_TAG_TO_DOCUMENT,
            user=self.admin_user,
            data='tag2'
        )
        ActivityLogFactory(
            modified_object=self.attachment,
            action_type=REMOVE_TAG_FROM_DOCUMENT,
            user=self.admin_user,
            data='tag3'
        )

    def test_get_queryset(self):
        queryset = self.document_tags_analyze_admin.get_queryset(self.request)
        expect(list(queryset)).to.eq([self.admin_user])
        expect(queryset.first().added_tags_count).to.eq(2)
        expect(queryset.first().removed_tags_count).to.eq(1)

    def test_added_tags_count(self):
        user = self.document_tags_analyze_admin.get_queryset(self.request)[0]
        expect(self.document_tags_analyze_admin.added_tags_count(user)).to.eq(2)

    def test_removed_tags_count(self):
        user = self.document_tags_analyze_admin.get_queryset(self.request)[0]
        expect(self.document_tags_analyze_admin.removed_tags_count(user)).to.eq(1)
