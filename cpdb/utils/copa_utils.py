EXCLUDE_TEXTS = [
    'CIVILIAN OFFICE OF POLICE ACCOUNTABILITY',
    'INDEPENDENT POLICE REVIEW AUTHORITY',
]

DATE_TIME_TEXTS = [
    'Date of IPRA',
    'Date of COPA',
    'Time of IPRA',
    'Time of COPA',
]

SUMMARY_TITLES = [
    'SUMMARY OF EVIDENCE',
    'SUMMARY OF INCIDENT',
    'SUMMARY OF THE INCIDENT',
    'INTRODUCTION',
]

EXACT_SUMMARY_TITLES = [
    'SUMMARY',
    'SUMMARY OF',
]


def _extract_paragraphs(attachment_text):
    paragraphs = attachment_text.replace(' \n', '\n').split('\n')
    return [
        paragraph for paragraph in paragraphs
        if not any([exclude_text in paragraph for exclude_text in EXCLUDE_TEXTS])
    ]


def _match_text(paragraph):
    return (
        any([before_text in paragraph for before_text in DATE_TIME_TEXTS]) or
        any([summary_title in paragraph for summary_title in SUMMARY_TITLES]) or
        any([paragraph.upper().endswith(f"{summary_title}:") for summary_title in SUMMARY_TITLES]) or
        any([paragraph == summary_title for summary_title in EXACT_SUMMARY_TITLES]) or
        any([paragraph.upper() == f"{summary_title}:" for summary_title in EXACT_SUMMARY_TITLES])
    )


def _is_title(paragraph):
    words = ''.join([i for i in paragraph if not i.isdigit()]).split()
    meaning_words = [word for word in words if len(word) > 2]
    return ' '.join(meaning_words).isupper()


def _is_alternative_title(paragraph):
    return paragraph.endswith(':')


def _next_title_index(paragraphs, is_title):
    return next(
        (index for index, paragraph in enumerate(paragraphs) if is_title(paragraph)),
        None
    )


def extract_copa_executive_summary(attachment_text):
    paragraphs = _extract_paragraphs(attachment_text)

    matched_index = None
    for index, paragraph in enumerate(paragraphs):
        if _match_text(paragraph):
            matched_index = index
    if matched_index is not None:
        filtered_paragraphs = paragraphs[(matched_index + 1):]
        next_title_index = (
            _next_title_index(filtered_paragraphs, _is_title) or
            _next_title_index(filtered_paragraphs, _is_alternative_title)
        )
        if next_title_index:
            return ' '.join(filtered_paragraphs[:next_title_index])
