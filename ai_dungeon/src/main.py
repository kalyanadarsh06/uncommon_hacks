import pyxel
<<<<<<< HEAD
import random
import math
import os
from enum import Enum
from level_manager import LevelManager, GameState
from ui_manager import UIManager

class WeaponType(Enum):
    SWORD = 1
    BOW = 2
    STAFF = 3

class Projectile:
    def __init__(self, x, y, dx, dy, damage, weapon_type, size=8):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.damage = damage
        self.weapon_type = weapon_type
        self.size = size
        self.active = True

    def update(self):
        self.x += self.dx
        self.y += self.dy
        # Deactivate if out of bounds
        if (self.x < 0 or self.x > pyxel.width or
            self.y < 0 or self.y > pyxel.height):
            self.active = False

    def draw(self):
        # Draw projectile based on weapon type
        Game.create_weapon_effect(Game, self.x, self.y, self.weapon_type)

class Enemy:
    def __init__(self, x, y, speed=1, health=60):
        self.x = x
        self.y = y
        self.speed = speed
        self.size = 16  # Larger enemy sprite
        self.max_health = health
        self.health = health
        self.hit_flash = 0  # Timer for hit animation

    def take_damage(self, amount):
        self.health -= amount
        self.hit_flash = 10  # Flash for 10 frames when hit
        
    def is_valid_move(self, new_x, new_y):
        # Check map boundaries with padding
        edge_padding = 40
        if new_x < edge_padding or new_x > pyxel.width - self.size - edge_padding or \
           new_y < edge_padding or new_y > pyxel.height - self.size - edge_padding:
            return False
            
        # Check rock collisions
        for rock_x, rock_y, rock_size in Game.rock_obstacles:
            if self.check_collision(new_x, new_y, rock_x, rock_y, rock_size):
                return False
                
        return True
        
    def check_collision(self, x1, y1, x2, y2, size):
        return (abs(x1 - x2) < size and abs(y1 - y2) < size)

    def update(self, player_x, player_y):
        if self.hit_flash > 0:
            self.hit_flash -= 1

        # Calculate direction to player
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Initialize movement variables
        dx_move = 0
        dy_move = 0
        
        # Movement settings
        chase_range = 150
        min_distance = 40
        awareness = 0.6
        
        # Get current behavior pattern
        self.chase_type = getattr(self, 'chase_type', random.random())
        self.stuck_timer = getattr(self, 'stuck_timer', 0)
        self.last_pos = getattr(self, 'last_pos', (self.x, self.y))
        
        # Check if stuck
        if abs(self.x - self.last_pos[0]) < 1 and abs(self.y - self.last_pos[1]) < 1:
            self.stuck_timer += 1
        else:
            self.stuck_timer = 0
        self.last_pos = (self.x, self.y)
        
        # If stuck, try a new direction
        if self.stuck_timer > 30:
            self.wander_angle = random.random() * 2 * math.pi
            self.stuck_timer = 0
        
        if distance < chase_range and self.chase_type > (1 - awareness):
            # Calculate movement avoiding obstacles
            if distance > min_distance:
                # Try to find clear path to player
                angle = math.atan2(dy, dx)
                # Test a few angles around the direct path
                angles = [angle, angle + 0.3, angle - 0.3, angle + 0.6, angle - 0.6]
                
                for test_angle in angles:
                    test_dx = math.cos(test_angle) * self.speed
                    test_dy = math.sin(test_angle) * self.speed
                    
                    # If this direction is clear, use it
                    if self.is_valid_move(self.x + test_dx, self.y + test_dy):
                        dx_move = test_dx
                        dy_move = test_dy
                        break
            else:
                # Circle around player
                angle = math.atan2(dy, dx) + math.pi/2
                dx_move = math.cos(angle) * self.speed * 0.8
                dy_move = math.sin(angle) * self.speed * 0.8
        else:
            # Wander with obstacle avoidance
            self.move_timer = getattr(self, 'move_timer', 0) + 1
            self.wander_angle = getattr(self, 'wander_angle', random.random() * 2 * math.pi)
            
            if self.move_timer >= 60 or not self.is_valid_move(self.x + dx_move, self.y + dy_move):
                self.move_timer = 0
                # Try several angles until finding a clear path
                for _ in range(8):
                    test_angle = random.random() * 2 * math.pi
                    test_dx = math.cos(test_angle) * self.speed
                    test_dy = math.sin(test_angle) * self.speed
                    if self.is_valid_move(self.x + test_dx, self.y + test_dy):
                        self.wander_angle = test_angle
                        break
            
            dx_move = math.cos(self.wander_angle) * self.speed * 0.7
            dy_move = math.sin(self.wander_angle) * self.speed * 0.7
        
        # Store movement for next frame
        self.prev_dx = dx_move
        self.prev_dy = dy_move
        
        # Apply movement with better boundary checking
        dx = dx_move
        dy = dy_move
            
        # Update position with boundary checking
        new_x = self.x + dx
        new_y = self.y + dy
            
        # Keep away from edges and corners
        edge_padding = 40  # Larger padding to avoid corners
        if edge_padding <= new_x <= pyxel.width - self.size - edge_padding:
            self.x = new_x
        else:
            # Push away from edges
            if new_x < edge_padding:
                dx_move = self.speed  # Move right
            else:
                dx_move = -self.speed  # Move left
            self.x += dx_move
            
        if edge_padding <= new_y <= pyxel.height - self.size - edge_padding:
            self.y = new_y
        else:
            # Push away from edges
            if new_y < edge_padding:
                dy_move = self.speed  # Move down
            else:
                dy_move = -self.speed  # Move up
            self.y += dy_move

    def draw(self):
        # Draw goblin with flash effect
        if self.hit_flash > 0 and self.hit_flash % 2 == 0:
            # Flash white
            pyxel.pal(11, 7)  # Replace green with white
        
        # Draw goblin sprite
        pyxel.blt(self.x, self.y, 0, 8, 0, self.size, self.size, 0)
        
        # Reset palette
        pyxel.pal()
            
        # Draw health bar (centered and properly scaled)
        base_width = self.size + 10
        health_scale = self.max_health / 60  # Scale relative to base health
        bar_width = int(base_width * min(health_scale, 2.5))  # Cap scaling at 2.5x
        bar_height = 4
        health_width = int(bar_width * (self.health / self.max_health))  # Proper percentage calculation
        bar_x = self.x + (self.size - bar_width) // 2
        bar_y = self.y - 8
        
        # Draw background (dark red)
        pyxel.rect(bar_x, bar_y, bar_width, bar_height, 1)
        # Draw health (color based on percentage)
        health_percent = self.health / self.max_health
        if health_percent > 0.6:
            color = 11  # Green
        elif health_percent > 0.3:
            color = 9   # Orange
        else:
            color = 8   # Red
        pyxel.rect(bar_x, bar_y, health_width, bar_height, color)
        # Draw border
        pyxel.rect(bar_x-1, bar_y-1, bar_width+2, 1, 0)  # Top
        pyxel.rect(bar_x-1, bar_y+bar_height, bar_width+2, 1, 0)  # Bottom
        pyxel.rect(bar_x-1, bar_y, 1, bar_height, 0)  # Left
        pyxel.rect(bar_x+bar_width, bar_y, 1, bar_height, 0)  # Right

