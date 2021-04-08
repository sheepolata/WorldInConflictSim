# WorldInConflictSim

## Upcoming updates

Basic GUI in place, using the GraphEngine.

Nodes are selectable to display more info on them.

Map is implemented as a grid, and is displayed. It is generated using a Perlin noise generator. Very simple, generate good region-size maps, but is limited for continent/country generation. Will need to change it eventually, but the grid structure will stay.

Next step is implementing auto generation of locations and communities, according to the map.

Optimisation is needed to the display of the map, for a grid size of 200x200, the FPS drops from stable 60 to around 20-25. Got some ideas to reduce the call to draw.rect :
- Reduce the number of rect to draw by grouping them in larger squares. Could be computationnal heavy or complex to put in place.
- Save the map grid as a image and draw this image. Best idea I think, if map changes during simulation, can simple regenerate the image with the new map and voila.

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
