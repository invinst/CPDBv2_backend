def percentile(objects, percentile_type='', key=None, percentile_rank=0.0, decimal_places=0):
    """
    :param objects: list of objects which have metric_{key} attribute
    :param percentile_type: percentile metric to be used to sorted by
    :param key: key attr to sorting with. If key is set, percentile_type param is ignored
    :param percentile_rank: e.g. filter all the scores larger than percentile_rank
    :param decimal_places: how much we will round the rank, 0 means no round
    Otherwise it added a stub (item, rank)
    :return:
    """
    metric_key = key if key else 'metric_{}'.format(percentile_type)
    percentile_key = 'percentile_{}'.format(key if key else percentile_type)

    in_ranking = [obj for obj in objects if hasattr(obj, metric_key)]
    if not in_ranking:
        return []

    sorted_scores = sorted(in_ranking, key=lambda x: getattr(x, metric_key))
    scores_length = len(sorted_scores)
    previous_score = getattr(sorted_scores[0], metric_key)
    current_rank = 0.0

    for i, item in enumerate(sorted_scores):
        if getattr(item, metric_key, 0.0) > previous_score:
            current_rank = 100.0 * i / scores_length
            current_rank = round(current_rank, decimal_places) if decimal_places > 0 else current_rank
            previous_score = getattr(item, metric_key)
        if current_rank >= percentile_rank:
            setattr(item, percentile_key, current_rank)

    return objects


def merge_metric(objects, new_metric_query_set, percentile_types):
    attr_names = ['metric_{}'.format(percentile_type) for percentile_type in percentile_types]

    existing_ids = [obj.id for obj in objects]
    new_objects = list(new_metric_query_set.exclude(id__in=existing_ids))
    old_object_dict = new_metric_query_set.filter(id__in=existing_ids).in_bulk()

    for obj in objects:
        for attr_name in attr_names:
            try:
                value = getattr(old_object_dict[obj.id], attr_name)
                setattr(obj, attr_name, value)
            except KeyError:
                pass

    return objects + new_objects
