from django.db import models

from data.models.common import TimeStampsModel
from data.models import Allegation


class ActivityPairCard(TimeStampsModel):
    officer1 = models.ForeignKey('data.Officer', on_delete=models.CASCADE, related_name='activity_pair_card1')
    officer2 = models.ForeignKey('data.Officer', on_delete=models.CASCADE, related_name='activity_pair_card2')
    important = models.BooleanField(default=False)
    last_activity = models.DateTimeField(null=True)

    # CACHED COLUMNS
    coaccusal_count = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.pk:
            self._set_coaccusal_count()
        super(ActivityPairCard, self).save(*args, **kwargs)

    def _set_coaccusal_count(self):
        self.coaccusal_count = Allegation.objects.filter(
            officerallegation__officer=self.officer1_id
        ).filter(
            officerallegation__officer=self.officer2_id
        ).distinct().count()