class Game:
    rock_obstacles = []
    
    def __init__(self):
        # Initialize game with larger window
        pyxel.init(600, 600, title="AI Dungeon Master")
        
        # Load sprite resources
        pyxel.load("../assets/sprites.pyxres")
        
        # Initialize managers
        self.level_manager = LevelManager()
        self.ui_manager = UIManager()
=======
from maze_generator import MazeGenerator
from game_state import Game, GameState, Player

class MazeGame:
    def __init__(self):
        # Initialize game window
        self.CELL_SIZE = 60  # Increased cell size for 600x600 window
        self.GRID_SIZE = 10
        window_size = self.CELL_SIZE * self.GRID_SIZE
        pyxel.init(window_size, window_size, title="AI Maze Escape")
        
        # Colors
        self.COLORS = {
            'wall': 5,      # Dark blue
            'player': 11,   # Yellow
            'coin': 10,     # Yellow
            'exit': 3,      # Green
            'path': 1,      # Dark blue
            'bg': 0,       # Black
            'text': 7,      # White
            'placed_block': 13,  # Purple for player-placed blocks
            'cursor': 14,   # Pink for cursor highlight
            'highlight': 6  # Light blue for highlighting
        }
>>>>>>> arun_branch
        
        # Initialize game components
        self.maze_generator = MazeGenerator()
        self.game = Game()
        
<<<<<<< HEAD
        # Initialize first level
        self.setup_combat()
