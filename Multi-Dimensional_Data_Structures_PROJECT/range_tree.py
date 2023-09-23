import pandas as pd
from main import letter_normalization

'''
Η λογική ενός δισδιάστατου (2D) Range Tree είναι ότι για μία δοθείσα συλλογή από σημεία P,
κατασκευάζουμε αρχικά ένα BBST (Binary Balanced Search Tree) βασισμένο στις συντεταγμένες x
των σημείων. Έπειτα, κάθε κόμβος του αρχικού BBST, αποθηκεύει ένα δευτερεύον BBST, το οποίο
κατασκευάζεται από τα σημεία που έχουν την ίδια συντεταγμένη x με τον τρέχοντα κόμβο, αλλά
ταξινομημένα βάσει των συντεταγμένων y τους.
'''


class Node1D:
    def __init__(self, y, i_list):
        self.y = y  # το y-value του κόμβου
        self.i_list = i_list    # λίστα με τους αριθμούς των rows του dataframe που αντιστοιχούν στα (x, y)
        self.left = None    # ο αριστερός κόμβος
        self.right = None   # ο δεξιός κόμβος
        self.height = 1  # το αρχικό ύψος του κόμβου

    def merge_i_list(self, i_list):
        # Συγχώνευση μιας λίστας με την υπάρχουσα λίστα του κόμβου και αφαίρεση διπλότυπων
        self.i_list.extend(i_list)
        self.i_list = list(set(self.i_list))


class RangeTree1D:
    def __init__(self, points):
        self.root = self.build(points)  # κατασκευή του 1D δέντρου για τα δοθέντα points

    def insert(self, root, y, i):
        # Εισαγωγή ενός νέου σημείου στο 1D δέντρο και εφαρμογή της διαδικασίας εξισορρόπησής του
        if not root:
            return Node1D(y, [i])
        if y == root.y:     # αν υπάρχει ήδη κόμβος με το ίδιο y-value, συγχωνεύστε σε μία λίστα τα i's
            root.merge_i_list([i])
        elif y < root.y:    # εισαγωγή του κόμβου στο αριστερό υπο-δέντρο
            root.left = self.insert(root.left, y, i)
        else:               # εισαγωγή του κόμβου στο δεξί υπο-δέντρο
            root.right = self.insert(root.right, y, i)

        # Ενημέρωση του ύψους του τρέχοντα κόμβου με βάση τα ύψη των υπο-δέντρων του
        root.height = 1 + max(self.get_height(root.left), self.get_height(root.right))

        # Υπολογισμός του παράγοντα ισορροπίας του τρέχοντα κόμβου
        balance = self.get_balance(root)

        # Αν ο κόμβος είναι "βαρύς" από τα αριστερά
        if balance > 1:
            # Αν το y είναι μεγαλύτερο από το y του αριστερού παιδιού του κόμβου,
            # τότε γίνεται αριστερή περιστροφή στο αριστερό παιδί του κόμβου
            if y > root.left.y:
                root.left = self.left_rotate(root.left)
            # Δεξιά περιστροφή του τρέχοντα κόμβου
            return self.right_rotate(root)

        # Αν ο κόμβος είναι "βαρύς" από τα δεξιά
        if balance < -1:
            # Αν το y είναι μικρότερο από το y του δεξιού παιδιού του κόμβου,
            # τότε γίνεται δεξιά περιστροφή στο δεξί παιδί του κόμβου
            if y < root.right.y:
                root.right = self.right_rotate(root.right)
            # Αριστερή περιστροφή του τρέχοντα κόμβου
            return self.left_rotate(root)

        return root

    def build(self, points):
        root = None
        for _, y, i in points:
            root = self.insert(root, y, i)
        return root

    # Συνάρτηση για επιστροφή του ύψους ενός κόμβου
    def get_height(self, node):
        if not node:
            return 0
        return node.height

    # Συνάρτηση για την επιστροφή του παράγοντα ισορροπίας ενός κόμβου
    # (η διαφορά ύψους μεταξύ των δύο υπο-δέντρων του)
    def get_balance(self, node):
        if not node:
            return 0
        return self.get_height(node.left) - self.get_height(node.right)

    # Περιστροφή κόμβου προς τα δεξιά
    def right_rotate(self, y):
        x = y.left
        T3 = x.right
        x.right = y
        y.left = T3
        y.height = max(self.get_height(y.left), self.get_height(y.right)) + 1
        x.height = max(self.get_height(x.left), self.get_height(x.right)) + 1
        return x

    # Περιστροφή κόμβου προς τα αριστερά
    def left_rotate(self, x):
        y = x.right
        T2 = y.left
        y.left = x
        x.right = T2
        x.height = max(self.get_height(x.left), self.get_height(x.right)) + 1
        y.height = max(self.get_height(y.left), self.get_height(y.right)) + 1
        return y

    # Αναζήτηση στο 1D δέντρο
    def query(self, node, y1, y2, result):
        if not node:
            return
        if y1 <= node.y <= y2:
            for i in node.i_list:
                result.append((node.y, i))
        if y1 < node.y:
            self.query(node.left, y1, y2, result)
        if y2 > node.y:
            self.query(node.right, y1, y2, result)


