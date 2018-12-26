import zipcodes
from django.conf import settings


class ZipCode(object):
    def __init__(self, pk, zip_code, url):
        self.pk = pk
        self.zip_code = zip_code
        self.url = url


def chicago_zip_codes():
    results = []
    for index, zip_code in enumerate(zipcodes.filter_by(zipcodes.list_all(), active=True, city='CHICAGO')):
        url = f"{settings.V1_URL}/url-mediator/session-builder?zip_code={zip_code['zip_code']}"
        results.append(ZipCode(pk=index, zip_code=zip_code['zip_code'], url=url))
    return results
