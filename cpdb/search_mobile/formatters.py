import datetime

from search.formatters import SimpleFormatter


class OfficerV2Formatter(SimpleFormatter):
    def get_latest_percentile(self, percentiles):
        current_year = datetime.datetime.now().year
        percentiles_from_now = filter(lambda x: x['year'] >= current_year, percentiles)

        if len(percentiles_from_now) > 0:
            return min(percentiles_from_now, key=lambda x: x['year'])

        return None

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
        serialized_doc = doc.to_dict()

        return {
            'crid': serialized_doc['crid']
        }


class TRRFormatter(SimpleFormatter):
    def doc_format(self, doc):
        serialized_doc = doc.to_dict()

        return {
            'id': serialized_doc['id']
        }
