from numpy.linalg import norm
from numpy import dot, zeros
import numpy as np
# συνάρτηση κατασκευής kshingle
def kshingle(text, k):

    shingle_set = []

    for i in range(len(text) - k + 1):
        shingle_set += [text[i:i+k]]
    
    return set(shingle_set)

# συνάρτηση κατασκευής one hot 
def one_hot_encoding(vocab, sent):

    one_hot = zeros(shape=(len(vocab),), dtype=int)
    
    for i, sh in enumerate(vocab):
        if sh in sent: one_hot[i] = 1

    return one_hot

# ομοιότητα συνημιτόνου
def cosine_similarity(u, v):
    if (u == 0).all() | (v == 0).all():
        return 0.
    else:
        return round(dot(u,v) / (norm(u)*norm(v)), 3)
    
# ομοιότητα jaccard binary
def jaccard_binary(x,y):
    """A function for finding the similarity between two binary vectors"""
    intersection = np.logical_and(x, y)
    union = np.logical_or(x, y)
    similarity = round(intersection.sum() / float(union.sum()), 3)
    return similarity

# ομοιότητα jaccard set
def jaccard_set(list1, list2):
    """Define Jaccard Similarity function for two sets"""
    intersection = len(list(set(list1).intersection(list2)))
    union = (len(list1) + len(list2)) - intersection
    return float(intersection) / union