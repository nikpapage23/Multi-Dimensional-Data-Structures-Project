import pandas as pd
from auxiliary import letter_normalization

# Αντιπροσωπεύει ένα σημείο στον δισδιάστατο (2D) χώρο,
# με συντεταγμένες x, y που μπορεί να έχει και συσχετισμένα δεδομένα.
class Point:
    def __init__(self, x, y, data=None):
        self.x = x
        self.y = y
        self.data = data


# Αντιπροσωπεύει ένα ορθογώνιο στον δισδιάστατο (2D) χώρο.
class Rect:
    def __init__(self, cx, cy, w, h):
        self.cx = cx    # η τιμή της συντεταγμένης x στο κέντρο του ορθογωνίου
        self.cy = cy    # η τιμή της συντεταγμένης y στο κέντρο του ορθογωνίου
        self.w = w      # το πλάτος του ορθογωνίου
        self.h = h      # το ύψος του ορθογωνίου

        # Βάσει των παραπάνω, υπολογίζονται οι τέσσερις πλευρές του ορθογωνίου
        # (δυτική, ανατολική, βόρεια, νότια).
        self.west_edge = cx - w/2
        self.east_edge = cx + w/2
        self.north_edge = cy - h/2
        self.south_edge = cy + h/2

    # Ελέγχει αν ένα δοθέν σημείο βρίσκεται εντός των ορίων του ορθογωνίου.
    def contains(self, point):
        point_x, point_y = point.x, point.y

        return (self.west_edge <= point_x <= self.east_edge and
                self.north_edge <= point_y <= self.south_edge)

    # Ελέγχει αν ένα άλλο ορθογώνιο τέμνει ή όχι το τρέχον ορθογώνιο.
    def intersects(self, other):
        return not (other.west_edge > self.east_edge or
                    other.east_edge < self.west_edge or
                    other.north_edge > self.south_edge or
                    other.south_edge < self.north_edge)


class QuadTree:
    def __init__(self, boundary, max_points=4, depth=0):
        self.boundary = boundary    # ο χώρος που καλύπτει ο κόμβος του Quad Tree
        self.max_points = max_points  # ο μέγιστος αριθμός σημείων που μπορεί να φιλοξενήσει ο κόμβος
        self.points = []    # λίστα με τα σημεία που φιλοξενεί ο κόμβος
        self.depth = depth  # το βάθος του κόμβου στο δέντρο
        self.divided = False  # μεταβλητή-flag για το αν ο κόμβος έχει διασπαστεί
        self.sw = None  # νοτιοδυτικός (southwest) υπο-κόμβος
        self.se = None  # νοτιοανατολικός (southeast) υπο-κόμβος
        self.ne = None  # βορειοανατολικός (northeast) υπο-κόμβος
        self.nw = None  # βορειοδυτικός (northwest) υπο-κόμβος

    # Διασπάει τον τρέχοντα κόμβο σε τέσσερις υπο-κόμβους.
    # Κάθε υπο-κόμβος αντιπροσωπεύει ένα τέταρτο (1/4) του χώρου που καλύπτει ο γονεϊκός κόμβος.
    def divide(self):
        cx, cy = self.boundary.cx, self.boundary.cy
        w, h = self.boundary.w / 2, self.boundary.h / 2

        self.nw = QuadTree(Rect(cx - w/2, cy - h/2, w, h), self.max_points, self.depth + 1)
        self.ne = QuadTree(Rect(cx + w/2, cy - h/2, w, h), self.max_points, self.depth + 1)
        self.se = QuadTree(Rect(cx + w/2, cy + h/2, w, h), self.max_points, self.depth + 1)
        self.sw = QuadTree(Rect(cx - w/2, cy + h/2, w, h), self.max_points, self.depth + 1)

        self.divided = True

    # Προσπαθεί να εισάγει ένα σημείο στο Quad Tree.
    def insert(self, point):
        if not self.boundary.contains(point):
            # Αν το σημείο δε βρίσκεται εντός των ορίων του τρέχοντα κόμβου, η εισαγωγή αποτυγχάνει.
            return False
        if len(self.points) < self.max_points:
            # Αν υπάρχει αρκετός χώρος στον τρέχοντα κόμβο, τότε το σημείο προστίθεται στον κόμβο.
            self.points.append(point)
            return True

        # Αν ο κόμβος έχει συμπληρώσει το μέγιστο πλήθος σημείων και δεν έχει διασπαστεί ακόμα,
        # τότε διασπάται με κλήση της μεθόδου divide().
        if not self.divided:
            self.divide()

        # Εισαγωγή του σημείου σε κάποιον από τους υπο-κόμβους που προέκυψαν από τη διάσπαση.
        return (self.ne.insert(point) or
                self.nw.insert(point) or
                self.se.insert(point) or
                self.sw.insert(point))

    # Αναζητά όλα τα σημεία που βρίσκονται εντός ενός δεδομένου ορθογωνίου (boundary).
    def query(self, boundary, found_points):
        if not self.boundary.intersects(boundary):
            # Αν το boundary ΔΕΝ τέμνει τον τρέχοντα κόμβο, τότε δεν υπάρχει λόγος
            # να συνεχίσουμε την αναζήτηση σ' αυτόν τον κόμβο ή στους υπο-κόμβους του.
            return False

        # Αν το boundary τέμνει τον τρέχοντα κόμβο, τότε ελέγχουμε κάθε σημείο
        # που βρίσκεται στον κόμβο για να δούμε αν βρίσκεται εντός του boundary.
        for point in self.points:
            if boundary.contains(point):
                found_points.append(point)

        # Αν ο τρέχοντας κόμβος έχει υπο-κόμβους (δηλαδή έχει διασπαστεί),
        # τότε επαναλαμβάνουμε τη διαδικασία αναζήτησης για κάθε υπο-κόμβο.
        if self.divided:
            self.nw.query(boundary, found_points)
            self.ne.query(boundary, found_points)
            self.se.query(boundary, found_points)
            self.sw.query(boundary, found_points)

        return found_points


