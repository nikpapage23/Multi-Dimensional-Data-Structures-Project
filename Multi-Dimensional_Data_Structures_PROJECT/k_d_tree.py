import pandas as pd

class Node:
    def __init__(self, point, axis):
        self.point = point
        self.left = None
        self.right = None
        self.axis = axis

class KDTree:
    def __init__(self):
        self.root = None

    def build(self, points, depth=0):
        if not points:
            return None

        axis = depth % 2
        points.sort(key=lambda x: x[axis])
        median = len(points) // 2

        node = Node(points[median], axis)
        node.left = self.build(points[:median], depth + 1)
        node.right = self.build(points[median + 1:], depth + 1)

        return node

    def insert(self, point):
        self.root = self._insert(self.root, point)

    def _insert(self, root, point, depth=0):
        if root is None:
            return Node(point, depth % 2)

        if point == root.point:
            return root

        if point[root.axis] < root.point[root.axis]:
            root.left = self._insert(root.left, point, depth + 1)
        else:
            root.right = self._insert(root.right, point, depth + 1)

        return root

    def query(self, rect, node=None):
        if node is None:
            node = self.root

        if node is None:
            return []

        x1, y1, x2, y2 = rect
        results = []

        if x1 <= node.point[0] <= x2 and y1 <= node.point[1] <= y2:
            results.append(node.point)

        if node.left and (node.axis == 1 or x1 <= node.point[0]):
            results.extend(self.query(rect, node.left))
        if node.right and (node.axis == 1 or x2 >= node.point[0]):
            results.extend(self.query(rect, node.right))

        return results

def build_kdtree():
    df = pd.read_csv("scientists_data.csv")
    points = []  # x , y = (int)surname, awards

    # Για κάθε εγγραφή του dataframe, υπολογίζουμε τις συντεταγμένες (x, y)
    # βάσει της αριθμητικής τιμής του πρώτου γράμματος του επωνύμου και του
    # αριθμού των βραβείων αντίστοιχα, και εισάγουμε το σημείο στη λίστα points.
    for i in range(len(df)):
        x = ord(df.iloc[i]['surname'][0]) - 65
        y = df.iloc[i]['awards']
        data = (df.iloc[i]['surname'], df.iloc[i]['awards'], df.iloc[i]['education'])
        points.append((x, y, i))

    # Δημιουργία δέντρου χρησιμοποιώντας τα x, y points
    kdtree = KDTree()
    kdtree.root = kdtree.build(points)

    return kdtree

def query_kdtree(kdtree, min_letter, max_letter, num_awards):
    # Υπολογισμός των αριθμητικών τιμών του ελάχιστου και του μέγιστου γράμματος
    min_letter = ord(min_letter) - 65
    max_letter = ord(max_letter) - 65

    # (x1, y1, x2, y2)
    rectangle = (min_letter, num_awards, max_letter, float('inf'))

    query_results = []
    query_results = kdtree.query(rectangle)

    final_results = []
    df = pd.read_csv("scientists_data.csv")

    for result in query_results:
        index = result[2]  # παίρνουμε το index από τα δεδομένα του Range Tree
        surname = df.iloc[index]['surname']
        awards = df.iloc[index]['awards']
        education = df.iloc[index]['education']
        final_results.append({"surname": surname, "awards": awards, "education": education})

    return final_results
