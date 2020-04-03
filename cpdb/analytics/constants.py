FREE_TEXT = 'free_text'
NO_INTERACTION = 'no_interaction'

QUERY_TYPES = [
    [FREE_TEXT, 'Free Text'],
    [NO_INTERACTION, 'No Interaction']
]

DOWNLOAD_EVENT_TYPE = 'DOWNLOAD_EVENT_TYPE'
VIEW_EVENT_TYPE = 'VIEW_EVENT_TYPE'

ATTACHMENT_FILE_TRACKING_EVENT_TYPE = (
    (DOWNLOAD_EVENT_TYPE, 'Download Event Type'),
    (VIEW_EVENT_TYPE, 'View Event Type')
)

GA_API_END_POINT = 'https://www.google-analytics.com/collect'
GA_API_VERSION = '1'
GA_ANONYMOUS_ID = '555'
CLICKY_API_END_POINT = 'http://in.getclicky.com/in.php'