def read_data():
    df = pd.read_csv("scientists_data.csv")
    points = []

    # Για κάθε εγγραφή του dataframe, υπολογίζουμε τις συντεταγμένες (x, y)
    # βάσει της αριθμητικής τιμής του πρώτου γράμματος του επωνύμου και του
    # αριθμού των βραβείων αντίστοιχα, και εισάγουμε το σημείο στη λίστα points.
    for i in range(len(df)):
        x = letter_normalization(df.iloc[i]['surname'][0])
        y = df.iloc[i]['awards']
        data = (df.iloc[i]['surname'], df.iloc[i]['awards'], df.iloc[i]['education'])
        points.append((x, y, data))

    return points


def build_quad_tree():
    points = read_data()

    # Μετατροπή της λίστας με τις πλειάδες, σε μία λίστα με αντικείμενα τύπου Point
    point_objects = [Point(x, y, data) for x, y, data in points]

    # Υπολογισμός των μέγιστων τιμών των συντεταγμένων x, y
    max_x = max(point[0] for point in points)
    max_y = max(point[1] for point in points)

    # Δημιουργία ενός ορθογωνίου για το Quad Tree που περιλαμβάνει όλα τα σημεία,
    # βάσει των μέγιστων συντεταγμένων που υπολογίστηκαν
    boundary = Rect(max_x / 2, max_y / 2, max_x, max_y)

    # Αρχικοποίηση του Quad Tree με το παραπάνω boundary και με το πολύ 4 σημεία ανά κόμβο
    qt = QuadTree(boundary, 4)

    # Εισαγωγή κάθε σημείου στο Quad Tree
    for point in point_objects:
        qt.insert(point)

    return qt


def query_quad_tree(tree, min_letter, max_letter, num_awards):
    # Υπολογισμός των αριθμητικών τιμών του ελάχιστου και του μέγιστου γράμματος
    min_letter = letter_normalization(min_letter)
    max_letter = letter_normalization(max_letter)

    # Εύρεση του μέγιστου αριθμού βραβείων που υπάρχει (max_y)
    points = read_data()
    max_awards = max(point[1] for point in points)

    # Δημιουργία του ορθογωνίου αναζήτησης, βάσει των δεδομένων του ερωτήματος
    center_x = (min_letter + max_letter) / 2
    center_y = (num_awards + max_awards) / 2
    width = max_letter - min_letter
    height = max_awards - num_awards
    search_boundary = Rect(center_x, center_y, width, height)

    # Αναζήτηση στο Quad Tree για τα σημεία που εμπίπτουν στο search_boundary
    matches = tree.query(search_boundary, [])

    query_results = []
    # Αποθήκευση των δεδομένων των σημείων σε λίστα
    for match in matches:
        surname, awards, education = match.data
        query_results.append({"surname": surname, "awards": awards, "education": education})

    return query_results
