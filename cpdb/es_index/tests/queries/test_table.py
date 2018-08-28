from django.test import SimpleTestCase
from django.contrib.gis.db import models

from robber import expect
from mock import patch

from data.models import Allegation
from es_index.queries.table import Table
from es_index.queries.exceptions import ForeignKeyNotFoundException


class TestTableOfficer(models.Model):
    name = models.CharField(max_length=20)

    class Meta:
        app_label = 'es_index'


class TestTableInvestigator(models.Model):
    name = models.CharField(max_length=20)
    officer = models.ForeignKey(TestTableOfficer, null=True)

    class Meta:
        app_label = 'es_index'


class TableTestCase(SimpleTestCase):
    def setUp(self):
        self.investigator_table = Table(TestTableInvestigator)
        self.officer_table = Table(TestTableOfficer)

    def test_name(self):
        expect(self.investigator_table.name).to.eq('es_index_testtableinvestigator')

    def test_field_names(self):
        expect(self.investigator_table.field_names()).to.eq(['id', 'name', 'officer_id'])

    def test_find_foreign_key_to(self):
        expect(
            lambda: self.investigator_table.find_foreign_key_to(Table(Allegation))
        ).to.throw_exactly(ForeignKeyNotFoundException)
        expect(
            self.investigator_table.find_foreign_key_to(self.officer_table).name
        ).to.eq('officer_id')

    def test_find_foreign_key_with_name(self):
        expect(
            lambda: self.investigator_table.find_foreign_key_with_name('allegation_id')
        ).to.throw_exactly(ForeignKeyNotFoundException)
        expect(
            self.investigator_table.find_foreign_key_with_name('officer_id').name
        ).to.eq('officer_id')

    def test_join_table(self):
        with patch('es_index.queries.table.join_expression', return_value='join') as join_expression_mock:
            join = self.investigator_table.join_table(
                alias='investigator',
                table=self.officer_table,
                table_alias='officer'
            )
            expect(join).to.eq('join')
            expect(join_expression_mock).to.be.called_with(
                'es_index_testtableinvestigator', 'investigator', 'officer_id', 'officer', 'id'
            )

    def test_join_table_reversed(self):
        with patch('es_index.queries.table.join_expression', return_value='join') as join_expression_mock:
            join = self.officer_table.join_table(
                alias='officer',
                table=self.investigator_table,
                table_alias='investigator'
            )
            expect(join).to.eq('join')
            expect(join_expression_mock).to.be.called_with(
                'es_index_testtableofficer', 'officer', 'id', 'investigator', 'officer_id'
            )

    def test_join_table_has_no_relationship(self):
        expect(lambda: self.investigator_table.join_table(
            alias='investigator',
            table=Table(Allegation),
            table_alias='allegation'
        )).to.throw_exactly(ForeignKeyNotFoundException)
