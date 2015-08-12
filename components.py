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


