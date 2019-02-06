from urllib.error import HTTPError

from django.test import SimpleTestCase
from robber import expect

from document_cloud.services.common import get_full_text
from shared.tests.utils import create_object


class CommonTestCase(SimpleTestCase):
    def test_get_full_text(self):
        text_content = """

        something


        something

        """
        cloud_document = create_object({'full_text': text_content.encode('utf8')})
        expect(get_full_text(cloud_document)).to.eq("""something
something""")

    def test_get_full_text_raise_HTTPError_exception(self):
        class Document(object):
            @property
            def full_text(self):
                raise HTTPError('Testing url', '404', 'Testing error', None, None)

        cloud_document = Document()
        expect(get_full_text(cloud_document)).to.eq('')

    def test_get_full_text_raise_NotImplementedError_exception(self):
        class Document(object):
            @property
            def full_text(self):
                raise NotImplementedError('Testing error')

        cloud_document = Document()
        expect(get_full_text(cloud_document)).to.eq('')
