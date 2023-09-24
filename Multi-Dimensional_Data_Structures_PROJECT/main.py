from trees.r_tree import *
from trees.k_d_tree import *
from trees.range_tree import *
from trees.quad_tree import *
from lsh.lsh import *
from lsh.tools import *
from auxiliary import display_results, save_results
from numpy import stack
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)


def lsh_test(lst, threshold, buc):
    # υπολογισμός hash functions ανάλογα με το πόσα buckets έχουμε
    if buc > 300:
        n_func = 20
    else:
        n_func = 10

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
    preferred_similarity = jaccard_binary

    # γειτονικά σημεία με similarity μεγαλύτερο από το user defined threshold
    actual_neighbors = lsh.neighbors(threshold, preferred_similarity)
    print(str(len(actual_neighbors)) + " candidates with at least " + str(int(threshold * 100))
          + " % similarity using " + preferred_similarity.__name__ + ":\n")

    i = 1
    for key in sorted(actual_neighbors, key=actual_neighbors.get):
        print(str(i) + ". Similarity: " + str(round(actual_neighbors[key] * 100, 2)) + "%")
        print(display_results([lst[key[0]]] + [lst[key[1]]]), end='\n\n')
        i += 1


def stemming_and_stopwords(df):
    stop_words = set(stopwords.words('english'))
    stemmer = PorterStemmer()
    # Εφαρμογή stemming και αφαίρεση των stopwords
    df.loc[:, 'education'] = df['education'].\
        apply(lambda doc: ' '.join([stemmer.stem(w) for w in doc.split() if w not in stop_words]))
    # Αφαίρεση χαρακτήρων που δεν είναι γράμματα αλφαβήτου
    df.loc[:, 'education'] = df['education'].\
        apply(lambda doc: ' '.join(letter for letter in doc.split() if letter.isalnum()))
    # Αφαίρεση αριθμών
    df['education'] = df['education'].str.replace(r'\d+', '', regex=True)
    # Αφαίρεση παρενθέσεων
    df['education'] = df['education'].str.replace(r'\(', '', regex=True)
    df['education'] = df['education'].str.replace(r'\)', '', regex=True)


def main_app(lsh_threshold, min_letter, max_letter, num_awards, user_choice):
    results = []

    if user_choice == 1:     # Δομή k-d tree
        k_d_tree = build_kdtree()
        results = query_kdtree(k_d_tree, min_letter, max_letter, num_awards)
    elif user_choice == 2:   # Δομή Quad tree
        quad_tree = build_quad_tree()
        results = query_quad_tree(quad_tree, min_letter, max_letter, num_awards)
    elif user_choice == 3:   # Δομή Range tree
        range_tree = build_range_tree()
        results = query_range_tree(range_tree, min_letter, max_letter, num_awards)
    elif user_choice == 4:   # Δομή R-tree
        rtree = build_rtree()
        results = query_rtree(rtree, min_letter, max_letter, num_awards)

    if results:
        save_results(results)   # αποθήκευση των συνολικών αποτελεσμάτων σε ένα εξωτερικό αρχείο
        n_buckets = len(results) * 2
        lsh_test(results, lsh_threshold, n_buckets)  # εφαρμογή μεθόδου LSH
    else:
        print("No results found for these inputs.")


if __name__ == '__main__':
    # Εισαγωγή των απαιτούμενων πληροφοριών αναζήτησης από τον χρήστη
    thresh = float(input("Εισάγετε ελάχιστο ποσοστό ομοιότητας (0 - 1): "))
    letter1, letter2 = input("Εισάγετε διάστημα ονομάτων στη μορφή X,X: ").upper().split(',')
    awards = int(input("Εισάγετε ελάχιστο αριθμό βραβείων: "))

    # Επιλογή πολυδιάστατης δομής για αποθήκευση των δεδομένων
    print("\n1. k-d tree\n2. Quad tree\n3. Range tree\n4. R-tree")
    user_input = int(input("Επιλέξτε δομή: "))

    main_app(thresh, letter1, letter2, awards, user_input)
