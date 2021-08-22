import math
import numpy as np

random_seed = 4011995
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

class AIKingdomControllerParams(object):

	BALANCED     = 0
	EXPANSIONIST = 1
	AGGRESSIVE   = 2
	ISOLATIONIST = 3
	MERCANTILE   = 4

	NOBEHAVIOUR = 99

	DIPLOSTANCE_ARCHETYPES = [BALANCED, EXPANSIONIST, AGGRESSIVE, ISOLATIONIST, MERCANTILE]

	DIPLOSTANCE_STR = {
		BALANCED     : "Balanced",
		EXPANSIONIST : "Expansionist",
		AGGRESSIVE   : "Aggresive",
		ISOLATIONIST : "Isolationist",
		MERCANTILE   : "Mercantile",

		NOBEHAVIOUR  : 99
	}

class KingdomParams(object):

	kingdomnamesonly_list = open("../data/namelists/kingdom_names_only.txt")
	kingdomnamesonly_from_file = kingdomnamesonly_list.readlines()
	kingdomnamesonly_list.close()

	GLOBAL_KINGDOM_NAMES_ONLY = [_s.replace('\n', '') for _s in kingdomnamesonly_from_file]

	kingdomadjonly_list = open("../data/namelists/kingdom_adj_only.txt")
	kingdomadjonly_from_file = kingdomadjonly_list.readlines()
	kingdomadjonly_list.close()

	GLOBAL_KINGDOM_ADJ_ONLY = [_s.replace('\n', '') for _s in kingdomadjonly_from_file]

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
		MILITARIST : "Mil.",
		BELIGERANT : "Bel.",
		RELIGIOUS  : "Rel.",
		CORPORATE  : "Cor.",
		SOCIALIST  : "Soc.",
		ANARCHIST  : "Ana.",
		SCIENTIFIC : "Sci."
	}

	GOVERNEMENT_TYPE_STR = {
		(MILITARIST, BELIGERANT) : ["Aggressive"],
		(MILITARIST, RELIGIOUS)  : ["Holy"],
		(MILITARIST, CORPORATE)  : ["Mercenary"],
		(MILITARIST, SOCIALIST)  : ["Free", "Soviet"],
		(MILITARIST, ANARCHIST)  : ["Anarchist"],
		(MILITARIST, SCIENTIFIC) : ["Powerful"],

		(BELIGERANT, RELIGIOUS)  : ["Unforgiving"],
		(BELIGERANT, CORPORATE)  : ["Syndicate"], 
		(BELIGERANT, SOCIALIST)  : ["Purist", "Revolutionnary"],
		(BELIGERANT, ANARCHIST)  : ["Barbarian"],
		(BELIGERANT, SCIENTIFIC) : ["Facist", "Utilitaristic", "Protectionnist", "Rejunevative"],

		(RELIGIOUS, CORPORATE)   : ["Ordered", "Sectarian"],
		(RELIGIOUS, SOCIALIST)   : ["United", "Benevolent"],
		(RELIGIOUS, ANARCHIST)   : ["Zealous"],
		(RELIGIOUS, SCIENTIFIC)  : ["Enlighted"],

		(CORPORATE, SOCIALIST)   : ["Mercantile"],
		(CORPORATE, ANARCHIST)   : ["Unified Chaos", "Artisanal"],
		(CORPORATE, SCIENTIFIC)  : ["Vanguard"],

		(SOCIALIST, ANARCHIST)   : ["People\'s"],
		(SOCIALIST, SCIENTIFIC)  : ["Humanist", "Materialist"],

		(ANARCHIST, SCIENTIFIC)  : ["Unforeseen"]
	}

	DEMOCRACY   = 0
	MONARCHY    = 1
	EMPIRE      = 2
	TRIBAL      = 4
	OLIGARCHY   = 5
	CORPORATION = 6
	DICTATURE   = 7

	NOGOV       = 99


	GOVERNEMENTS_STR_SIMPLE = {
		DEMOCRACY   : "Democracy",
		MONARCHY    : "Monarchy",
		EMPIRE      : "Empire",
		TRIBAL      : "Tribal system",
		OLIGARCHY   : "Oligarchy",
		CORPORATION : "Guild",
		DICTATURE   : "Dictature",

		NOGOV       : "EMPTY GOV."
	}

	GOVERNEMENTS_STR = {
		DEMOCRACY   : ["Democracy", "Republic", "Commonwealth"],
		MONARCHY    : ["Monarchy", "Sovereignty", "Principality"],
		EMPIRE      : ["Empire", "Federation", "Confederation"],
		TRIBAL      : ["Tribes", "Nations", "Dynasty"],
		OLIGARCHY   : ["Oligarchy", "Aristocracy", "Technocracy"],
		CORPORATION : ["Corporation", "Organisation", "Guild"],
		DICTATURE   : ["Dictature", "Monocracy", "Autocracy"],

		NOGOV       : ["EMPTY GOV."]
	}

	GOVERNEMENTS = [DEMOCRACY, MONARCHY, EMPIRE, TRIBAL, OLIGARCHY, CORPORATION, DICTATURE]

	GOVERNEMENT_FROM_POLICIES = {
		(MILITARIST, BELIGERANT) : [DEMOCRACY, MONARCHY, EMPIRE, TRIBAL, OLIGARCHY, DICTATURE],
		(MILITARIST, RELIGIOUS)  : [MONARCHY, EMPIRE, TRIBAL, OLIGARCHY, DICTATURE],
		(MILITARIST, CORPORATE)  : [OLIGARCHY, EMPIRE],
		(MILITARIST, SOCIALIST)  : [CORPORATION, OLIGARCHY],
		(MILITARIST, ANARCHIST)  : [TRIBAL, DEMOCRACY],
		(MILITARIST, SCIENTIFIC) : [OLIGARCHY, MONARCHY, EMPIRE],

		(BELIGERANT, RELIGIOUS)  : [MONARCHY, EMPIRE, TRIBAL, OLIGARCHY, DICTATURE],
		(BELIGERANT, CORPORATE)  : [CORPORATION, EMPIRE, OLIGARCHY],
		(BELIGERANT, SOCIALIST)  : [TRIBAL, DEMOCRACY, EMPIRE, DICTATURE],
		(BELIGERANT, ANARCHIST)  : [TRIBAL, EMPIRE, DEMOCRACY],
		(BELIGERANT, SCIENTIFIC) : [DEMOCRACY, OLIGARCHY, EMPIRE, DICTATURE],

		(RELIGIOUS, CORPORATE)   : [CORPORATION, OLIGARCHY, MONARCHY],
		(RELIGIOUS, SOCIALIST)   : [MONARCHY, TRIBAL],
		(RELIGIOUS, ANARCHIST)   : [TRIBAL],
		(RELIGIOUS, SCIENTIFIC)  : [CORPORATION, OLIGARCHY, MONARCHY],

		(CORPORATE, SOCIALIST)   : [CORPORATION, TRIBAL, EMPIRE],
		(CORPORATE, ANARCHIST)   : [CORPORATION, TRIBAL, DICTATURE],
		(CORPORATE, SCIENTIFIC)  : [CORPORATION],

		(SOCIALIST, ANARCHIST)   : [DICTATURE, EMPIRE],
		(SOCIALIST, SCIENTIFIC)  : [EMPIRE, TRIBAL],

		(ANARCHIST, SCIENTIFIC)  : [OLIGARCHY, TRIBAL, EMPIRE, DICTATURE]
	}

	GOVERNEMENTS_AFFINITY = {
		DEMOCRACY   : {
			DEMOCRACY   : 20,
			MONARCHY    : -10,
			EMPIRE      : -10,
			TRIBAL      : 10,
			OLIGARCHY   : 5,
			CORPORATION : 15,
			DICTATURE   : -20
		},
		MONARCHY    : {
			DEMOCRACY   : 0,
			MONARCHY    : 15,
			EMPIRE      : 15,
			TRIBAL      : -5,
			OLIGARCHY   : 5,
			CORPORATION : -5,
			DICTATURE   : 5
		},
		EMPIRE      : {
			DEMOCRACY   : -10,
			MONARCHY    : 10,
			EMPIRE      : -5,
			TRIBAL      : 0,
			OLIGARCHY   : 10,
			CORPORATION : 5,
			DICTATURE   : 15
		},
		TRIBAL      : {
			DEMOCRACY   : 15,
			MONARCHY    : -10,
			EMPIRE      : -15,
			TRIBAL      : 25,
			OLIGARCHY   : -10,
			CORPORATION : -5,
			DICTATURE   : -15
		},
		OLIGARCHY   : {
			DEMOCRACY   : -25,
			MONARCHY    : 10,
			EMPIRE      : 0,
			TRIBAL      : -10,
			OLIGARCHY   : 25,
			CORPORATION : 10,
			DICTATURE   : 0
		},
		CORPORATION : {
			DEMOCRACY   : 30,
			MONARCHY    : 10,
			EMPIRE      : -15,
			TRIBAL      : 15,
			OLIGARCHY   : -15,
			CORPORATION : -30,
			DICTATURE   : 0
		},
		DICTATURE   : {
			DEMOCRACY   : -20,
			MONARCHY    : 10,
			EMPIRE      : 10,
			TRIBAL      : -20,
			OLIGARCHY   : 10,
			CORPORATION : -10,
			DICTATURE   : -20
		}
	}

	# DIPLOSTANCE_ARCHETYPES = [BALANCED, EXPANSIONIST, AGGRESSIVE, ISOLATIONIST, MERCANTILE]
	DIPLOSTANCE_FROM_GOV = {
		(MILITARIST, BELIGERANT) : (AIKingdomControllerParams.DIPLOSTANCE_ARCHETYPES, [1, 4, 4, 3, 0]),
		(MILITARIST, RELIGIOUS)  : (AIKingdomControllerParams.DIPLOSTANCE_ARCHETYPES, [2, 4, 2, 4, 1]),
		(MILITARIST, CORPORATE)  : (AIKingdomControllerParams.DIPLOSTANCE_ARCHETYPES, [2, 3, 1, 0, 4]),
		(MILITARIST, SOCIALIST)  : (AIKingdomControllerParams.DIPLOSTANCE_ARCHETYPES, [3, 3, 3, 1, 1]),
		(MILITARIST, ANARCHIST)  : (AIKingdomControllerParams.DIPLOSTANCE_ARCHETYPES, [1, 2, 4, 1, 0]),
		(MILITARIST, SCIENTIFIC) : (AIKingdomControllerParams.DIPLOSTANCE_ARCHETYPES, [2, 4, 2, 4, 2]),

		(BELIGERANT, RELIGIOUS)  : (AIKingdomControllerParams.DIPLOSTANCE_ARCHETYPES, [1, 4, 4, 2, 0]),
		(BELIGERANT, CORPORATE)  : (AIKingdomControllerParams.DIPLOSTANCE_ARCHETYPES, [2, 2, 1, 0, 4]), 
		(BELIGERANT, SOCIALIST)  : (AIKingdomControllerParams.DIPLOSTANCE_ARCHETYPES, [1, 4, 4, 1, 0]),
		(BELIGERANT, ANARCHIST)  : (AIKingdomControllerParams.DIPLOSTANCE_ARCHETYPES, [1, 2, 4, 1, 0]),
		(BELIGERANT, SCIENTIFIC) : (AIKingdomControllerParams.DIPLOSTANCE_ARCHETYPES, [1, 3, 3, 1, 1]),

		(RELIGIOUS, CORPORATE)   : (AIKingdomControllerParams.DIPLOSTANCE_ARCHETYPES, [2, 3, 1, 3, 4]),
		(RELIGIOUS, SOCIALIST)   : (AIKingdomControllerParams.DIPLOSTANCE_ARCHETYPES, [2, 1, 1, 4, 2]),
		(RELIGIOUS, ANARCHIST)   : (AIKingdomControllerParams.DIPLOSTANCE_ARCHETYPES, [1, 4, 3, 1, 1]),
		(RELIGIOUS, SCIENTIFIC)  : (AIKingdomControllerParams.DIPLOSTANCE_ARCHETYPES, [2, 1, 1, 4, 3]),

		(CORPORATE, SOCIALIST)   : (AIKingdomControllerParams.DIPLOSTANCE_ARCHETYPES, [2, 1, 1, 0, 4]),
		(CORPORATE, ANARCHIST)   : (AIKingdomControllerParams.DIPLOSTANCE_ARCHETYPES, [2, 2, 3, 0, 4]),
		(CORPORATE, SCIENTIFIC)  : (AIKingdomControllerParams.DIPLOSTANCE_ARCHETYPES, [3, 2, 1, 1, 4]),

		(SOCIALIST, ANARCHIST)   : (AIKingdomControllerParams.DIPLOSTANCE_ARCHETYPES, [2, 1, 3, 1, 1]),
		(SOCIALIST, SCIENTIFIC)  : (AIKingdomControllerParams.DIPLOSTANCE_ARCHETYPES, [2, 3, 1, 1, 3]),

		(ANARCHIST, SCIENTIFIC)  : (AIKingdomControllerParams.DIPLOSTANCE_ARCHETYPES, [1, 3, 2, 1, 3])
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

	RELATION_DISPLAY_GRADIENT = [
		(237, 41, 56),
		(178, 95, 74),
		(235, 235, 235),
		(59, 202, 109),
		(0, 255, 127)
	]

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