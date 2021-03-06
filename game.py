from math import sqrt

from config import *

from libtcodpy import random_get_int as randint
import libtcodpy as libtcod
####################
# Class Components TODO: Get this onto a separate file
####################
class Fighter:
    """
    TODO: Relabel this to like 'living thing' or something.
    """
    def __init__(self, body, mind, will, death_function=None):
        #Primary statistics
        self.body = body
        self.mind = mind
        self.will = will
        
        #Derived statistics
        self.constitution = int((self.body + self.will)/2 + 1)
        self.max_hp = self.constitution * 2 * 10
        self.hp = self.max_hp
        
        self.speed = int((.75 * mind) + (.25 * body))
        
        self.ego = (int(mind + will)/2) + 1

        #Skills
        self.dodge = 0
        self.parry = 0
        self.block = 0
        self.unarmed = 0
 
        # Combat System Stats
        self.defense = self.speed + self.dodge/2 + self.parry/2 + self.block/2
        self.power = self.body + self.speed
        
        # Old
        #self.max_hp = hp
        #self.hp = hp
        #self.defense = defense
        #self.power = power
        self.death_function = death_function
        

    def take_damage(self, damage):
        if damage > 0:
            self.hp -= damage
            if(self.hp <= 0):
                function = self.death_function
                if function is not None:
                    function(self.owner)
 
    def attack(self, target):
        damage = self.power - target.fighter.defense
        if(damage > 0):
            print("%s attacks %s for %s damage." % (self.owner.name, target.name, damage))
            target.fighter.take_damage(damage)
        else:
            print("%s tickles %s" % (self.owner.name, target.name))

class BasicMonster:
    def take_turn(self):
        """
        Beelines for player and attacks.
        """
        monster = self.owner
        if(libtcod.map_is_in_fov(fov_map, monster.x, monster.y)): 
            if monster.distance_to(player) >= 2:
                monster.move_towards(player.x, player.y)
            elif(player.fighter.hp > 0):
                monster.fighter.attack(player)

####################
# Classes TODO: Get this onto a separate file
####################
class Rect:
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def center(self):
        return (self.x1 + self.x2)/2,(self.y1 + self.y2)/2

    def intersect(self, other):
            #returns true if this rectangle intersects with another one
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)


class Tile:
    def __init__(self, blocked, block_sight = None):
        self.blocked = blocked
        self.explored = False

        if block_sight is None:
            block_sight = blocked
        self.block_sight = block_sight

class Object:
    #this is a generic object: the player, a monster, an item, the stairs...
    #it's always represented by a character on screen.
    def __init__(self, x, y, char, name, color, blocks=False,
                    fighter=None, ai=None):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks = blocks
        self.fighter = fighter
        if(self.fighter):
            self.fighter.owner = self
        self.ai = ai
        if(self.ai):
            self.ai.owner = self

    def move(self, dx, dy):
        if not is_blocked(self.x + dx, self.y + dy):
            self.x += dx
            self.y += dy

    def move_towards(self, target_x, target_y):
        """
        Take the shortest path to target coordinates.
        """

        #vector from this object to the target, and distance
        dx = target_x - self.x
        dy = target_y - self.y
        distance = sqrt(dx ** 2 + dy ** 2)
 
        #normalize it to length 1 (preserving direction), then round it and
        #convert to integer so the movement is restricted to the map grid
        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        self.move(dx, dy)
    
    def distance_to(self, other):
        #return the distance to another object
        dx = other.x - self.x
        dy = other.y - self.y
        return sqrt(dx ** 2 + dy ** 2)

    def draw(self):
        #set the color and then draw the character that represents this object at its position
        libtcod.console_set_default_foreground(con, self.color)
        libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)
 
    def clear(self):
        #erase the character that represents this object
        libtcod.console_put_char(con, self.x, self.y, ' ', libtcod.BKGND_NONE)

    def send_to_back(self):
        """
        Puts object at start of draw queue.
        TODO: Draw queue should be a priority queue/heap.
        """
        global objects
        objects.remove(self)
        objects.insert(0,self)

def player_death(player):
    global STATE
    print('You dead son.')
    STATE = 'dead'

    player.char = '%'
    player.color = libtcod.dark_red

def monster_death(monster):
    print('%s is dead.' % monster.name.capitalize())
    monster.char = '%'
    monster.color = libtcod.dark_red
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = 'remains of %s' % monster.name
    monster.send_to_back()

def player_move_or_attack(dx, dy):
    global fov_recompute
    x = player.x + dx
    y = player.y + dy

    target = None
    for object in objects:
        if object.fighter and object.x == x and object.y == y:
            target = object
            break

    if target is not None:
        player.fighter.attack(target)
    else:
        player.move(dx, dy)
        fov_recompute = True

def handle_keys():
    global fov_recompute
    #key = libtcod.console_check_for_keypress()  #real-time
    key = libtcod.console_wait_for_keypress(True)  #turn-based
 
    if key.vk == libtcod.KEY_ENTER and key.lalt:
        #Alt+Enter: toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
 
    elif key.vk == libtcod.KEY_ESCAPE:
        return "exit"  #exit game
 
    #movement keys
    if STATE == 'playing':
        if libtcod.console_is_key_pressed(libtcod.KEY_UP):      player_move_or_attack(0, -1) 
        elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):  player_move_or_attack(0, 1)
        elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):  player_move_or_attack(-1, 0)
        elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT): player_move_or_attack(1, 0)
        else:
            return 'didnt-take-turn' 
 
#############################################
# Initialization & Main Loop
#############################################
 
#libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'TITLE', False)
libtcod.sys_set_fps(LIMIT_FPS)

con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)


############################################
# Globals
############################################

fighter_component = Fighter(4,4,4, death_function=player_death)

