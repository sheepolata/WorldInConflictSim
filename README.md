# WorldInConflictSim

## Upcoming updates

Next, an UI will be put in place, using the GraphEngine.

For now, everything will go through the `main` branch. Will see according to the development of the project if several branches are needed.

## Setup

### How to install it from scratch

How to install python, all the libs and how to run it. TODO.

### How to run it

Need to implement a basic UI and some sort of interaction of monitoring. Then TODO.

## Model & Behaviours

TODO

## Update repo with git:

This is personnal notes, you can use it as is if you wish but you'll need to set it up. (`git submodules` are new to me at the creation of this repo)

`git config alias.updatesubs '!git submodule foreach git pull origin main'`

So `git updatesubs` will update all submodules from the main branch.

`git config --global alias.updateall "!git pull && git updatesubs"`

So `git updateall` should pull the main git repo and all the main submodules.

## Notes :

A simulation of a medfan world composed of different races and communities.

###Ressources: 

- Wealth
- Materials
- Food

Each day it can be produced by creating or transforming it.

Ressources are produced passively by pops.

###Location:

Represent the environment and the buildings present somewhere in the world.

- Has base ressources production
- Has space (max storage for ressources and max quarter/building buildable, base max population)
- Has a base happiness value
- Has buildings
- Has quarters (potentially, not sure how to implement it yet)

###Communities:

- Has a location
- Composed of several races
- Has a happiness

Based on happiness (itself based on several factor, detailed explanation coming later), the population of a community increase or decrease.

###Buildings:

TO BE IMPLEMENTED

Each building cost materials and possibly wealth.

- Industry: +xx% materials production; cost materials
- Farming: +xx% food production; cost materials
- Housing: +xx max population; cost food and materials
- Warehouse: +xx% max ressources
- Luxury: +xx Weatlh; -xx materials

###Population:
- Race

Rest TBD
