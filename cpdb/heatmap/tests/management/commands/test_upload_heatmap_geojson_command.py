import gzip
import json

from django.test import TestCase
from django.contrib.gis.geos import Point, MultiPolygon, Polygon
from django.core.management import call_command

from robber import expect
from mock import patch

from data.factories import (
    AllegationFactory, AreaFactory, OfficerAllegationFactory, RacePopulationFactory, OfficerFactory)
from data.constants import COMMUNITY_AREA_CHOICE
from heatmap.management.commands.upload_heatmap_geojson import Command


class UploadHeatmapGeoJSONCommandTestCase(TestCase):
    def setUp(self):
        self.command = Command()

    def create_officer_allegation(self, count, area, **kwargs):
        for _ in range(count):
            allegation = AllegationFactory()
            area.allegation_set.add(allegation)
            OfficerAllegationFactory(
                allegation=allegation,
                **kwargs
            )

    def test_get_heatmap_cluster_data(self):
        AllegationFactory(point=Point([20, 22]))
        AllegationFactory(point=Point([23, 22]))
        expect(self.command.get_heatmap_cluster_data()).to.eq(json.dumps({
            'type': 'FeatureCollection',
            'features': [{
                'type': 'Feature',
                'geometry': {
                    'coordinates': [20.0, 22.0],
                    'type': 'Point'
                },
                'properties': {
                    'weight': 1
                }
            }, {
                'type': 'Feature',
                'geometry': {
                    'coordinates': [23.0, 22.0],
                    'type': 'Point'
                },
                'properties': {
                    'weight': 1
                }
            }]
        }))

    def test_save_to_gzip_file(self):
        expected_content = 'Sample Content'
        file_name = self.command.save_to_gzip_file(expected_content)
        with gzip.open(file_name) as f:
            expect(f.read()).to.eq(expected_content)

    def test_get_community_discipline_count(self):
        area = AreaFactory(area_type=COMMUNITY_AREA_CHOICE)
        self.create_officer_allegation(5, area, final_outcome='100')
        self.create_officer_allegation(5, area, final_outcome='900')
        result = json.loads(self.command.get_community_data())
        expect(result['features']).to.have.length(1)
        expect(result['features'][0]['properties']['allegation_count']).to.eq(10)
        expect(result['features'][0]['properties']['discipline_count']).to.eq(5)

    def test_get_community_most_complaints_officers(self):
        area = AreaFactory(area_type=COMMUNITY_AREA_CHOICE)
        officer1 = OfficerFactory(id=12, first_name='John', last_name='Fenedy')
        officer2 = OfficerFactory(id=23, first_name='Jerome', last_name='Finnigan')
        officer3 = OfficerFactory(id=34, first_name='Raymond', last_name='Piwnicki')
        officer4 = OfficerFactory(id=45, first_name='Sean', last_name='Campbell')
        self.create_officer_allegation(7, area=area, officer=officer1)
        self.create_officer_allegation(6, area=area, officer=officer2)
        self.create_officer_allegation(5, area=area, officer=officer3)
        self.create_officer_allegation(4, area=area, officer=officer4)
        result = json.loads(self.command.get_community_data())
        expect(result['features']).to.have.length(1)
        expect(result['features'][0]['properties']['most_complaints_officers']).to.eq([
            {
                'full_name': 'John Fenedy',
                'complaints_count': 7,
                'id': 12
            },
            {
                'full_name': 'Jerome Finnigan',
                'complaints_count': 6,
                'id': 23
            },
            {
                'full_name': 'Raymond Piwnicki',
                'complaints_count': 5,
                'id': 34
            }
        ])

    def test_get_community_data(self):
        area = AreaFactory(
            area_type=COMMUNITY_AREA_CHOICE,
            name='Hyde Park',
            id=123,
            median_income='$60,400',
            polygon=MultiPolygon(Polygon((
                (87.940101, 42.023135),
                (87.523661, 42.023135),
                (87.523661, 41.644286),
                (87.940101, 41.644286),
                (87.940101, 42.023135))))
        )
        RacePopulationFactory(area=area, race='White', count=1000)
        RacePopulationFactory(area=area, race='Black', count=500)
        expect(self.command.get_community_data()).to.eq(json.dumps({
            'type': 'FeatureCollection',
            'features': [{
                'type': 'Feature',
                'properties': {
                    'id': 123,
                    'name': 'Hyde Park',
                    'allegation_count': 0,
                    'discipline_count': 0,
                    'most_complaints_officers': [],
                    'population': 1500,
                    'median_income': '$60,400',
                    'race_count': [{
                        'race': 'White',
                        'count': 1000
                    }, {
                        'race': 'Black',
                        'count': 500
                    }]
                },
                'geometry': {
                    'type': 'MultiPolygon',
                    'coordinates': [[[
                        [87.940101, 42.023135],
                        [87.523661, 42.023135],
                        [87.523661, 41.644286],
                        [87.940101, 41.644286],
                        [87.940101, 42.023135]
                    ]]]
                }
            }]
        }))

    @patch('heatmap.management.commands.upload_heatmap_geojson.BlockBlobService', autospec=True)
    def test_handle(self, mock_block_blob_service):
        call_command('upload_heatmap_geojson')
        mock_instance = mock_block_blob_service.return_value
        expect(mock_instance.create_container.called).to.be.true()
        expect(mock_instance.set_blob_service_properties.called).to.be.true()
        expect(mock_instance.create_blob_from_path.called).to.be.true()
