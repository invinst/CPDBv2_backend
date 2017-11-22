def set_aliases(indexer_class, pk, aliases):
    document = indexer_class.doc_type_klass.get(pk)
    record = indexer_class().get_queryset().get(pk=pk)

    # set db record
    record.tags = aliases
    record.save()

    # update record's index
    document.update(tags=aliases)
