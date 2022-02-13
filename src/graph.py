import sys

sys.path.append('./GraphEngine')

import math
import pygame

import ggraph
import delaunaytriangulation as dt
import parameters as params
import utils


class CityNode(ggraph.gNode):
    HUMAN_CITY_FILE = "../data/fx/human_city.png"
    HUMAN_CITY_IMAGE = pygame.image.load(HUMAN_CITY_FILE)
    HUMAN_CITY_CONTOUR_FILE = "../data/fx/human_city_contour.png"
    HUMAN_CITY_CONTOUR_IMAGE = pygame.image.load(HUMAN_CITY_CONTOUR_FILE)

    ELF_CITY_FILE = "../data/fx/elven_city.png"
    ELF_CITY_IMAGE = pygame.image.load(ELF_CITY_FILE)
    ELF_CITY_CONTOUR_FILE = "../data/fx/elven_city_contour.png"
    ELF_CITY_CONTOUR_IMAGE = pygame.image.load(ELF_CITY_CONTOUR_FILE)

    DWARF_CITY_FILE = "../data/fx/dwarven_city.png"
    DWARF_CITY_IMAGE = pygame.image.load(DWARF_CITY_FILE)
    DWARF_CITY_CONTOUR_FILE = "../data/fx/dwarven_city_contour.png"
    DWARF_CITY_CONTOUR_IMAGE = pygame.image.load(DWARF_CITY_CONTOUR_FILE)

    HALFLING_CITY_FILE = "../data/fx/halflings_city.png"
    HALFLING_CITY_IMAGE = pygame.image.load(HALFLING_CITY_FILE)
    HALFLING_CITY_CONTOUR_FILE = "../data/fx/halflings_city_contour.png"
    HALFLING_CITY_CONTOUR_IMAGE = pygame.image.load(HALFLING_CITY_CONTOUR_FILE)

    CARAVAN_ICON_FILE = "../data/fx/caravan_icon.png"
    CARAVAN_ICON_IMAGE = pygame.image.load(CARAVAN_ICON_FILE)

    def __init__(self, _id):
        if isinstance(_id, int):
            _id = str(_id)
        super(CityNode, self).__init__(_id)

        self.info["pos"] = (0, 0)
        self.info["radius"] = 15
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

    def drawEdges_relations(self, surface, width=1):
        try:
            self.info["pos"]
        except KeyError:
            warnings.warn("{} does not possess a position information (info[\"pos\"])".format(self.id), stacklevel=2)
            return

        try:
            radius = self.info["radius"]
        except KeyError:
            radius = 8

        color = (0, 0, 0)

        for e in self.edges:
            if e.end == self:
                pygame.draw.circle(surface, color, (self.info["pos"][0], self.info["pos"][1] - radius), radius * 1.2,
                                   width=width)
            else:
                try:
                    rel_value = sum(
                        list(self.info["community"].kingdom.relations[e.end.info["community"].kingdom].values()))

                    rel_color_index = math.floor(utils.normalise(rel_value, mini=-100, maxi=100) * len(
                        params.UserInterfaceParams.RELATION_DISPLAY_GRADIENT))
                    color = params.UserInterfaceParams.RELATION_DISPLAY_GRADIENT[rel_color_index]

                    if self.parent.oriented:
                        v = (e.end.info["pos"][0] - self.info["pos"][0], e.end.info["pos"][1] - self.info["pos"][1])
                        mag_v = np.linalg.norm(np.array(v))
                        u = (v[0] / mag_v, v[1] / mag_v)
                        ep = (e.end.info["pos"][0] - radius * 1.5 * u[0], e.end.info["pos"][1] - radius * 1.5 * u[1])
                        drawer.arrow(surface, color, self.info["pos"], ep)
                    else:
                        pygame.draw.line(surface, color, self.info["pos"], e.end.info["pos"], width=width)
                except KeyError:
                    warnings.warn("{} does not possess a position information (info[\"pos\"])".format(e.end.id),
                                  stacklevel=2)

    def drawNode_image(self, surface, color, outline_color=(255, 255, 255)):

        if self.info["community"] == None:
            self.drawNode(surface, color, outline_color=outline_color, outline_width=3)
            return

        if self.info["community"].kingdom.main_race == params.RaceParams.HUMAN:
            _used_image = CityNode.HUMAN_CITY_IMAGE
            _contour_image = CityNode.HUMAN_CITY_CONTOUR_IMAGE
        elif self.info["community"].kingdom.main_race == params.RaceParams.ELF:
            _used_image = CityNode.ELF_CITY_IMAGE
            _contour_image = CityNode.ELF_CITY_CONTOUR_IMAGE
        elif self.info["community"].kingdom.main_race == params.RaceParams.DWARF:
            _used_image = CityNode.DWARF_CITY_IMAGE
            _contour_image = CityNode.DWARF_CITY_CONTOUR_IMAGE
        elif self.info["community"].kingdom.main_race == params.RaceParams.HALFING:
            _used_image = CityNode.HALFLING_CITY_IMAGE
            _contour_image = CityNode.HALFLING_CITY_CONTOUR_IMAGE
        else:
            _used_image = CityNode.HUMAN_CITY_IMAGE
            _contour_image = CityNode.HUMAN_CITY_CONTOUR_IMAGE

        _used_rect = _used_image.get_rect()
        _contour_rect = _contour_image.get_rect()

        _used_rect.center = params.map_coord_to_screen_coord_centered(self.info["location"].map_position)
        _contour_rect.center = params.map_coord_to_screen_coord_centered(self.info["location"].map_position)
        surface.blit(utils.colorize(_used_image, color), _used_rect)
        surface.blit(utils.colorize(_contour_image, outline_color, toone=True), _contour_rect)

        if self.info["community"].caravan_arrived_countdown > 0:
            _rect = CityNode.CARAVAN_ICON_IMAGE.get_rect()
            _rect.center = params.map_coord_to_screen_coord_centered(self.info["location"].map_position)
            _rect.center = (_rect.center[0], _rect.center[1] + self.info["community"].caravan_arrived_countdown)
            surface.blit(utils.colorize(CityNode.CARAVAN_ICON_IMAGE, (255, 255, 255), toone=True), _rect)


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
                n.draw_roads(surface, params.UserInterfaceParams.TILE_TYPE_COLORS[params.TileParams.ROAD],
                             params.UserInterfaceParams.TILE_TYPE_COLORS[params.TileParams.DIRT_ROAD])
                n.draw_dirt_roads(surface, params.UserInterfaceParams.TILE_TYPE_COLORS[params.TileParams.ROAD],
                                  params.UserInterfaceParams.TILE_TYPE_COLORS[params.TileParams.DIRT_ROAD])

        if self._draw_edges:
            for n in self.nodes:
                color = (204, 204, 204)
                # n.drawEdges(surface, color, width=4)
                n.drawEdges_relations(surface, width=4)

        if self._draw_nodes:
            for n in self.nodes:
                try:
                    color = n.info["color"]
                except KeyError:
                    color = (255, 255, 255)

                try:
                    out_color = n.info["outline_color"]
                    # n.drawNode(surface, color, outline_color=out_color, outline_width=2)
                    n.drawNode_image(surface, color, outline_color=out_color)
                except KeyError:
                    # n.drawNode(surface, color, outline_width=2)
                    n.drawNode_image(surface, color, outline_width=2)

        if self._draw_delaunay:
            self.drawDelaunay(surface, (0, 0, 255))
