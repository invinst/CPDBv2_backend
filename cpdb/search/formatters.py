from django.conf import settings

from lawsuit.models import Lawsuit


class Formatter(object):
    def format(self):
        raise NotImplementedError


class SimpleFormatter(Formatter):
    def get_highlight(self, doc):
        try:
            return {
                key: list(val)
                for key, val in doc.meta.highlight.to_dict().items()
            }
        except AttributeError:
            return

    def doc_format(self, doc):
        return doc.to_dict()

    def process_doc(self, doc):
        result = self.doc_format(doc)
        result['id'] = doc._id

        highlight = self.get_highlight(doc)
        if highlight:
            result['highlight'] = highlight

        return result

    def format(self, response):
        return [self.process_doc(doc) for doc in response.hits]

    def serialize(self, docs):
        return [self.process_doc(doc) for doc in docs]


class DataFormatter(Formatter):
    def get_queryset(self, ids):
        raise NotImplementedError

    def item_format(self, item):
        raise NotImplementedError

    def items(self, docs):
        ids = [doc._id for doc in docs]
        return self.get_queryset(ids)

    def serialize(self, docs):
        return [self.item_format(item) for item in self.items(docs)]

    def format(self, response):
        return self.serialize(response.hits)


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
            'percentile_allegation': serialized_doc.get('complaint_percentile', None),
            'percentile_allegation_civilian': serialized_doc.get('civilian_allegation_percentile', None),
            'percentile_allegation_internal': serialized_doc.get('internal_allegation_percentile', None),
            'percentile_trr': serialized_doc.get('trr_percentile', None)
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
    def get_text_content_highlight(self, doc):
        try:
            first_attachment_inner_hit = doc.meta.inner_hits.attachment_files.hits[0]
            return first_attachment_inner_hit.meta.highlight['attachment_files.text_content']
        except (KeyError, IndexError, AttributeError):
            return

    def get_highlight(self, doc):
        highlight = super(CRFormatter, self).get_highlight(doc) or {}
        text_content_highlight = self.get_text_content_highlight(doc)
        if text_content_highlight:
            highlight['text_content'] = list(text_content_highlight)
        return highlight

    def doc_format(self, doc):
        return {
            'crid': doc.crid,
            'to': doc.to,
            'incident_date': doc.incident_date,
            'category': doc.category,
            'sub_category': doc.sub_category,
            'address': doc.address,
            'victims': [victim.to_dict() for victim in getattr(doc, 'victims', [])],
            'coaccused': [officer.to_dict() for officer in getattr(doc, 'coaccused', [])],
        }


TRRFormatter = SimpleFormatter
AreaFormatter = SimpleFormatter


class LawsuitFormatter(DataFormatter):
    def get_queryset(self, ids):
        return Lawsuit.objects.filter(id__in=ids)

    def item_format(self, item):
        return {
            'id': item.id,
            'case_no': item.case_no,
            'primary_cause': item.primary_cause,
            'to': item.v2_to,
            'summary': item.summary,
            'incident_date': item.incident_date.strftime('%Y-%m-%d') if item.incident_date else None
        }


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


class SearchTermFormatter(SimpleFormatter):
    def doc_format(self, doc):
        serialized_doc = doc.to_dict()
        link = serialized_doc.get('link', '')
        return {
            'id': serialized_doc['slug'],
            'name': serialized_doc['name'],
            'category_name': serialized_doc.get('category_name', ''),
            'description': serialized_doc.get('description', ''),
            'call_to_action_type': serialized_doc.get('call_to_action_type', ''),
            'link': f'{settings.V1_URL}{link}' if link else '',
        }

    def process_doc(self, doc):
        return self.doc_format(doc)
