Building a prototype using libtcod 1.5.1.

Note that all these files need to be in your libtcod directory, i.e.

    /usr/lib/libtcod/python/THESE-FILES-GO-HERE

The reason is I failed to install libtcod properly, or, more accurately, libtcod has really poor management and installation instructions (i.e. none. If you actually look at their documentation, even the filenames aren't correct, nor the directories inside the source).

Roadmap:
1) Follow tutorial up to initial combat stages
2) Expand on event processing + logging
3) Introduce UI and event stream
4) Mechanics - All possible attacks
5) Mechanics - Counters and 'Instincts'
6) Mechanics - Positioning and Movement
7) AI - General priority matrix (think chess with weighted modifiers)
8) AI - Non-combat priority matrix (i.e. NPCs)
9) AI - Advanced combat AI
10) AI - Group dynamics (swarming, ranged supporting, buffing/debuffing)
