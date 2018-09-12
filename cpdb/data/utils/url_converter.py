import re


def get_pdf_url(url):
    return re.sub(r'html$', 'pdf', url)
