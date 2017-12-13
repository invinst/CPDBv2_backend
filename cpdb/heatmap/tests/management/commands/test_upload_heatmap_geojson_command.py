import gzip
import json

from django.test import TestCase
from django.contrib.gis.geos import Point
from django.core.management import call_command

from robber import expect
from mock import patch

from data.factories import AllegationFactory
from heatmap.management.commands.upload_heatmap_geojson import Command


class UploadHeatmapGeoJSONCommandTestCase(TestCase):
    def setUp(self):
        AllegationFactory(point=Point([20, 22]))
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
            }]
        }))

    def test_save_to_gzip_file(self):
        expected_content = 'Sample Content'
        file_name = self.command.save_to_gzip_file(expected_content)
        with gzip.open(file_name) as f:
            expect(f.read()).to.eq(expected_content)

    @patch('heatmap.management.commands.upload_heatmap_geojson.BlockBlobService', autospec=True)
    def test_handle(self, mock_block_blob_service):
        call_command('upload_heatmap_geojson')
        mock_instance = mock_block_blob_service.return_value
        expect(mock_instance.create_container.called).to.be.true()
        expect(mock_instance.set_blob_service_properties.called).to.be.true()
        expect(mock_instance.create_blob_from_path.called).to.be.true()
