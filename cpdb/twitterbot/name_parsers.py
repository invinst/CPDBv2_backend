import logging

from django.conf import settings
from rosette.api import API, DocumentParameters, RosetteException

logger = logging.getLogger(__name__)


class RosettePersonNameParser:
    def __init__(self):
        self.api = API(user_key=settings.ROSETTE_API_KEY)
        self.api.setOption('linkEntities', False)
        self.type = 'PERSON'

    def parse(self, content):
        source, text = content
        params = DocumentParameters()
        params['content'] = text
        try:
            entities = self.api.entities(params)
        except RosetteException, exception:
            logger.error('Error while parsing "%s": %s' % (text, str(exception)))
            return []
        return [(source, e['mention']) for e in entities['entities'] if e['type'] == self.type]
