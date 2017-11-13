class Formatter(object):
    def format(self):
        raise NotImplementedError


class SimpleFormatter(Formatter):
    def doc_format(self, doc):
        return doc.to_dict()

    def format(self, response):
        def process_doc(doc):
            result = self.doc_format(doc)
            result['id'] = doc._id
            return result
        return [process_doc(doc) for doc in response.hits]


class OfficerFormatter(SimpleFormatter):
    def doc_format(self, doc):
        serialized_doc = doc.to_dict()
        tags = serialized_doc.get('tags', [])

        return {
            'text': serialized_doc['full_name'],
            'payload': {
                'result_reason': ', '.join(tags),
                'result_text': serialized_doc['full_name'],
                'result_extra_information':
                    serialized_doc['badge'] and 'Badge # {badge}'.format(badge=serialized_doc['badge']) or '',
                'to': serialized_doc['to'],
                'visual_token_background_color': serialized_doc['visual_token_background_color'],
                'tags': tags
            }
        }


class CoAccusedOfficerFormatter(SimpleFormatter):
    def doc_format(self, doc):
        serialized_doc = doc.to_dict()
        reason = 'coaccused with {name} ({badge})'.format(
            name=serialized_doc['co_accused_officer']['full_name'],
            badge=serialized_doc['co_accused_officer']['badge']
        )

        return {
            'text': serialized_doc['full_name'],
            'payload': {
                'result_reason': reason,
                'result_text': serialized_doc['full_name'],
                'result_extra_information':
                    serialized_doc['badge'] and 'Badge # {badge}'.format(badge=serialized_doc['badge']) or '',
                'to': serialized_doc['to']
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
                'result_text': serialized_doc['name'],
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
