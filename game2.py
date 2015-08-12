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

        # Secondary layer for field of vision purposes
        self.fov = l.map_new(MAP_WIDTH, MAP_HEIGHT)
        self.fovRecompute = True
        
        # Set up game/map here
        self.spawnPlayer()
        self.makeMap()
       
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                l.map_set_properties(self.fov,
                    x, y, not self.map[x][y].block_sight,
                    not self.map[x][y].blocked)
 
        # Blit is what updates the main surface to your work surface
        l.console_blit(self.canvas, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)
        
        while(self.state):
            self.renderAll()

            l.console_blit(self.canvas, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)
            l.console_flush()        

            # Remove old positions first
            for obj in self.objects:
                obj.clear()
    
            action = self.handleKeys()
            if action == 'exit':
                self.state = 0
                break
            elif self.state == 1 and action != 'didnt-take-turn':
                for obj in self.objects:
                    if obj.ai:
                        obj.ai.take_turn()
            
    
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

    def genObjects(self, room):
        """
        Generates stuff in a room.

        TODO: Generalize this for all first-time generation of a room.
        """
        numMonsters = randint(0, 0, MAX_ROOM_MONSTERS)
        for i in range(numMonsters):
            x = randint(0, room.x1, room.x2)
            y = randint(0, room.y1, room.y2)
            if not self.isBlocked(x,y):    
                if(randint(0, 0, 100) < 80): #80% chance
                    fighter_component = Fighter(3, 3, 3, death_function=monster_death)
                    ai_component = BasicMonster()
                    monster = Object(self, x, y, 'o', 
                        'orc', libtcod.desaturated_green, blocks=True,
                        fighter=fighter_component,
                        ai=ai_component)
                else:
                    fighter_component = Fighter(4, 4, 4, death_function=monster_death)
                    ai_component = BasicMonster()
                    monster = Object(self, x, y, 'T', 
                        'troll', libtcod.darker_green, blocks=True,
                        fighter=fighter_component,
                        ai=ai_component)
                self.objects.append(monster)
        
    def spawnPlayer(self):
        """
        Only allows one instance of a player.
        """    
        self.player = Object(self, 0, 0, '@', 'Player', l.white, blocks=True)
        self.objects.append(self.player)
        
        pass

    def handleKeys(self):
        #key = l.console_check_for_keypress() #THIS DOESN'T BLOCK
        key = l.console_wait_for_keypress(True) #THIS BLOCKS
        
        if key.vk == l.KEY_ENTER and key.lalt:  #Alt + Enter Full Screening
            l.console_set_full_screen(not l.console_is_fullscreen())
        elif(key.vk == l.KEY_ESCAPE):
            self.state = 0
            return 'exit'
        if(self.state):
            if(l.console_is_key_pressed(l.KEY_UP)):          self.playerMove(0,-1)
            elif(l.console_is_key_pressed(l.KEY_DOWN)):      self.playerMove(0,1)
            elif(l.console_is_key_pressed(l.KEY_LEFT)):      self.playerMove(-1,0)
            elif(l.console_is_key_pressed(l.KEY_RIGHT)):     self.playerMove(1,0)
            else:
                pass

    def playerMove(self, dx, dy):
        x = self.player.x + dx
        y = self.player.y + dy

        target = None
        for obj in self.objects:
            if obj.fighter and obj.x == x and obj.y == y:
                target = obj
                break
        if target is not None:
            self.player.fighter.attack(target)
        else:
            self.player.move(dx, dy)
            self.fovRecompute = True
    ##################################
    # MAP STUFF
    ##################################
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

    def renderAll(self):
        if self.fovRecompute:
            self.fovRecompute = False
            l.map_compute_fov(self.fov, 
                self.player.x, self.player.y, 
                TORCH_RADIUS,
                FOV_LIGHT_WALLS, FOV_ALGO)
        
            for y in range(MAP_HEIGHT):
                for x in range(MAP_WIDTH):
                    visible = l.map_is_in_fov(self.fov, x, y)
                    wall = self.map[x][y].block_sight
                    if not visible:
                        if self.map[x][y].explored:
                            if wall:
                                l.console_set_char_background(self.canvas, 
                                    x, y, color_dark_wall, l.BKGND_SET)
                            else:
                                l.console_set_char_background(self.canvas, 
                                    x, y, color_dark_ground, l.BKGND_SET)
                    else:
                        if wall:
                            l.console_set_char_background(self.canvas, 
                                x, y, color_light_wall, l.BKGND_SET )
                        else:
                            l.console_set_char_background(self.canvas, 
                                x, y, color_light_ground, l.BKGND_SET ) 
                        self.map[x][y].explored = True

        for obj in self.objects:
            if(obj != self.player):
                obj.draw()
        self.player.draw()

        l.console_blit(self.canvas, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)

    #l.console_set_default_foreground(con, libtcod.white)
    #l.console_print_ex(con, 1, SCREEN_HEIGHT - 2, libtcod.BKGND_NONE, libtcod.LEFT,
    #    'HP:%s/%s' % (player.fighter.hp, player.fighter.max_hp))
    
             
if __name__ == "__main__":
    g = Game("Hi")
