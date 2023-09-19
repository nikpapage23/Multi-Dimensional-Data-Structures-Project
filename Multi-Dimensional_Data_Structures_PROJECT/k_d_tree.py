import pandas as pd
from scipy.spatial import cKDTree

class KDTree:
    def __init__(self, point, left=None, right=None):
        self.point = point
        self.left = left
        self.right = right

def kd_tree(points, depth=0):
    if len(points) == 0:
        return None

    k = 2  # 2-dimensional space
    axis = depth % k

    points.sort(key=lambda x: x[axis])
    median = len(points) // 2

    return KDTree(
        point=points[median],
        left=kd_tree(points[:median], depth + 1),
        right=kd_tree(points[median + 1:], depth + 1)
    )

def insert(node, point, depth=0):
    if node is None:
        return KDTree(point)

    k = 2  # 2-dimensional space
    axis = depth % k

    if point[axis] < node.point[axis]:
        node.left = insert(node.left, point, depth + 1)
    else:
        node.right = insert(node.right, point, depth + 1)

    return node

def print_tree(node, depth=0):
    if node is None:
        return
    print("  " * depth + str(node.point))
    print_tree(node.left, depth + 1)
    print_tree(node.right, depth + 1)

def range_query(node, min_point, max_point, depth=0):
    if node is None:
        return []

    k = 2  # 2-dimensional space
    axis = depth % k

    if min_point[0] <= node.point[0] <= max_point[0] and min_point[1] <= node.point[1] <= max_point[1]:
        left_points = range_query(node.left, min_point, max_point, depth + 1)
        right_points = range_query(node.right, min_point, max_point, depth + 1)
        return left_points + [node.point] + right_points
    elif min_point[axis] <= node.point[axis]:
        return range_query(node.left, min_point, max_point, depth + 1)
    else:
        return range_query(node.right, min_point, max_point, depth + 1)



def build_kdtree():
    df = pd.read_csv("scientists_data.csv")
    points_xy = []  # x , y = (int)surname, awards
    data_mapping = {}  # Mapping x,y -> education

    # Αποθήκευση των δεδομένων surname & awards του .csv σε πίνακα
    # και mapping όλων των στοιχείων για εύκολη πρόσβαση στο education
    for i in range(len(df)):
        x = ord(df.iloc[i]['surname'][0]) - 65
        y = df.iloc[i]['awards']
        data = (df.iloc[i]['surname'], df.iloc[i]['awards'], df.iloc[i]['education'])
        points_xy.append([x, y])
        data_mapping[i] = data

    # Δημιουργία δέντρου χρησιμοποιώντας τα x, y points
    kdtree = kd_tree(points_xy)

    return kdtree, data_mapping


def query_kdtree(kdtree, data_mapping, min_letter, max_letter, num_awards):
    # Υπολογισμός των αριθμητικών τιμών του ελάχιστου και του μέγιστου γράμματος
    min_letter = ord(min_letter) - 65
    max_letter = ord(max_letter) - 65

    min_point = (min_letter, max_letter)
    max_point = (num_awards, float('inf'))

    print("\nPoints in range", min_point, "to", max_point)

    matches = range_query(kdtree, min_point, max_point)

    for point in matches:
        print(point)

    # TODO: Convert results to readable form