#create object representing the player
player = Object(0,0, '@', 'player', libtcod.white, blocks = True, 
            fighter=fighter_component)
player.x = 25
player.y = 23

npc = Object(SCREEN_WIDTH/2 - 5, SCREEN_HEIGHT/2, '@', 'npc',  libtcod.yellow, blocks = True)

#the list of objects with those two
objects = [player,npc] 

#global map
m = None

STATE = 'playing'
player_action = None

#############################################
# Functions
#############################################

def is_blocked(x,y):
    global m, objects
    if m[x][y].blocked:
        return True

    for object in objects:
        if object.blocks and object.x == x and object.y == y:
            return True

    return False

def place_objects(room):
    global objects
    num_monsters = randint(0, 0, MAX_ROOM_MONSTERS)
    for i in range(num_monsters):
        x = randint(0, room.x1, room.x2)
        y = randint(0, room.y1, room.y2)
        if not is_blocked(x,y):    
            if(randint(0, 0, 100) < 80): #80% chance
                fighter_component = Fighter(3, 3, 3, death_function=monster_death)
                ai_component = BasicMonster()
                monster = Object(x,y, 'o', 'orc', libtcod.desaturated_green, blocks=True,
                    fighter=fighter_component,
                    ai=ai_component)
            else:
                fighter_component = Fighter(4, 4, 4, death_function=monster_death)
                ai_component = BasicMonster()
                monster = Object(x, y, 'T', 'troll', libtcod.darker_green, blocks=True,
                    fighter=fighter_component,
                    ai=ai_component)

            objects.append(monster)
        
def create_room(room):
    global m
    for x in range(room.x1 + 1, room.x2 + 1):
        for y in range(room.y1 + 1, room.y2 + 1):
            m[x][y].blocked = False
            m[x][y].block_sight = False

def create_h_tunnel(x1, x2, y):
    global m
    for x in range(min(x1, x2), max(x1, x2) + 1):
        m[x][y].blocked = False
        m[x][y].block_sight = False

def create_v_tunnel(y1,y2,x):
    global m
    for y in range(min(y1, y2), max(y1, y2) + 1):
        m[x][y].blocked = False
        m[x][y].block_sight = False

def make_map():
    global m, player
    
    #Default map
    m = [[Tile(True) for y in range(MAP_HEIGHT)] for _ in range(MAP_WIDTH)]

    rooms = []
    num_rooms = 0
    

    for r in range(MAX_ROOMS):
        w = randint(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        h = randint(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        x = randint(0, 0, MAP_WIDTH - w - 1)
        y = randint(0, 0, MAP_HEIGHT - h - 1)
   
        new_room = Rect(x, y, w, h)

        failed = False
        for other_room in rooms:
            if(new_room.intersect(other_room)):
                failed = True
                break
        if not failed:
            create_room(new_room)
            place_objects(new_room)
            (new_x, new_y) = new_room.center()
            #Special case for first room; puts player in there
            if num_rooms == 0:
                player.x = new_x
                player.y = new_y 
            else:
                (prev_x, prev_y) = rooms[num_rooms - 1].center()
                if(randint(0, 0, 1) == 1):
                    #first move horizontally, then vertically
                    create_h_tunnel(prev_x, new_x, prev_y)
                    create_v_tunnel(prev_y, new_y, new_x)
                else:
                    #first move vertically, then horizontally
                    create_v_tunnel(prev_y, new_y, prev_x)
                    create_h_tunnel(prev_x, new_x, new_y)
            rooms.append(new_room)
            num_rooms += 1

make_map()

def render_all():
    global fov_map, color_dark_wall, color_light_wall
    global color_dark_ground, color_light_ground
    global fov_recompute
    global m, objects

    if fov_recompute:
        fov_recompute = False
        libtcod.map_compute_fov(fov_map, player.x, player.y, TORCH_RADIUS,
            FOV_LIGHT_WALLS, FOV_ALGO)
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                visible = libtcod.map_is_in_fov(fov_map, x, y)
                wall = m[x][y].block_sight
                if not visible:
                    if m[x][y].explored:
                        if wall:
                            libtcod.console_set_char_background(con, 
                                x, y, color_dark_wall, libtcod.BKGND_SET)
                        else:
                            libtcod.console_set_char_background(con, 
                                x, y, color_dark_ground, libtcod.BKGND_SET)
                else:
                    if wall:
                        libtcod.console_set_char_background(con, 
                            x, y, color_light_wall, libtcod.BKGND_SET )
                    else:
                        libtcod.console_set_char_background(con, 
                            x, y, color_light_ground, libtcod.BKGND_SET ) 
                    m[x][y].explored = True

    for object in objects:
        if(object != player):
            object.draw()
    player.draw()

    libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)

    libtcod.console_set_default_foreground(con, libtcod.white)
    libtcod.console_print_ex(con, 1, SCREEN_HEIGHT - 2, libtcod.BKGND_NONE, libtcod.LEFT,
        'HP:%s/%s' % (player.fighter.hp, player.fighter.max_hp))
    
 
fov_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)
fov_recompute = True
for y in range(MAP_HEIGHT):
    for x in range(MAP_WIDTH):
        libtcod.map_set_properties(fov_map, 
            x, y, not m[x][y].block_sight, 
            not m[x][y].blocked)

while not libtcod.console_is_window_closed():
    
    render_all()
     
    #blit the contents of "con" to the root console and present it
    libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)
    libtcod.console_flush()
 
    #erase all objects at their old locations, before they move
    for object in objects:
        object.clear()
 
    #handle keys and exit game if needed
    player_action = handle_keys()
    if player_action == 'exit':
        break
    elif STATE == 'playing' and player_action != 'didnt-take-turn':
        for object in objects:
            if object.ai:
                object.ai.take_turn()
