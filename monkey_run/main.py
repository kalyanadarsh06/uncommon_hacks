import pyxel
import random

class MonkeyRun:
    def __init__(self):
        # Initialize game window
        pyxel.init(160, 120, title="Monkey Run")
        
        # Game states
        self.GAME_RUNNING = 0
        self.GAME_OVER = 1
        
        # Initialize game state
        self.reset_game()
        
        # Start the game
        pyxel.run(self.update, self.draw)
    
    def reset_game(self):
        # Game state
        self.state = self.GAME_RUNNING
        
        # Player properties
        self.lanes = [30, 60, 90, 120]  # 4 lanes for movement
        self.current_lane = 1  # Start in second lane
        self.player_x = self.lanes[self.current_lane]
        self.player_y = 100  # Fixed vertical position
        
        # Game properties
        self.score = 0
        self.coconuts_hit = 0
        self.speed = 2  # Initial game speed
        self.max_speed = 5
        self.speed_increment = 0.001
        
        # Objects
        self.bananas = []  # [x, y]
        self.coconuts = []  # [x, y]
        self.banana_peels = []  # [x, y]
        self.trees = []  # [x, y]
        
        # Spawn timers
        self.banana_timer = 0
        self.coconut_timer = 0
        self.peel_timer = 0
        self.tree_timer = 0
    
    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
            
        if self.state == self.GAME_OVER:
            if pyxel.btnp(pyxel.KEY_R):
                self.reset_game()
            return
            
        # Player movement
        if pyxel.btnp(pyxel.KEY_LEFT) and self.current_lane > 0:
            self.current_lane -= 1
        if pyxel.btnp(pyxel.KEY_RIGHT) and self.current_lane < 3:
            self.current_lane += 1
            
        # Update player position smoothly
        self.player_x += (self.lanes[self.current_lane] - self.player_x) * 0.2
        
        # Increase speed over time
        self.speed = min(self.speed + self.speed_increment, self.max_speed)
        
        # Spawn objects
        self._spawn_objects()
        
        # Update object positions and check collisions
        self._update_objects()
        
        # Check game over conditions
        if self.coconuts_hit >= 3:
            self.state = self.GAME_OVER
    
    def _spawn_objects(self):
        # Spawn bananas
        if self.banana_timer <= 0 and random.random() < 0.03:
            lane = random.randint(0, 3)
            self.bananas.append([self.lanes[lane], -10])
            self.banana_timer = 30
        self.banana_timer = max(0, self.banana_timer - 1)
        
        # Spawn coconuts
        if self.coconut_timer <= 0 and random.random() < 0.02:
            lane = random.randint(0, 3)
            self.coconuts.append([self.lanes[lane], -10])
            self.coconut_timer = 45
        self.coconut_timer = max(0, self.coconut_timer - 1)
        
        # Spawn banana peels
        if self.peel_timer <= 0 and random.random() < 0.01:
            lane = random.randint(0, 3)
            self.banana_peels.append([self.lanes[lane], -10])
            self.peel_timer = 60
        self.peel_timer = max(0, self.peel_timer - 1)
        
        # Spawn trees
        if self.tree_timer <= 0 and random.random() < 0.01:
            lane = random.randint(0, 3)
            self.trees.append([self.lanes[lane], -20])
            self.tree_timer = 90
        self.tree_timer = max(0, self.tree_timer - 1)
    
    def _update_objects(self):
        # Update bananas
        for banana in self.bananas[:]:
            banana[1] += self.speed
            # Check collision
            if abs(banana[0] - self.player_x) < 8 and abs(banana[1] - self.player_y) < 8:
                self.score += 10
                self.bananas.remove(banana)
            elif banana[1] > 130:
                self.bananas.remove(banana)
                
        # Update coconuts
        for coconut in self.coconuts[:]:
            coconut[1] += self.speed
            # Check collision
            if abs(coconut[0] - self.player_x) < 8 and abs(coconut[1] - self.player_y) < 8:
                self.coconuts_hit += 1
                self.score = max(0, self.score - 5)
                self.coconuts.remove(coconut)
            elif coconut[1] > 130:
                self.coconuts.remove(coconut)
                
        # Update banana peels
        for peel in self.banana_peels[:]:
            peel[1] += self.speed
            # Check collision
            if abs(peel[0] - self.player_x) < 8 and abs(peel[1] - self.player_y) < 8:
                self.score = max(0, self.score - 3)
                self.banana_peels.remove(peel)
            elif peel[1] > 130:
                self.banana_peels.remove(peel)
                
        # Update trees
        for tree in self.trees[:]:
            tree[1] += self.speed
            # Check collision
            if abs(tree[0] - self.player_x) < 8 and abs(tree[1] - self.player_y) < 8:
                self.state = self.GAME_OVER
            elif tree[1] > 130:
                self.trees.remove(tree)
    
    def draw(self):
        pyxel.cls(11)  # Light blue background
        
        if self.state == self.GAME_RUNNING:
            # Draw lanes
            for lane in self.lanes:
                pyxel.line(lane, 0, lane, 120, 13)
            
            # Draw player (monkey)
            pyxel.rect(self.player_x - 4, self.player_y - 4, 8, 8, 14)  # Brown
            
            # Draw bananas
            for banana in self.bananas:
                pyxel.circ(banana[0], banana[1], 2, 10)  # Yellow
                
            # Draw coconuts
            for coconut in self.coconuts:
                pyxel.circ(coconut[0], coconut[1], 3, 5)  # Dark brown
                
            # Draw banana peels
            for peel in self.banana_peels:
                pyxel.rect(peel[0] - 2, peel[1] - 1, 4, 2, 10)  # Yellow
                
            # Draw trees
            for tree in self.trees:
                pyxel.rect(tree[0] - 3, tree[1] - 8, 6, 16, 3)  # Green
            
            # Draw score and coconuts hit
            pyxel.text(4, 4, f"SCORE: {self.score}", 0)
            pyxel.text(4, 12, f"COCONUTS: {self.coconuts_hit}/3", 0)
            
        else:  # Game Over screen
            pyxel.text(60, 50, "GAME OVER", 8)
            pyxel.text(45, 60, f"FINAL SCORE: {self.score}", 8)
            pyxel.text(40, 70, "PRESS R TO RESTART", 8)
            pyxel.text(45, 80, "PRESS Q TO QUIT", 8)

MonkeyRun()
