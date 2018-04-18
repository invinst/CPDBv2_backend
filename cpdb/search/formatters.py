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
                'result_text': serialized_doc['full_name'],
                'name': serialized_doc['full_name'],
                'to': serialized_doc['to'],
                'tags': serialized_doc.get('tags', []),
                'birth_year': serialized_doc['birth_year'],
                'race': serialized_doc['race'],
                'gender': serialized_doc['gender'],
                'badge': serialized_doc.get('badge'),
                'rank': serialized_doc['rank'],
                'unit': serialized_doc.get('unit'),
                'appointed_date': serialized_doc['date_of_appt'],
                'resignation_date': serialized_doc.get('date_of_resignation'),
                'allegation_count': serialized_doc.get('allegation_count', 0),
                'sustained_count': serialized_doc.get('sustained_count', 0),
                'trr_count': serialized_doc.get('trr_count', 0),
                'discipline_count': serialized_doc.get('discipline_count', 0),
                'honorable_mention_count': serialized_doc.get('honorable_mention_count', 0),
                'civilian_compliment_count': serialized_doc.get('civilian_compliment_count', 0),
                'percentiles': serialized_doc.get('percentiles', []),
            }
        }


class UnitOfficerFormatter(SimpleFormatter):
    def doc_format(self, doc):
        serialized_doc = doc.to_dict()
        tags = serialized_doc.get('tags', [])

        unit_description = serialized_doc.get('unit_description', None)
        if unit_description is not None:
            extra_info = unit_description
        else:
            extra_info = serialized_doc['badge'] and 'Badge # {badge}'.format(badge=serialized_doc['badge']) or ''

        return {
            'text': serialized_doc['full_name'],
            'payload': {
                'result_reason': ', '.join(tags),
                'result_text': serialized_doc['full_name'],
                'result_extra_information': extra_info,
                'to': serialized_doc['to'],
                'visual_token_background_color': serialized_doc['visual_token_background_color'],
                'tags': tags,
                'unit': serialized_doc.get('unit', None),
                'rank': serialized_doc.get('rank', None),
                'salary': None,
                'race': serialized_doc['race'],
                'sex': serialized_doc['sex'],
                'birth_year': serialized_doc['birth_year'],
                'allegation_count': serialized_doc.get('allegation_count', 0),
                'sustained_count': serialized_doc.get('sustained_count', 0)
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