=======
        # Start first level
        self.init_level()
        self.game.state = GameState.PLAYING
>>>>>>> arun_branch
        
        # Start the game loop
        pyxel.run(self.update, self.draw)
    
<<<<<<< HEAD
    def reset_player(self):
        """Reset player to starting position with initial attributes."""
        self.player_x = 300  # Center of 600x600
        self.player_y = 300
        self.player_speed = 4.0  # Even faster player speed
        self.player_size = 32   # Much larger player sprite
        self.player_health = 100
        self.player_direction = 1
        
        # Weapon system
        self.current_weapon = WeaponType.SWORD
        self.weapons = {
            WeaponType.SWORD: {"damage": 30, "cooldown": 15, "duration": 10},  # More damage, faster cooldown
            WeaponType.BOW: {"damage": 20, "cooldown": 25, "duration": 5},    # More damage, faster cooldown
            WeaponType.STAFF: {"damage": 25, "cooldown": 35, "duration": 15}  # More damage, faster cooldown
        }
        self.attacking = False
        self.attack_frame = 0
        self.attack_cooldown = 0
        
        # Clear lists
        self.projectiles = []
        self.enemies = []
    
    def check_collision(self, x1, y1, x2, y2, size):
        return (abs(x1 - x2) < size and abs(y1 - y2) < size)
        
    def check_circle_rect_collision(self, circle_x, circle_y, circle_radius, rect_x, rect_y, rect_w, rect_h):
        # Find closest point on rectangle to circle center
        closest_x = max(rect_x, min(circle_x, rect_x + rect_w))
        closest_y = max(rect_y, min(circle_y, rect_y + rect_h))
        
        # Calculate distance between closest point and circle center
        distance_x = circle_x - closest_x
        distance_y = circle_y - closest_y
        distance_squared = distance_x * distance_x + distance_y * distance_y
        
        return distance_squared < (circle_radius * circle_radius)
        
    def is_valid_move(self, new_x, new_y):
        # Check map boundaries with padding
        edge_padding = 40
        if new_x < edge_padding or new_x > pyxel.width - self.size - edge_padding or \
           new_y < edge_padding or new_y > pyxel.height - self.size - edge_padding:
            return False
            
        # Check rock collisions
        for rock_x, rock_y, rock_size in Game.rock_obstacles:
            if self.check_circle_rect_collision(rock_x, rock_y, rock_size + 5,
                                              new_x, new_y, self.size, self.size):
                return False
                
        return True
    
    def check_attack_hit(self, enemy):
        # Calculate attack hitbox based on player direction
        attack_x = self.player_x
        attack_y = self.player_y
        if self.player_direction == 0:  # up
            attack_y -= self.player_size
        elif self.player_direction == 1:  # right
            attack_x += self.player_size
        elif self.player_direction == 2:  # down
            attack_y += self.player_size
        else:  # left
            attack_x -= self.player_size
        
        return self.check_collision(attack_x, attack_y, enemy.x, enemy.y, self.player_size + 4)
    
    def create_projectile(self):
        speed = 4
        if self.current_weapon == WeaponType.BOW:
            # Create arrow projectile
            dx = speed if self.player_direction == 1 else -speed if self.player_direction == 3 else 0
            dy = speed if self.player_direction == 2 else -speed if self.player_direction == 0 else 0
            return Projectile(self.player_x, self.player_y, dx, dy, 
                            self.weapons[self.current_weapon]["damage"], 6)
        elif self.current_weapon == WeaponType.STAFF:
            # Create magic projectile that moves in all directions
            projectiles = []
            for angle in range(0, 360, 45):  # 8 directions
                rad = math.radians(angle)
                dx = speed * math.cos(rad)
                dy = speed * math.sin(rad)
                projectiles.append(Projectile(self.player_x, self.player_y, dx, dy,
                                            self.weapons[self.current_weapon]["damage"], 12))
            return projectiles
        return None

=======
    def init_level(self):
        """Initialize a new level."""
        maze_data = self.maze_generator.generate_maze(self.game.current_level)
        self.game.init_level(maze_data)
    
