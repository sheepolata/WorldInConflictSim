
import warnings
import traceback
import numpy as np
import random

import utils

class Graph(object):
    def __init__(self, node_type=None, oriented=True):
        if node_type == None:
            self.node_type = Node
        else:
            self.node_type = node_type
        self.nodes = []
        self.edges = []

        self.triangulation = None

    def addNode(self, n):
        if not n in self.nodes:
            n.parent = self
            self.nodes.append(n)
        else:
            warnings.warn("{} already in nodes".format(n.id))

    def addEdge(self, n1, n2, bidirectionnal=None, add_missing_nodes=True):
        if bidirectionnal == None:
            bidirectionnal = not self.oriented
        if add_missing_nodes:
            if not n1 in self.nodes:
                self.addNode(n1)
            if not n2 in self.nodes:
                self.addNode(n2)

        if not [n1, n2] in self.edges:
            self.edges.append([n1, n2])
        if bidirectionnal:
            if not [n2, n1] in self.edges:
                self.edges.append([n2, n1])

        n1.addEdge(n2, bidirectionnal=bidirectionnal)

    def getNodeByID(self, _id):
        for n in self.nodes:
            if n.id == _id:
                return n
        return None

    def hasEdgeBetween(self, n1, n2):
        if self.oriented:
            return [n1, n2] in self.edges
        else:
            return [n1, n2] in self.edges or [n2, n1] in self.edges

    def getEdgeNumber(self):
        if self.oriented:
            return len(self.edges)
        else:
            edge_set = []
            for e in self.edges:
                if not e in edge_set and not [e[1], e[0]] in edge_set:
                    edge_set.append(e)
            return len(edge_set)

    def random_tree_graph(self, nb_node, max_children=4):
        self.reset()
        self.oriented = False

        _id = 0
        n = self.node_type(str(_id))
        E = [n]
        _id += 1

        while E != []:
            current = E[0]
            E = E[1:]
            self.addNode(current)

            if len(self.nodes) < (nb_node-max_children):
                new_nb = random.randint(1, max_children)
            else:
                new_nb = len(self.nodes) - (nb_node-max_children)
            # new = []
            for i in range(new_nb):
                # new.append(self.node_type(str(_id)))
                tmp = self.node_type(str(_id))
                _id += 1

                E.append(tmp)
                self.addNode(tmp)
                self.addEdge(current, tmp)


    def random_connected_graph(self, nb_node, sparseness, oriented):
        self.reset()
        self.oriented = oriented

        if sparseness < (nb_node-1):
            sparseness = nb_node-1
        if sparseness > nb_node*(nb_node-1)/2.0:
            sparseness = nb_node*(nb_node-1)/2.0

        print("Generating unoriented graph (N={}, S={})".format(nb_node, sparseness))

        for i in range(nb_node):
            _node = self.node_type(str(i))
            if self.nodes != []:
                self.addEdge(_node, np.random.choice(self.nodes), add_missing_nodes=False)
            self.addNode(_node)

        while self.getEdgeNumber() < sparseness:
            # print("here")
            self.addEdge(np.random.choice(self.nodes), np.random.choice(self.nodes), add_missing_nodes=False)

    def complete_graph(self, nb_node):
        self.reset()
        self.oriented = False

        for i in range(nb_node):
            self.addNode(self.node_type(str(i)))

        for n in self.nodes:
            for o in self.nodes:
                if n != o:
                    self.addEdge(n, o)


    def serialise(self):
        s = ""
        for n in self.nodes:
            s += n.serialise() + "\n"
        return s[:-1]

    def reset(self):
        del self.nodes[:]
        del self.edges[:]
        self.oriented = True

class Node(object):
    def __init__(self, _id):
        self.id = _id

        self.parent = None
        self.edges = []

        self.info = {}

    def addEdge(self, other, bidirectionnal=False):
        _e = Edge(self, other)
        if not self.hasEdge(_e):
            self.edges.append(_e)
        else:
            warnings.warn("{} is already in {}'s edges".format(other.id, self.id), stacklevel=2)

        if bidirectionnal:
            other.addEdge(self)

    def hasEdge(self, edge):
        for e in self.edges:
            if e.equal(edge):
                return True
        return False

    def equal(self, other):
        if self.id == other.id:
            return True
        return False

    def serialise(self):
        s = "{} ---->".format(self.id)
        if self.edges == []:
            s += " NONE"
        else:
            for i, e in enumerate(self.edges):
                if i == 0:
                    s += " {}".format(e.end.id)
                else:
                    space = ""
                    for sp in range(len(self.id)):
                        space += " "
                    s += "\n{} |---> {}".format(space, e.end.id)
        return s


class Edge(object):
    def __init__(self, parent, n):
        self.parent = parent
        self.end = n

    def equal(self, other):
        if self.parent == other.parent and self.end == other.end:
            return True
        return False


def run_test():
    n1 = Node("1")
    n2 = Node("2")
    n3 = Node("3")

    n1.addEdge(n1)
    n1.addEdge(n3)
    n2.addEdge(n3, bidirectionnal=True)
    n1.addEdge(n3, bidirectionnal=True)

    graph = Graph()
    graph.add_node(n1)
    graph.add_node(n2)
    graph.add_node(n3)

    print(graph.serialise())


if __name__ == '__main__':
    run_test()