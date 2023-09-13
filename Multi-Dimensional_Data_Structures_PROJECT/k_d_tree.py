import pandas as pd
import numpy as np
from scipy.spatial import cKDTree


class KDTree:
    def __init__(self):
        self.data_list = []  # Λίστα για αποθήκευση των δεδομένων


def build_kdtree():
    df = pd.read_csv("scientists_data.csv")
    points_xy = []  # Store numerical data points
    data_mapping = {}  # Create a mapping between KD-tree indices and data

    for i in range(len(df)):
        x = ord(df.iloc[i]['surname'][0]) - 65
        y = df.iloc[i]['awards']
        data = (df.iloc[i]['surname'], df.iloc[i]['awards'], df.iloc[i]['education'])
        points_xy.append([x, y])
        data_mapping[i] = data  # Create a mapping between index and data

    kdtree = cKDTree(points_xy)  # Create a KD-tree using numerical points
    return kdtree, points_xy, data_mapping  # Return the KD-tree and data mapping


def query_kdtree(kdtree, min_letter, max_letter, num_awards):
    # Υπολογισμός των αριθμητικών τιμών του ελάχιστου και του μέγιστου γράμματος
    min_letter = ord(min_letter) - 65
    max_letter = ord(max_letter) - 65

    # UPDATE se liges wres

    print(indices)
