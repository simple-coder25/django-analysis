def frequency_dist(data, slice=200):
    result = {}

    for value in data:
        if value not in result:
            result[value] = 1
        else:
            result[value] += 1

    if result:
        result = sorted(result.items(), key=lambda v: v[1], reverse=True)[:slice]
        result = dict(result)

    return result
