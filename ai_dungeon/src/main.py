import pyxel
import random
import math
import json
import os
from enum import Enum
from puzzle_generator import PuzzleGenerator
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
    def __init__(self, x, y, speed=1):
        self.x = x
        self.y = y
        self.speed = speed
        self.size = 8
        self.health = 100
        self.move_timer = 0
        self.direction = random.randint(0, 3)  # 0: up, 1: right, 2: down, 3: left
        self.hit_flash = 0  # Timer for hit animation

    def take_damage(self, amount):
        self.health -= amount
        self.hit_flash = 10  # Flash for 10 frames when hit

    def update(self, player_x, player_y):
        if self.hit_flash > 0:
            self.hit_flash -= 1

        # Change direction every 30 frames
        self.move_timer += 1
        if self.move_timer >= 30:
            self.direction = random.randint(0, 3)
            self.move_timer = 0

        # Move based on current direction
        if self.direction == 0:  # up
            self.y = max(0, self.y - self.speed)
        elif self.direction == 1:  # right
            self.x = min(pyxel.width - self.size, self.x + self.speed)
        elif self.direction == 2:  # down
            self.y = min(pyxel.height - self.size, self.y + self.speed)
        else:  # left
            self.x = max(0, self.x - self.speed)

    def draw(self):
        # Draw goblin with flash effect
        if self.hit_flash > 0 and self.hit_flash % 2 == 0:
            # Flash white
            pyxel.rect(self.x, self.y, self.size, self.size, 7)
        else:
            # Draw normal goblin
            Game.create_goblin(Game, self.x, self.y)
        # Draw health bar
        health_width = (self.size * self.health) // 100
        pyxel.rect(self.x, self.y - 2, health_width, 1, 11)

