# import the pygame module, so you can use it
import pygame
from pygame.locals import *
import random
import numpy as np

import sys
sys.path.append('./GraphEngine')

# import drawer
# import ggraph
# import console
import graphdisplay as gd
import view
import myglobals



# GlobalLog = console.Console()
# InfoConsole = console.Console()

# define a main function
def main():
    # define a variable to control the main loop
    running = True

    graph = None

    display = gd.GraphDisplay(graph, caption="A World in Conflict")

    display.set_log(myglobals.LogConsole)
    display.set_info(myglobals.InfoConsole)

    selected = None
    paused = False

    day = 0

    # main loop
    while running:

        t = pygame.time.get_ticks()
        # deltaTime in seconds.
        # deltaTime = (t - getTicksLastFrame) / 1000.0

        # event handling, gets all event from the event queue
        for event in pygame.event.get():
            # only do something if the event is of type QUIT
            if event.type == pygame.QUIT:
                # change the value to False, to exit the main loop
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == K_r:
                    pass
                if event.key == K_c:
                    pass
                if event.key == K_SPACE:
                    paused = not paused
                if event.key == K_s:
                    pass
                if event.key == K_p:
                    pass
                if event.key == K_d:
                    pass

        if not paused:
            # Update model

            # myglobals.InfoConsole.log("test", day)


            day += 1

        myglobals.InfoConsole.clear()
        # update_info()
        myglobals.InfoConsole.log("{}".format(view.LogConsole.get_date_to_string(day)))
        myglobals.InfoConsole.push_front("{:.1f} FPS".format(display.clock.get_fps()))
        display.main_loop_end()

     
     
# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
if __name__=="__main__":
    # call the main function
    main()