from django.test.testcases import TestCase

from data.models import Allegation
from data.factories import AreaFactory
from data_versioning.utils import get_many_to_many_fields, get_foreign_key_fields


class UtilsTestCase(TestCase):
    def test_get_many_to_many_fields(self):
        areas = AreaFactory.create_batch(2)
        content = {'crid': '123456', 'areas': areas}
        self.assertEqual(get_many_to_many_fields(Allegation, content), {'areas': areas})
        self.assertEqual(content, {'crid': '123456', 'areas': areas})
        self.assertEqual(get_many_to_many_fields(Allegation, content, pop=True), {'areas': areas})
        self.assertEqual(content, {'crid': '123456'})

        content = {'crid': '234567', 'areas': areas[0]}
        self.assertEqual(get_many_to_many_fields(Allegation, content), {'areas': areas[:1]})

    def test_get_many_to_many_fields_non_list_val(self):
        area = AreaFactory()
        content = {'crid': '123456', 'areas': area}
        self.assertEqual(get_many_to_many_fields(Allegation, content), {'areas': [area]})

    def test_get_foreign_key_fields(self):
        area = AreaFactory()
        content = {'crid': '123456', 'beat': area}
        self.assertEqual(get_foreign_key_fields(Allegation, content), {'beat': area})
        self.assertEqual(content, {'crid': '123456', 'beat': area})
        self.assertEqual(get_foreign_key_fields(Allegation, content, pop=True), {'beat': area})
        self.assertEqual(content, {'crid': '123456'})
