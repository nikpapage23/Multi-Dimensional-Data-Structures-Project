from numpy.linalg import norm
from numpy import dot, zeros

def kshingle(text, k):

    shingle_set = []

    for i in range(len(text) - k + 1):
        shingle_set += [text[i:i+k]]
    
    return set(shingle_set)

def one_hot_encoding(vocab, sent):

    one_hot = zeros(shape=(len(vocab),), dtype=int)
    
    for i, sh in enumerate(vocab):
        if sh in sent: one_hot[i] = 1

    return one_hot

def cosine_similarity(u, v):
    if (u == 0).all() | (v == 0).all():
        return 0.
    else:
        return round(dot(u,v) / (norm(u)*norm(v)), 3)
