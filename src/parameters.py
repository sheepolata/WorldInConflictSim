import math
import numpy as np

# random_seed = 6011995
random_seed = -1
if random_seed < 0:
	rng = np.random.default_rng()
else:
	rng = np.random.default_rng(random_seed)

class TileParams(object):

	WATER     = 0
	PLAINS    = 1
	MOUNTAINS = 2
	HILLS     = 3
	DEEPWATER = 4
	PEAKS     = 5
	DESERT    = 6
	BEACH     = 7
	FOREST    = 8
	ROAD      = 9
	DIRT_ROAD = 10

	TYPES = [WATER, PLAINS, MOUNTAINS, HILLS, DEEPWATER, PEAKS, DESERT, BEACH, FOREST]

	TYPES_STR = {
		WATER     : "WATER",
		PLAINS    : "PLAINS",
		MOUNTAINS : "MOUNTAINS",
		HILLS     : "HILLS",
		DEEPWATER : "DEEPWATER",
		PEAKS     : "PEAKS",
		DESERT    : "DESERT",
		BEACH     : "BEACH",
		FOREST    : "FOREST",
		ROAD      : "ROAD",
		DIRT_ROAD : "DIRT_ROAD"
	}

	TYPE_TO_COST = {
	    DEEPWATER : 10,
	    WATER     : 6,
	    DESERT    : 3,
	    BEACH     : 1,
	    PLAINS    : 1,
	    HILLS     : 2,
	    MOUNTAINS : 6,
	    PEAKS     : 10,
	    FOREST    : 3
	}

class LocationParams(object):

	PLAINS    = 0
	MOUNTAINS = 1
	SEASIDE   = 2
	DESERT    = 3
	FOREST    = 4
	HILL      = 5
	ARCHETYPES = [PLAINS, MOUNTAINS, SEASIDE, DESERT, FOREST, HILL]

	ARCHETYPES_STR = {
		PLAINS    : "PLAINS",
		MOUNTAINS : "MOUNTAINS",
		SEASIDE   : "SEASIDE",
		DESERT    : "DESERT",
		FOREST    : "FOREST",
		HILL      : "HILL"
	}

	LOCATION_COLORS = {
		PLAINS    : (113,204,0),
		MOUNTAINS : (139,69,19),
		SEASIDE   : (15,94,156),
		DESERT    : (194,178,128),
		FOREST    : (56,102,0),
		HILL      : (205,133,63)
	}

class Race(object):

	def __init__(self, name, positive_growth_rate_perthousand, negative_growth_rate_perthousand, pref_loc, hat_loc):
		self.name = name

		self.affinities = {}

		self.positive_growth_rate_factor = 1.0 + (positive_growth_rate_perthousand*0.001)
		self.negative_growth_rate_factor = 1.0 + (negative_growth_rate_perthousand*0.001)

		self.preferred_locations = pref_loc
		self.hated_locations     = hat_loc

	def set_affinity(self, other_race, aff):
		self.affinities[other_race] = aff

class RaceParams(object):
	
	BASE_POP_VALUE = 500
	
	RACE_PREFERRED_LOCATION_FACTOR = 0.1
	KINGDOM_MAIN_RACE_BOOST        = 0.1

	HUMAN   = Race("Humans"  , 0, 0, [LocationParams.PLAINS], [LocationParams.MOUNTAINS])
	ELF     = Race("Elves"   , 0, 0, [LocationParams.FOREST], [LocationParams.MOUNTAINS, LocationParams.HILL])
	DWARF   = Race("Dwarves" , 0, 0, [LocationParams.MOUNTAINS], [LocationParams.FOREST])

	HALFING = Race("Halfings", 0, 0, [LocationParams.HILL], [LocationParams.DESERT])

	RACES = [HUMAN, ELF, DWARF, HALFING]


