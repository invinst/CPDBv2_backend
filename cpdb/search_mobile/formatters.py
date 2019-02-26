from django.utils import timezone

from search.formatters import SimpleFormatter


class OfficerV2Formatter(SimpleFormatter):
    def get_latest_percentile(self, percentiles):
        current_year = timezone.now().year
        percentiles_until_now = list(filter(lambda x: x['year'] <= current_year, percentiles))

        if len(percentiles_until_now) > 0:
            return max(percentiles_until_now, key=lambda x: x['year'])

        return []

    def doc_format(self, doc):
        serialized_doc = doc.to_dict()

        return {
            'id': int(serialized_doc['id']),
            'name': serialized_doc['full_name'],
            'badge': serialized_doc['badge'],
            'percentile': self.get_latest_percentile(serialized_doc.get('percentiles', []))
        }


class CRFormatter(SimpleFormatter):
    def doc_format(self, doc):
        return {
            'crid': doc.crid,
            'incident_date': doc.incident_date,
            'category': getattr(doc, 'category', '') or 'Unknown'
        }


class TRRFormatter(SimpleFormatter):
    def doc_format(self, doc):
        serialized_doc = doc.to_dict()

        return {
            'id': serialized_doc['id']
        }
