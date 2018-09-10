from django.test import SimpleTestCase
from django.db import models

from robber import expect

from es_index.queries.base_query import BaseQuery


class TestBaseQueryAuthor(models.Model):
    name = models.CharField(max_length=20)

    class Meta:
        app_label = 'es_index'


class TestBaseQueryArticle(models.Model):
    author = models.ForeignKey(TestBaseQueryAuthor)

    class Meta:
        app_label = 'es_index'


class ArticleQuery(BaseQuery):
    base_table = TestBaseQueryArticle
    joins = {
        'author': TestBaseQueryAuthor
    }
    fields = {
        'author_id': 'author_id',
        'name': 'author.name'
    }


class BaseQueryTestCase(SimpleTestCase):
    def setUp(self):
        self.query = ArticleQuery()

    def test_field_aliases(self):
        expect(self.query.field_aliases()).to.eq(['author_id', 'name'])

    def test_field_names_to_group(self):
        expect(self.query.field_names_to_group).to.eq(['base_table.author_id', 'author.name'])

    def test_fields_with_alias(self):
        expect(self.query.fields_with_alias()).to.eq(
            'base_table.author_id AS author_id, author.name AS name'
        )