class Game:
    def create_explorer(self, x, y):
        # Brown hat (color 4)
        pyxel.rect(x+2, y, 4, 1, 4)
        pyxel.rect(x+1, y+1, 6, 1, 4)
        
        # Face (color 15 - peach)
        pyxel.rect(x+2, y+2, 4, 2, 15)
        
        # Eyes (color 0 - black)
        pyxel.pset(x+2, y+2, 0)
        pyxel.pset(x+5, y+2, 0)
        
        # Body (color 6 - light grey for shirt)
        pyxel.rect(x+2, y+4, 4, 3, 6)
        
        # Arms (color 15 - peach)
        pyxel.rect(x+1, y+4, 1, 2, 15)
        pyxel.rect(x+6, y+4, 1, 2, 15)
        
        # Legs (color 4 - brown pants)
        pyxel.rect(x+2, y+7, 2, 1, 4)
        pyxel.rect(x+4, y+7, 2, 1, 4)

    def create_goblin(self, x, y):
        # Head (color 11 - green)
        pyxel.rect(x+2, y+1, 4, 3, 11)
        
        # Eyes (color 8 - red)
        pyxel.pset(x+2, y+2, 8)
        pyxel.pset(x+5, y+2, 8)
        
        # Ears (color 11 - green)
        pyxel.rect(x+1, y+2, 1, 2, 11)
        pyxel.rect(x+6, y+2, 1, 2, 11)
        
        # Body (color 11 - green)
        pyxel.rect(x+2, y+4, 4, 3, 11)
        
        # Arms (color 11 - green)
        pyxel.rect(x+1, y+4, 1, 2, 11)
        pyxel.rect(x+6, y+4, 1, 2, 11)
        
        # Legs (color 11 - green)
        pyxel.rect(x+2, y+7, 2, 1, 11)
        pyxel.rect(x+4, y+7, 2, 1, 11)

    def create_weapon_effect(self, x, y, weapon_type):
        if weapon_type == WeaponType.SWORD:
            # Blade (color 7 - white)
            pyxel.rect(x+3, y+1, 2, 6, 7)
            # Handle (color 4 - brown)
            pyxel.rect(x+2, y+6, 4, 2, 4)
        elif weapon_type == WeaponType.BOW:
            # Arrow
            pyxel.tri(x+6, y+3, x+4, y+2, x+4, y+4, 7)  # Arrow head
            pyxel.rect(x+1, y+3, 4, 1, 4)  # Arrow shaft
        elif weapon_type == WeaponType.STAFF:
            # Magic orb
            pyxel.circb(x+3, y+3, 3, 12)
            pyxel.circb(x+3, y+3, 2, 12)
            pyxel.circ(x+3, y+3, 1, 7)

    def __init__(self):
        # Initialize game
        pyxel.init(240, 180, title="AI Dungeon Master")
        
        # Initialize managers
        self.level_manager = LevelManager()
        self.puzzle_generator = PuzzleGenerator()
        self.ui_manager = UIManager()
        
        # Player attributes
        self.reset_player()
        
        # Game state
        self.current_puzzle = None
        self.puzzle_input = ""
        
        # Start the game
        pyxel.run(self.update, self.draw)
    
    def reset_player(self):
        """Reset player to starting position with initial attributes."""
        self.player_x = 120
        self.player_y = 90
        self.player_speed = 2
        self.player_size = 8
        self.player_health = 100
        self.player_direction = 1
        
        # Weapon system
        self.current_weapon = WeaponType.SWORD
        self.weapons = {
            WeaponType.SWORD: {"damage": 25, "cooldown": 20, "duration": 10},
            WeaponType.BOW: {"damage": 15, "cooldown": 30, "duration": 5},
            WeaponType.STAFF: {"damage": 20, "cooldown": 40, "duration": 15}
        }
        self.attacking = False
        self.attack_frame = 0
        self.attack_cooldown = 0
        
        # Clear lists
        self.projectiles = []
        self.enemies = []
    
    def check_collision(self, x1, y1, x2, y2, size):
        return (abs(x1 - x2) < size and abs(y1 - y2) < size)
    
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

    def update(self):
        # Exit if Q is pressed
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
            
        # Update UI
        self.ui_manager.update()
        
        # Handle different game states
        if self.level_manager.game_state == GameState.PUZZLE:
            self.update_puzzle()
        elif self.level_manager.game_state == GameState.COMBAT:
            self.update_combat()
        elif self.level_manager.game_state == GameState.TRANSITION:
            self.update_transition()
    
    def update_puzzle(self):
        """Handle puzzle state updates."""
        # Generate new puzzle if needed
        if not self.current_puzzle:
            puzzle_json = self.puzzle_generator.generate_puzzle(self.level_manager.current_level)
            self.current_puzzle = json.loads(puzzle_json)
            self.puzzle_input = ""
        
        # Handle puzzle input
        # Check for number inputs (both number row and numpad)
        number_keys = {
            pyxel.KEY_0: '0', pyxel.KEY_1: '1', pyxel.KEY_2: '2', pyxel.KEY_3: '3', pyxel.KEY_4: '4',
            pyxel.KEY_5: '5', pyxel.KEY_6: '6', pyxel.KEY_7: '7', pyxel.KEY_8: '8', pyxel.KEY_9: '9',
            pyxel.KEY_KP_0: '0', pyxel.KEY_KP_1: '1', pyxel.KEY_KP_2: '2', pyxel.KEY_KP_3: '3',
            pyxel.KEY_KP_4: '4', pyxel.KEY_KP_5: '5', pyxel.KEY_KP_6: '6', pyxel.KEY_KP_7: '7',
            pyxel.KEY_KP_8: '8', pyxel.KEY_KP_9: '9'
        }
        
        for key, value in number_keys.items():
            if pyxel.btnp(key):
                self.puzzle_input += value
        
        # Handle letters (A-Z)
        letter_keys = {
            pyxel.KEY_A: 'A', pyxel.KEY_B: 'B', pyxel.KEY_C: 'C', pyxel.KEY_D: 'D',
            pyxel.KEY_E: 'E', pyxel.KEY_F: 'F', pyxel.KEY_G: 'G', pyxel.KEY_H: 'H',
            pyxel.KEY_I: 'I', pyxel.KEY_J: 'J', pyxel.KEY_K: 'K', pyxel.KEY_L: 'L',
            pyxel.KEY_M: 'M', pyxel.KEY_N: 'N', pyxel.KEY_O: 'O', pyxel.KEY_P: 'P',
            pyxel.KEY_Q: 'Q', pyxel.KEY_R: 'R', pyxel.KEY_S: 'S', pyxel.KEY_T: 'T',
            pyxel.KEY_U: 'U', pyxel.KEY_V: 'V', pyxel.KEY_W: 'W', pyxel.KEY_X: 'X',
            pyxel.KEY_Y: 'Y', pyxel.KEY_Z: 'Z'
        }
        
        for key, value in letter_keys.items():
            if pyxel.btnp(key):
                self.puzzle_input += value
        
        # Backspace
        if pyxel.btnp(pyxel.KEY_BACKSPACE):
            self.puzzle_input = self.puzzle_input[:-1]
        
        # Handle space
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.puzzle_input += " "
        
        # Submit answer
        if pyxel.btnp(pyxel.KEY_RETURN):
            # Compare answers case-insensitively and ignore extra whitespace
            player_answer = self.puzzle_input.strip().lower()
            correct_answer = self.current_puzzle["solution"].strip().lower()
            if player_answer == correct_answer:
                self.ui_manager.show_message("Puzzle Solved!", 60)
                self.level_manager.puzzle_solved = True
                self.level_manager.game_state = GameState.COMBAT
                self.setup_combat()
            else:
                self.ui_manager.show_message(f"Incorrect. Your answer: {self.puzzle_input}", 60)
        
        # Show hint
        if pyxel.btnp(pyxel.KEY_H):
            self.ui_manager.show_hints = True
            self.ui_manager.current_hint = (self.ui_manager.current_hint + 1) % len(self.current_puzzle["hints"])
    
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
    
    def update_combat(self):
        """Handle combat state updates."""
        self.update_player_combat()
        
        # Check if all enemies are defeated
        if len(self.enemies) == 0:
            self.level_manager.enemies_defeated = True
            self.level_manager.game_state = GameState.TRANSITION
    
    def update_transition(self):
        """Handle transition between levels."""
        if self.level_manager.next_level():
            if self.level_manager.is_game_complete():
                self.ui_manager.show_message("Congratulations! You've escaped the dungeon!", 120)
                pyxel.quit()
            else:
                # Reset puzzle state
                self.current_puzzle = None
                self.puzzle_input = ""
                self.ui_manager.show_hints = False
                self.ui_manager.current_hint = 0
                # Show level transition message
                self.ui_manager.show_message(f"Level {self.level_manager.current_level}", 60)
    
    def update_player_combat(self):
        
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
        
        # Player movement and direction
        if pyxel.btn(pyxel.KEY_LEFT):
            self.player_x = max(0, self.player_x - self.player_speed)
            self.player_direction = 3
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.player_x = min(pyxel.width - self.player_size, self.player_x + self.player_speed)
            self.player_direction = 1
        if pyxel.btn(pyxel.KEY_UP):
            self.player_y = max(0, self.player_y - self.player_speed)
            self.player_direction = 0
        if pyxel.btn(pyxel.KEY_DOWN):
            self.player_y = min(pyxel.height - self.player_size, self.player_y + self.player_speed)
            self.player_direction = 2
        
        # Attack control
        weapon_data = self.weapons[self.current_weapon]
        if pyxel.btnp(pyxel.KEY_SPACE) and not self.attacking and self.attack_cooldown == 0:
            self.attacking = True
            self.attack_frame = weapon_data["duration"]
            
            # Create projectiles for ranged weapons
            if self.current_weapon in [WeaponType.BOW, WeaponType.STAFF]:
                proj = self.create_projectile()
                if isinstance(proj, list):
                    self.projectiles.extend(proj)
                elif proj:
                    self.projectiles.append(proj)
        
        # Update attack
        if self.attacking:
            self.attack_frame -= 1
            if self.attack_frame <= 0:
                self.attacking = False
                self.attack_cooldown = weapon_data["cooldown"]
        
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        # Update projectiles
        self.projectiles = [p for p in self.projectiles if p.active]
        for projectile in self.projectiles:
            projectile.update()
        
        # Update enemies and check for dead enemies
        enemies_to_remove = []
        for enemy in self.enemies:
            enemy.update(self.player_x, self.player_y)
            
            # Check for collision with player
            if self.check_collision(self.player_x, self.player_y, 
                                  enemy.x, enemy.y, self.player_size):
                # Move player back to previous position
                self.player_x = prev_x
                self.player_y = prev_y
                # Reduce player health (once per frame)
                self.player_health = max(0, self.player_health - 1)
            
            # Check for sword attack hit
            if self.current_weapon == WeaponType.SWORD:
                if self.attacking and self.attack_frame == weapon_data["duration"] - 1:
                    if self.check_attack_hit(enemy):
                        enemy.take_damage(weapon_data["damage"])
            
            # Check for projectile hits
            for projectile in self.projectiles:
                if (abs(projectile.x - enemy.x) < enemy.size and
                    abs(projectile.y - enemy.y) < enemy.size):
                    enemy.take_damage(projectile.damage)
                    projectile.active = False
            
            # Check if enemy is dead
            if enemy.health <= 0:
                enemies_to_remove.append(enemy)
        
        # Remove dead enemies
        for enemy in enemies_to_remove:
            self.enemies.remove(enemy)
    
    def draw(self):
        pyxel.cls(0)
        
        # Draw based on game state
        if self.level_manager.game_state == GameState.PUZZLE:
            self.draw_puzzle()
        elif self.level_manager.game_state == GameState.COMBAT:
            self.draw_combat()
        
        # Draw any active messages
        self.ui_manager.draw_message()
    
    def draw_puzzle(self):
        """Draw the puzzle interface."""
        if self.current_puzzle:
            self.ui_manager.show_puzzle(self.current_puzzle)
    
    def draw_combat(self):
        """Draw the combat interface."""
        # Get level colors
        colors = self.level_manager.level_data.get_colors()
        
        # Draw background (simple for now, can be enhanced with tiles)
        pyxel.rect(0, 0, pyxel.width, pyxel.height, colors["floor"])
        
        # Draw player
        self.create_explorer(self.player_x, self.player_y)
        
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw()
        
        # Draw projectiles
        for proj in self.projectiles:
            if proj.active:
                proj.draw()
        
        # Draw weapon effect during attack
        if self.attacking:
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
            self.create_weapon_effect(attack_x, attack_y, self.current_weapon)
        
        # Draw UI elements
        self.ui_manager.show_combat(self.player_health, self.level_manager.current_level)

if __name__ == '__main__':
    Game()
