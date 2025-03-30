import pyxel
import random
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ObstacleGenerator:
    def __init__(self):
        # Configure Gemini API
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env file")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('models/gemini-1.5-pro')

    def generate_obstacles(self, score, current_speed):
        """Generate obstacles using Gemini API based on current game state"""
        prompt = f"""
        Generate obstacles for a monkey runner game. Return only a JSON array of objects.
        Current score: {score}
        Current speed: {speed}
        
        Each object should have:
        - "type": one of ["banana", "coconut", "peel", "tree"]
        - "lane": number from 0-3 (representing 4 lanes)
        - "spacing": number of frames to wait before next obstacle
        
        Rules:
        1. Make it harder as score/speed increases
        2. Ensure patterns are challenging but fair
        3. Include more rewards (bananas) when score is low
        4. Add more hazards (coconuts/trees) at higher scores
        5. Return 5-10 obstacles
        
        Example format:
        [
            {{"type": "banana", "lane": 2, "spacing": 30}},
            {{"type": "coconut", "lane": 1, "spacing": 45}}
        ]
        """

        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            # Extract and validate JSON
            import re
            import json
            json_match = re.search(r'\[.*\]', text, re.DOTALL)
            if json_match:
                obstacles = json.loads(json_match.group(0))
                return obstacles
        except Exception as e:
            print(f"Error generating obstacles: {e}")
        
        # Fallback: return some basic obstacles
        return [
            {"type": "banana", "lane": random.randint(0, 3), "spacing": 30},
            {"type": "coconut", "lane": random.randint(0, 3), "spacing": 45}
        ]

class MonkeyRun:
    def __init__(self):
        # Initialize game window
        pyxel.init(160, 120, title="Monkey Run")
        
        # Initialize obstacle generator
        self.obstacle_gen = ObstacleGenerator()
        
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
        self.obstacles = []  # List of active obstacles
        self.obstacle_queue = []  # Queue of upcoming obstacles
        
        # Generate initial obstacles
        self._generate_new_obstacles()
    
    def _generate_new_obstacles(self):
        """Get new obstacles from Gemini when queue is low"""
        if len(self.obstacle_queue) < 5:
            new_obstacles = self.obstacle_gen.generate_obstacles(self.score, self.speed)
            self.obstacle_queue.extend(new_obstacles)
    
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
        
        # Update and spawn obstacles
        self._update_obstacles()
        
        # Generate new obstacles if needed
        self._generate_new_obstacles()
        
        # Check game over conditions
        if self.coconuts_hit >= 3:
            self.state = self.GAME_OVER
    
    def _update_obstacles(self):
        # Spawn new obstacles from queue
        if self.obstacle_queue and len(self.obstacles) < 10:
            next_obstacle = self.obstacle_queue[0]
            self.obstacles.append({
                "type": next_obstacle["type"],
                "x": self.lanes[next_obstacle["lane"]],
                "y": -10,
                "spacing": next_obstacle["spacing"]
            })
            self.obstacle_queue.pop(0)
        
        # Update existing obstacles
        for obstacle in self.obstacles[:]:
            obstacle["y"] += self.speed
            
            # Check collisions
            if abs(obstacle["x"] - self.player_x) < 8 and abs(obstacle["y"] - self.player_y) < 8:
                if obstacle["type"] == "banana":
                    self.score += 10
                    self.obstacles.remove(obstacle)
                elif obstacle["type"] == "coconut":
                    self.coconuts_hit += 1
                    self.score = max(0, self.score - 5)
                    self.obstacles.remove(obstacle)
                elif obstacle["type"] == "peel":
                    self.score = max(0, self.score - 3)
                    self.obstacles.remove(obstacle)
                elif obstacle["type"] == "tree":
                    self.state = self.GAME_OVER
            
            # Remove off-screen obstacles
            elif obstacle["y"] > 130:
                self.obstacles.remove(obstacle)
    
    def draw(self):
        pyxel.cls(11)  # Light blue background
        
        if self.state == self.GAME_RUNNING:
            # Draw lanes
            for lane in self.lanes:
                pyxel.line(lane, 0, lane, 120, 13)
            
            # Draw player (monkey)
            pyxel.rect(self.player_x - 4, self.player_y - 4, 8, 8, 14)  # Brown
            
            # Draw obstacles
            for obstacle in self.obstacles:
                if obstacle["type"] == "banana":
                    pyxel.circ(obstacle["x"], obstacle["y"], 2, 10)  # Yellow
                elif obstacle["type"] == "coconut":
                    pyxel.circ(obstacle["x"], obstacle["y"], 3, 5)  # Dark brown
                elif obstacle["type"] == "peel":
                    pyxel.rect(obstacle["x"] - 2, obstacle["y"] - 1, 4, 2, 10)  # Yellow
                elif obstacle["type"] == "tree":
                    pyxel.rect(obstacle["x"] - 3, obstacle["y"] - 8, 6, 16, 3)  # Green
            
            # Draw score and coconuts hit
            pyxel.text(4, 4, f"SCORE: {self.score}", 0)
            pyxel.text(4, 12, f"COCONUTS: {self.coconuts_hit}/3", 0)
            
        else:  # Game Over screen
            pyxel.text(60, 50, "GAME OVER", 8)
            pyxel.text(45, 60, f"FINAL SCORE: {self.score}", 8)
            pyxel.text(40, 70, "PRESS R TO RESTART", 8)
            pyxel.text(45, 80, "PRESS Q TO QUIT", 8)

if __name__ == "__main__":
    MonkeyRun()