class Node2D:
    def __init__(self, x, points):
        self.x = x  # το x-value του κόμβου
        self.y_tree = RangeTree1D(points)   # το 1D δέντρο του κόμβου που περιέχει τα σημεία που έχουν το ίδιο x
        self.left = None    # ο αριστερός κόμβος
        self.right = None   # ο δεξιός κόμβος
        self.height = 1     # το αρχικό ύψος του κόμβου

    def merge_point(self, y, i):
        # Συγχώνευση ενός σημείου με την ίδια συντεταγμένη x στο y_tree του κόμβου
        self.y_tree.insert(self.y_tree.root, y, i)


class RangeTree2D:
    def __init__(self, points):
        self.root = self.build(points)  # κατασκευή του 2D δέντρου για τα δοθέντα points

    def insert(self, root, x, y, i, points):
        # Εισαγωγή ενός νέου σημείου στο 2D δέντρο και εφαρμογή της διαδικασίας εξισορρόπησής του
        if not root:
            return Node2D(x, [(x, y, i)])
        if x == root.x:     # αν υπάρχει ήδη κόμβος με το ίδιο x-value, κάνε εισαγωγή κόμβου στο αντίστοιχο y_tree
            root.y_tree.root = root.y_tree.insert(root.y_tree.root, y, i)
        elif x < root.x:    # εισαγωγή του κόμβου στο αριστερό υπο-δέντρο
            root.left = self.insert(root.left, x, y, i, [(x, y, i)])
        else:               # εισαγωγή του κόμβου στο δεξί υπο-δέντρο
            root.right = self.insert(root.right, x, y, i, [(x, y, i)])

        # Ενημέρωση του ύψους του τρέχοντα κόμβου με βάση τα ύψη των υπο-δέντρων του
        root.height = 1 + max(self.get_height(root.left), self.get_height(root.right))

        # Υπολογισμός του παράγοντα ισορροπίας του τρέχοντα κόμβου
        balance = self.get_balance(root)

        # Αν ο κόμβος είναι "βαρύς" από τα αριστερά
        if balance > 1:
            # Αν το x είναι μεγαλύτερο από το x του αριστερού παιδιού του κόμβου,
            # τότε γίνεται αριστερή περιστροφή στο αριστερό παιδί του κόμβου
            if x > root.left.x:
                root.left = self.left_rotate(root.left)
            # Αριστερή περιστροφή του τρέχοντα κόμβου
            return self.right_rotate(root)

        # Αν ο κόμβος είναι "βαρύς" από τα δεξιά
        if balance < -1:
            # Αν το x είναι μικρότερο από το x του δεξιού παιδιού του κόμβου,
            # τότε γίνεται δεξιά περιστροφή στο δεξί παιδί του κόμβου
            if x < root.right.x:
                root.right = self.right_rotate(root.right)
            # Δεξιά περιστροφή του τρέχοντα κόμβου
            return self.left_rotate(root)

        return root

    def build(self, points):
        root = None
        for point in points:
            x, y, i = point
            root = self.insert(root, x, y, i, [point])
        return root

    # Συνάρτηση για επιστροφή του ύψους ενός κόμβου
    def get_height(self, node):
        if not node:
            return 0
        return node.height

    # Συνάρτηση για την επιστροφή του παράγοντα ισορροπίας ενός κόμβου
    # (η διαφορά ύψους μεταξύ των δύο υπο-δέντρων του)
    def get_balance(self, node):
        if not node:
            return 0
        return self.get_height(node.left) - self.get_height(node.right)

    # Περιστροφή προς τα δεξιά
    def right_rotate(self, y):
        x = y.left
        T3 = x.right
        x.right = y
        y.left = T3
        y.height = max(self.get_height(y.left), self.get_height(y.right)) + 1
        x.height = max(self.get_height(x.left), self.get_height(x.right)) + 1
        return x

    # Περιστροφή προς τα αριστερά
    def left_rotate(self, x):
        y = x.right
        T2 = y.left
        y.left = x
        x.right = T2
        x.height = max(self.get_height(x.left), self.get_height(x.right)) + 1
        y.height = max(self.get_height(y.left), self.get_height(y.right)) + 1
        return y

    # Αναζήτηση στο 2D δέντρο
    def query(self, node, x1, x2, y1, y2, result):
        if not node:
            return
        if x1 <= node.x <= x2:
            y_result = []
            node.y_tree.query(node.y_tree.root, y1, y2, y_result)
            for y, i in y_result:
                result.append((node.x, y, i))
        if x1 < node.x:
            self.query(node.left, x1, x2, y1, y2, result)
        if x2 > node.x:
            self.query(node.right, x1, x2, y1, y2, result)


