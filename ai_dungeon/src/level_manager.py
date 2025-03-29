import json
import pyxel
from enum import Enum

class GameState(Enum):
    PUZZLE = 1
    COMBAT = 2
    TRANSITION = 3

class Level:
    def __init__(self, level_number):
        self.level_number = level_number
        self.enemy_health = 100 + (level_number * 20)  # Enemies get stronger each level
        self.enemy_damage = 1 + (level_number)         # Enemies hit harder each level
        self.enemy_speed = 1 + (level_number * 0.2)    # Enemies move faster each level
        self.background_color = level_number % 3        # Cycle through different background colors
        
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
        
    def create_enemies(self):
        """Create enemies for this level."""
        num_enemies = 2 + (self.level_number // 2)  # More enemies in later levels
        enemies = []
        positions = [(40, 50), (180, 50), (40, 130), (180, 130), (110, 90)]
        
        for i in range(min(num_enemies, len(positions))):
            x, y = positions[i]
            enemies.append({
                "x": x,
                "y": y,
                "health": self.enemy_health,
                "damage": self.enemy_damage,
                "speed": self.enemy_speed
            })
        return enemies

class LevelManager:
    def __init__(self):
        self.current_level = 1
        self.max_levels = 10
        self.game_state = GameState.PUZZLE
        self.level_data = Level(self.current_level)
        self.puzzle_solved = False
        self.enemies_defeated = False
        
    def next_level(self):
        """Advance to the next level if conditions are met."""
        if self.puzzle_solved and self.enemies_defeated:
            self.current_level += 1
            self.level_data = Level(self.current_level)
            self.puzzle_solved = False
            self.enemies_defeated = False
            self.game_state = GameState.PUZZLE
            return True
        return False
    
    def is_game_complete(self):
        """Check if all levels are complete."""
        return self.current_level > self.max_levels
