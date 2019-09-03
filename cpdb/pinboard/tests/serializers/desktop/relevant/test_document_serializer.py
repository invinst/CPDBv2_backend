from datetime import datetime

from django.contrib.gis.geos import Point
from django.test import TestCase

import pytz
from robber import expect

from pinboard.serializers.desktop.relevant.document_serializer import AllegationSerializer, DocumentSerializer
from data.factories import (
    OfficerFactory,
    AllegationFactory,
    AllegationCategoryFactory,
    OfficerAllegationFactory,
    AttachmentFileFactory,
)
from pinboard.factories import PinboardFactory


class DocumentSerializerTestCase(TestCase):
    def test_serialization(self):
        pinned_officer = OfficerFactory(
            id=1,
            rank='Police Officer',
            first_name='Jerome',
            last_name='Finnigan',
            allegation_count=10,
            trr_percentile='99.99',
            complaint_percentile='88.88',
            civilian_allegation_percentile='77.77',
            internal_allegation_percentile='66.66',
        )
        relevant_allegation = AllegationFactory(
            crid='1',
            incident_date=datetime(2002, 2, 21, tzinfo=pytz.utc),
            most_common_category=AllegationCategoryFactory(category='Operation/Personnel Violations'),
            point=Point([0.01, 0.02]),
        )
        AttachmentFileFactory(
            id=1,
            file_type='document',
            title='relevant document 1',
            allegation=relevant_allegation,
            show=True,
            preview_image_url="https://assets.documentcloud.org/CRID-1-CR-p1-normal.gif",
            url='http://cr-1-document.com/',
        )

        pinboard = PinboardFactory(
            id='66ef1560',
            title='Test pinboard',
            description='Test description',
        )
        pinboard.officers.set([pinned_officer])
        OfficerAllegationFactory(officer=pinned_officer, allegation=relevant_allegation)

        expect(pinboard.relevant_documents.count()).to.eq(1)
        expect(AllegationSerializer(pinboard.relevant_documents[0].allegation).data).to.eq({
            'crid': '1',
            'category': 'Operation/Personnel Violations',
            'incident_date': '2002-02-21',
            'coaccused': [{
                'id': 1,
                'rank': 'Police Officer',
                'full_name': 'Jerome Finnigan',
                'coaccusal_count': None,
                'percentile': {
                    'year': 2016,
                    'percentile_trr': '99.9900',
                    'percentile_allegation_civilian': '77.7700',
                    'percentile_allegation_internal': '66.6600',
                    'percentile_allegation': '88.8800',
                },
                'allegation_count': 10,
            }],
            'point': {
                'lon': 0.01,
                'lat': 0.02,
            },
        })
        expect(DocumentSerializer(pinboard.relevant_documents.first()).data).to.eq({
            'id': 1,
            'preview_image_url': "https://assets.documentcloud.org/CRID-1-CR-p1-normal.gif",
            'url': 'http://cr-1-document.com/',
            'allegation': {
                'crid': '1',
                'category': 'Operation/Personnel Violations',
                'incident_date': '2002-02-21',
                'coaccused': [{
                    'id': 1,
                    'rank': 'Police Officer',
                    'full_name': 'Jerome Finnigan',
                    'coaccusal_count': None,
                    'allegation_count': 10,
                    'percentile': {
                        'year': 2016,
                        'percentile_trr': '99.9900',
                        'percentile_allegation': '88.8800',
                        'percentile_allegation_civilian': '77.7700',
                        'percentile_allegation_internal': '66.6600',
                    }
                }],
                'point': {
                    'lon': 0.01,
                    'lat': 0.02,
                },
            }
        })
