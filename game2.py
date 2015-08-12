from config import *
from components import *
from classes import *

from math import sqrt

import libtcodpy as l
from libtcodpy import random_get_int as randint

class Game:
    """
    Exactly what you think. Note that we can't have more than one
    game running at the same time because of the console_init_root.

    NOTE: There is NO differentiation between a single map and a game.

    TODO: Allow more than one game.
          MAYBE separate GAME and game WORLD.
    """   
    def __init__(self, title='Game'):
        self.state = 1
        self.map = None
        self.rooms = []
        self.numRooms = 0
        self.objects = []
        self.player = None


        # Actual surface you see
        l.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, title, False)
        l.sys_set_fps(LIMIT_FPS)

        # Hidden work surface for all the calculations/changes
        self.canvas = l.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Set up game/map here
        self.spawnPlayer()
        self.makeMap()
        
        # Blit is what updates the main surface to your work surface
        self.updateSurface()
 
        while(self.state):
            self.updateSurface()
            l.console_flush()        
            self.handleKeys()
    
    def isBlocked(self, x, y):
        """
        Checks to see if tile at (x,y) is blocked.

        NOTE: This is one of those situations where I'm not sure if
        the function should be in the caller (object) because that's
        what uses the function, or in the owner of the data (Game).

        TODO: Consider moving this to Object. It doesn't cause
        side effects, so why not?
        """
        if self.map[x][y].blocked:
            return True
        for obj in self.objects:
            if obj.blocks and obj.x == x and obj.y == y:
                return True
        return False

    def spawnPlayer(self):
        """
        Only allows one instance of a player.
        """    
        self.player = Object(self, 0, 0, '@', 'Player', l.white, blocks=True)
        self.objects.append(self.player)
        
        pass

    def updateSurface(self):
        l.console_blit(self.canvas, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)

    def handleKeys(self):
        #key = l.console_check_for_keypress() #THIS DOESN'T BLOCK
        key = l.console_wait_for_keypress(True) #THIS BLOCKS
        
        if key.vk == l.KEY_ENTER and key.lalt:  #Alt + Enter Full Screening
            l.console_set_full_screen(not l.console_is_fullscreen())
        elif(key.vk == l.KEY_ESCAPE):
            self.state = 0
            return 'exit'
        if(self.state):
            if(l.console_is_key_pressed(l.KEY_UP)):          self.player.move(0,-1)
            elif(l.console_is_key_pressed(l.KEY_DOWN)):      self.player.move(0,1)
            elif(l.console_is_key_pressed(l.KEY_LEFT)):      self.player.move(-1,0)
            elif(l.console_is_key_pressed(l.KEY_RIGHT)):     self.player.move(0,1)
            else:
                pass

    def createRoom(self, room):
        for x in range(room.x1 + 1, room.x2 + 1):
            for y in range(room.y1 + 1, room.y2 + 1):
                self.map[x][y].blocked = False
                self.map[x][y].block_sight = False

    def createHTunnel(self, x1, x2, y):
        """
        Creates a horizontal tunnel.
        """
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.map[x][y].blocked = False
            self.map[x][y].block_sight = False

    def createVTunnel(self, y1,y2,x):
        """
        Creates a vertical tunnel.
        """
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.map[x][y].blocked = False
            self.map[x][y].block_sight = False

    def makeMap(self):
        """
        Generates the first map.

        TODO: Generalize this function for successive iterations.
        """
        self.map = [[Tile(True) for y in range(MAP_HEIGHT)] for _ in range(MAP_WIDTH)]

        self.rooms = []
        self.numRooms = 0
    
        for r in range(MAX_ROOMS):
            w = randint(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
            h = randint(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
            x = randint(0, 0, MAP_WIDTH - w - 1)
            y = randint(0, 0, MAP_HEIGHT - h - 1)
   
            new_room = Rect(x, y, w, h)

            failed = False
            for other_room in self.rooms:
                if(new_room.intersect(other_room)):
                    failed = True
                    break
            if not failed:
                self.createRoom(new_room)
                #place_objects(new_room)
                (new_x, new_y) = new_room.center()
                
                #Special case for first room; puts player in there
                if self.numRooms == 0:
                    self.player.x = new_x
                    self.player.y = new_y 
                else:
                    (prev_x, prev_y) = self.rooms[self.numRooms - 1].center()
                    if(randint(0, 0, 1) == 1):
                        #first move horizontally, then vertically
                        self.createHTunnel(prev_x, new_x, prev_y)
                        self.createVTunnel(prev_y, new_y, new_x)
                    else:
                        #first move vertically, then horizontally
                        self.createVTunnel(prev_y, new_y, prev_x)
                        self.createHTunnel(prev_x, new_x, new_y)
                self.rooms.append(new_room)
                self.numRooms += 1

if __name__ == "__main__":
    g = Game("Hi")
