

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
		FOREST    : "FOREST"
	}

	TYPE_TO_COST = {
	    DEEPWATER : 10,
	    WATER     : 9,
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