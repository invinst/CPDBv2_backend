from django.db.models import Func


def percentile(scores, percentile_rank, key='value', inline=False, decimal_places=0):
    """
    :param scores: list of dicts
    :param percentile_rank: e.g. filter all the scores larger than percentile_rank
    :param key: key of dicts which we used to sorted by
    :param inline: default False, if True then the rank will be added into `percentile_{key}`
    :decimal_places: how much we will round the rank, 0 means no round
    Otherwise it added a stub (item, rank)
    :return:
    """
    if not scores:
        return []
    if key not in scores[0]:
        raise ValueError('Can not find the corresponding key')

    sorted_scores = sorted(scores, key=lambda x: x[key])
    scores_length = len(sorted_scores)
    previous_score = sorted_scores[0][key]
    current_rank = 0
    results = sorted_scores if inline else []

    for i, item in enumerate(sorted_scores):
        if item[key] > previous_score:
            current_rank = 100.0 * i / scores_length
            current_rank = round(current_rank, decimal_places) if decimal_places > 0 else current_rank
            previous_score = item[key]
        if current_rank >= percentile_rank:
            if inline:
                item['percentile_{}'.format(key.replace('metric_', ''))] = current_rank
            else:
                results.append((item, current_rank))

    return results


class Round(Func):
    function = 'ROUND'
    template = '%(function)s(CAST(%(expressions)s as numeric), 4)'
