from django.core.management import BaseCommand
from django.db.models import Q

from data.constants import RACE_UNKNOWN_STRINGS
from data.models import Victim, Complainant, Involvement, Officer


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        for klass in [Victim, Complainant, Involvement, Officer]:
            query = Q()
            for race_string in RACE_UNKNOWN_STRINGS:
                query |= Q(race__iexact=race_string)
            klass.objects.filter(query).update(race='Unknown')
