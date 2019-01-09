class SimpleFormatter(object):
    def doc_format(self, doc):
        return doc.to_dict()

    def process_doc(self, doc):
        result = self.doc_format(doc)
        result['id'] = doc._id
        try:
            result['highlight'] = {
                key: [el for el in val]
                for key, val in doc.meta.highlight.to_dict().items()
            }
        except AttributeError:
            pass
        return result

    def format(self, response):
        return [self.process_doc(doc) for doc in response.hits]

    def serialize(self, docs):
        return [self.process_doc(doc) for doc in docs]


class OfficerFormatter(SimpleFormatter):
    def doc_format(self, doc):
        serialized_doc = doc.to_dict()
        return {
            'name': serialized_doc.get('full_name'),
            'to': serialized_doc.get('to'),
            'tags': serialized_doc.get('tags', []),
            'birth_year': serialized_doc.get('birth_year'),
            'race': serialized_doc.get('race'),
            'gender': serialized_doc.get('gender'),
            'badge': serialized_doc.get('badge'),
            'rank': serialized_doc.get('rank'),
            'unit': serialized_doc.get('unit'),
            'appointed_date': serialized_doc.get('date_of_appt'),
            'resignation_date': serialized_doc.get('date_of_resignation'),
            'allegation_count': serialized_doc.get('allegation_count', 0),
            'sustained_count': serialized_doc.get('sustained_count', 0),
            'trr_count': serialized_doc.get('annotated_trr_count', 0),
            'discipline_count': serialized_doc.get('discipline_count', 0),
            'honorable_mention_count': serialized_doc.get('honorable_mention_count', 0),
            'civilian_compliment_count': serialized_doc.get('civilian_compliment_count', 0),
            'major_award_count': serialized_doc.get('major_award_count', 0),
            'honorable_mention_percentile': serialized_doc.get('honorable_mention_percentile'),
            'percentiles': serialized_doc.get('percentiles', []),
        }


class UnitFormatter(SimpleFormatter):
    def doc_format(self, doc):
        serialized_doc = doc.to_dict()
        tags = serialized_doc.get('tags', [])
        description = serialized_doc.get('description', '')
        return {
            'tags': tags,
            'name': serialized_doc['name'],
            'description': description,
            'to': serialized_doc['to']
        }


class OfficerV2Formatter(SimpleFormatter):
    def doc_format(self, doc):
        serialized_doc = doc.to_dict()
        tags = serialized_doc.get('tags', [])
        badge = serialized_doc['badge']

        return {
            'result_text': serialized_doc['full_name'],
            'result_extra_information': badge and f'Badge # {badge}' or '',
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


class ReportFormatter(SimpleFormatter):
    def doc_format(self, doc):
        return {
            'publication': doc.publication,
            'author': doc.author,
            'title': doc.title,
            'excerpt': doc.excerpt,
            'tags': getattr(doc, 'tags', []),
        }


class CRFormatter(SimpleFormatter):
    def doc_format(self, doc):
        return {
            'crid': doc.crid,
            'to': doc.to,
            'incident_date': doc.incident_date,
        }


TRRFormatter = SimpleFormatter
AreaFormatter = SimpleFormatter


class RankFormatter(SimpleFormatter):
    def doc_format(self, doc):
        serialized_doc = doc.to_dict()
        return {
            'name': serialized_doc['rank'],
            'active_officers_count': serialized_doc['active_officers_count'],
            'officers_most_complaints': serialized_doc.get('officers_most_complaints', []),
        }


class ZipCodeFormatter(SimpleFormatter):
    def doc_format(self, doc):
        serialized_doc = doc.to_dict()
        return {
            'name': serialized_doc['zip_code'],
            'url': serialized_doc['url']
        }
