from django.conf import settings
from rosette.api import API, DocumentParameters, RosetteException


class RosettePersonNameParser:
    def __init__(self):
        self.api = API(user_key=settings.ROSETTE_API_KEY)
        self.api.setOption('linkEntities', False)
        self.type = 'PERSON'

    def parse(self, content):
        params = DocumentParameters()
        params['content'] = content
        try:
            entities = self.api.entities(params)
        except RosetteException:
            return []
        return [e['mention'] for e in entities['entities'] if e['type'] == self.type]