def build_range_tree():
    df = pd.read_csv("scientists_data.csv")
    points = []

    # Για κάθε εγγραφή του dataframe, υπολογίζουμε τις συντεταγμένες (x, y)
    # βάσει της αριθμητικής τιμής του πρώτου γράμματος του επωνύμου και του
    # αριθμού των βραβείων αντίστοιχα, και εισάγουμε το σημείο στη λίστα points.
    for i in range(len(df)):
        x = ord(df.iloc[i]['surname'][0]) - 65
        y = df.iloc[i]['awards']
        points.append((x, y, i))

    range_tree = RangeTree2D(points)    # δημιουργία ενός νέου Range Tree για τα δοθέντα points
    return range_tree


def query_range_tree(range_tree, min_letter, max_letter, num_awards):
    # Υπολογισμός των αριθμητικών τιμών του ελάχιστου και του μέγιστου γράμματος
    min_letter = letter_normalization(min_letter)
    max_letter = letter_normalization(max_letter)

    # Ορισμός των διαστημάτων τόσο στη συντεταγμένη x όσο και στη y, πάνω στα οποία θα γίνει η αναζήτηση
    x_range = (min_letter, max_letter)
    y_range = (num_awards, float('inf'))

    query_results = []
    # Αποστολή ερωτήματος στο Range Tree και αποθήκευση των αποτελεσμάτων στη λίστα query_results
    range_tree.query(range_tree.root, x_range[0], x_range[1], y_range[0], y_range[1], query_results)

    final_results = []
    df = pd.read_csv("scientists_data.csv")
    # Ανάκτηση των δεδομένων και αποθήκευσή τους σε λίστα
    for result in query_results:
        index = result[2]  # παίρνουμε το index από τα δεδομένα του Range Tree
        surname = df.iloc[index]['surname']
        awards = df.iloc[index]['awards']
        education = df.iloc[index]['education']
        final_results.append({"surname": surname, "awards": awards, "education": education})

    return final_results
