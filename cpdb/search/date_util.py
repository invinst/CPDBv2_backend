import re

from dateparser.search import search_dates
from dateparser import parse


MIN_DATE_STRING = 6
DIGITS_MODIFIER_PATTERN = r'\d{1,2}st|\d{1,2}nd|\d{1,2}rd|\d{1,2}th'
DIGITS_PATTERN = r'\d{1,4}'
MONTHS_PATTERN = 'january|february|march|april|may|june|july|august|september|october|november|december|' \
                 'jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec'
DELIMITERS_PATTERN = r'[/\:\-\,\s\_\+\@]'
COMPONENT_PATTERN = r'({}|{}|{})\,?'.format(MONTHS_PATTERN, DIGITS_MODIFIER_PATTERN, DIGITS_PATTERN)
DATE_PATTERN = '^({})({}({}))*$'.format(COMPONENT_PATTERN, DELIMITERS_PATTERN, COMPONENT_PATTERN)
SPLIT_DATE_TOKEN = 'SPLIT_DATE_TOKEN'


def _remove_illegal_words(string):
    string = re.sub(' +', ' ', string.lower())
    legal_words = [term if re.match(DATE_PATTERN, term) else SPLIT_DATE_TOKEN for term in string.split()]
    return ' '.join(legal_words)


def _is_complete_date(date_string):
    return len(date_string) >= MIN_DATE_STRING and parse(date_string, settings={'STRICT_PARSING': True})


def _search_first_date(string):
    candidates = search_dates(string, languages=['en'], settings={'STRICT_PARSING': True})
    if candidates:
        first_term, first_date = candidates[0]
        remaining = ''.join(string.split(first_term)[1:])
        if _is_complete_date(first_term):
            return first_date, remaining
        return None, remaining
    return None, ''


def find_dates_from_string(string):
    string = _remove_illegal_words(string)

    dates = []
    date, remaining = _search_first_date(string)
    if date:
        dates.append(date)

    while remaining:
        date, remaining = _search_first_date(remaining)
        if date and date not in dates:
            dates.append(date)

    return dates
