import sys
sys.path.append('./GraphEngine')


import ggraph
import delaunaytriangulation as dt


class CityNode(ggraph.gNode):

	def __init__(self, _id):
		if isinstance(_id, int):
			_id = str(_id)
		super(CityNode, self).__init__(_id)

		self.info["pos"]    = (0, 0)
		self.info["radius"] = 8
		self.info["color"] = (255, 255, 255)

		self.info["location"] = None
		self.info["community"] = None

		self.info["rect"] = None

class CityGraph(ggraph.gGraph):

	def __init__(self):
		super(CityGraph, self).__init__(node_type=CityNode, oriented=False)

		self._draw_delaunay = False

	def get_node_by_location(self, loc):
		for n in self.nodes:
			if n.info["location"] == loc:
				return n
		return None

	def setDelaunay(self, dcl=-1):
		dict_pos = {}
		for n in self.nodes:
			dict_pos[n.id] = n.info["location"].map_position

		self.triangulation = dt.Delaunay_Triangulation(dict_pos)
		self.triangulation.delaunay_cut_links = dcl
		self.triangulation.update()

	def computeDelaunay(self):
		# self.delaunay_points = np.array([p.info["pos"] for p in self.nodes])
		# self.delaunay = Delaunay(self.delaunay_points)
		dict_pos = {}
		for n in self.nodes:
			dict_pos[n.id] = n.info["location"].map_position

		self.triangulation.update(new_positions=dict_pos)