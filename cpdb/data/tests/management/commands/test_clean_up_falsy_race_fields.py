from django.core.management import call_command
from django.test.testcases import TestCase
from robber import expect

from data.factories import OfficerFactory, VictimFactory, ComplainantFactory, InvolvementFactory
from data.models import Officer, Victim, Complainant, Involvement


class CleanUpFalsyRaceFieldsTestCase(TestCase):
    def test_handle(self):
        models = [Victim, Complainant, Involvement, Officer]
        factories = [VictimFactory, ComplainantFactory, InvolvementFactory, OfficerFactory]

        for model, factory in zip(models, factories):

            factory(race='Black')
            factory(race='')
            factory(race='Unknown')
            factory(race='nan')

            call_command('clean_up_falsy_race_fields')

            expect(model.objects.filter(race='').count()).to.eq(0)
            expect(model.objects.filter(race='nan').count()).to.eq(0)
            expect(model.objects.filter(race='Unknown').count()).to.eq(3)
