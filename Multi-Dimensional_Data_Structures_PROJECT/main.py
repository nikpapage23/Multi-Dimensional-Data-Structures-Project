from r_tree import *
from range_tree import *
from beautifultable import BeautifulTable
import time
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)


def display_results(results_list):
    table = BeautifulTable(maxwidth=150)
    table.column_headers = ["Surname", "Awards", "Education"]

    sorted_list = sorted(results_list, key=lambda x: x["surname"])

    for result in sorted_list:
        table.append_row([result["surname"], result["awards"], result["education"]])

    print(table)


if __name__ == '__main__':
    # Εισαγωγή των απαιτούμενων πληροφοριών αναζήτησης από τον χρήστη
    lsh_threshold = float(input("Εισάγετε ελάχιστο ποσοστό ομοιότητας (0 - 1): "))
    min_letter, max_letter = input("Εισάγετε διάστημα ονομάτων στη μορφή X,X: ").split(',')
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

    end_time = time.time()
    print(end_time - start_time)

