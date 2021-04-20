import math
import numpy as np

# random_seed = 4011995
random_seed = -1
if random_seed < 0:
	rng = np.random.default_rng()
else:
	rng = np.random.default_rng(random_seed)

def randrange(a, b):
	return a + rng.random()*(b-a)

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

class CommunityParams(object):

	BASE_POP_VALUE = 500

class Race(object):

	SINGULAR_NAME = {
		"Humans"   : "Human",
		"Elves"    : "Elf",
		"Dwarves"  : "Dwarf",
		"Halfings" : "Halfing"
	}

	ADJECTIVE_NAME = {
		"Humans"   : "Human",
		"Elves"    : "Elven",
		"Dwarves"  : "Dwarven",
		"Halfings" : "Halfing"
	}

	def __init__(self, name, positive_growth_rate_perthousand, negative_growth_rate_perthousand, pref_loc, hat_loc):
		self.name           = name
		self.name_singular  = Race.SINGULAR_NAME[self.name]
		self.name_adjective = Race.ADJECTIVE_NAME[self.name]

		self.affinities = {}

		self.positive_growth_rate_factor = 1.0 + (positive_growth_rate_perthousand*0.001)
		self.negative_growth_rate_factor = 1.0 + (negative_growth_rate_perthousand*0.001)

		self.preferred_locations = pref_loc
		self.hated_locations     = hat_loc

	def set_affinity(self, other_race, aff):
		self.affinities[other_race] = aff

class RaceParams(object):
	
	RACE_PREFERRED_LOCATION_FACTOR = 0.1
	KINGDOM_MAIN_RACE_BOOST        = 0.15

	HUMAN   = Race("Humans"  , 0, 0, [LocationParams.PLAINS], [LocationParams.MOUNTAINS])
	ELF     = Race("Elves"   , 0, 0, [LocationParams.FOREST], [LocationParams.MOUNTAINS, LocationParams.HILL])
	DWARF   = Race("Dwarves" , 0, 0, [LocationParams.MOUNTAINS], [LocationParams.FOREST])

	HALFING = Race("Halfings", 0, 0, [LocationParams.HILL], [LocationParams.DESERT])

	RACES = [HUMAN, ELF, DWARF, HALFING]

	def randomiseArchetypePreference():
		for r in RaceParams.RACES:
			new_pl = rng.choice(LocationParams.ARCHETYPES, int(1+rng.random()*2), replace=False)
			new_hl = rng.choice(list(set(LocationParams.ARCHETYPES)-set(new_pl)), int(1+rng.random()*2), replace=False)
	
			r.preferred_locations = new_pl
			r.hated_locations     = new_hl

			print(f"{r.name} prefs in {[LocationParams.ARCHETYPES_STR[a] for a in new_pl]} and hated is {[LocationParams.ARCHETYPES_STR[a] for a in new_hl]}")

class SocialClass(object):

	ADJECTIVE_NAME = {
		"Nobility"    : "Nobles",
		"Bourgeoisie" : "Bourgeois",
		"Middle"      : "Commoners",
		"Poor"        : "Destitutes"
	}

	ADJECTIVE_SHORT_NAME = {
		"Nobility"    : "Nobl.",
		"Bourgeoisie" : "Bourg.",
		"Middle"      : "Com.",
		"Poor"        : "Poor"
	}

	def __init__(self, name, brf, drf):
		self.name = name
		self.adjective = SocialClass.ADJECTIVE_NAME[self.name]
		self.adjective_short = SocialClass.ADJECTIVE_SHORT_NAME[self.name]
		self.birth_rate_factor = brf
		self.death_rate_factor = drf

class SocialClassParams(object):

	NOBILITY    = SocialClass("Nobility"   , 1.00, 1.00)
	BOURGEOISIE = SocialClass("Bourgeoisie", 1.00, 1.00)
	MIDDLE      = SocialClass("Middle"     , 1.00, 1.00)
	POOR        = SocialClass("Poor"       , 1.00, 1.00)

	CLASSES = [NOBILITY, BOURGEOISIE, MIDDLE, POOR]

