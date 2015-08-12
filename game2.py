from config import *
import libtcodpy as l

class Game:
    """
    Exactly what you think. Note that we can't have more than one
    game running at the same time because of the console_init_root.

    TODO: Allow more than one game.
    """
    
    def __init__(self, title='Game'):
        self.state = 1
        # Actual surface you see
        l.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, title, False)
        l.sys_set_fps(LIMIT_FPS)

        # Hidden work surface for all the calculations/changes
        self.canvas = l.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Blit is what updates the main surface to your work surface
        self.updateSurface()
 
        while(self.state):
            self.updateSurface()
            l.console_flush()        
            self.handleKeys()
    
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
            if(l.console_is_key_pressed(l.KEY_UP)):          print("Went up!")
            elif(l.console_is_key_pressed(l.KEY_DOWN)):      print("Went down!")
            elif(l.console_is_key_pressed(l.KEY_LEFT)):      print("Went left!")
            elif(l.console_is_key_pressed(l.KEY_RIGHT)):     print("Went right!")
            else:
                pass

if __name__ == "__main__":
    g = Game("Hi")
