import scipy.spatial as scispa
import numpy as np
import utils

def find_neighbors(pindex, triang):
    return triang.vertex_neighbor_vertices[1][triang.vertex_neighbor_vertices[0][pindex]:triang.vertex_neighbor_vertices[0][pindex+1]]

class Delaunay_Triangulation(object):
    """docstring for Delaunay_Triangulation"""
    def __init__(self, node_positions, dcl=-1):
        #keys:idNode value:(x, y)
        self.node_positions = node_positions
        #key:idNode value:[x, y]
        self.positions_only = {}
        #key:idNode value:its_neighbours_as_id_list
        self.neighbours = {}

        self.triangulation = None

        self.delaunay_cut_links = dcl

    def update(self, new_positions=None):
        if new_positions != None:
            self.node_positions = new_positions

        if not self.node_positions:
            return

        for idn in self.node_positions.keys():
            node_number = int(idn)
            self.positions_only[node_number] = [self.node_positions[idn][0], self.node_positions[idn][1]]

        self.triangulation = scispa.Delaunay([self.positions_only[k] for k in self.positions_only.keys()])

        self.compute_neighbours()

    def compute_neighbours(self):
        for nodenb in self.positions_only.keys():
            # print("nodenb", nodenb)
            neighbor_indices = find_neighbors(nodenb, self.triangulation)

            neighbours_names = []
            for nid in neighbor_indices:
                if self.delaunay_cut_links > 0:
                    dist = utils.distance2p(self.positions_only[nodenb], self.positions_only[nid])
                    if dist < self.delaunay_cut_links:
                        neighbours_names.append(str(nid))
                else:
                    neighbours_names.append(str(nid))

            self.neighbours[str(nodenb)] = neighbours_names

    def get_neighbours_of(self, idNode):
        return self.neighbours[idNode]
