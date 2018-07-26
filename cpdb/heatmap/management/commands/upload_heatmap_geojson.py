import json
import gzip
from tempfile import NamedTemporaryFile

from django.core.management import BaseCommand
from django.conf import settings
from django.db import connection
from django.db.models import Count, Sum
from django.contrib.gis.geos.factory import fromstr

from tqdm import tqdm
from azure.storage.blob import BlockBlobService, PublicAccess, ContentSettings
from azure.storage.common.models import CorsRule

from data.models import Area, OfficerAllegation, Officer
from data.constants import COMMUNITY_AREA_CHOICE, ALLEGATION_MIN_DATETIME


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
            FROM data_allegation
            WHERE
                incident_date >= \'%s 00:00:00\'
                AND point IS NOT NULL
            GROUP BY
                ST_SnapToGrid( ST_SetSRID(point, 4326), %s, %s)
            ''' % (settings.ALLEGATION_MIN, grid_size, grid_size)
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

    def get_community_data(self):
        areas = Area.objects.filter(area_type=COMMUNITY_AREA_CHOICE, polygon__isnull=False)

        area_dict = {
            'type': 'FeatureCollection',
            'features': [],
        }
        for area in tqdm(areas):
            polygon = json.loads(area.polygon.geojson)

            area_json = {
                'type': 'Feature',
                'properties': {
                    'id': area.id,
                    'name': area.name,
                    'allegation_count': OfficerAllegation.objects.filter(
                        allegation__areas__id=area.id,
                        allegation__incident_date__gte=ALLEGATION_MIN_DATETIME,
                    ).distinct().count(),
                    'discipline_count': OfficerAllegation.objects.filter(
                        allegation__areas__id=area.id,
                        allegation__incident_date__gte=ALLEGATION_MIN_DATETIME,
                        disciplined=True
                    ).distinct().count(),
                    'most_complaints_officers': [
                        {
                            'full_name': officer.full_name,
                            'complaints_count': officer.complaints_count,
                            'id': officer.id
                        }
                        for officer in Officer.objects.filter(
                            officerallegation__allegation__areas__id=area.id,
                            officerallegation__allegation__incident_date__gte=ALLEGATION_MIN_DATETIME,
                        ).annotate(
                            complaints_count=Count('officerallegation__allegation_id')
                        ).order_by('-complaints_count')[:3]
                    ],
                    'population': area.racepopulation_set.aggregate(population=Sum('count'))['population'],
                    'median_income': area.median_income,
                    'race_count': list(area.racepopulation_set.order_by('-count').values('race', 'count'))
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
            'community.geojson',
            file_path=self.save_to_gzip_file(self.get_community_data()),
            content_settings=content_settings
        )
