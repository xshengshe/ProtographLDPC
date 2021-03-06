import random
import tempfile
import os
import subprocess

from libs.TannerGraph import *

'''
A class for the handling of Regular LDPC matrices in tanner graph form

The tanner graph is stored as a dictionary, row indices (check nodes) are mapped to lists of column indices (variable
nodes) to indicate bipartite connections. Although this class defines regular matrices, it is not a requirement that
row and column weightages be constant. This is attempted in the respective constructions, but is not always possible
given the following premise for completely regular codes:
h = w * (c/r) where h = height, w = width, c = column weightage, r = row weightage

args: input to enable construction. input follows the following construction patern: h = n * (c / r) where c / r is not
explicitly simplified

construction specifies the method by which the matrix corresponding to args will be created
'''


class RegularLDPC(TannerGraph):

    # parameters:
    #   args: list of arguments needed for regular ldpc construction
    #   construction: the type of construction to be used
    # return:
    #   a fully defined Regular LDPC code
    def __init__(self, args, construction, verbose=False):
        TannerGraph.__init__(self, args, construction=construction)

        self.width = int(self.args[0])

        #
        # args provided [width (n_bits), height (n_checks), 1s per col]
        #
        # Because r is dependent on width, height, and c (assuming regularity), defining c results
        # in limiting the constructor to one possible r value.
        # The resulting n, c, r values are passed to the constructor.
        #
        if len(self.args) == 3:
            self.height = int(self.args[1])
            self.n = int(self.args[0])
            self.c = int(self.args[2])
            self.r = int((self.width / self.height) * self.c)
            if verbose:
                print("INFO: Regular code: inferred average ones per row as", self.r)
                if self.height*self.r!= self.width*self.c:
                    print("WARNING: Code parameters don't allow a perfectly regular code. " + \
                    "The row or column weights will be variable depending on the construction method.")
        else:
            raise RuntimeError("invalid input provided")

        self.tanner_graph = \
            RegularLDPC.get_parity_check_graph(self.n, self.height, self.r, self.c, self.construction)

    # parameters:
    #   n: int, the width of the LDPC code, the codeword length
    #   height: int, the height of the LDPC code, the number of check nodes
    #   r: int, the weight of each row of the LDPC code
    #   c: int, the weight of each column of the code
    #   method: String, the construction to be employed
    @staticmethod
    def get_parity_check_graph(n, m, r, c, method):

        if method == "peg":
            # use PEG (progressive edge growth) algorithm
            # we will use the peg/ library for this purpose

            # first step is to create a degree distribution file
            # which is trivial in our case since we have regular codes
            with tempfile.NamedTemporaryFile(mode='w', delete=False, dir=os.getcwd()) as f:
                degFileName = f.name
                f.write('1\n')  # number of degrees
                f.write(str(c) + '\n')  # degree of variable node
                f.write('1.0\n')  # probability of the degree occurring

            peg_library_path = os.path.join(os.path.dirname(__file__),
                                            os.path.join(os.path.pardir, os.path.pardir), 'peg')
            peg_exec_path = os.path.join(peg_library_path, 'MainPEG')

            # now create temporary file name to be used for output of peg
            with tempfile.NamedTemporaryFile(mode='w', delete=False, dir=os.getcwd()) as f:
                outFileName = f.name

            # run PEG
            # create seed first
            peg_seed = random.randrange(10000000)
            subprocess.run(peg_exec_path + ' -numM ' + str(m) + ' -numN ' + str(n) +
                           ' -codeName ' + outFileName + ' -degFileName ' + degFileName +
                           ' -q -seed ' + str(peg_seed), shell=True)

            os.remove(degFileName)
            # create the initial empty graph
            tanner_graph = {}
            for i in range(m):
                tanner_graph[i] = []

            # now read the graph generated by PEG
            with open(outFileName) as f:
                # verify first two lines are n and m respectively
                assert n == int(f.readline().rstrip('\n'))
                assert m == int(f.readline().rstrip('\n'))
                _ = f.readline()
                # ignore third line which contains number of columns for remaining lines
                check_num = 0
                for line in f:
                    vals = [int(val) for val in line.rstrip('\n').rstrip(' ').split(' ')]
                    for val in vals:
                        if val != 0:  # 0 is used to denote absence of variable node
                            tanner_graph.get(check_num).append(val - 1)
                    check_num += 1
                assert check_num == m
            os.remove(outFileName)
            return tanner_graph

        # Gallager's construction of random LDPC matrices
        # although this construction yields perfectly regular codes, it is not a reliable construction:
        #   it is impossible to enforce regularity while strictly maintaining a provided height and width
        elif method == "gallager":

            if n % r != 0:
                raise RuntimeError("Gallager construction: " +
                                   "cannot generate perfectly regular matrix for the given arguments")

            # keeps track of all created submatrices
            submatrices = []
            for i in range(c):
                # creates random submatrix, appends it to list
                submatrices.append(SubGraph(n, r))

            # merges all matrices in submatrices for final ldpc matrix
            return RegularLDPC.merge(submatrices, n, r)

        # ------------------------------------------
        # Duplicate code included for easier reading
        # ------------------------------------------

        # enforces constant row weight
        elif method == "populate-rows":

            # constructs initial empty parity check matrix
            tanner_graph = {}
            for i in range(m):
                tanner_graph[i] = []

            width = n
            height = m

            # all possible 1s locations (index in column)
            available_indices = []

            k = n * c
            for i in range(k - 1, -1, -1):
                # fills available indices with column indices
                available_indices.append(i % width)

            placed_entries = 0
            for i in range(height):
                for j in range(r):

                    # loops through all index positions in available indices, stops when the row does not contain a 1 at
                    # a specified index
                    l = 0
                    while l < len(available_indices) and tanner_graph.get(i).count(available_indices[l]) == 1:
                        l += 1

                    # if all entries have been placed
                    if l + placed_entries == k:

                        # choose a random column index and populate the matrix at that location
                        random_index = random.choice(range(width))
                        while tanner_graph.get(i).count(random_index) == 1:
                            random_index = random.choice(range(width))

                        tanner_graph.get(i).append(random_index)

                    # if not all entries have been placed
                    else:

                        # choose a random column index
                        random_index = random.choice(range(len(available_indices)))
                        while tanner_graph.get(i).count(available_indices[random_index]) != 0 and len(
                                available_indices) > 1:
                            random_index = random.choice(range(len(available_indices)))

                        # populate the matrix at specified location
                        tanner_graph.get(i).append(available_indices.pop(random_index))
                        placed_entries += 1

            return tanner_graph

        # enforces constant column weight
        elif method == "populate-columns":

            # create the initial empty graph
            tanner_graph = {}
            for i in range(n):
                tanner_graph[i] = []

            width = n
            height = m

            # contains all the possible indices for population
            available_indices = []

            k = n * c
            for i in range(k - 1, -1, -1):
                # fills available indices with row indices
                available_indices.append(i % height)

            placed_entries = 0
            for i in range(width):
                for j in range(c):

                    # loops through available entries to find an index that is not already populated
                    l = 0
                    while l < len(available_indices) and tanner_graph.get(i).count(available_indices[l]) == 1:
                        l += 1

                    # if all entries have been placed
                    if placed_entries + l == k:

                        # choose a random row index, not restrained by available indices
                        random_index = random.choice(range(height))
                        while tanner_graph.get(i).count(random_index) == 1:
                            random_index = random.choice(range(height))

                        # populate matrix at that location
                        tanner_graph.get(i).append(random_index)

                    # if not all 1s have been placed
                    else:

                        # choose a random available index
                        random_index = random.choice(range(len(available_indices)))
                        while tanner_graph.get(i).count(available_indices[random_index]) != 0 and len(
                                available_indices) > 1:
                            random_index = random.choice(range(len(available_indices)))

                        # populate matrix at that location
                        tanner_graph.get(i).append(available_indices.pop(random_index))
                        placed_entries += 1

            return transpose(tanner_graph, height)
        else:
            raise RuntimeError('Invalid construction method')

    '''
    as part of the Gallager construction, this function stacks all the generated submatrices vertically
    (in this case sub graphs). Because of the nature of LDPC codes, the order of the stacking is irrelevant,
    and subsequently random
    '''

    # parameters:
    #   submatrices: list of TannerGraph.tanner_graph: dictionary tanner_graphs to be stacked
    #   n: int, the width of each codeword
    #   r: int, the weight of each row of each submatrix in submatrices
    # return:
    #   a TannerGraph.tanner_graph dictionary containing the entire code constructed from individual submatrices
    @staticmethod
    def merge(submatrices, n, r):
        merged = {}
        for i in range(len(submatrices)):
            for j in range(int(n / r)):
                merged[int(i * n / r + j)] = submatrices[i].map[j]
        return merged


# the equivalent of the submatrix in Gallager's construction, used only for Gallager's construction
class SubGraph:

    # parameters:
    #   n: int, the width of the cumulative code
    #   r: int, the weight of each row in the cumulative code
    def __init__(self, n, r):

        # creates graph with appropriate no. check nodes
        self.map = {}
        for i in range(int(n / r)):
            self.map[i] = []

        # defines all possible indices, randomizes for sparse parity-codeword mapping
        codeword_indices = list(range(0, n))
        random.shuffle(codeword_indices)

        # assigns codeword bits to parity check equations
        for i in range(int(n / r)):
            for j in range(int(r)):
                self.map[i].append(codeword_indices[i * r + j])

    def __repr__(self):
        return str(self.map)
