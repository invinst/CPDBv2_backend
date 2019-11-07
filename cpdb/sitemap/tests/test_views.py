from datetime import datetime

from django.test import TestCase, Client
from django.utils import timezone
from rest_framework import status

from freezegun import freeze_time
from robber import expect

from data.factories import OfficerFactory, AllegationFactory, PoliceUnitFactory, AttachmentFileFactory
from trr.factories import TRRFactory


@freeze_time(datetime(2019, 3, 18, tzinfo=timezone.get_default_timezone()))
class SitemapViewSetTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_sitemap_index_view(self):
        response = self.client.get('/sitemap.xml')
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.content.decode('utf8')).to.eq(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            '<sitemap><loc>https://example.com/sitemap-static.xml</loc></sitemap>'
            '<sitemap><loc>https://example.com/sitemap-officer.xml</loc></sitemap>'
            '<sitemap><loc>https://example.com/sitemap-allegation.xml</loc></sitemap>'
            '<sitemap><loc>https://example.com/sitemap-trr.xml</loc></sitemap>'
            '<sitemap><loc>https://example.com/sitemap-unit.xml</loc></sitemap>'
            '<sitemap><loc>https://example.com/sitemap-attachment.xml</loc></sitemap>\n'
            '</sitemapindex>\n'
        )

    def test_sitemap_static_page_view(self):
        response = self.client.get('/sitemap-static.xml')
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.content.decode('utf8')).to.eq(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            '<url>'
            '<loc>https://example.com</loc>'
            '<changefreq>daily</changefreq>'
            '<priority>0.5</priority>'
            '</url>'
            '<url>'
            '<loc>https://example.com/collaborate/</loc>'
            '<changefreq>daily</changefreq>'
            '<priority>0.5</priority>'
            '</url>'
            '<url>'
            '<loc>https://example.com/terms/</loc>'
            '<changefreq>daily</changefreq>'
            '<priority>0.5</priority>'
            '</url>\n'
            '</urlset>\n'
        )

    def test_sitemap_officer_view(self):
        OfficerFactory(id=123, first_name='Jerome', last_name='Finnigan', allegation_count=2)
        OfficerFactory(id=456, first_name='Luke', last_name='Skywalker', allegation_count=3)
        OfficerFactory(id=789, first_name='Kevin', last_name='Osborn', allegation_count=1)

        response = self.client.get('/sitemap-officer.xml')
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.content.decode('utf8')).to.eq(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            '<url>'
            '<loc>https://example.com/officer/456/luke-skywalker/</loc>'
            '<lastmod>2019-03-18</lastmod>'
            '<changefreq>daily</changefreq>'
            '<priority>0.5</priority>'
            '</url>'
            '<url>'
            '<loc>https://example.com/officer/123/jerome-finnigan/</loc>'
            '<lastmod>2019-03-18</lastmod>'
            '<changefreq>daily</changefreq>'
            '<priority>0.5</priority>'
            '</url>'
            '<url>'
            '<loc>https://example.com/officer/789/kevin-osborn/</loc>'
            '<lastmod>2019-03-18</lastmod>'
            '<changefreq>daily</changefreq>'
            '<priority>0.5</priority>'
            '</url>\n'
            '</urlset>\n'
        )

    def test_sitemap_allegation_view(self):
        AllegationFactory(crid='123', coaccused_count=2)
        AllegationFactory(crid='456', coaccused_count=3)
        AllegationFactory(crid='789', coaccused_count=1)

        response = self.client.get('/sitemap-allegation.xml')

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.content.decode('utf8')).to.eq(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            '<url>'
            '<loc>https://example.com/complaint/456/</loc>'
            '<lastmod>2019-03-18</lastmod>'
            '<changefreq>daily</changefreq>'
            '<priority>0.5</priority>'
            '</url>'
            '<url>'
            '<loc>https://example.com/complaint/123/</loc>'
            '<lastmod>2019-03-18</lastmod>'
            '<changefreq>daily</changefreq>'
            '<priority>0.5</priority>'
            '</url>'
            '<url>'
            '<loc>https://example.com/complaint/789/</loc>'
            '<lastmod>2019-03-18</lastmod>'
            '<changefreq>daily</changefreq>'
            '<priority>0.5</priority>'
            '</url>\n'
            '</urlset>\n'
        )

    def test_sitemap_trr_view(self):
        TRRFactory(id=123)
        TRRFactory(id=789)
        TRRFactory(id=456)

        response = self.client.get('/sitemap-trr.xml')

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.content.decode('utf8')).to.eq(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            '<url>'
            '<loc>https://example.com/trr/123/</loc>'
            '<lastmod>2019-03-18</lastmod>'
            '<changefreq>daily</changefreq>'
            '<priority>0.5</priority>'
            '</url>'
            '<url>'
            '<loc>https://example.com/trr/456/</loc>'
            '<lastmod>2019-03-18</lastmod>'
            '<changefreq>daily</changefreq>'
            '<priority>0.5</priority>'
            '</url>'
            '<url>'
            '<loc>https://example.com/trr/789/</loc>'
            '<lastmod>2019-03-18</lastmod>'
            '<changefreq>daily</changefreq>'
            '<priority>0.5</priority>'
            '</url>\n'
            '</urlset>\n'
        )

    def test_sitemap_unit_view(self):
        PoliceUnitFactory(id=123, unit_name='002')
        PoliceUnitFactory(id=789, unit_name='001')
        PoliceUnitFactory(id=456, unit_name='003')

        response = self.client.get('/sitemap-unit.xml')

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.content.decode('utf8')).to.eq(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            '<url>'
            '<loc>https://example.com/unit/001/</loc>'
            '<lastmod>2019-03-18</lastmod>'
            '<changefreq>daily</changefreq>'
            '<priority>0.5</priority>'
            '</url>'
            '<url>'
            '<loc>https://example.com/unit/002/</loc>'
            '<lastmod>2019-03-18</lastmod>'
            '<changefreq>daily</changefreq>'
            '<priority>0.5</priority>'
            '</url>'
            '<url>'
            '<loc>https://example.com/unit/003/</loc>'
            '<lastmod>2019-03-18</lastmod>'
            '<changefreq>daily</changefreq>'
            '<priority>0.5</priority>'
            '</url>\n'
            '</urlset>\n'
        )

    def test_sitemap_attachment_view(self):
        AttachmentFileFactory(id=1, file_type='Video', show=True)
        AttachmentFileFactory(id=9, file_type='Audio', show=True)
        AttachmentFileFactory(id=2, file_type='document', show=False)
        AttachmentFileFactory(id=3, file_type='document', show=True)
        AttachmentFileFactory(id=5, file_type='document', show=True)
        AttachmentFileFactory(id=4, file_type='document', show=True)

        response = self.client.get('/sitemap-attachment.xml')

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.content.decode('utf8')).to.eq(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            '<url>'
            '<loc>https://example.com/document/3/</loc>'
            '<lastmod>2019-03-18</lastmod>'
            '<changefreq>daily</changefreq>'
            '<priority>0.5</priority>'
            '</url>'
            '<url>'
            '<loc>https://example.com/document/4/</loc>'
            '<lastmod>2019-03-18</lastmod>'
            '<changefreq>daily</changefreq>'
            '<priority>0.5</priority>'
            '</url>'
            '<url>'
            '<loc>https://example.com/document/5/</loc>'
            '<lastmod>2019-03-18</lastmod>'
            '<changefreq>daily</changefreq>'
            '<priority>0.5</priority>'
            '</url>\n'
            '</urlset>\n'
        )

    def test_sitemap_not_exists_view(self):
        response = self.client.get('/sitemap-not_exists.xml')
        expect(response.status_code).to.eq(status.HTTP_404_NOT_FOUND)