class ModelParams(object):

	TILE_TYPE_TO_LOCATION_ARCHETYPE = {
		TileParams.PLAINS    : LocationParams.PLAINS,
		TileParams.FOREST    : LocationParams.FOREST,
		TileParams.MOUNTAINS : LocationParams.MOUNTAINS,
		TileParams.PEAKS     : LocationParams.MOUNTAINS,
		TileParams.HILLS     : LocationParams.HILL,
		TileParams.DESERT    : LocationParams.DESERT,
		TileParams.BEACH     : LocationParams.SEASIDE,
		TileParams.WATER     : LocationParams.SEASIDE,
		TileParams.DEEPWATER : LocationParams.SEASIDE
	}

	MAP_SIZE = 100
	GEN_ROADS_LIMIT = 250

	# 0.01 consumed per week per pop
	FOOD      = 0
	# Used to build stuff
	MATERIALS = 1
	# Affect happiness; 0.01 consumed per month per pop
	WEALTH    = 2

	RESSOURCES = [FOOD, MATERIALS, WEALTH]
	RESSOURCES_STR = {
		FOOD:"FOOD",
		MATERIALS:"MATERIALS",
		WEALTH:"WEALTH"
	}


class UserInterfaceParams(object):
	
	TILE_TYPE_COLORS = {
		TileParams.DEEPWATER : (15,94,156),
		TileParams.WATER     : (28,163,236),
		TileParams.DESERT    : (194,178,128),
		TileParams.BEACH     : (237,201,175),
		TileParams.PLAINS    : (0, 168, 0),
		TileParams.HILLS     : (205,133,63),
		TileParams.MOUNTAINS : (160,82,45),
		TileParams.PEAKS     : (128,0,0),
		TileParams.FOREST    : (85,107,47),
		TileParams.ROAD      : (119,136,153),
		TileParams.DIRT_ROAD : (155,118,83)
	}

	SCREENSIZE                     = (1280, 720)
	GRAPH_SURFACE_WIDTH_PROPORTION = 0.6
	INFO_SURFACE_HEIGHT_PROPORTION = 0.6
	MBGC                           = (128, 128, 128)
	IBGC                           = (64, 64, 64)
	LBGC                           = (168, 168, 168)

	COLOR_LIST = {
		"Black" 		: 	(0,0,0),
	  	"White" 		: 	(255,255,255),
	  	"Red" 			: 	(255,0,0),
	  	"Lime" 			: 	(0,255,0),
	  	"Blue" 			: 	(0,0,255),
	  	"Yellow" 		: 	(255,255,0),
	  	"Cyan" 			: 	(0,255,255),
	  	"Magenta" 		: 	(255,0,255),
	  	"Silver" 		: 	(192,192,192),
	  	"Gray" 			: 	(128,128,128),
	  	"Maroon" 		: 	(128,0,0),
	  	"Olive" 		: 	(128,128,0),
	  	"Green" 		: 	(0,128,0),
	  	"Purple" 		: 	(128,0,128),
	  	"Teal" 			: 	(0,128,128),
	  	"Navy" 			: 	(0,0,128),
  	 	"Orange" 		: 	(255,165,0),
  	 	"Olivedrab" 	: 	(107,142,35),
  	 	"Aqua" 			: 	(0,255,255),
  	 	"Aquamarine" 	: 	(127,255,212),
  	 	"Midnightblue" 	: 	(25,25,112),
  	 	"Darkmagenta" 	: 	(139,0,139),
  	 	"Chocolate" 	: 	(210,105,30)
  	}

	KINGDOM_TO_COLOR = {}

def map_coord_to_screen_coord(map_coord):
	tw = UserInterfaceParams.SCREENSIZE[0]*UserInterfaceParams.GRAPH_SURFACE_WIDTH_PROPORTION / ModelParams.MAP_SIZE
	th = UserInterfaceParams.SCREENSIZE[1] / ModelParams.MAP_SIZE

	_x = (map_coord[0] * tw)
	_y = (map_coord[1] * th)

	return (_x, _y)

def map_coord_to_screen_coord_centered(map_coord):
	ceiled_tw = math.ceil(UserInterfaceParams.SCREENSIZE[0]*UserInterfaceParams.GRAPH_SURFACE_WIDTH_PROPORTION / ModelParams.MAP_SIZE)
	ceiled_th = math.ceil(UserInterfaceParams.SCREENSIZE[1] / ModelParams.MAP_SIZE)

	tw = UserInterfaceParams.SCREENSIZE[0]*UserInterfaceParams.GRAPH_SURFACE_WIDTH_PROPORTION / ModelParams.MAP_SIZE
	th = UserInterfaceParams.SCREENSIZE[1] / ModelParams.MAP_SIZE

	tile_size = (ceiled_tw, ceiled_th)

	_x = (map_coord[0] * tw) + tile_size[0]/2
	_y = (map_coord[1] * th) + tile_size[1]/2

	return (_x, _y)