# WorldInConflictSim

## Update git:
`git config alias.updatesubs '!git submodule foreach git pull origin main'`
So `git updatesubs` will update all submodules from the main branch.

## Notes :

A simulation of a medfan world composed of different races and communities.

- Ressources: each day it can be produced by creating or transforming it
	- Wealth
	- Materials
	- Food

Communities:
- Has a location
- Has a max population
- Composed of several races
- Has buildings/quarters 

Quarters:
- Industrial: +xx% materials production; cost materials
- Agricultural: +xx% food production; cost materials
- Housing: +xx max population; cost food and materials
- Warehouse: +xx% max ressources
- Luxury: +xx Weatlh; -xx materials

Location:
- Has base ressources production
- Has space (max storage for ressources and max quarter/building buildable, base max population)
- Has a base happiness value

Population:
- Race
- Happiness value ( 0 < h < 100)