class KingdomParams(object):

	DEMOCRACY   = 0
	MONARCHY    = 1
	EMPIRE      = 2
	ARISTOCRACY = 3

	NOGOV       = 99

	GOVERNEMENTS = [DEMOCRACY, MONARCHY, EMPIRE, ARISTOCRACY]

	GOVERNEMENTS_STR = {
		DEMOCRACY   : "Democracy",
		MONARCHY    : "Monarchy",
		EMPIRE      : "Empire",
		ARISTOCRACY : "Aristocracy",

		NOGOV       : "EMPTY GOV."
	}

	MILITARIST = 0
	BELIGERANT = 1
	RELIGIOUS  = 2
	CORPORATE  = 3
	SOCIALIST  = 4
	ANARCHIST  = 5
	SCIENTIFIC = 6

	NOPOL      = 99

	POLITICS = [MILITARIST, BELIGERANT, RELIGIOUS, CORPORATE, SOCIALIST, ANARCHIST, SCIENTIFIC]

	POLITICS_AFFINITY = {
		MILITARIST : {
			MILITARIST : -10,
			BELIGERANT : -20,
			RELIGIOUS  : 0,
			CORPORATE  : 5,
			SOCIALIST  : 0,
			ANARCHIST  : -10,
			SCIENTIFIC : 10
		},
		BELIGERANT : {
			MILITARIST : -10,
			BELIGERANT : -20,
			RELIGIOUS  : 0,
			CORPORATE  : 0,
			SOCIALIST  : 0,
			ANARCHIST  : 20,
			SCIENTIFIC : 10
		},
		RELIGIOUS : {
			MILITARIST : 0,
			BELIGERANT : 0,
			RELIGIOUS  : 30,
			CORPORATE  : -10,
			SOCIALIST  : 10,
			ANARCHIST  : -30,
			SCIENTIFIC : -10
		},
		CORPORATE : {
			MILITARIST : 10,
			BELIGERANT : 10,
			RELIGIOUS  : -10,
			CORPORATE  : -20,
			SOCIALIST  : 0,
			ANARCHIST  : -20,
			SCIENTIFIC : 15
		},
		SOCIALIST : {
			MILITARIST : 0,
			BELIGERANT : -10,
			RELIGIOUS  : -5,
			CORPORATE  : 10,
			SOCIALIST  : 30,
			ANARCHIST  : -20,
			SCIENTIFIC : 0	
		},
		ANARCHIST : {
			MILITARIST : 10,
			BELIGERANT : 10,
			RELIGIOUS  : -20,
			CORPORATE  : -5,
			SOCIALIST  : -5,
			ANARCHIST  : 40,
			SCIENTIFIC : -10
		},	
		SCIENTIFIC : {
			MILITARIST : 15,
			BELIGERANT : -5,
			RELIGIOUS  : -10,
			CORPORATE  : 5,
			SOCIALIST  : 0,
			ANARCHIST  : -15,
			SCIENTIFIC : 20
		}
	}

	POLITICS_STR = {
		MILITARIST : "Militarist",
		BELIGERANT : "Beligerant",
		RELIGIOUS  : "Religious",
		CORPORATE  : "Corporate",
		SOCIALIST  : "Socialist",
		ANARCHIST  : "Anarchist",
		SCIENTIFIC : "Scientific",

		NOPOL      : "EMPTY POLITIC"
	}

	POLITICS_STR_SHORT = {
		MILITARIST : "Mili.",
		BELIGERANT : "Beli.",
		RELIGIOUS  : "Reli.",
		CORPORATE  : "Corp.",
		SOCIALIST  : "Soci.",
		ANARCHIST  : "Anar.",
		SCIENTIFIC : "Scie."
	}

	GOVERNEMENT_TYPE_STR = {
		(MILITARIST, BELIGERANT) : "Aggressive",
		(MILITARIST, RELIGIOUS)  : "Holy",
		(MILITARIST, CORPORATE)  : "TBD",
		(MILITARIST, SOCIALIST)  : "TBD",
		(MILITARIST, ANARCHIST)  : "Anarchist",
		(MILITARIST, SCIENTIFIC) : "Powerful",

		(BELIGERANT, RELIGIOUS)  : "Unforgiving",
		(BELIGERANT, CORPORATE)  : "TBD",
		(BELIGERANT, SOCIALIST)  : "TBD",
		(BELIGERANT, ANARCHIST)  : "Barbarian",
		(BELIGERANT, SCIENTIFIC) : "TBD",

		(RELIGIOUS, CORPORATE)   : "TBD",
		(RELIGIOUS, SOCIALIST)   : "TBD",
		(RELIGIOUS, ANARCHIST)   : "Zealous",
		(RELIGIOUS, SCIENTIFIC)  : "Enlighted",

		(CORPORATE, SOCIALIST)   : "Mercantile",
		(CORPORATE, ANARCHIST)   : "TBD",
		(CORPORATE, SCIENTIFIC)  : "TBD",

		(SOCIALIST, ANARCHIST)   : "Poeple\'s",
		(SOCIALIST, SCIENTIFIC)  : "TBD",

		(ANARCHIST, SCIENTIFIC)  : "Unforeseen"

	}

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

	MAP_SIZE = 150
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

def screen_coord_to_map_coord(screen_coord):
	# tw = UserInterfaceParams.SCREENSIZE[0]*UserInterfaceParams.GRAPH_SURFACE_WIDTH_PROPORTION / ModelParams.MAP_SIZE
	# th = UserInterfaceParams.SCREENSIZE[1] / ModelParams.MAP_SIZE

	_tw = (screen_coord[0] / (UserInterfaceParams.SCREENSIZE[0]*UserInterfaceParams.GRAPH_SURFACE_WIDTH_PROPORTION)) * ModelParams.MAP_SIZE
	_th = (screen_coord[1] / UserInterfaceParams.SCREENSIZE[1]) * ModelParams.MAP_SIZE

	# _x = (map_coord[0] * tw)
	# _y = (map_coord[1] * th)

	return (math.floor(_tw), math.floor(_th))

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