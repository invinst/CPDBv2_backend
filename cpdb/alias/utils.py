def set_aliases(doc_type_class, model_class, pk, aliases):
    # set db record
    record = model_class.objects.get(pk=pk)
    record.tags = aliases
    record.save()

    # update record's index
    document = doc_type_class.get(pk)
    document.update(tags=aliases)
