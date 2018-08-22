from django.test.testcases import TestCase
from robber import expect

from data.utils.url_converter import get_pdf_url


class URLConverterTestCase(TestCase):
    def test_get_pdf_url(self):
        pdf_url = get_pdf_url('https://www.documentcloud.org/documents/3518954-CRID-299780-CR.html')
        expect(pdf_url).to.eq('https://www.documentcloud.org/documents/3518954-CRID-299780-CR.pdf')
