from django.test import TestCase
from django.core.management import call_command

from data.models import Area
from data.factories import AreaFactory


class CommandTestCase(TestCase):
    def test_fix_community_area_type(self):
        AreaFactory(area_type='Community', name='UPPER CASE')
        self.assertEqual(Area.objects.filter(area_type='Community').count(), 1)
        self.assertEqual(Area.objects.filter(area_type='community').count(), 0)

        call_command('fix_community_area_type')

        self.assertEqual(Area.objects.filter(area_type='Community').count(), 0)
        self.assertEqual(Area.objects.filter(area_type='community').count(), 1)
        self.assertEqual(Area.objects.first().name, 'Upper Case')
