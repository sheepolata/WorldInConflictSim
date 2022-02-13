# import the pygame module, so you can use it
import pygame
from pygame.locals import *
import numpy as np
import pprint

import sys

sys.path.append('./GraphEngine')

import graphdisplay as gd
import view
import myglobals
import model
import parameters as params


# define a main function
def main():
    print("START INIT")
    # define a variable to control the main loop
    running = True

    mp = params.ModelParams.MAP_SIZE
    gen_roads = mp <= params.ModelParams.GEN_ROADS_LIMIT

    params.RaceParams.randomiseArchetypePreference()

    mymodel = model.Model(map_size=mp)
    mymodel.random_model_map_basic(mp)
    thread = model.SimThread(mymodel)

    graph = mymodel.generate_graph_delaunay_basic(gen_roads)
    graph._draw_edges = not gen_roads
    graph._draw_roads = gen_roads

    display = view.UserInterface(mymodel, graph)

    # graph.setDelaunay()
    # graph._draw_delaunay = True
    # graph.computeDelaunay()

    display.set_log(myglobals.LogConsoleInst)
    display.set_info(myglobals.InfoConsole, force_max=True)

    _p = thread.pause()
    display._display_pause = _p

    thread.start()

    print("START SIM")

    # main loop
    while running:

        display.clear_info_console()

        # event handling, gets all event from the event queue
        for event in pygame.event.get():
            # only do something if the event is of type QUIT
            if event.type == pygame.QUIT:
                # change the value to False, to exit the main loop
                thread.stop()
                running = False
            elif event.type == pygame.MOUSEBUTTONUP:
                # LMB
                if event.button == 1 and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    pass
                elif event.button == 1:
                    mpos = pygame.mouse.get_pos()

                    # Check if collide with city node
                    if display.collide_graph_surface(mpos):
                        smth = False
                        for city_node in display.graph.nodes:
                            if city_node.collide_point(mpos):
                                display.selected = city_node
                                smth = True
                                break
                        if not smth:
                            if display.selected != None:
                                if display.selected.info["community"] != None:
                                    display.selected.info["community"].reset_show_booleans()
                                display.selected = None

                # print(mpos)

                # MMB
                if event.button == 2:
                    pass
                # RMB
                if event.button == 3 and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    pass
                if event.button == 3:
                    pass
            elif event.type == pygame.MOUSEMOTION:
                mpos = pygame.mouse.get_pos()

                smth = False
                if display.collide_graph_surface(mpos):
                    mcoord = params.screen_coord_to_map_coord(mpos)

                    for city_node in display.graph.nodes:
                        if city_node.info["location"].in_area_of_influence(mcoord):
                            display.hovered = city_node
                            smth = True
                            break
                if not smth:
                    display.hovered = None

            elif event.type == pygame.KEYDOWN:
                if event.key == K_F2 and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    display._display_pause = True
                    thread.pause(forced=True)

                    mymodel.reset()
                    mymodel.set_map()
                    mymodel.random_model_map_basic(mp)
                    graph = mymodel.generate_graph_delaunay_basic(gen_roads)
                    graph._draw_edges = not gen_roads
                    graph._draw_roads = gen_roads
                    display.graph = graph
                    display.reset()

                # thread.pause(forced=False)
                elif event.key == K_F2:
                    display._display_pause = True
                    thread.pause(forced=True)

                    mymodel.reset()
                    mymodel.random_model_map_basic(mp)
                    graph = mymodel.generate_graph_delaunay_basic(gen_roads)
                    graph._draw_edges = not gen_roads
                    graph._draw_roads = gen_roads
                    display.graph = graph
                    # display.reset_nodes_only()
                    display.reset()

                # thread.pause(forced=False)
                if event.key == K_RIGHT:
                    thread.increase_speed()
                    if thread.is_fastest_speed():
                        display._draw_voronoi = False
                if event.key == K_LEFT:
                    if thread.is_fastest_speed():
                        display._draw_voronoi = True
                    thread.decrease_speed()
                if event.key == K_SPACE:
                    _p = thread.pause()
                    display._display_pause = _p
                if event.key == K_F1:
                    graph._draw_edges = not graph._draw_edges
                if event.key == K_F3:
                    if thread.is_fastest_speed():
                        display._draw_voronoi = False
                    else:
                        display._draw_voronoi = not display._draw_voronoi
                if event.key == K_k:
                    if display.selected != None and display.selected.info["community"] != None:
                        display.selected.info["community"].show_kingdom = not display.selected.info[
                            "community"].show_kingdom
                    else:
                        pass
                if event.key == K_d:
                    if display.selected != None and display.selected.info["community"] != None:
                        if display.selected.info["community"].show_kingdom:
                            display.selected.info["community"].show_kingdom_details = not display.selected.info[
                                "community"].show_kingdom_details
                    else:
                        pass
                if event.key == K_r:
                    if display.selected != None and display.selected.info["community"] != None:
                        display.selected.info["community"].show_ressources = not display.selected.info[
                            "community"].show_ressources
                    else:
                        mymodel.show_race = not mymodel.show_race
                if event.key == K_l:
                    if display.selected != None and display.selected.info["community"] != None:
                        display.selected.info["community"].show_landmarks = not display.selected.info[
                            "community"].show_landmarks
                if event.key == K_p:
                    if display.selected != None and display.selected.info["community"] != None:
                        display.selected.info["community"].show_pop_details = not display.selected.info[
                            "community"].show_pop_details
                    else:
                        mymodel.show_population = not mymodel.show_population
                if event.key == K_h:
                    if display.selected != None and display.selected.info["community"] != None:
                        display.selected.info["community"].show_happiness_details = not display.selected.info[
                            "community"].show_happiness_details
                    else:
                        mymodel.show_happiness = not mymodel.show_happiness
                if event.key == K_o:
                    if display.selected != None and display.selected.info["community"] != None:
                        display.selected.info["community"].show_events = not display.selected.info[
                            "community"].show_events
                if event.key == K_b:
                    if display.selected != None and display.selected.info["community"] != None:
                        display.selected.info["community"].show_buildings = not display.selected.info[
                            "community"].show_buildings

        # if display.selected != None:
        # 	pp = pprint.PrettyPrinter(indent=4)
        # 	pp.pprint(display.selected.info["community"].hapiness_details)

        display.update_info_tab()
        display.insert_info_console(
            "inc./dec. with →/←; SPACE to pause; (Ctrl+)F2 to reset (all), F3 to display kingdoms", 1)
        display.insert_info_console(
            f"{'' if not thread._paused else 'PAUSED '}{thread.freq if thread.freq > 0 else 'Fastest'} days/second", 1)
        # display.insert_info_console("{}".format("Play" if not thread._paused else "Paused"), 1)

        display.main_loop_end()

    print("END SIM")


# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
if __name__ == "__main__":
    # call the main function
    main()
