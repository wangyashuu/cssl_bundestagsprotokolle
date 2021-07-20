import numpy as np

def sorted_topn(x, y, top_n=None):
    if top_n == None:
        top_n = len(x)
    sorted_indices = np.argsort(y)[::-1][:top_n]
    sorted_x = x[sorted_indices]
    sorted_y = y[sorted_indices]
    return sorted_x, sorted_y


def get_response_counts(comments, top_n=7):
    types = {}
    for cs in comments:
        ts = [t for c in cs for t in c.split()]
        unique_ts = np.unique(ts)
        for t in unique_ts:
            if t in types:
                types[t] += 1
            else:
                types[t] = 1

    keys = np.array(list(types.keys()))
    values = np.array([types[k] for k in keys])
    return sorted_topn(keys, values, top_n)


def get_party_sepcified_reaction_counts(parties, comments, top_n=None):
    counts = np.sum(comments, axis=0)
    return sorted_topn(parties, counts, top_n)


def get_comment_for_speaker(parties, speaker, comment):
    speaker_indicator = parties.reshape(1, -1) == speaker.reshape(-1, 1)
    return (speaker_indicator.T*1) @ (comment*1)
