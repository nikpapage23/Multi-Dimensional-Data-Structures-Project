from r_tree import *
from k_d_tree import *
from range_tree import *
from quad_tree import *
from lsh.lsh import *
from lsh.tools import *
from beautifultable import BeautifulTable
import warnings
import time
warnings.filterwarnings("ignore", category=FutureWarning)
from numpy import stack
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer

def display_results(results_list):
    table = BeautifulTable(maxwidth=150)
    table.column_headers = ["Surname", "Awards", "Education"]

    sorted_list = sorted(results_list, key=lambda x: x["surname"])

    for result in sorted_list:
        table.append_row([result["surname"], result["awards"], result["education"]])

    print(table)
    print(str(len(table))+" results")

def lsh_test(lst, thrs, buc):
    print(str(buc)+" buckets")
    # υπολογισμός hash functions ανάλογα με το πόσα buckets έχουμε
    if buc > 300:
        n_func = 20
    else:
        n_func = 10
    print(str(n_func)+ " hash functions")
    lst = sorted(lst, key=lambda x: x["surname"])
    # μετατροπή λίστας σε dataframe
    df = pd.DataFrame(lst)
    # επεξεργασία κειμένου
    stemming_and_stopwords(df)
    # δεδομένα για hashing
    data = df['education'].to_list()

    # δημιουργία του vocabulary των shingles        
    vocabulary = set().union(*[kshingle(sent, 2) for sent in data])
    
    # αναπαράσταση των κειμένων ως one hot
    one_hot_matrix = stack([one_hot_encoding(vocabulary, sent) for sent in data]).T

    # δημιουργία του LSH μοντέλου με n_func και buc
    lsh = LSH(n_func, 5).fit(one_hot_matrix, buc)

    # η μετρική ομοιότητας που θα χρησιμοποιηθεί 
    prefferedSimilarity = jaccard_binary

    # γειτονικά σημεία με similarity μεγαλύτερο από το user defined threshold
    actual_neigbors = lsh.neighbors(thrs, prefferedSimilarity)
    print(str(len(actual_neigbors))+" candidates with at least "+str(int(thrs*100))+" % similarity using "+prefferedSimilarity.__name__)
    print(actual_neigbors, end='\n\n')

def stemming_and_stopwords(df):
    stop_words = set(stopwords.words('english'))
    stemmer = PorterStemmer()
    df.loc[:, 'education'] = df['education'].apply(lambda doc: ' '.join([stemmer.stem(w) for w in doc.split() if w not in stop_words]))
    # αφαίρεση χαρακτήρων που δεν είναι γράμματα αλφαβήτου
    df.loc[:, 'education'] = df['education'].apply(lambda doc: ' '.join(letter for letter in doc.split() if letter.isalnum()))
    # αφαίρεση αριθμών
    df['education'] = df['education'].str.replace(r'\d+', '', regex=True)
    # αφαίρεση παρενθέσεων
    df['education'] = df['education'].str.replace(r'\(', '', regex=True)
    df['education'] = df['education'].str.replace(r'\)', '', regex=True)

def main_app(lsh_threshold, min_letter, max_letter, num_awards, user_choice):
    start_time = time.time()
    if user_choice == 1:     # Δομή k-d tree
        k_d_tree = build_kdtree()
        results = query_kdtree(k_d_tree, min_letter, max_letter, num_awards)
        n_buckets = len(results) * 2
        display_results(results)
        lsh_test(results, lsh_threshold, n_buckets)
    elif user_choice == 2:   # Δομή Quad tree
        quad_tree = build_quad_tree()
        results = query_quad_tree(quad_tree, min_letter, max_letter, num_awards)
        n_buckets = len(results) * 2
        display_results(results)
        lsh_test(results, lsh_threshold, n_buckets)
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


if __name__ == '__main__':
    # Εισαγωγή των απαιτούμενων πληροφοριών αναζήτησης από τον χρήστη
    lsh_threshold = float(input("Εισάγετε ελάχιστο ποσοστό ομοιότητας (0 - 1): "))
    min_letter, max_letter = input("Εισάγετε διάστημα ονομάτων στη μορφή X,X: ").upper().split(',')
    num_awards = int(input("Εισάγετε ελάχιστο αριθμό βραβείων: "))
    # Επιλογή πολυδιάστατης δομής για αποθήκευση των δεδομένων
    print("\n1. k-d tree\n2. Quad tree\n3. Range tree\n4. R-tree")
    user_choice = int(input("Επιλέξτε δομή: "))

    main_app(lsh_threshold, min_letter, max_letter, num_awards, user_choice)
