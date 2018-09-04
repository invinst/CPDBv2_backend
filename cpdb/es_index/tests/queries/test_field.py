from django.test import SimpleTestCase
from django.contrib.gis.db import models

from robber import expect

from es_index.queries.field import Field
from es_index.queries.table import Table


class TestFieldPaper(models.Model):
    class Meta:
        app_label = 'es_index'


class TestFieldAuthor(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        app_label = 'es_index'


class Article(models.Model):
    name = models.CharField(max_length=255)
    allegation = models.ForeignKey(TestFieldAuthor)

    class Meta:
        app_label = 'es_index'


class FieldTestCase(SimpleTestCase):
    def setUp(self):
        self.name_field = Field(Article._meta.get_field('name'))
        self.foreign_field = Field(Article._meta.get_field('allegation'))

    def test_is_foreign_key_to(self):
        expect(
            self.foreign_field.is_foreign_key_to(Table(TestFieldAuthor))
        ).to.be.true()
        expect(
            self.foreign_field.is_foreign_key_to(Table(TestFieldPaper))
        ).to.be.false()

    def test_is_foreign_key(self):
        expect(self.foreign_field.is_foreign_key()).to.be.true()
        expect(
            self.name_field.is_foreign_key()
        ).to.be.false()

    def test_name(self):
        expect(self.name_field.name).to.eq('name')
        expect(self.foreign_field.name).to.eq('allegation_id')

    def test_related_table(self):
        expect(self.foreign_field.related_table).to.eq(TestFieldAuthor)

    def test_kind(self):
        expect(self.name_field.kind).to.eq('varchar')
        expect(self.foreign_field.kind).to.eq('integer')
