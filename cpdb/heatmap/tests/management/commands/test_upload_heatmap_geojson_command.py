import gzip
import json

from django.test import TestCase
from django.contrib.gis.geos import Point, MultiPolygon, Polygon
from django.core.management import call_command

from robber import expect
from mock import patch

from data.factories import AllegationFactory, AreaFactory, OfficerAllegationFactory, AllegationCategoryFactory
from data.constants import COMMUNITY_AREA_CHOICE
from heatmap.management.commands.upload_heatmap_geojson import Command


class UploadHeatmapGeoJSONCommandTestCase(TestCase):
    def setUp(self):
        area = AreaFactory(id=123, name='Hyde Park', area_type=COMMUNITY_AREA_CHOICE, polygon=MultiPolygon(Polygon((
            (87.940101, 42.023135),
            (87.523661, 42.023135),
            (87.523661, 41.644286),
            (87.940101, 41.644286),
            (87.940101, 42.023135))))
        )
        AreaFactory(id=124, name='Lincoln Square', area_type=COMMUNITY_AREA_CHOICE, polygon=MultiPolygon(Polygon((
            (81, 41),
            (82, 41),
            (82, 42),
            (81, 42),
            (81, 41))))
        )
        allegation1 = AllegationFactory(point=Point([20, 22]))
        allegation2 = AllegationFactory(point=Point([23, 22]))
        area.allegation_set.add(allegation1, allegation2)
        allegation_category = AllegationCategoryFactory(category='Operation/Personnel Violations')
        OfficerAllegationFactory(
            allegation=allegation1,
            allegation_category=allegation_category,
            final_finding='NS',
            final_outcome='100'
        )
        OfficerAllegationFactory(
            allegation=allegation2,
            allegation_category=allegation_category,
            final_finding='SU',
            final_outcome='100'
        )
        self.command = Command()

    def test_get_heatmap_cluster_data(self):
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

    def test_get_community_data(self):
        expect(self.command.get_community_data()).to.eq(json.dumps({
            'type': 'FeatureCollection',
            'features': [{
                'type': 'Feature',
                'properties': {
                    'id': 123,
                    'name': 'Hyde Park',
                    'complaints_count': 2,
                    'sustaineds_count': 1,
                    'most_common_complaint': 'Operation/Personnel Violations',
                    'most_common_discipline': 'Reprimand'
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
            }, {
                'type': 'Feature',
                'properties': {
                    'id': 124,
                    'name': 'Lincoln Square',
                    'complaints_count': 0,
                    'sustaineds_count': 0,
                    'most_common_complaint': 'N/A',
                    'most_common_discipline': 'N/A'
                },
                'geometry': {
                    'type': 'MultiPolygon',
                    'coordinates': [[[
                        [81.0, 41.0],
                        [82.0, 41.0],
                        [82.0, 42.0],
                        [81.0, 42.0],
                        [81.0, 41.0]
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
