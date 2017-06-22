class Formatter(object):
    def format(self):
        raise NotImplementedError


class SimpleFormatter(Formatter):
    def doc_format(self, doc):
        return doc.to_dict()

    def format(self, response):
        def process_doc(doc):
            result = self.doc_format(doc)
            result['doc_id'] = doc._id
            return result
        return [process_doc(doc) for doc in response.hits]


class OfficerFormatter(SimpleFormatter):
    def doc_format(self, doc):
        serialized_doc = doc.to_dict()

        return {
            'text': serialized_doc['full_name'],
            'payload': {
                'result_reason': ', '.join(serialized_doc.get('tags', [])),
                'result_text': serialized_doc['full_name'],
                'result_extra_information':
                    serialized_doc['badge'] and 'Badge # {badge}'.format(badge=serialized_doc['badge']) or '',
                'to': serialized_doc['to']
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
        return {
            'text': doc.name,
            'payload': {
                'result_text': doc.name,
                'result_extra_information': doc.description,
                'url': doc.url
            }
        }


class NameFormatter(SimpleFormatter):
    def doc_format(self, doc):
        return {
            'text': doc.name,
            'payload': {
                'result_text': doc.name,
                'url': doc.url
            }
        }


class OfficerV2Formatter(SimpleFormatter):
    def doc_format(self, doc):
        return {
            'result_text': doc.full_name,
            'result_extra_information': doc.badge and 'Badge # {badge}'.format(badge=doc.badge) or '',
            'to': doc.to
        }


class NameV2Formatter(SimpleFormatter):
    def doc_format(self, doc):
        return {
            'result_text': doc.name,
            'url': doc.url
        }


class FAQFormatter(SimpleFormatter):
    def doc_format(self, doc):
        return {
            'question': doc.question,
            'answer': doc.answer
        }


class ReportFormatter(SimpleFormatter):
    def doc_format(self, doc):
        return {
            'publication': doc.publication,
            'author': doc.author,
            'title': doc.title,
            'excerpt': doc.excerpt
        }
