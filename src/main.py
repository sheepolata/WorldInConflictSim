# import the pygame module, so you can use it
import pygame
from pygame.locals import *
import random
import numpy as np

import sys
sys.path.append('./GraphEngine')

import graphdisplay as gd
import view
import myglobals
import model

# define a main function
def main():
	# define a variable to control the main loop
	running = True

	mymodel = model.Model()
	mymodel.test_model_init()

	thread = model.SimThread(mymodel)

	graph = view.CityGraph(mymodel)

	graph.generate_graph_from_model()

	display = view.UserInterface(mymodel, graph)

	display.set_log(myglobals.LogConsole)
	display.set_info(myglobals.InfoConsole)

	thread.freq = 200
	thread.start()

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
				#LMB
				if event.button == 1 and pygame.key.get_mods() & pygame.KMOD_CTRL:
					pass
				elif event.button == 1:
					mpos = pygame.mouse.get_pos()
					# print(mpos)
					smth = False
					for city_node in display.graph.nodes:
						if city_node.collide_point(mpos):
							display.selected = city_node
							smth = True
							break
					if not smth:
						display.selected = None
							
				#MMB
				if event.button == 2:
					pass
				#RMB
				if event.button == 3 and pygame.key.get_mods() & pygame.KMOD_CTRL:
					pass
				if event.button == 3:
					pass
			elif event.type == pygame.KEYDOWN:
				if event.key == K_r:
					pass
				if event.key == K_c:
					pass
				if event.key == K_SPACE:
					thread.pause()
				if event.key == K_s:
					pass
				if event.key == K_p:
					pass
				if event.key == K_d:
					pass

		display.update_info_tab()

		display.main_loop_end()

	 
	 
# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
if __name__=="__main__":
	# call the main function
	main()

	print("END")