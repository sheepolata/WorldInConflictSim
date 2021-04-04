# import the pygame module, so you can use it
import pygame
from pygame.locals import *
import warnings
import random
import numpy as np
import math
from scipy.spatial import Delaunay

import delaunaytriangulation as dt
import graphmodel as gm
import drawer
import utils

class gNode(gm.Node):

    def draw(self, surface, color):
        self.drawNode(surface, color)
        self.drawEdges(surface, color)

    def drawNode(self, surface, color, outline_color=(255, 255, 255)):
        try:
            self.info["pos"]
        except KeyError:
            warnings.warn("{} does not possess a position information (info[\"pos\"])".format(self.id))
            return

        try:
            radius = self.info["radius"]
        except KeyError:
            radius = 8

        pygame.draw.circle(surface, color, self.info["pos"], radius)
        pygame.draw.circle(surface, outline_color, self.info["pos"], radius, width=2)

    def drawEdges(self, surface, color):
        try:
            self.info["pos"]
        except KeyError:
            warnings.warn("{} does not possess a position information (info[\"pos\"])".format(self.id), stacklevel=2)
            return

        try:
            radius = self.info["radius"]
        except KeyError:
            radius = 8

        for e in self.edges:
            if e.end == self:
                pygame.draw.circle(surface, (255, 255, 255), (self.info["pos"][0], self.info["pos"][1]-radius), radius*1.2, width=1)
            else:
                try:
                    if self.parent.oriented:
                        v = (e.end.info["pos"][0] - self.info["pos"][0], e.end.info["pos"][1] - self.info["pos"][1])
                        mag_v = np.linalg.norm(np.array(v))
                        u = (v[0] / mag_v, v[1] / mag_v)
                        ep = (e.end.info["pos"][0] - radius*1.5*u[0], e.end.info["pos"][1]- radius*1.5*u[1])
                        drawer.arrow(surface, (255, 255, 255), self.info["pos"], ep)
                    else:
                        pygame.draw.line(surface, (255, 255, 255), self.info["pos"], e.end.info["pos"])
                except KeyError:
                    warnings.warn("{} does not possess a position information (info[\"pos\"])".format(e.end.id), stacklevel=2)

    def move(self, direction, speed, limits=(1280, 720), collision=True):
        try:
            self.info["pos"]
        except KeyError:
            self.info["pos"] = [0, 0]

        new_pos = [0, 0]
        new_pos[0] = (self.info["pos"][0] + math.cos(direction) * speed) % limits[0]
        new_pos[1] = (self.info["pos"][1] + math.sin(direction) * speed) % limits[1]

        if collision:
            for other in self.parent.nodes:
                if not self.equal(other):
                    _count = 0
                    while self.collide(other):
                        new_pos[0] = (self.info["pos"][0] + math.cos(utils.angle_from_points(self.info["pos"], other.info["pos"])) * 1) % limits[0]
                        new_pos[1] = (self.info["pos"][1] + math.sin(utils.angle_from_points(self.info["pos"], other.info["pos"])) * 1) % limits[1]
                        _count += 1
                        if _count > 50:
                            break

        self.info["pos"][0] = new_pos[0]
        self.info["pos"][1] = new_pos[1]



    def collide(self, other):
        # print("{} <= {}".format(utils.distance2p(self.info["pos"], other.info["pos"]), max(self.info["radius"], other.info["radius"])))
        return utils.distance2p(self.info["pos"], other.info["pos"]) <= max(self.info["radius"], other.info["radius"])*2

    def collide_point(self, point):
        return utils.distance2p(self.info["pos"], point) <= self.info["radius"]

    def applyForces(self, speed=1, spring_rest_distance=75, collision=True):
        edges_force_vectors = []
        del_force_vectors = []

        attraction_factor = 0.8
        repulsion_factor = 1.4

        _t = 0.1
        t_up = 1.00 + _t
        t_down = 1.00 - _t

        for e in self.edges:
            if self.equal(e.end):
                continue
            try:
                dist = utils.distance2p(e.end.info["pos"], self.info["pos"])
                if dist >= spring_rest_distance*t_up:
                    f = {"force":[e.end.info["pos"][0] - self.info["pos"][0], e.end.info["pos"][1] - self.info["pos"][1]]}
                    f["f_dist"] = utils.normalise(dist, mini=spring_rest_distance, maxi=spring_rest_distance*3) * attraction_factor
                    edges_force_vectors.append(f)
                elif dist <= spring_rest_distance*t_down:
                    # f = {"force":[self.info["pos"][0] - e.end.info["pos"][0], self.info["pos"][1] - e.end.info["pos"][1]]} # OLD WAY
                    opposite_angle = (utils.angle_from_points(self.info["pos"], e.end.info["pos"]) + math.pi) % (2*math.pi)
                    op_e = [self.info["pos"][0] + dist*math.cos(opposite_angle), self.info["pos"][1] + dist*math.sin(opposite_angle)]
                    f = {"force":[self.info["pos"][0] - op_e[0], self.info["pos"][1] - op_e[1]]}
                    f["f_dist"] = utils.normalise(dist, mini=0, maxi=spring_rest_distance) * repulsion_factor
                    edges_force_vectors.append(f)
            except KeyError:
                warnings.warn("{} or {} does not possess a position information (info[\"pos\"])".format(self.id, e.end.id), stacklevel=2)

        # for other in self.parent.nodes:
        #     if self.equal(other):
        #         continue
        #     if gm.Edge(self, other) in self.edges:
        #         continue
        #     try:
        #         dist = utils.distance2p(other.info["pos"], self.info["pos"])
        #         # if dist >= spring_rest_distance*t_up and dist <= spring_rest_distance*3:
        #         #     f = {"force":[other.info["pos"][0] - self.info["pos"][0], other.info["pos"][1] - self.info["pos"][1]]}
        #         #     f["f_dist"] = utils.normalise(dist, mini=spring_rest_distance*1.5, maxi=spring_rest_distance*3) * attraction_factor 
        #         #     edges_force_vectors.append(f)
        #         if dist < spring_rest_distance*t_down:
        #             opposite_angle = (utils.angle_from_points(self.info["pos"], other.info["pos"]) + math.pi) % (2*math.pi)
        #             op_e = [self.info["pos"][0] + dist*math.cos(opposite_angle), self.info["pos"][1] + dist*math.sin(opposite_angle)]
        #             f = {"force":[self.info["pos"][0] - op_e[0], self.info["pos"][1] - op_e[1]]}
        #             f["f_dist"] = utils.normalise(dist, mini=0, maxi=spring_rest_distance) * repulsion_factor * 1.2
        #             edges_force_vectors.append(f)
        #     except KeyError:
        #         warnings.warn("{} or {} does not possess a position information (info[\"pos\"])".format(self.id, other.id), stacklevel=2)

        for n_id in self.parent.triangulation.get_neighbours_of(self.id):
            neigh = self.parent.getNodeByID(n_id)

            if self.equal(neigh):
                continue
            if gm.Edge(self, neigh) in self.edges:
                continue

            dist = utils.distance2p(neigh.info["pos"], self.info["pos"])

            if dist >= spring_rest_distance*t_up and dist <= spring_rest_distance*3:
                f = {"force":[neigh.info["pos"][0] - self.info["pos"][0], neigh.info["pos"][1] - self.info["pos"][1]]}
                f["f_dist"] = utils.normalise(dist, mini=spring_rest_distance*1.5, maxi=spring_rest_distance*3) * attraction_factor * 0.6
                del_force_vectors.append(f)
            if dist < spring_rest_distance*t_down:
                opposite_angle = (utils.angle_from_points(self.info["pos"], neigh.info["pos"]) + math.pi) % (2*math.pi)
                op_e = [self.info["pos"][0] + dist*math.cos(opposite_angle), self.info["pos"][1] + dist*math.sin(opposite_angle)]
                f = {"force":[self.info["pos"][0] - op_e[0], self.info["pos"][1] - op_e[1]]}
                f["f_dist"] = utils.normalise(dist, mini=0, maxi=spring_rest_distance) * repulsion_factor * 1.4
                del_force_vectors.append(f)


        final_force = [0, 0]

        if edges_force_vectors != []:
            for f in edges_force_vectors:
                final_force[0] += f["force"][0] * f["f_dist"]
                final_force[1] += f["force"][1] * f["f_dist"]

            final_force[0] /= len(edges_force_vectors)
            final_force[1] /= len(edges_force_vectors)
        elif del_force_vectors != []:
            for f in del_force_vectors:
                final_force[0] += f["force"][0] * f["f_dist"]
                final_force[1] += f["force"][1] * f["f_dist"]

            final_force[0] /= len(del_force_vectors)
            final_force[1] /= len(del_force_vectors)

        final_force_mag = np.linalg.norm(np.array(final_force))

        spd_factor = 1
        if final_force_mag > spring_rest_distance:
            spd_factor = utils.normalise(final_force_mag, mini=spring_rest_distance*t_up, maxi=spring_rest_distance*3)
        else:
            spd_factor = 1 - utils.normalise(final_force_mag, mini=0, maxi=spring_rest_distance*t_down)

        if spd_factor > -0.005 and spd_factor < 0.005:
            spd_factor = 0
        # else:
        #     utils.clamp(spd_factor, -1, 1)

        # if final_force_mag < 0.5:
        #     spd_factor = 0

        self.move(math.atan2(final_force[1], final_force[0]), speed*spd_factor, collision=collision)

