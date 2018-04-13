class Formatter(object):
    def format(self):
        raise NotImplementedError


class SimpleFormatter(Formatter):
    def doc_format(self, doc):
        return doc.to_dict()

    def process_doc(self, doc):
        result = self.doc_format(doc)
        result['id'] = doc._id
        return result

    def format(self, response):
        return [self.process_doc(doc) for doc in response.hits]

    def serialize(self, docs):
        return [self.process_doc(doc) for doc in docs]


class OfficerFormatter(SimpleFormatter):
    def doc_format(self, doc):
        serialized_doc = doc.to_dict()
        return {
            'text': serialized_doc['full_name'],
            'payload': {
                'name': serialized_doc['full_name'],
                'to': '/officer/{}'.format(serialized_doc['id']),
                'birth_year': serialized_doc['birth_year'],
                'race': serialized_doc['race'],
                'gender': serialized_doc['race'],
                'badge': serialized_doc.get('badge', 0),
                'rank': serialized_doc['rank'],
                'unit': serialized_doc['unit'],
                'appointed_date': serialized_doc['date_of_appt'],
                'resignation_date': serialized_doc.get('date_of_resignation'),
                'allegation_count': serialized_doc.get('allegation_count'),
                'sustained_count': serialized_doc.get('sustained_count'),
                'civilian_compliment_count': serialized_doc.get('civilian_compliment_count'),
                'percentiles': serialized_doc.get('percentiles'),
            }
        }


class UnitFormatter(SimpleFormatter):
    def doc_format(self, doc):
        serialized_doc = doc.to_dict()
        tags = serialized_doc.get('tags', [])
        return {
            'text': serialized_doc['name'],
            'payload': {
                'tags': tags,
                'result_text': serialized_doc['description'],
                'result_extra_information': serialized_doc['name'],
                'to': serialized_doc['to']
            }
        }


class NameFormatter(SimpleFormatter):
    def doc_format(self, doc):
        serialized_doc = doc.to_dict()
        tags = serialized_doc.get('tags', [])
        return {
            'text': serialized_doc['name'],
            'payload': {
                'tags': tags,
                'result_text': serialized_doc['name'],
                'url': serialized_doc['url']
            }
        }


class OfficerV2Formatter(SimpleFormatter):
    def doc_format(self, doc):
        serialized_doc = doc.to_dict()
        tags = serialized_doc.get('tags', [])
        badge = serialized_doc['badge']

        return {
            'result_text': serialized_doc['full_name'],
            'result_extra_information': badge and 'Badge # {badge}'.format(badge=badge) or '',
            'to': serialized_doc['to'],
            'tags': tags
        }


class NameV2Formatter(SimpleFormatter):
    def doc_format(self, doc):
        serialized_doc = doc.to_dict()
        tags = serialized_doc.get('tags', [])

        return {
            'tags': tags,
            'result_text': serialized_doc['name'],
            'url': serialized_doc['url'],
        }


class FAQFormatter(SimpleFormatter):
    def doc_format(self, doc):
        return {
            'question': doc.question,
            'answer': doc.answer,
            'tags': getattr(doc, 'tags', []),
        }


class ReportFormatter(SimpleFormatter):
    def doc_format(self, doc):
        return {
            'publication': doc.publication,
            'author': doc.author,
            'title': doc.title,
            'excerpt': doc.excerpt,
            'tags': getattr(doc, 'tags', []),
        }


class CrFormatter(SimpleFormatter):
    def doc_format(self, doc):
        serialized_doc = doc.to_dict()
        return {
            'text': serialized_doc['crid'],
            'payload': {
                'result_text': serialized_doc['crid'],
                'to': serialized_doc['to']
            }
        }


class AreaFormatter(SimpleFormatter):
    def doc_format(self, doc):
        serialized_doc = doc.to_dict()
        results = {
            'text': serialized_doc['name'],
            'payload': serialized_doc
        }
        results['payload']['result_text'] = serialized_doc['name']
        return results
