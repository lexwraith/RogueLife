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
    """
    Base class for pretty much everything using component OOP.

    NOTE: There's a two way connection between Game and Object.
    Not sure if that is a good idea or not.

    TODO: Consider making the game a static class variable.
    Why would each instance need its own pointer?
    """
    def __init__(self, game, x, y, char, name, color, blocks=False,
                    fighter=None, ai=None):
        self.game = game
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks = blocks
        self.fighter = fighter
        
        # Components go here
        if(self.fighter):
            self.fighter.owner = self
        self.ai = ai
        if(self.ai):
            self.ai.owner = self

    def move(self, dx, dy):
        if not self.game.isBlocked(self.x + dx, self.y + dy):
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