>>>>>>> arun_branch
    def update(self):
        """Update game state."""
        if self.game.state == GameState.PLAYING:
            # Handle input
            if not self.game.player.moving:
                if pyxel.btnp(pyxel.KEY_UP):
                    self.game.start_movement(0, -1)
                elif pyxel.btnp(pyxel.KEY_DOWN):
                    self.game.start_movement(0, 1)
                elif pyxel.btnp(pyxel.KEY_LEFT):
                    self.game.start_movement(-1, 0)
                elif pyxel.btnp(pyxel.KEY_RIGHT):
                    self.game.start_movement(1, 0)
                elif pyxel.btnp(pyxel.KEY_R):  # Reset game with blockcide message
                    self.game.commit_blockcide()
            
<<<<<<< HEAD
        # Update UI
        self.ui_manager.update()
        
        # Update invincibility timer
        if hasattr(self, 'invincible_timer') and self.invincible_timer > 0:
            self.invincible_timer -= 1
        
        # Handle different game states
        if self.level_manager.game_state == GameState.COMBAT:
            self.update_combat()
        elif self.level_manager.game_state == GameState.TRANSITION:
            self.update_transition()
    

    
    def setup_combat(self):
        """Prepare the combat phase."""
        # Reset player position
        self.reset_player()
        
        # Create enemies for this level
        enemy_data = self.level_manager.level_data.create_enemies()
        self.enemies = []
        for data in enemy_data:
            enemy = Enemy(data["x"], data["y"], data["speed"])
            enemy.health = data["health"]
            self.enemies.append(enemy)
            
        # Generate rock obstacles based on walls in tilemap
        Game.rock_obstacles = []
        for y, row in enumerate(self.level_manager.level_data.tilemap):
            for x, (tile_type, _) in enumerate(row):
                if tile_type == 'wall':
                    # Convert tilemap coordinates to pixel coordinates
                    rock_x = x * 16
                    rock_y = y * 16
                    Game.rock_obstacles.append((rock_x, rock_y, 16))
    
    def update_combat(self):
        """Handle combat state updates."""
        # Initialize enemies if needed
        if not hasattr(self, 'enemies') or len(self.enemies) == 0:
            self.setup_combat()
            
        self.update_player_combat()
        
        # Check if all enemies are defeated
        if len(self.enemies) == 0:
            self.level_manager.enemies_defeated = True
            self.level_manager.game_state = GameState.TRANSITION
    
    def update_transition(self):
        """Handle transition between levels."""
        if self.level_manager.next_level():
            if self.level_manager.is_game_complete():
                self.draw_large_text(100, pyxel.height//2 - 20, "Congratulations!", 7, scale=4)
                self.draw_large_text(100, pyxel.height//2 + 20, "You've escaped the dungeon!", 7, scale=4)
                pyxel.quit()
            else:
                # Show level transition message
                self.draw_large_text(200, pyxel.height//2, f"Level {self.level_manager.current_level}", 7, scale=4)
    
    def update_player_combat(self):
        # Check for player death
        if self.player_health <= 0:
            self.draw_large_text(180, pyxel.height//2, "Game Over! You died!", 8, scale=4)
            pyxel.quit()
            return
            
        # Weapon switching
        if pyxel.btnp(pyxel.KEY_1):
            self.current_weapon = WeaponType.SWORD
        elif pyxel.btnp(pyxel.KEY_2):
            self.current_weapon = WeaponType.BOW
        elif pyxel.btnp(pyxel.KEY_3):
            self.current_weapon = WeaponType.STAFF
        
        # Store previous position for collision detection
        prev_x = self.player_x
        prev_y = self.player_y
        
        # Player movement and direction (no diagonal movement)
        moved_horizontal = False
        moved_vertical = False
        
        if pyxel.btn(pyxel.KEY_LEFT):
            self.player_x = max(0, self.player_x - self.player_speed)
            self.player_direction = 3
            moved_horizontal = True
        elif pyxel.btn(pyxel.KEY_RIGHT):
            self.player_x = min(pyxel.width - self.player_size, self.player_x + self.player_speed)
            self.player_direction = 1
            moved_horizontal = True
            
        if not moved_horizontal:  # Only allow vertical movement if not moving horizontally
            if pyxel.btn(pyxel.KEY_UP):
                self.player_y = max(0, self.player_y - self.player_speed)
                self.player_direction = 0
            elif pyxel.btn(pyxel.KEY_DOWN):
                self.player_y = min(pyxel.height - self.player_size, self.player_y + self.player_speed)
                self.player_direction = 2
            
        # Check for ladder collision when all enemies are defeated
        if len(self.enemies) == 0:
            ladder_size = 16
            if (abs(self.player_x - self.level_manager.level_data.ladder_x) < ladder_size and
                abs(self.player_y - self.level_manager.level_data.ladder_y) < ladder_size):
                self.level_manager.enemies_defeated = True
                self.level_manager.game_state = GameState.TRANSITION
        
        # Attack control
        weapon_data = self.weapons[self.current_weapon]
        if pyxel.btnp(pyxel.KEY_SPACE) and not self.attacking and self.attack_cooldown == 0:
            self.attacking = True
            self.attack_frame = weapon_data["duration"]
=======
            # Update cursor position with WASD
            if pyxel.btnp(pyxel.KEY_W):
                self.game.cursor.move(0, -1, self.GRID_SIZE)
            elif pyxel.btnp(pyxel.KEY_S):
                self.game.cursor.move(0, 1, self.GRID_SIZE)
            elif pyxel.btnp(pyxel.KEY_A):
                self.game.cursor.move(-1, 0, self.GRID_SIZE)
            elif pyxel.btnp(pyxel.KEY_D):
                self.game.cursor.move(1, 0, self.GRID_SIZE)
>>>>>>> arun_branch
            
            # Place block with F key at cursor position
            if pyxel.btnp(pyxel.KEY_F):
                self.game.try_place_block()
                
            # Destroy block with E key at cursor position
            if pyxel.btnp(pyxel.KEY_E):
                self.game.try_destroy_block()
            
<<<<<<< HEAD
            # Check for collision with player if not invincible
            if not hasattr(self, 'invincible_timer') or self.invincible_timer <= 0:
                if self.check_collision(self.player_x, self.player_y, 
                                      enemy.x, enemy.y, self.player_size):
                    # Calculate knockback direction
                    dx = self.player_x - enemy.x
                    dy = self.player_y - enemy.y
                    distance = math.sqrt(dx * dx + dy * dy)
                    
                    if distance > 0:
                        # Apply strong knockback
                        knockback = 20
                        dx = (dx / distance) * knockback
                        dy = (dy / distance) * knockback
                        
                        # Apply knockback to player
                        self.player_x = max(0, min(pyxel.width - self.player_size, self.player_x + dx))
                        self.player_y = max(0, min(pyxel.height - self.player_size, self.player_y + dy))
                        
                        # Push enemy back slightly
                        enemy.x = max(0, min(pyxel.width - enemy.size, enemy.x - dx * 0.3))
                        enemy.y = max(0, min(pyxel.height - enemy.size, enemy.y - dy * 0.3))
                    
                    # Reduce player health and add invincibility frames
                    self.player_health = max(0, self.player_health - 5)  # More damage but less frequent
                    self.invincible_timer = 45  # 0.75 seconds of invincibility
=======
            # Update player movement
            self.game.update_player_movement()
>>>>>>> arun_branch
            
            # Check win/lose conditions
            self.game.check_game_over()
            self.game.check_level_complete()
            
        elif self.game.state == GameState.LEVEL_COMPLETE:
            if pyxel.btnp(pyxel.KEY_RETURN):
                self.game.current_level += 1  # Increase difficulty
                self.init_level()
                self.game.state = GameState.PLAYING
                
        elif self.game.state == GameState.GAME_OVER:
            if pyxel.btnp(pyxel.KEY_R):
                self.game.reset_game()
                self.init_level()
                
        elif self.game.state == GameState.BLOCKCIDE:
            if pyxel.btnp(pyxel.KEY_R):
                self.game.reset_game()
                self.init_level()
    
    def draw(self):
        """Draw the game."""
        pyxel.cls(self.COLORS['bg'])
        
<<<<<<< HEAD
        # Draw based on game state
        if self.level_manager.game_state == GameState.COMBAT:
            self.draw_combat()
        
        # Draw any active messages
        self.ui_manager.draw_message()
    

    
    def draw_large_text(self, x, y, text, color, shadow=True, scale=2):
        """Draw scaled up text with optional shadow."""
        if shadow:
            # Draw shadow slightly offset
            for dy in range(scale):
                for dx in range(scale):
                    pyxel.text(x + dx + scale, y + dy + scale, text, 0)
        # Draw main text
        for dy in range(scale):
            for dx in range(scale):
                pyxel.text(x + dx, y + dy, text, color)

    def draw_combat(self):
        """Draw the combat interface."""
        # Draw the level tilemap
        level = self.level_manager.level_data
        colors = level.get_colors()
        
        # Draw the level
        self.level_manager.level_data.draw_level()
        
        # Draw ladder to next level if all enemies are defeated
        if len(self.enemies) == 0:
            ladder_x = self.level_manager.level_data.ladder_x
            ladder_y = self.level_manager.level_data.ladder_y
            # Draw larger ladder
            # Vertical poles
            pyxel.rect(ladder_x, ladder_y, 6, 40, 4)
            pyxel.rect(ladder_x + 34, ladder_y, 6, 40, 4)
            # Horizontal rungs
            for i in range(5):
                pyxel.rect(ladder_x, ladder_y + i*8, 40, 4, 4)
            # Draw exit text above ladder
            exit_text = "EXIT!"
            self.draw_large_text(ladder_x + 5, ladder_y - 30, exit_text, 7, scale=3)
=======
        # Draw grid and visited cells
        for y in range(self.GRID_SIZE):
            for x in range(self.GRID_SIZE):
                if self.game.grid[y][x]:
                    self.draw_cell(x, y, self.COLORS['path'])
        
        # Draw walls
        for wall in self.game.walls:
            self.draw_cell(wall[0], wall[1], self.COLORS['wall'])
        
        # Draw player-placed blocks
        for block in self.game.player_placed_blocks:
            self.draw_cell(block[0], block[1], self.COLORS['placed_block'])
        
        # Draw coins
        for coin in self.game.coin_positions:
            self.draw_coin(coin[0], coin[1])
        
        # Draw goal (top-right corner)
        self.draw_cell(self.GRID_SIZE - 1, 0, self.COLORS['exit'])
        
        # Draw player
        self.draw_player(self.game.player.x, self.game.player.y)
>>>>>>> arun_branch
        
        # Draw cursor with highlight effect
        cursor_x = self.game.cursor.x
        cursor_y = self.game.cursor.y
        pos = [cursor_x, cursor_y]
        
        # Draw lighter version of whatever is under the cursor
        if pos in self.game.walls or pos in self.game.player_placed_blocks:
            color = self.COLORS['highlight']  # Lighter color for destroyable objects
        elif pos == [self.GRID_SIZE - 1, 0]:  # Top-right corner
            color = self.COLORS['highlight']  # Lighter green for goal
        else:
            color = self.COLORS['cursor']  # Default cursor color
            
        self.draw_cell(cursor_x, cursor_y, color)
        
<<<<<<< HEAD
        # Draw player with damage flash (red)
        if hasattr(self, 'invincible_timer') and self.invincible_timer > 0:
            if self.invincible_timer % 4 < 2:  # Flash red
                pyxel.pal(7, 8)
        
        # Draw player sprite based on direction
        if self.player_direction == 1:  # Facing right
            pyxel.blt(self.player_x, self.player_y, 0, 0, 0, self.player_size, self.player_size, 0)
        else:  # Facing left
            pyxel.blt(self.player_x, self.player_y, 0, 0, 0, -self.player_size, self.player_size, 0)
        
        pyxel.pal()  # Reset palette
        
        # Draw attack effect if attacking
        if self.attacking:
            attack_x = self.player_x + (self.player_size if self.player_direction == 1 else -self.player_size)
            # Draw weapon sprite based on type
            if self.current_weapon == WeaponType.SWORD:
                pyxel.blt(attack_x, self.player_y, 0, 16, 0, 8, 8, 0)
            elif self.current_weapon == WeaponType.BOW:
                pyxel.blt(attack_x, self.player_y, 0, 24, 0, 8, 8, 0)
            elif self.current_weapon == WeaponType.STAFF:
                pyxel.blt(attack_x, self.player_y, 0, 32, 0, 8, 8, 0)
        
        # Draw UI background
        pyxel.rect(10, 10, 300, 80, 1)
        pyxel.rectb(10, 10, 300, 80, 7)
        
        # Draw health bar
        bar_x, bar_y = 20, 20
        bar_width = 280
        bar_height = 20
        
        # Health bar background (dark red)
        pyxel.rect(bar_x, bar_y, bar_width, bar_height, 1)
        
        # Health bar fill with color based on health
        health_width = int((bar_width * self.player_health) / 100)
        health_color = 11 if self.player_health > 60 else 9 if self.player_health > 30 else 8
        pyxel.rect(bar_x, bar_y, health_width, bar_height, health_color)
        
        # Health text
        health_text = f"HP: {self.player_health}"
        text_x = bar_x + (bar_width - len(health_text) * 4) // 2
        pyxel.text(text_x, bar_y + 7, health_text, 7)
        
        # Level text
        level_text = f"LEVEL {self.level_manager.current_level}"
        pyxel.text(20, 50, level_text, 7)
        
        # Weapon text
        weapon_names = {WeaponType.SWORD: "SWORD", WeaponType.BOW: "BOW", WeaponType.STAFF: "STAFF"}
        weapon_text = f"WEAPON: {weapon_names[self.current_weapon]}"
        pyxel.text(20, 65, weapon_text, 7)
=======
        # Draw UI
        self.draw_ui()
        
        # Draw coins and costs
        pyxel.text(4, 4, f"Coins: {self.game.coins}", self.COLORS['text'])
        next_place_cost = self.game.get_next_block_cost()
        next_destroy_cost = self.game.get_next_destroy_cost()
        pyxel.text(4, 12, f"Place Cost: {next_place_cost}", self.COLORS['text'])
        pyxel.text(4, 20, f"Destroy Cost: {next_destroy_cost}", self.COLORS['text'])
        pyxel.text(4, 28, f"Level: {self.game.current_level}", self.COLORS['text'])
        pyxel.text(4, 36, f"Levels Beaten: {self.game.levels_beaten}", self.COLORS['text'])
        
        # Draw instructions
        pyxel.text(4, pyxel.height - 40, "Arrow keys to move", self.COLORS['text'])
        pyxel.text(4, pyxel.height - 32, "WASD to move cursor", self.COLORS['text'])
        pyxel.text(4, pyxel.height - 24, "F to place block", self.COLORS['text'])
        pyxel.text(4, pyxel.height - 16, "E to remove wall/block", self.COLORS['text'])
        pyxel.text(4, pyxel.height - 8, "R to forfeit game", self.COLORS['text'])
        
        # Draw game over screen
        if self.game.state == GameState.GAME_OVER:
            self.draw_centered_text("Game Over!", pyxel.height // 2)
            self.draw_centered_text("Press R to restart", pyxel.height // 2 + 10)
            self.draw_centered_text(f"Levels Beaten: {self.game.levels_beaten}", pyxel.height // 2 + 20)
        
        # Draw level complete screen
        elif self.game.state == GameState.LEVEL_COMPLETE:
            self.draw_centered_text("Level Complete!", pyxel.height // 2)
            self.draw_centered_text("Press ENTER for next level", pyxel.height // 2 + 10)
        
        # Draw blockcide screen
        elif self.game.state == GameState.BLOCKCIDE:
            self.draw_centered_text("You commit blockcide and die.", pyxel.height // 2)
            self.draw_centered_text(f"Levels Beaten: {self.game.levels_beaten}", pyxel.height // 2 + 10)
            self.draw_centered_text("Press R to restart", pyxel.height // 2 + 20)
    
    def draw_cell(self, x, y, color):
        """Draw a single cell."""
        pyxel.rect(
            x * self.CELL_SIZE,
            y * self.CELL_SIZE,
            self.CELL_SIZE - 1,
            self.CELL_SIZE - 1,
            color
        )
    
    def draw_coin(self, x, y):
        """Draw a coin."""
        center_x = x * self.CELL_SIZE + self.CELL_SIZE // 2
        center_y = y * self.CELL_SIZE + self.CELL_SIZE // 2
        radius = self.CELL_SIZE // 4
        pyxel.circ(center_x, center_y, radius, self.COLORS['coin'])
    
    def draw_player(self, x, y):
        """Draw the player."""
        center_x = x * self.CELL_SIZE + self.CELL_SIZE // 2
        center_y = y * self.CELL_SIZE + self.CELL_SIZE // 2
        radius = self.CELL_SIZE // 3
        pyxel.circ(center_x, center_y, radius, self.COLORS['player'])
    
    def draw_ui(self):
        """Draw game UI."""
        # Score and level
        pyxel.text(4, 20, f"Level: {self.game.current_level}", 7)
    
    def draw_centered_text(self, text, y):
        """Draw text centered on screen."""
        x = (pyxel.width - len(text) * 4) // 2
        pyxel.text(x, y, text, self.COLORS['text'])
        
    def reset_game(self):
        """Reset the game state without reinitializing Pyxel."""
        self.game = Game()
        self.init_level()
        self.game.state = GameState.PLAYING
>>>>>>> arun_branch

if __name__ == '__main__':
    MazeGame()
