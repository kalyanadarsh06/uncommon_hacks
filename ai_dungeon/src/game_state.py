from enum import Enum

class GameState(Enum):
    PLAYING = 1
    GAME_OVER = 2
    LEVEL_COMPLETE = 3
    GAME_COMPLETE = 4

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.score = 0
        self.collected_coins = 0
        self.moving = False
        self.move_direction = [0, 0]  # [dx, dy]

class Lava:
    def __init__(self, size):
        self.size = size
        self.cracked_panels = set()  # Empty set for now
        
    def update(self, walls):
        """Disabled lava update."""
        return False

class Game:
    def __init__(self):
        self.current_level = 1
        self.state = GameState.PLAYING
        self.max_levels = 5
        self.grid = []  # Tracks visited cells
        self.walls = []
        self.coins = []
        self.exit_pos = [0, 0]
        self.size = 10
        
    def init_level(self, maze_data):
        """Initialize a new level with maze data."""
        self.walls = maze_data["walls"]
        self.coins = maze_data["coins"]
        self.exit_pos = maze_data["exit"]
        self.size = maze_data["size"]
        self.grid = [[False] * self.size for _ in range(self.size)]
        
        # Mark starting position as visited
        start_x, start_y = maze_data["start"]
        self.grid[start_y][start_x] = True
        
        # Initialize player and lava
        self.player = Player(start_x, start_y)
        self.lava = Lava(self.size)
        
    def is_wall(self, x, y):
        """Check if position contains a wall."""
        return [x, y] in self.walls
        
    def collect_coin(self, x, y):
        """Collect coin at position if it exists."""
        if [x, y] in self.coins:
            self.coins.remove([x, y])
            self.player.collected_coins += 1
            self.player.score += 100
            
    def update_player_movement(self):
        """Continue player movement until hitting wall or boundary."""
        if not self.player.moving:
            return
            
        new_x = self.player.x + self.player.move_direction[0]
        new_y = self.player.y + self.player.move_direction[1]
        
        # Check if new position is valid
        if (0 <= new_x < self.size and 
            0 <= new_y < self.size and 
            not self.is_wall(new_x, new_y)):
            self.player.x = new_x
            self.player.y = new_y
            self.grid[new_y][new_x] = True  # Mark cell as visited
            self.collect_coin(new_x, new_y)
        else:
            self.player.moving = False
            self.player.move_direction = [0, 0]
            
    def start_movement(self, dx, dy):
        """Start player movement in specified direction."""
        if not self.player.moving:
            self.player.moving = True
            self.player.move_direction = [dx, dy]
            
    def check_game_over(self):
        """Game over check disabled for now."""
        pass
            
    def check_level_complete(self):
        """Check if player has reached the exit."""
        if [self.player.x, self.player.y] == self.exit_pos:
            if self.current_level >= self.max_levels:
                self.state = GameState.GAME_COMPLETE
            else:
                self.state = GameState.LEVEL_COMPLETE
                self.current_level += 1
