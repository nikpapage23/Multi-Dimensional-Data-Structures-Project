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


def jaccard(v, u):
    return round(len(set(v) & set(u)) / len(set(v) | set(u)), 3)
    

def cosine_similarity(u, v):
    if (u == 0).all() | (v == 0).all():
        return 0.
    else:
        return round(dot(u,v) / (norm(u)*norm(v)), 3)


class StringToIntTransformer:
    def __init__(self):
        self.char_to_int_mapping = {}
        self.max_value = float('-inf')
        self.min_value = float('+inf')


    # method to fill char_to_int_mapping
    def fit(self, X, y=None):
        for string in X:
            for char in string:
                if char.isalpha():
                    ascii_val = ord(char.upper()) - ord('A') + 1
                    if char not in self.char_to_int_mapping:
                        self.char_to_int_mapping[char] = ascii_val
        return self
    
    
    def transform(self, X):

        X_transformed = []
        for string in X:
        
            value = 0
            for char in string:
                if char.isalpha():
                    value += self.char_to_int_mapping.get(char.upper(), 0)
                    break

            X_transformed.append(value)

        return X_transformed
    

    def scale(self, char_bound):

        values = self.transform(char_bound)

        min_value = min(self.char_to_int_mapping.values())
        max_value = max(self.char_to_int_mapping.values())

        scaled_values = []
        for value in values:
            scaled_values += [int((value - 1) * (self.max_value - self.min_value) / (26 - 1) + self.min_value)]

        return scaled_values