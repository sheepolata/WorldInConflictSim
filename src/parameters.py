import math

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
	ROADS     = 9

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
		ROADS     : "ROADS"
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
	ARCHETYPES = [PLAINS, MOUNTAINS, SEASIDE]

	ARCHETYPES_STR = {
		PLAINS : "PLAINS",
		MOUNTAINS : "MOUNTAINS",
		SEASIDE : "SEASIDE"
	}

	LOCATION_COLORS = {
		PLAINS    : (86, 125, 70),
		MOUNTAINS : (139,69,19),
		SEASIDE   : (15,94,156)
	}

class ModelParams(object):

	TILE_TYPE_TO_LOCATION_ARCHETYPE = {
		TileParams.PLAINS    : LocationParams.PLAINS,
		TileParams.FOREST    : LocationParams.PLAINS,
		TileParams.MOUNTAINS : LocationParams.MOUNTAINS,
		TileParams.HILLS     : LocationParams.MOUNTAINS,
		TileParams.PEAKS     : LocationParams.MOUNTAINS,
		TileParams.DESERT    : LocationParams.PLAINS,
		TileParams.BEACH     : LocationParams.SEASIDE,
		TileParams.WATER     : LocationParams.SEASIDE,
		TileParams.DEEPWATER : LocationParams.SEASIDE
	}

	MAP_SIZE = 100

class UserInterfaceParams(object):
	
	TILE_TYPE_COLORS = {
		TileParams.DEEPWATER : (15,94,156),
		TileParams.WATER     : (28,163,236),
		TileParams.DESERT    : (194,178,128),
		TileParams.BEACH     : (194,178,128),
		TileParams.PLAINS    : (0, 168, 0),
		TileParams.HILLS     : (205,133,63),
		TileParams.MOUNTAINS : (160,82,45),
		TileParams.PEAKS     : (128,0,0),
		TileParams.FOREST    : (85,107,47),
		TileParams.ROADS     : (119,136,153)
	}

	SCREENSIZE                     = (1280, 720)
	GRAPH_SURFACE_WIDTH_PROPORTION = 0.6
	INFO_SURFACE_HEIGHT_PROPORTION = 0.6
	MBGC                           = (128, 128, 128)
	IBGC                           = (64, 64, 64)
	LBGC                           = (168, 168, 168)

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