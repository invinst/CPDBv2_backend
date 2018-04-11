from datetime import datetime, date

from django.core.urlresolvers import reverse
from django.contrib.gis.geos import Point

from rest_framework.test import APITestCase
from rest_framework import status
from robber import expect
import pytz

from data.factories import (
    OfficerFactory, AllegationFactory, OfficerAllegationFactory, ComplainantFactory, AreaFactory,
    PoliceWitnessFactory, InvestigatorFactory, InvestigatorAllegationFactory,
    AllegationCategoryFactory, AttachmentFileFactory, OfficerBadgeNumberFactory, VictimFactory
)
from data.constants import MEDIA_TYPE_DOCUMENT, MEDIA_TYPE_AUDIO, MEDIA_TYPE_VIDEO
from cr.tests.mixins import CRTestCaseMixin


class CRMobileViewSetTestCase(CRTestCaseMixin, APITestCase):
    def test_retrieve(self):
        area = AreaFactory(name='Lincoln Square')
        officer1 = OfficerFactory(
            id=123,
            first_name='Mr',
            last_name='Foo',
            gender='M',
            race='White',
            appointed_date=date(2001, 1, 1),
            birth_year=1993
        )
        OfficerBadgeNumberFactory(officer=officer1, star='12345', current=True)
        allegation = AllegationFactory(
            crid='12345',
            point=Point(12, 21),
            incident_date=datetime(2002, 2, 28, tzinfo=pytz.utc),
            add1=3510,
            add2='Michigan Ave',
            city='Chicago',
            location='09',
            beat=area,
            is_officer_complaint=False,
            summary='Summary'
        )
        ComplainantFactory(allegation=allegation, gender='M', race='Black', age='18')
        VictimFactory(allegation=allegation, gender='M', race='Black', age=53)
        OfficerAllegationFactory(
            officer=officer1, allegation=allegation, final_finding='SU',
            final_outcome='100',
            recc_outcome='400',
            start_date=date(2003, 3, 20),
            end_date=date(2006, 5, 26),
            allegation_category=AllegationCategoryFactory(
                category='Operation/Personnel Violations',
                allegation_name='NEGLECT OF DUTY/CONDUCT UNBECOMING - ON DUTY'
            )
        )
        officer = OfficerFactory(
            id=3,
            first_name='Raymond',
            last_name='Piwinicki',
            gender='M',
            race='White',
            appointed_date=date(2001, 5, 1)
        )
        OfficerAllegationFactory(
            officer=officer,
            final_finding='SU',
            start_date=date(2003, 2, 28),
            allegation__incident_date=date(2002, 2, 28),
            allegation__is_officer_complaint=False
        )
        PoliceWitnessFactory(officer=officer, allegation=allegation)
        investigator = OfficerFactory(
            id=1,
            first_name='Ellis',
            last_name='Skol',
            appointed_date=date(2001, 5, 1)
        )
        OfficerAllegationFactory(
            officer=investigator,
            final_finding='NS',
            start_date=date(2003, 2, 28),
            allegation__incident_date=date(2002, 2, 28),
            allegation__is_officer_complaint=False
        )
        investigator = InvestigatorFactory(officer=investigator)
        InvestigatorAllegationFactory(
            allegation=allegation,
            investigator=investigator,
            current_rank='IPRA investigator'
        )

        AttachmentFileFactory(
            allegation=allegation,
            title='CR document',
            url='http://cr-document.com/',
            file_type=MEDIA_TYPE_DOCUMENT
        )

        AttachmentFileFactory(
            allegation=allegation,
            title='audio',
            url='http://audio.hear',
            file_type=MEDIA_TYPE_AUDIO
        )

        AttachmentFileFactory(
            allegation=allegation,
            title='video',
            url='http://video.see',
            file_type=MEDIA_TYPE_VIDEO
        )

        self.refresh_index()

        response = self.client.get(reverse('api-v2:cr-mobile-detail', kwargs={'pk': '12345'}))
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq({
            'crid': '12345',
            'coaccused': [
                {
                    'id': 123,
                    'full_name': 'Mr Foo',
                    'gender': 'Male',
                    'race': 'White',
                    'final_finding': 'Sustained',
                    'recc_outcome': 'Separation',
                    'final_outcome': 'Reprimand',
                    'category': 'Operation/Personnel Violations',
                    'subcategory': 'NEGLECT OF DUTY/CONDUCT UNBECOMING - ON DUTY',
                    'start_date': '2003-03-20',
                    'end_date': '2006-05-26'
                }
            ],
            'complainants': [
                {
                    'race': 'Black',
                    'gender': 'Male',
                    'age': 18
                }
            ],
            'point': {
                'long': 12.0,
                'lat': 21.0
            },
            'incident_date': '2002-02-28',
            'address': '3510 Michigan Ave, Chicago',
            'location': 'Police Communications System',
            'beat': {'name': 'Lincoln Square'},
            'involvements': [
                {
                    'involved_type': 'investigator',
                    'officers': [{
                        'id': 1,
                        'abbr_name': 'E. Skol',
                        'extra_info': '1 case(s)'
                    }]
                },
                {
                    'involved_type': 'police witnesses',
                    'officers': [{
                        'id': 3,
                        'abbr_name': 'R. Piwinicki',
                        'extra_info': 'Male, White'
                    }]
                }
            ],
            'videos': [
                {
                    'title': 'video',
                    'url': 'http://video.see'
                }
            ],
            'audios': [
                {
                    'title': 'audio',
                    'url': 'http://audio.hear'
                }
            ],
            'documents': [
                {
                    'title': 'CR document',
                    'url': 'http://cr-document.com/'
                }
            ]
        })
