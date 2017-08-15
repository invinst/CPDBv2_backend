from search.doc_types import OfficerDocType, CoAccusedOfficerDocType
from elasticsearch_dsl import Q


def set_aliases(indexer_class, pk, aliases):
    document = indexer_class.doc_type_klass.get(pk)
    record = indexer_class().get_queryset().get(pk=pk)

    # set db record
    record.tags = aliases
    record.save()

    # update record's index
    document.update(tags=aliases)

    # updating an OfficerDocType `tags` value does not cascade to its corresponding CoAccusedOfficerDocType,
    # so we need to update them manually.
    if indexer_class.doc_type_klass is OfficerDocType:
        # find matching co-accused documents
        query = Q('nested', path='co_accused_officer', query=Q('term', co_accused_officer__id=pk))
        searcher = CoAccusedOfficerDocType().search()
        coaccused_docs = searcher.query(query).scan()

        # update the tags
        for coaccused_doc in coaccused_docs:
            coaccused_doc.co_accused_officer.tags = aliases
            coaccused_doc.save()
