import sys
sys.path.append('./GraphEngine')

import pygame

import ggraph
import delaunaytriangulation as dt
import parameters as params


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

	def draw_roads(self, surface, road_color, dirt_road_color):
		if "roads" in self.info:
			for r in self.info["roads"].keys():
				p = self.info["roads"][r]
				try:
					pos_only = [params.map_coord_to_screen_coord_centered((t.x, t.y)) for t in p]
					if len(pos_only) >= 2:
						pygame.draw.lines(surface, road_color, False, pos_only, width=4)
				except KeyError:
					pass

	def draw_dirt_roads(self, surface, road_color, dirt_road_color):
		if "dirt_roads" in self.info:
			for r in self.info["dirt_roads"].keys():
				p = self.info["dirt_roads"][r]
				try:
					pos_only = [params.map_coord_to_screen_coord_centered((t.x, t.y)) for t in p[:-1]]
					if len(pos_only) >= 2:
						pygame.draw.lines(surface, dirt_road_color, False, pos_only, width=1)
				except KeyError:
					pass

	def drawNode(self, surface, color, outline_color=(255, 255, 255), outline_width=2):
		super(CityNode, self).drawNode(surface, color, outline_color=outline_color, outline_width=outline_width)

class CityGraph(ggraph.gGraph):

	def __init__(self):
		super(CityGraph, self).__init__(node_type=CityNode, oriented=False)

		self._draw_delaunay = False
		self._draw_nodes = True
		self._draw_edges = True
		self._draw_roads = True

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

	def draw(self, surface):
		if self._draw_roads:
			for n in self.nodes:
				n.draw_roads(surface, params.UserInterfaceParams.TILE_TYPE_COLORS[params.TileParams.ROAD], params.UserInterfaceParams.TILE_TYPE_COLORS[params.TileParams.DIRT_ROAD])
				n.draw_dirt_roads(surface, params.UserInterfaceParams.TILE_TYPE_COLORS[params.TileParams.ROAD], params.UserInterfaceParams.TILE_TYPE_COLORS[params.TileParams.DIRT_ROAD])
		
		if self._draw_edges:
			for n in self.nodes:
				color = (204, 204, 204)
				n.drawEdges(surface, color, width=4)

		if self._draw_nodes:
			for n in self.nodes:
				try:
					color = n.info["color"]
				except KeyError:
					color = (255, 255, 255)
				try:
					out_color = n.info["outline_color"]
					n.drawNode(surface, color, outline_color=out_color, outline_width=2)
				except KeyError:
					n.drawNode(surface, color, outline_width=2)


		if self._draw_delaunay:
			self.drawDelaunay(surface, (0, 0, 255))