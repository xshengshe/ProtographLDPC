
import Utils
from TannerGraph import *


class Protograph(TannerGraph):
    """
    This TannerGraph subclass constructs the tanner_graph dictionary as a dictionary of lists of ProtographEntry objects.
    This allows each entry to have an entry value not necessarily equal to 1.
    """

    # parameters:
    #   args: list(list()), a list of entries where each entry is a list of length three. These entry lists contain
    #   their row value at position 0, column value at position 1, and value at position 2
    # return:
    #   a fully constructed Protograph object
    def __init__(self, args):
        TannerGraph.__init__(self, args)

        self.tanner_graph = Protograph.create_tanner_graph_for_protograph(args)

        self.height = len(self.tanner_graph)
        self.width = self.get_width()

    # return:
    #   the width of a protograph tanner_graph (the superclass get_width does not work here as entry values should no longer by inferred)
    def get_width(self):
        max = 0
        for row in self.tanner_graph:
            for entry in self.getRow(row):
                if entry.index > max:
                    max = entry.index
        return max + 1

    '''
    Constructs a protograph object from the supplied point list
    '''

    # parameters:
    #   points: list, the list of points defining the protograph
    # return:
    #   the tanner_graph which represents the Protograph object
    @staticmethod
    def create_tanner_graph_for_protograph(points):

        protograph = TannerGraph(None)

        num_rows = 0
        for entry in points:
            if entry[0] + 1 > num_rows:
                num_rows = entry[0] + 1

        for row in range(num_rows):
            protograph.addRow()

        for entry in points:
            protograph.getRow(entry[0]).append(ProtographEntry(entry[1], entry[2]))

        return protograph.tanner_graph



    '''
    This method allows the protograph to be queried as if was defined by a matrix structure. This is necessary here and
    not in TannerGraph as Protographs are the only TannerGraphs who's values can be greater than 1.
    '''

    # parameters:
    #   r: int, row index of fetched entry
    #   c: int, col index of fetched entry
    # return:
    #   the value of the entry at location [r, c] in self.tanner_graph
    def get(self, r, c):
        row = self.getRow(r)
        for entry in row:
            if entry.index == c:
                return entry.value
        return 0

    def get_max_index(self, row):
        row = self.tanner_graph[row]
        max_index = 0
        for i in range(len(row)):
            if row[i].index > max_index:
                max_index = row[i].index
        return max_index

    def contains_index(self, index, row):
        pulled = self.tanner_graph[row]
        for e in pulled:
            if e.index == index:
                return True
        return False

    def as_matrix(self):
        return get_matrix_representation(self)

def get_matrix_representation(protograph):
    matrix = []
    for i in range(protograph.height):
        row = []
        if i in protograph.tanner_graph:
            for j in range(protograph.get_max_index(i) + 1):
                if protograph.contains_index(j, i):
                    row.append(protograph.get(i, j))
                else:
                    row.append(0)
        matrix.append(row)
    normalize(matrix)
    return matrix



'''
This class represents a protograph entry; it allows for entry values to be greater than 1 
'''


class ProtographEntry:

    def __init__(self, index, value):
        self.value = value
        self.index = index
