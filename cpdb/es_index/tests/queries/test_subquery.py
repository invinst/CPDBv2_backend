from django.test import SimpleTestCase
from django.contrib.gis.db import models

from robber import expect

from es_index.queries.subquery import Subquery
from es_index.queries.table import Table
from es_index.queries.distinct_query import DistinctQuery


class TestSubqueryAuthor(models.Model):
    name = models.CharField(max_length=20)

    class Meta:
        app_label = 'es_index'


class TestSubqueryPublisher(models.Model):
    name = models.CharField(max_length=200)

    class Meta:
        app_label = 'es_index'


class TestSubqueryArticle(models.Model):
    author = models.ForeignKey(TestSubqueryAuthor)
    publisher = models.ForeignKey(TestSubqueryPublisher)

    class Meta:
        app_label = 'es_index'


class TestSubqueryComment(models.Model):
    article = models.ForeignKey(TestSubqueryArticle)

    class Meta:
        app_label = 'es_index'


class ArticleQuery(DistinctQuery):
    base_table = TestSubqueryArticle
    joins = {
        'author': TestSubqueryAuthor
    }
    fields = {
        'id': 'id',
        'publisher_id': 'publisher_id',
        'name': 'author.name'
    }


class SubqueryTestCase(SimpleTestCase):
    def setUp(self):
        self.subquery = Subquery(ArticleQuery(), on='publisher_id')

    def test_field_names(self):
        expect(self.subquery.field_names).to.eq(['publisher_id', 'id', 'name'])

    def test_join_table(self):
        publisher_table = Table(TestSubqueryPublisher)

        expect(
            self.subquery.join_table(
                's1',
                publisher_table,
                'publisher'
            )
        ).to.eq(
            'LEFT JOIN '
            '( SELECT DISTINCT ON (base_table.id) '
            'base_table.publisher_id AS publisher_id, base_table.id AS id, author.name AS name '
            'FROM es_index_testsubqueryarticle base_table '
            'LEFT JOIN es_index_testsubqueryauthor author ON author.id = base_table.author_id ) s1 '
            'ON s1.publisher_id = publisher.id'
        )

    def test_left_on(self):
        subquery = Subquery(ArticleQuery(), on='id', left_on='article_id')
        comment_table = Table(TestSubqueryComment)

        expect(
            subquery.join_table(
                's1',
                comment_table,
                'comment'
            )
        ).to.eq(
            'LEFT JOIN '
            '( SELECT DISTINCT ON (base_table.id) '
            'base_table.publisher_id AS publisher_id, base_table.id AS id, author.name AS name '
            'FROM es_index_testsubqueryarticle base_table '
            'LEFT JOIN es_index_testsubqueryauthor author ON author.id = base_table.author_id ) s1 '
            'ON s1.id = comment.article_id'
        )

    def test_get_kind(self):
        expect(self.subquery.get_kind('publisher_id')).to.eq('integer')

    def test_join_table_with_table(self):
        subquery = Subquery(TestSubqueryArticle, on='id', left_on='article_id')
        comment_table = Table(TestSubqueryComment)

        expect(
            subquery.join_table(
                's1',
                comment_table,
                'comment'
            )
        ).to.eq(
            'LEFT JOIN es_index_testsubqueryarticle s1 ON s1.id = comment.article_id'
        )
