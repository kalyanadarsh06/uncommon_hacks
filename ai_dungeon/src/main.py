import pyxel

class Game:
    def __init__(self):
        # Initialize the game window (160x120 is a classic retro resolution)
        pyxel.init(160, 120, title="AI Dungeon Master")
        
        # Player attributes
        self.player_x = 80  # Start in middle of screen
        self.player_y = 60
        self.player_speed = 2
        
        # Start the game
        pyxel.run(self.update, self.draw)
    
    def update(self):
        # Exit if Q is pressed
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        
        # Player movement
        if pyxel.btn(pyxel.KEY_LEFT):
            self.player_x = max(0, self.player_x - self.player_speed)
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.player_x = min(pyxel.width - 8, self.player_x + self.player_speed)
        if pyxel.btn(pyxel.KEY_UP):
            self.player_y = max(0, self.player_y - self.player_speed)
        if pyxel.btn(pyxel.KEY_DOWN):
            self.player_y = min(pyxel.height - 8, self.player_y + self.player_speed)
    
    def draw(self):
        # Clear screen with color 0 (black)
        pyxel.cls(0)
        
        # Draw player as an 8x8 rectangle with color 8 (red)
        pyxel.rect(self.player_x, self.player_y, 8, 8, 8)
        
        # Draw some text
        pyxel.text(5, 5, "AI DUNGEON MASTER", 7)

if __name__ == '__main__':
    Game()
