DOCUMENT_TYPES = [
    ('CR', 'CR'),
    ('CPB', 'CPB'),
    ('TRR', 'TRR'),
    ('DOCUMENT', 'DOCUMENT'),
    ('OCIR', 'OCIR'),
    ('OBR', 'OBR'),
    ('AR', 'AR'),
    ('CHI-R', 'CHI-R'),
    ('incident/offense', 'Incident/Offense Report')
]

DOCUMENT_CRAWLER_SUCCESS = 'Success'
DOCUMENT_CRAWLER_FAILED = 'Failed'

DOCUMENT_CRAWLER_STATUS_CHOICES = (
    (DOCUMENT_CRAWLER_SUCCESS, DOCUMENT_CRAWLER_SUCCESS),
    (DOCUMENT_CRAWLER_FAILED, DOCUMENT_CRAWLER_FAILED)
)

REPROCESS_TEXT_MAX_RETRIES = 3
