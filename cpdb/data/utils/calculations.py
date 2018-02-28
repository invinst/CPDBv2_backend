def calc_percentile_rank(scores, your_score):
    count = 0
    for score in scores:
        if score < your_score:
            count += 1
    percentile_rank = 100.0 * count / len(scores)
    return percentile_rank


def percentile(scores, percentile_rank):
    sorted_key = sorted(scores, key=scores.get)
    sorted_scores = []
    for key in sorted_key:
        sorted_scores.append(scores[key])
    top = []
    for key in sorted_key:
        rank = calc_percentile_rank(sorted_scores, scores[key])
        if rank >= percentile_rank:
            top.append((key, rank))
    return top
