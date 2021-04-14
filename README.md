# WorldInConflictSim

## News and DevLogs

### 14/04/2021

Log event added to communities, so record all local activity. Only caravans are logged for now.

Can display or hide information about current selected community using keyboard input.

Added a small animation when a caravan arrives to a city.

Receiving a caravan now slightly boost the race's birth rate.

Added a method to randomise race location archetype preferences. It randomise the model and make things less predictible.

RaceParams.KINGDOM_MAIN_RACE_BOOST from 0.2 to 0.15 -> Will investigate the impact of the change over some test, but initially it seems to reduce the bias toward a kingdom main race.

### 13/04/2021

Cities are now little city icon, different for each governement! Yay!

Balancing is decent. If a kingdom has a main race that can thrive in its location, this race will grow much more than other, but other can still be present with the randomness of life and caravans.
If a kingdom main race is not in its prefered location or is in a hated location, then it will still be there but with less proportion.

Added a main race to the kingdom. A kindgom is favouring a race, chosen randomly amoung the race of the community at creation. The main race of a kingdom gets a boost to birth rate.
The randomness of life is influence by the kingdom, such as the main race's randomness of life is more clement. Basically, the main race have a slight bonus to the birth rate of the randomness of life.

Temporarely removed population control.

Added a caravan system and removed the migration (for now). From time to time, a caravan can spawn at a city and bring a small amount of a random race to that city. Allow some mix of population and keep things interesting.

Added a Hill location archetype and did some balancing.

### 12/04/2021

Added a migration system. Fro each city, a certain number of population come from neighbouring cities, depending on happiness levels. Not conclusive yet.
Note: though about a random caravan system, randomly a small population (around 100 or so) of one race (chosen randomly) could come and settle in a city. When such a caravan settle, the randomness_of_like value for this race could be bumped to increase the chance of this race to prosper.

Added 4 races (Humans, Elves, Dwarves and Halflings). Each race have preferred and hated location archetype. The birth rate of a race in their preferred location is increased, and the death rate in their hated locations is increased.

Changed the frequency of pop update and randomness_of_life update without changing their values.

Added Forest location archetype and did some balancing

All communities now start with 100 pop (instead of a random percentage of max pop).

Add small dirt roads from location to each of its landmark.

Added Desert city archetype. Also added a population control part to growth rate in case of low food production. Moved pop update from weekly to monthly.

Landmarks are now generated with the map, and not with the city graph.

Added landmarks. Landmarks have an influence on the attractiveness of a location, either a positive influence or a negative one. They are displayed on the map as little icons.
If a landmark is in the area of influence of a location, its influence will be added to the base happiness of that location.
For now, it generates 1.5 times the number of locations landmarks.
May need to revise naming of the landmarks. The names are randonly taken from a list (2 lists for positive and negative landmarks), but a crossway can be placed in the middle of the water. Doesn't matter much though.

Added area_of_influence to location, as a polygon calculated via Voronoi.

The random object is set in parameters.py. It is now possible to set the seed for random generation. Usefull for parameter tests and balancing.

### 11/04/2021

Added Kingdom data. Each community is part of a Kingdom (for now, one kingdom per community).

Kingdoms can be displayed and hidden by pressing K. Used a Voronoi tiling to display the frontiers.
Displaying the Voronoi tiling is hitting the render performance as map size increase. Recommended map size is downed to 200 (from 250). With 200, it still drops 10/15 FPS while rendering the frontiers but the drop is reasonnable.

Changed heuristic in A* to take into account the average travelling cost for tile types. SIGNIFICANTLY improved performances. Note to self: heuristics ARE IMPORTANT!

Test some quadmap generation. Inconclusive for now. Will be used for some sort of split and merge algorithm, if I manages to finish it.

Changed roads display from one tile to a line between 2 locations, using pygame.draw.lines() and the A* calculated path.

Moved some more parameters to parameters.py (like the map size and the colors for each type).

