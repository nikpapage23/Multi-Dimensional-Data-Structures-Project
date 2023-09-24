import pandas as pd
from rtree import index
from auxiliary import letter_normalization

class RTree:
    def __init__(self):
        self.idx = index.Index()  # Δημιουργία ενός R-tree index
        self.data_list = []  # Λίστα για αποθήκευση των δεδομένων

    def insert(self, item_id, item, x, y):
        self.idx.insert(item_id, (x, y, x, y))
        self.data_list.append(item)

    def search(self, query_bbox):
        return list(self.idx.intersection(query_bbox))


def build_rtree():
    df = pd.read_csv("scientists_data.csv")
    rtree = RTree()  # Δημιουργία ενός νέου R-tree

    # Για κάθε εγγραφή του dataframe, υπολογίζουμε τις συντεταγμένες (x, y)
    # βάσει της αριθμητική τιμής του πρώτου γράμματος του επωνύμου και του
    # αριθμού των βραβείων αντίστοιχα, και εισάγουμε το στοιχείο στο R-tree.
    for i in range(len(df)):
        x = letter_normalization(df.iloc[i]['surname'][0])
        y = df.iloc[i]['awards']
        data = (df.iloc[i]['surname'], df.iloc[i]['awards'], df.iloc[i]['education'])
        rtree.insert(i, data, x, y)  # Εισαγωγή του στοιχείου στο R-tree

    return rtree


def query_rtree(rtree, min_letter, max_letter, num_awards):
    # Υπολογισμός των αριθμητικών τιμών του ελάχιστου και του μέγιστου γράμματος

    min_letter = letter_normalization(min_letter)
    max_letter = letter_normalization(max_letter)

    query_bbox = (min_letter, num_awards, max_letter, float('inf'))
    matches = rtree.search(query_bbox)  # Αναζήτηση στο R-tree με βάση το δοθέν query_bbox

    query_results = []
    # Ανάκτηση των δεδομένων από τα αποτελέσματα της αναζήτησης
    for match in matches:
        surname, awards, education = rtree.data_list[match]
        query_results.append({"surname": surname, "awards": awards, "education": education})

    return query_results