class gGraph(gm.Graph):

    def __init__(self, node_type=None, oriented=True):
        super().__init__(node_type=node_type, oriented=oriented)
        self.delaunay_points = None
        self.delaunay = None
        self._draw_delaunay = True

    def setDelaunay(self):
        dict_pos = {}
        for n in self.nodes:
            dict_pos[n.id] = n.info["pos"]

        self.triangulation = dt.Delaunay_Triangulation(dict_pos)
        self.triangulation.delaunay_cut_links = 150
        self.triangulation.update()

    def computeDelaunay(self):
        # self.delaunay_points = np.array([p.info["pos"] for p in self.nodes])
        # self.delaunay = Delaunay(self.delaunay_points)
        dict_pos = {}
        for n in self.nodes:
            dict_pos[n.id] = n.info["pos"]

        self.triangulation.update(new_positions=dict_pos)

    def drawDelaunay(self, surface, color):
        for n in self.nodes:
            dneigh = self.triangulation.get_neighbours_of(n.id)
            for dn in dneigh:
                pygame.draw.line(surface, color, n.info["pos"], self.getNodeByID(dn).info["pos"])

    def draw(self, surface):
        for n in self.nodes:
            try:
                color = n.info["color"]
            except KeyError:
                color = (255, 255, 255)
            n.drawEdges(surface, color)
        for n in self.nodes:
            try:
                color = n.info["color"]
            except KeyError:
                color = (255, 255, 255)
            n.drawNode(surface, color)
        
        if self._draw_delaunay:
            self.drawDelaunay(surface, (0, 0, 255))