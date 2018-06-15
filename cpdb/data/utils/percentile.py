def percentile(objects, percentile_rank=0.0, key='value', decimal_places=0):
    """
    :param objects: list of objects
    :param percentile_rank: e.g. filter all the scores larger than percentile_rank
    :param key: key of dicts which we used to sorted by
    :param decimal_places: how much we will round the rank, 0 means no round
    Otherwise it added a stub (item, rank)
    :return:
    """
    if not objects:
        return []
    if not hasattr(objects[0], key):
        raise ValueError('Can not find the corresponding {}'.format(key))
    sorted_scores = sorted(objects, key=lambda x: getattr(x, key))
    scores_length = len(sorted_scores)
    previous_score = getattr(sorted_scores[0], key)
    current_rank = 0.0
    results = sorted_scores

    for i, item in enumerate(sorted_scores):
        if getattr(item, key) > previous_score:
            current_rank = 100.0 * i / scores_length
            current_rank = round(current_rank, decimal_places) if decimal_places > 0 else current_rank
            previous_score = getattr(item, key)
        if current_rank >= percentile_rank:
            setattr(item, 'percentile_{}'.format(key.replace('metric_', '')), current_rank)

    return results
