# Defunct for now.

class Fighter:
    def __init__(self, hp, defense, power):
        self.max_hp = hp
        self.hp = hp
        self.defense = defense
        self.power = power

class BasicMonster:
    def take_turn(self):
        monster = self.owner
        
        print('The %s growls!' % self.owner.name)

