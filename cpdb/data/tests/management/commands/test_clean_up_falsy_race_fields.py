from datetime import datetime

from django.core.management import call_command
from django.test import override_settings
from django.test.testcases import TestCase

from robber import expect
from freezegun import freeze_time
import pytz

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

    @override_settings(TIME_ZONE='UTC')
    def test_handle_update(self):
        models = [Victim, Complainant, Involvement, Officer]
        factories = [VictimFactory, ComplainantFactory, InvolvementFactory, OfficerFactory]

        for model, factory in zip(models, factories):
            with freeze_time(lambda: datetime(2017, 3, 3, 12, 0, 1, tzinfo=pytz.utc)):
                object_1 = factory(race='')
                object_2 = factory(race='Black')

            with freeze_time(lambda: datetime(2018, 4, 4, 12, 0, 1, tzinfo=pytz.utc)):
                call_command('clean_up_falsy_race_fields')
                object_1.refresh_from_db()

            expect(object_1.race).to.eq('Unknown')
            expect(object_1.updated_at).to.eq(datetime(2018, 4, 4, 12, 0, 1, tzinfo=pytz.utc))
            expect(object_2.race).to.eq('Black')
            expect(object_2.updated_at).to.eq(datetime(2017, 3, 3, 12, 0, 1, tzinfo=pytz.utc))
