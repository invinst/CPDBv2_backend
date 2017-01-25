class OfficerDocumentCompleterTransformer(object):
    def transform(self, built, content_type):
        return {
            'input': [built['full_name'], built['badge']],
            'output': built['full_name'],
            'context': {
                'content_type': content_type
            },
            'payload': {
                'result_text': built['full_name'],
                'result_extra_information': built['badge'] and 'Badge #{badge}'.format(badge=built['badge']),
                'url': built['url']
            }
        }
