def percentile(scores, percentile_rank, key='value', inline=False):
    """
    :param scores: list of dict
    :param percentile_rank: e.g. filter all the scores larger than percentile_rank
    :param key: key of dict which we used to sorted by
    :param inline: default False, if True then the rank will be added into `percentile_{key}`
    Otherwise it added an stub (item, rank)
    :return:
    """
    if key not in scores[0]:
        raise ValueError('Can not found the corresponding key')

    sorted_scores = sorted(scores, key=lambda x: x[key])
    scores_length = len(sorted_scores)
    previous_score = sorted_scores[0][key]
    current_rank = 0
    results = sorted_scores if inline else []

    for i, item in enumerate(sorted_scores):
        if item[key] > previous_score:
            current_rank = 100.0 * i / scores_length
            previous_score = item[key]
        if current_rank >= percentile_rank:
            if inline:
                item['percentile_'+key] = current_rank
            else:
                results.append((item, current_rank))

    return results