### 10/04/2021

Add road generation on the map, using A\* implemenation on the Map. Quite inefficient with large sized maps, recommended with map size 150 max. Higher values will yield in very long computation time for A\*.
Will think of an improvement at some point.

Created a parameters.py to hold all enumerations and diverse parameters.

### 09/04/2021

Map has now 3 Perlin noise layers, one for the basic terrain, one for the forests and one for the deserts. Much slower generation because of the 3 Perlin noise layers.
This way, the terrain looks much better, but still not exactly what I want.

Communities and locations are now places according to the map, and the graph is generated with a Delaunay triangulation to set the neighbours, with long distance links cut. It can occur that some cities are cut from the rest. No solution for now.

### Older news

GUI in place, using the GraphEngine.

Nodes are selectable to display more info on them.

Render optimisation is done, now stable 60fps even with a grid sized 1000x1000 (though the generation of such grid is long, might need to revise/optimise this later).

The map is drawn to an image file (data/fx/map.png) and this image is redrawn each loop. MUCH MORE efficient than drawing each tile as a rectangle.
To update the map mid-simulation, need to call `UserInterface.save_map_image()` after any modification to the grid model.

Map is implemented as a grid, and is displayed. It is generated using Perlin noise generator. Very simple, generate good region-size maps, but is limited for continent/country generation. Will need to change it eventually, but the grid structure will stay.

For now, everything will go through the `main` branch. Will see according to the development of the project if several branches are needed.

## Setup and usage

### Setup: How to install it from scratch

Install Python version >= 3.8 from [here](https://www.python.org/downloads/).

Install Git Bash from [here](https://git-scm.com/downloads). You can also install Git Desktop from [here](https://docs.github.com/en/desktop/installing-and-configuring-github-desktop/installing-github-desktop#downloading-and-installing-github-desktop) if you wish, but Git Bash is necessary nonetheless.

Clone, fork or download the project.

Open a terminal (I personally use *Windows PowerShell*) in the root of the project, if not done yet.

Run 

`git submodule update --init --recursive`

### How to update the repo

If you're using it for a one time experience, just skip this. If you intend to follow it closely and regularly pull the code to stay up to date, here is how.

To update the main repository, run:

`git pull`

Or use GitHub Desktop interface.

To update the submodules, run:

`git submodule foreach git pull origin main`

You can also set a git alias using

`git config alias.updatesubs '!git submodule foreach git pull origin main'`

and then run

`git updatesubs`

You can also setup a global alias that does everything for you, if you don't have time to loose:

`git config --global alias.updateall '!git pull && git submodule foreach git pull origin main'`

and run `git updateall` when you want to update your repository.

### How to run it

First, put yourself in the `src` folder with your terminal.
After the setup (that needs to be done only once), you can run the simulation with:

`python ./main.py`

or if you use Windows:

`python .\main.py`

## Model & Behaviours

TODO

## Notes :

A simulation of a medfan world composed of different races and communities.

### Ressources: 

- Wealth
- Materials
- Food

Each day it can be produced by creating or transforming it.

Ressources are produced passively by pops.

### Location:

Represent the environment and the buildings present somewhere in the world.

- Has base ressources production
- Has space (max storage for ressources and max quarter/building buildable, base max population)
- Has a base happiness value
- Has buildings
- Has quarters (potentially, not sure how to implement it yet)

### Communities:

- Has a location
- Composed of several races
- Has a happiness

Based on happiness (itself based on several factor, detailed explanation coming later), the population of a community increase or decrease.

### Buildings:

TO BE IMPLEMENTED

Each building cost materials and possibly wealth.

- Industry: +xx% materials production; cost materials
- Farming: +xx% food production; cost materials
- Housing: +xx max population; cost food and materials
- Warehouse: +xx% max ressources
- Luxury: +xx Weatlh; -xx materials

### Population:
- Race

Rest TBD
