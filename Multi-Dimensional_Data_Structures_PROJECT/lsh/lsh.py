from numpy import array, zeros, empty
from random import shuffle 
from itertools import combinations
from copy import deepcopy


class MinHash:
    def __init__(self, one_hot_matrix, nfuncs):
        self.one_hot_matrix = one_hot_matrix    # one hot μητρώο
        self.shape = one_hot_matrix.shape   # διαστάσεις του μητρώου
        self.nfuncs = nfuncs    # κάθετη διάσταση του signature του Μ
        self.functions = self.build_functions(nfuncs)   # δημιουργία hash functions
        self.sign_matrix = None     # signatures

    def _hash(self):
        # one_hot indices διάνυσμα
        hash_indices = list(range(1, self.shape[0]+1))

        # shuffle 
        shuffle(hash_indices)

        return hash_indices

    # επιστρέφει μια δισδιάστατη λίστα των μεταθέσεων δεικτών
    def build_functions(self, nfuncs):
        return [self._hash() for _ in range(nfuncs)]

    # παίρνει ως όρισμα ένα one hot διάνυσμα και κατασκευάζει ένα compressed signature διάνυσμα  
    def _signature_matrix(self):
        sign_matrix = empty(shape=(self.nfuncs, self.shape[1]), dtype=int)

        for i, func in enumerate(self.functions):
            perm_sign = zeros(self.shape[1])
            j = 1
            
            while (perm_sign == 0).any():
                idx = func.index(j)
                row = self.one_hot_matrix[idx]

                mask = (perm_sign == 0) & (row == 1)
                perm_sign[mask] = j
                j += 1
                
            sign_matrix[i] = perm_sign
        
        self.sign_matrix = deepcopy(sign_matrix)

        return sign_matrix


class LSH:
    def __init__(self, nfuncs, bands):
        self.nfuncs = nfuncs    # μέγεθος του shingle
        self.bands = bands  # ορίζει το μέγεθος του band
        self.hash_tables = []   # μια λίστα που θα περιέχει τα hash tables
        self.num_buckets = None
        self.hash_method = None
        
    # μέθοδος για να χωρίσει τα signature μητρώα σε bands
    def partition_into_bands(self, sm):

        # ελέγχει αν το signature μπορεί να χωριστεί στα bands
        assert sm.shape[0] % self.bands == 0
        
        # γραμμές σε κάθε band
        r = sm.shape[0] // self.bands
        
        # χωρίζει σε bands και επιλέγει r γραμμές για να εισάγει
        bands = [sm[i:i+r] for i in range(0, sm.shape[0], r)]
        
        return array(bands)
    
    # Κάνε hash κάθε band του μητρώου Μ σε ένα hash table με k buckets
    def fit(self, data, num_buckets):
        self.num_buckets = num_buckets
        
        # δημιουργεί το minhash αντικείμενο
        self.hash_method = MinHash(data, nfuncs=self.nfuncs)

        # η ταυτότητα κάθε αρχείου αναπαρίσταται από τη στήλη
        sign_matrix = self.hash_method._signature_matrix()

        # χωρίζει σε bands
        bands = self.partition_into_bands(sign_matrix)

        for band in bands:
            # φτιάχνει ένα κενό hash table με k buckets
            hash_table = [set() for _ in range(self.num_buckets)]

            # κάνει hash κάθε στήλη του band σε ένα bucket στο hash table
            for j, column in enumerate(band.T):

                # υπολογίζει τη hash τιμή της στήλης
                hash_value = hash(tuple(column)) % self.num_buckets

                # βάζει τη στήλη στο αντίστοιχο bucket στο hash table
                hash_table[hash_value].add(j)

            # βάζει το hash table στη λίστα
            self.hash_tables.append(hash_table)

        return self

    def _get_candidates(self):
        # Ένα σετ που αποθηκεύει τα candidate ζεύγη
        candidates = [set() for _ in range(self.num_buckets)]

        # Βρίσκει τα pairs για κάθε band
        for hash_table in self.hash_tables:

            for i, bucket in enumerate(hash_table):
                # Αν το bucket έχει παραπάνω από μια στήλη
                if len(bucket) > 1:
                    # Βάλε όλα τα ζεύγη στο candidates set
                    candidates[i].update(combinations(bucket, 2))

        # Return the candidate column pairs
        return candidates  

    def neighbors(self, similar, dist_func):
        cands = set().union(*self._get_candidates())
        actual_neighbors = {}

        # for each pair in each bucket of each band
        for c1, c2 in cands:

            # βρες το similarity
            sim = dist_func(self.hash_method.one_hot_matrix[:, c1], self.hash_method.one_hot_matrix[:, c2])
            
            # αν είναι πάνω από το threshold
            if sim >= similar:
                actual_neighbors[c1, c2] = sim

        return actual_neighbors
