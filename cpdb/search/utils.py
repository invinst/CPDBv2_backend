import zipcodes
from django.conf import settings


class ZipCode(object):
    def __init__(self, pk, zip_code, to):
        self.pk = pk
        self.zip_code = zip_code
        self.to = to


def chicago_zip_codes():
    results = []
    for index, zip_code in enumerate(zipcodes.filter_by(zipcodes.list_all(), active=True, city='CHICAGO')):
        to = '{domain}/url-mediator/session-builder?zip_code={zip_code}'.format(
            domain=settings.V1_URL, zip_code=zip_code['zip_code']
        )
        results.append(ZipCode(pk=index, zip_code=zip_code['zip_code'], to=to))
    return results
