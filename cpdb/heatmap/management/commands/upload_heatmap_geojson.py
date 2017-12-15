import json
import gzip
from tempfile import NamedTemporaryFile

from django.core.management import BaseCommand
from django.conf import settings
from django.db import connection
from django.db.models import Count
from django.contrib.gis.geos.factory import fromstr

from tqdm import tqdm
from azure.storage.blob import BlockBlobService, PublicAccess, ContentSettings
from azure.storage.common.models import CorsRule

from data.models import Area, Allegation
from data.constants import NEIGHBORHOODS_AREA_CHOICE, DISCIPLINE_CODES, OUTCOMES_DICT


# pragma: no cover
class Command(BaseCommand):
    help = (
        'Upload heatmap geojsons to Azure storage.'
        'Rerun whenever we import new data.'
        )

    _prev_total = 0

    def get_heatmap_cluster_data(self):
        kursor = connection.cursor()

        grid_size = 0.0005

        kursor.execute('''
            SELECT
                COUNT( point ) AS count,
                ST_AsText( ST_Centroid(ST_Collect( point )) ) AS center
            FROM data_allegation WHERE point IS NOT NULL
            GROUP BY
                ST_SnapToGrid( ST_SetSRID(point, 4326), %s, %s)
            ''' % (grid_size, grid_size)
            )
        kclusters = kursor.fetchall()
        ret = {'features': [], 'type': 'FeatureCollection'}

        for cluster in kclusters:
            point = fromstr(cluster[1])
            weight = cluster[0]

            allegation_json = {
                'type': 'Feature',
                'properties': {
                    'weight': weight
                },
                'geometry': {
                    'coordinates': [point.x, point.y],
                    'type': 'Point'
                }
            }
            ret['features'].append(allegation_json)

        return json.dumps(ret)

    def get_neighborhood_data(self):
        areas = Area.objects.filter(area_type=NEIGHBORHOODS_AREA_CHOICE, polygon__isnull=False)

        area_dict = {
            'type': 'FeatureCollection',
            'features': [],
        }
        for area in tqdm(areas):
            polygon = json.loads(area.polygon.geojson)

            most_common_complaint = Allegation.objects.filter(
                    areas__id=area.id,
                    officerallegation__allegation_category__category__isnull=False)\
                .distinct()\
                .values('officerallegation__allegation_category__category')\
                .annotate(category_count=Count('id'))\
                .order_by('-category_count').first()
            most_common_discipline = Allegation.objects.filter(
                    areas__id=area.id,
                    officerallegation__final_outcome__in=DISCIPLINE_CODES)\
                .distinct()\
                .values('officerallegation__final_outcome')\
                .annotate(outcome_count=Count('id'))\
                .order_by('-outcome_count').first()

            area_json = {
                'type': 'Feature',
                'properties': {
                    'id': area.id,
                    'name': area.name,
                    'complaints_count': Allegation.objects.filter(areas__id=area.id).distinct().count(),
                    'sustaineds_count': Allegation.objects.filter(
                        areas__id=area.id,
                        officerallegation__final_finding='SU').distinct().count(),
                    'most_common_complaint':
                        most_common_complaint.get('officerallegation__allegation_category__category')
                        if most_common_complaint
                        else 'N/A',
                    'most_common_discipline':
                        OUTCOMES_DICT.get(most_common_discipline.get('officerallegation__final_outcome'))
                        if most_common_discipline
                        else 'N/A'
                },
                'geometry': polygon
            }

            area_dict['features'].append(area_json)
        return json.dumps(area_dict)

    def save_to_gzip_file(self, content):
        tmp_file = NamedTemporaryFile(delete=False)
        with gzip.open(tmp_file.name, 'wb') as f:
            f.write(content)
        return tmp_file.name

    def handle(self, *args, **options):
        content_settings = ContentSettings(content_type='application/json', content_encoding='gzip')

        block_blob_service = BlockBlobService(
            account_name=settings.AZURE_STORAGE_ACCOUNT_NAME, account_key=settings.AZURE_STORAGE_ACCOUNT_KEY)
        block_blob_service.create_container('heatmap', public_access=PublicAccess.Blob)
        block_blob_service.set_blob_service_properties(cors=[CorsRule(['*'], ['GET'])])

        block_blob_service.create_blob_from_path(
            'heatmap',
            'cluster.geojson',
            file_path=self.save_to_gzip_file(self.get_heatmap_cluster_data()),
            content_settings=content_settings
        )
        block_blob_service.create_blob_from_path(
            'heatmap',
            'neighborhood.geojson',
            file_path=self.save_to_gzip_file(self.get_neighborhood_data()),
            content_settings=content_settings
        )
