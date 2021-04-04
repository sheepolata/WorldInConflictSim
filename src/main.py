# import the pygame module, so you can use it
import pygame
from pygame.locals import *
import random

import sys
sys.path.append("./graphics")
import ggraph

screensize = (1280, 720)

# define a main function
def main():
     
    # initialize the pygame module
    pygame.init()
    # load and set the logo
    # logo = pygame.image.load("logo32x32.jpg")
    # pygame.display.set_icon(logo)
    pygame.display.set_caption("World in Conflict Simulation")

    clock = pygame.time.Clock()
    getTicksLastFrame = 0

    # create screen surface on screen that has the size of 240 x 180
    screen = pygame.display.set_mode(screensize)
    main_surface = pygame.Surface(screensize)

    bg_color = (128, 128, 128)
    main_surface.fill(bg_color)
     
    # define a variable to control the main loop
    running = True

    graph = ggraph.gGraph(node_type=ggraph.gNode)

    nb_node = 30
    # sparseness = random.randint(nb_node-1, int(nb_node*(nb_node-1)/2.0))
    sparseness = nb_node-1

    collision_on = True

    apply_forces_on = True

    def generate():
        # graph.complete_graph(nb_node)
        # graph.random_connected_graph(nb_node, random.randint(nb_node-1, nb_node*(nb_node-1)/2.0), True)
        # graph.random_connected_graph(nb_node, sparseness, True)
        graph.random_connected_graph(nb_node, sparseness, False)
        # graph.random_tree_graph(nb_node)
        for n in graph.nodes:
            n.info["pos"] = [random.randint(0, screensize[0]), random.randint(0, screensize[1])]
            n.info["radius"] = 12
            # n.info["color"] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            n.info["color"] = (0, 0, 0)
        graph.setDelaunay()
        print(graph.serialise())
    generate()


    # print(graph.serialise())

    selected = None

    # main loop
    while running:

        t = pygame.time.get_ticks()
        # deltaTime in seconds.
        deltaTime = (t - getTicksLastFrame) / 1000.0

        # event handling, gets all event from the event queue
        for event in pygame.event.get():
            # only do something if the event is of type QUIT
            if event.type == pygame.QUIT:
                # change the value to False, to exit the main loop
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == K_r:
                    graph.reset()
                    generate()
                if event.key == K_c:
                    collision_on = not collision_on
                if event.key == K_SPACE:
                    apply_forces_on = not apply_forces_on
                if event.key == K_s:
                    for n in graph.nodes:
                        n.info["pos"] = [random.randint(0, screensize[0]), random.randint(0, screensize[1])]
                if event.key == K_p:
                    for n in graph.nodes:
                        n.info["pos"] = [screensize[0]/2, screensize[1]/2]
                if event.key == K_d:
                    graph._draw_delaunay = not graph._draw_delaunay


        graph.computeDelaunay()
        # print(graph.triangulation.triangulation)
        # print(graph.triangulation.get_neighbours_of("0"))

        if apply_forces_on:
            for n in graph.nodes:
                n.applyForces(collision=collision_on)

        main_surface.fill(bg_color)
        graph.draw(main_surface)


        screen.blit(main_surface, (0, 0))

        pygame.display.update()

        getTicksLastFrame = t

        clock.tick(60)

     
     
# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
if __name__=="__main__":
    # call the main function
    main()