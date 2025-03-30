import json
import pyxel
import random
from enum import Enum

class GameState(Enum):
    COMBAT = 1
    TRANSITION = 2

class Level:
    def __init__(self, level_number):
        self.level_number = level_number
        self.enemy_damage = 2 + (level_number * 0.5)    # Increased base damage and scaling
        self.enemy_speed = 1.5 + (level_number * 0.4)  # Better speed scaling per level
        self.enemy_health = 60 + (level_number * 20)   # Health scales with level
        self.ladder_x = 550  # Updated ladder x position for larger map
        self.ladder_y = 50   # Updated ladder y position for larger map
        
        # Generate tilemap
        self.tilemap = self.generate_tilemap()
        
        # Tile indices in image bank 1
        self.tiles = {
            'floor': [0, 16, 32],  # Three floor variants
            'wall': [48, 64, 80],   # Three wall variants
            'torch': [0],           # Torch decoration
            'skull': [8]            # Skull decoration
        }
        
        # Color schemes for different levels
        self.color_schemes = {
            1: {"wall": 5, "floor": 1, "accent": 9},   # Dark dungeon
            2: {"wall": 3, "floor": 11, "accent": 10}, # Forest ruins
            3: {"wall": 2, "floor": 4, "accent": 8},   # Crystal caves
            4: {"wall": 1, "floor": 13, "accent": 12}, # Ice dungeon
            5: {"wall": 8, "floor": 2, "accent": 14}   # Lava fortress
        }
        
    def get_colors(self):
        """Get the color scheme for this level."""
        level_type = ((self.level_number - 1) % 5) + 1
        return self.color_schemes[level_type]
        
    def generate_tilemap(self):
        """Generate a tilemap for the current level."""
        width = 38  # 600/16 rounded up
        height = 38
        tilemap = []
        
        # Create empty tilemap with floor tiles
        for y in range(height):
            row = []
            for x in range(width):
                # Add random floor tile variant
                variant = random.randint(0, 2)
                row.append(('floor', variant))
            tilemap.append(row)
        
        # Add walls around the edges
        for x in range(width):
            variant = random.randint(0, 2)
            tilemap[0][x] = ('wall', variant)
            tilemap[height-1][x] = ('wall', variant)
        
        for y in range(height):
            variant = random.randint(0, 2)
            tilemap[y][0] = ('wall', variant)
            tilemap[y][width-1] = ('wall', variant)
        
        # Add some random wall obstacles
        num_obstacles = random.randint(5, 10)
        for _ in range(num_obstacles):
            x = random.randint(2, width-3)
            y = random.randint(2, height-3)
            size = random.randint(2, 4)
            
            for i in range(size):
                for j in range(size):
                    if 0 <= y+i < height and 0 <= x+j < width:
                        variant = random.randint(0, 2)
                        tilemap[y+i][x+j] = ('wall', variant)
        
        # Add some decorative elements
        num_decorations = random.randint(5, 10)
        for _ in range(num_decorations):
            x = random.randint(1, width-2)
            y = random.randint(1, height-2)
            if tilemap[y][x][0] == 'floor':
                if random.random() < 0.5:
                    tilemap[y][x] = ('torch', 0)
                else:
                    tilemap[y][x] = ('skull', 0)
        
        return tilemap



        
    def draw_level(self):
        """Draw the level tilemap."""
        # Draw the background
        colors = self.get_colors()
        pyxel.cls(colors['floor'])
        
        # Draw tiles
        for y, row in enumerate(self.tilemap):
            for x, (tile_type, variant) in enumerate(row):
                screen_x = x * 16
                screen_y = y * 16
                
                if tile_type == 'floor':
                    # Draw floor tile
                    pyxel.blt(screen_x, screen_y, 1, self.tiles['floor'][variant], 0, 16, 16, 0)
                elif tile_type == 'wall':
                    # Draw wall tile
                    pyxel.blt(screen_x, screen_y, 1, self.tiles['wall'][variant], 0, 16, 16, 0)
                elif tile_type == 'torch':
                    # Draw floor under torch
                    pyxel.blt(screen_x, screen_y, 1, self.tiles['floor'][0], 0, 16, 16, 0)
                    # Draw torch
                    pyxel.blt(screen_x + 4, screen_y + 4, 1, self.tiles['torch'][0], 0, 8, 8, 0)
                elif tile_type == 'skull':
                    # Draw floor under skull
                    pyxel.blt(screen_x, screen_y, 1, self.tiles['floor'][0], 0, 16, 16, 0)
                    # Draw skull
                    pyxel.blt(screen_x + 4, screen_y + 4, 1, self.tiles['skull'][0], 0, 8, 8, 0)
        
    def create_enemies(self):
        """Create enemies for this level."""
        # Start with 4 enemies, increase by 1 each level up to a max of 8
        num_enemies = min(4 + (self.level_number - 1), 8)
        enemies = []
        
        # Create spawn positions far from player start (300, 300)
        positions = [
            (50, 50),     # Top left
            (550, 50),    # Top right
            (50, 550),    # Bottom left
            (550, 550),   # Bottom right
            (50, 300),    # Middle left
            (550, 300),   # Middle right
            (300, 50),    # Top middle
            (300, 550),   # Bottom middle
            (400, 400)    # Inner bottom right
        ]
        
        # Randomly select positions for enemies
        selected_positions = random.sample(positions, min(num_enemies, len(positions)))
        
        base_health = 60  # Lower initial health
        health_increase = 20  # Health increase per level
        
        for x, y in selected_positions:
            enemies.append({
                "x": x,
                "y": y,
                "health": base_health + (self.level_number - 1) * health_increase,
                "damage": self.enemy_damage,
                "speed": self.enemy_speed
            })
        return enemies

class LevelManager:
    def __init__(self):
        self.current_level = 1
        self.max_levels = 10
        self.game_state = GameState.COMBAT
        self.level_data = Level(self.current_level)
        self.enemies_defeated = False
        
    def next_level(self):
        """Advance to the next level if conditions are met."""
        if self.enemies_defeated:
            self.current_level += 1
            self.level_data = Level(self.current_level)
            self.enemies_defeated = False
            self.game_state = GameState.COMBAT
            return True
        return False
    
    def is_game_complete(self):
        """Check if all levels are complete."""
        return self.current_level > self.max_levels
