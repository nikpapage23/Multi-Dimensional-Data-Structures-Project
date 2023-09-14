from r_tree import *
from range_tree import *
from beautifultable import BeautifulTable
import time
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

from lsh.lsh import *
from lsh.tools import *
from numpy import stack
from numpy.random import choice
import math
from os.path import dirname, abspath
from sys import path

from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer

# Get the path to the project root directory
root_dir = dirname(dirname(abspath(__file__)))
# Add the root directory to the system path
path.append(root_dir)

def display_results(results_list):
    table = BeautifulTable(maxwidth=150)
    table.column_headers = ["Surname", "Awards", "Education"]

    sorted_list = sorted(results_list, key=lambda x: x["surname"])

    for result in sorted_list:
        table.append_row([result["surname"], result["awards"], result["education"]])

    print(table)
    print("Search Results: "+str(len(table)))

def lsh_test(lst, thrs, buc):
    print("Number of buckets: "+str(buc))
    # calculate the number of hash functions based on buckets total number
    if buc > 300:
        n_func = 20
    else:
        n_func = 10
    print("Number of functions: "+str(n_func))
    lst = sorted(lst, key=lambda x: x["surname"])
    # convert list to df
    df = pd.DataFrame(lst)
    # text preprocessing
    stemming_and_stopwords(df)
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
    lsh = LSH(n_func, 5).fit(one_hot_matrix, buc)

    # get neigbors with similarity bigger than threshold%
    actual_neigbors = lsh.neighbors(thrs, cosine_similarity)
    print(str(len(actual_neigbors))+" point pairs in space with similarity >= "+str(thrs*100)+"%")
    print(actual_neigbors, end='\n\n')
    '''
    q_vec = choice(2, len(vocabulary))

    r=0.1 # radius to search
    nearest_neigbors = lsh.get_nearest_neighbors(q_vec, r)
    print(str(len(nearest_neigbors))+f" point pairs withing radius {r} of query")
    
    print(nearest_neigbors)
    '''

def stemming_and_stopwords(df):
    stop_words = set(stopwords.words('english'))
    stemmer = PorterStemmer()
    df.loc[:, 'education'] = df['education'].apply(lambda doc: ' '.join([stemmer.stem(w) for w in doc.split() if w not in stop_words]))
    # αφαίρεση χαρακτήρων που δεν είναι γράμματα αλφαβήτου
    df.loc[:, 'education'] = df['education'].apply(lambda doc: ' '.join(letter for letter in doc.split() if letter.isalnum()))
    # αφαίρεση αριθμών
    df['education'] = df['education'].str.replace(r'\d+', '', regex=True)
    # αφαίρεση παρενθέσεων
    df['education'] = df['education'].str.replace(r'(', '', regex=True)
    df['education'] = df['education'].str.replace(r')', '', regex=True)

if __name__ == '__main__':
    # Εισαγωγή των απαιτούμενων πληροφοριών αναζήτησης από τον χρήστη
    lsh_threshold = float(input("Εισάγετε ελάχιστο ποσοστό ομοιότητας (0 - 1): "))
    min_letter, max_letter = input("Εισάγετε διάστημα ονομάτων στη μορφή X,X: ").upper().split(',')
    num_awards = int(input("Εισάγετε ελάχιστο αριθμό βραβείων: "))

    # Επιλογή πολυδιάστατης δομής για αποθήκευση των δεδομένων
    print("\n1. k-d tree\n2. Quad tree\n3. Range tree\n4. R-tree")
    user_choice = int(input("Επιλέξτε δομή: "))

    start_time = time.time()

    if user_choice == 1:     # Δομή k-d tree
        pass
    elif user_choice == 2:   # Δομή Quad tree
        pass
    elif user_choice == 3:   # Δομή Range tree
        range_tree = build_range_tree()
        results = query_range_tree(range_tree, min_letter, max_letter, num_awards)
        display_results(results)
        n_buckets = len(results) * 2
        lsh_test(results, lsh_threshold, n_buckets)
    elif user_choice == 4:   # Δομή R-tree
        rtree = build_rtree()
        results = query_rtree(rtree, min_letter, max_letter, num_awards)
        display_results(results)
        n_buckets = len(results) * 2
        lsh_test(results, lsh_threshold, n_buckets)

    end_time = time.time()
    print(end_time - start_time)

