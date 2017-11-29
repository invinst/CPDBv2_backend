from django.conf import settings

from google.cloud.language import enums, types, LanguageServiceClient


class GoogleNaturalLanguageNameParser:
    def __init__(self):
        if not settings.TEST:
            self.client = LanguageServiceClient()  # pragma: no cover
        self.type = enums.Entity.Type.PERSON

    def parse(self, content):
        source, text = content
        document = types.Document(content=text, type=enums.Document.Type.PLAIN_TEXT)
        entities = self.client.analyze_entities(document=document).entities
        return [(source, e.name) for e in entities if e.type == self.type]
