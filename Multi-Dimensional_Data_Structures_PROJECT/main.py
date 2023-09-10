from r_tree import *
from beautifultable import BeautifulTable
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
import time

from lsh import *
from tools import *
from numpy import stack
from numpy.random import choice

def display_results(results_list):
    table = BeautifulTable(maxwidth=150)
    table.column_headers = ["Surname", "Awards", "Education"]

    sorted_list = sorted(results_list, key=lambda x: x["surname"])

    for result in sorted_list:
        table.append_row([result["surname"], result["awards"], result["education"]])

    print(table)
    print("Results: "+str(len(table)))

def lsh_test(lst, thrs):
    # convert list to df
    df = pd.DataFrame(lst)
    # data to hash
    data = df['education'].to_list()
    
    # shingle size step
    k = 2

    # create vocabulary with shingles        
    vocabulary = set().union(*[kshingle(sent, k) for sent in data])
    
    # one hot representation of each document
    one_hot_matrix = stack([one_hot_encoding(vocabulary, sent) for sent in data]).T

    # create LSH model providing the bands magnitute 
    # in fit hashes each column for each band of the sign matrix M to a hash table with k buckets
    lsh = LSH(nfuncs=50, bands=5).fit(one_hot_matrix, 1000)

    # get neigbors with similarity bigger than threshold%
    print("All point pairs in space with similarity >= "+str(thrs*100)+"%")
    actual_neigbors = lsh.neighbors(thrs, cosine_similarity)
    print("Total: "+str(len(actual_neigbors)))
    print(actual_neigbors, end='\n\n')
    '''
    q_vec = choice(2, len(vocabulary))

    r=0.1 # radius to search
    nearest_neigbors = lsh.get_nearest_neighbors(q_vec, r)
    print(f"All point pairs withing radius {r} of query")
    
    print(nearest_neigbors)
    '''


if __name__ == '__main__':
    # Εισαγωγή των απαιτούμενων πληροφοριών αναζήτησης από τον χρήστη
    lsh_threshold = float(input("Εισάγετε ελάχιστο ποσοστό ομοιότητας (0 - 1): "))
    min_letter, max_letter = input("Εισάγετε διάστημα ονομάτων στη μορφή X,X: ").upper().split(',')
    num_awards = int(input("Εισάγετε ελάχιστο αριθμό βραβείων: "))

    # Επιλογή πολυδιάστατης δομής για αποθήκευση των δεδομένων
    print("\n1. k-d tree\n2. Quad tree\n3. Range tree\n4. R-tree")
    choice = int(input("Επιλέξτε δομή: "))

    start_time = time.time()

    if choice == 1:     # Δομή k-d tree
        pass
    elif choice == 2:   # Δομή Quad tree
        pass
    elif choice == 3:   # Δομή Range tree
        range_tree = build_range_tree()
        results = query_range_tree(range_tree, min_letter, max_letter, num_awards)
        display_results(results)
    elif choice == 4:   # Δομή R-tree
        rtree = build_rtree()
        results = query_rtree(rtree, min_letter, max_letter, num_awards)
        display_results(results)
        lsh_test(results, lsh_threshold)

    end_time = time.time()
    print(end_time - start_time)

