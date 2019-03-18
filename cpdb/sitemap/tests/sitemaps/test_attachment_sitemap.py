from datetime import datetime

from django.test import TestCase
from sitemap.sitemaps.attachment_sitemap import AttachmentSitemap

from robber import expect
from freezegun import freeze_time
import pytz

from data.factories import AttachmentFileFactory


class AttachmentSitemapTestCase(TestCase):
    def test_class_properties(self):
        expect(AttachmentSitemap.changefreq).to.eq('daily')
        expect(AttachmentSitemap.priority).to.eq(0.5)

    def test_items(self):
        AttachmentFileFactory(id=1, file_type='Video', show=True)
        AttachmentFileFactory(id=9, file_type='Audio', show=True)
        AttachmentFileFactory(id=2, file_type='document', show=False)
        attachment_3 = AttachmentFileFactory(id=3, file_type='document', show=True)
        attachment_5 = AttachmentFileFactory(id=5, file_type='document', show=True)
        attachment_4 = AttachmentFileFactory(id=4, file_type='document', show=True)

        items = list(AttachmentSitemap().items())

        expect(items).to.have.length(3)
        expect(items[0]).to.eq(attachment_3)
        expect(items[1]).to.eq(attachment_4)
        expect(items[2]).to.eq(attachment_5)

    def test_lastmod(self):
        attachment = AttachmentFileFactory(id=123)
        with freeze_time(datetime(2018, 4, 4, 12, 0, 1, tzinfo=pytz.utc)):
            attachment.title = 'title'
            attachment.save()

        attachment.refresh_from_db()

        expect(AttachmentSitemap().lastmod(attachment)).to.eq(datetime(2018, 4, 4, 12, 0, 1, tzinfo=pytz.utc))
