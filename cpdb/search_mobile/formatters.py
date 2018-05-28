from search.formatters import SimpleFormatter


class OfficerV2Formatter(SimpleFormatter):
    def doc_format(self, doc):
        return {
            'id': int(doc.meta.id),
            'name': doc.full_name,
            'extra_info': doc.badge and 'Badge # {badge}'.format(badge=doc.badge) or '',
            'url': doc.to
        }


class ReportFormatter(SimpleFormatter):
    def doc_format(self, doc):
        return {
            'id': int(doc.meta.id),
            'publication': doc.publication,
            'title': doc.title,
            'publish_date': doc.publish_date
        }


class UnitFormatter(SimpleFormatter):
    def doc_format(self, doc):
        return {
            'id': int(doc.meta.id),
            'text': doc.name,
            'url': doc.url,
            'active_member_count': doc.active_member_count,
            'member_count': doc.member_count
        }
