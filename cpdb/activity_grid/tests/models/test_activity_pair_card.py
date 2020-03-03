from django.test.testcases import TestCase

from robber.expect import expect
from mock import patch


from activity_grid.models import ActivityPairCard
from activity_grid.factories import ActivityPairCardFactory
from data.factories import OfficerFactory, AllegationFactory, OfficerAllegationFactory


class ActivityPairCardTestCase(TestCase):
    def test_update_coaccusal_count_when_create(self):
        officer_1 = OfficerFactory()
        officer_2 = OfficerFactory()

        allegation_1 = AllegationFactory()
        allegation_2 = AllegationFactory()
        OfficerAllegationFactory(allegation=allegation_1, officer=officer_1)
        OfficerAllegationFactory(allegation=allegation_1, officer=officer_2)
        OfficerAllegationFactory(allegation=allegation_2, officer=officer_1)
        OfficerAllegationFactory(allegation=allegation_2, officer=officer_2)
        OfficerAllegationFactory(officer=officer_1)
        OfficerAllegationFactory(officer=officer_2)

        pair_card = ActivityPairCard.objects.create(
            officer1=officer_1,
            officer2=officer_2
        )

        pair_card.refresh_from_db()
        expect(pair_card.coaccusal_count).to.eq(2)

    @patch('activity_grid.models.ActivityPairCard._set_coaccusal_count')
    def test_not_update_coaccusal_count_when_update(self, mock_set_coaccusal_count):
        officer_1 = OfficerFactory()
        officer_2 = OfficerFactory()

        pair_card = ActivityPairCardFactory(
            officer1=officer_1,
            officer2=officer_2,
        )

        expect(mock_set_coaccusal_count).to.be.called_once()
        mock_set_coaccusal_count.reset_mock()

        pair_card.important = True
        pair_card.save()
        expect(mock_set_coaccusal_count).not_to.be.called()
