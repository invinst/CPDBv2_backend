from django.test import TestCase
from django.core.management import call_command

from robber import expect

from data.factories import AllegationFactory, AreaFactory
from data.models import Allegation, Area


class ClearTableTestCase(TestCase):
    def test_handle_single_table(self):
        AllegationFactory()

        call_command('cleartable', 'data.allegation')

        expect(Allegation.objects.count()).to.equal(0)

    def test_handle_multiple_tables(self):
        AllegationFactory()
        AreaFactory()

        call_command('cleartable', 'data.allegation', 'data.area')

        expect(Allegation.objects.count()).to.equal(0)
        expect(Area.objects.count()).to.equal(0)
