from django.test.testcases import TestCase
from robber import expect

from data.utils.url_converter import get_pdf_url


class URLConverterTestCase(TestCase):
    def test_get_pdf_url(self):
        pdf_url_1 = get_pdf_url('https://www.documentcloud.org/documents/3518954-CRID-299780-CR.html')
        pdf_url_2 = get_pdf_url('https://www.documentcloud.org/html/documents/html/3518954-CRID-299780-CR.html')
        pdf_url_3 = get_pdf_url('https://www.documentcloud.org/documents/3518954-CRID-299780-CR.xml')
        expect(pdf_url_1).to.eq('https://www.documentcloud.org/documents/3518954-CRID-299780-CR.pdf')
        expect(pdf_url_2).to.eq('https://www.documentcloud.org/html/documents/html/3518954-CRID-299780-CR.pdf')
        expect(pdf_url_3).to.eq('https://www.documentcloud.org/documents/3518954-CRID-299780-CR.xml')
