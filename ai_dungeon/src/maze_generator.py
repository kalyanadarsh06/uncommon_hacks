import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from collections import deque

class MazeGenerator:
    def __init__(self):
        # Configure Gemini API
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env file")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('models/gemini-1.5-pro')

    def generate_maze(self, level, size=10):
        """Generate a maze with walls, coins, and start/exit positions using Gemini."""
        # Calculate complexity factors based on level
        min_walls = (size * 2) + (level * 5)  # More walls at higher levels
        min_turns = 2 + level         # More required turns at higher levels
        path_length = size + (level * 2) # Longer minimum path at higher levels
        
        prompt = f"""
        Generate a {size}x{size} maze for level {level}. Return only a JSON object with this exact structure:
        {{
            "walls": [[x1,y1], [x2,y2], ...],  // List of wall coordinates
            "coins": [[x1,y1], [x2,y2], ...],  // List of coin coordinates
            "start": [0,{size-1}],            // Starting position (fixed at bottom-left)
            "exit": [{size-1},0],            // Exit position (fixed at top-right)
            "size": {size}                   // Maze size
        }}

        SPECIFIC REQUIREMENTS FOR LEVEL {level}:
        1. GUARANTEED PATH REQUIREMENT:
           - There MUST be a clear path from start [0,{size-1}] to exit [{size-1},0]
           - Do NOT block this path with walls
           - The path can be direct for level 1, more complex for higher levels

        2. WALL PLACEMENT:
           - Add {min_walls} wall blocks around the guaranteed path
           - Walls should create some challenge but not block the path
           - Higher levels can have more walls but must keep path clear

        3. COIN PLACEMENT:
           - Place {level + 3} coins along or near the guaranteed path
           - Some coins can be in side paths for extra challenge
           - Coins should be reachable without getting stuck

        CRITICAL RULES:
        - Start at [0,{size-1}] (bottom-left)
        - Exit at [{size-1},0] (top-right)
        - ENSURE the path from start to exit is clear
        - Make it feel like level {level} but keep it solvable
        """
        
        # Add a unique seed to prevent duplicate mazes
        prompt += f"\nUnique seed: {level * 1000 + hash(str(size)) % 1000}"

        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                response = self.model.generate_content(prompt)
                text = response.text.strip()
                
                # Extract and validate JSON
                import re
                json_match = re.search(r'\{.*\}', text, re.DOTALL)
                if not json_match:
                    continue
                    
                maze_data = json.loads(json_match.group(0))
                
                # Validate maze data
                if self._validate_maze(maze_data):
                    return maze_data
                    
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                
        # If all attempts fail, return a simple solvable maze
        return self._generate_fallback_maze(level, size)
    
    def _validate_maze(self, maze_data):
        """Validate maze data and ensure it's solvable."""
        try:
            # Check required keys
            required_keys = ['walls', 'coins', 'start', 'exit', 'size']
            if not all(key in maze_data for key in required_keys):
                return False

            size = maze_data['size']
            walls = maze_data['walls']
            start = maze_data['start']
            exit_pos = maze_data['exit']
            coins = maze_data['coins']

            # Validate coordinates
            if not all(0 <= x < size and 0 <= y < size for x, y in walls + [start] + [exit_pos] + coins):
                return False

            # Validate start and exit positions
            if start != [0, size-1] or exit_pos != [size-1, 0]:
                return False

            # Verify that walls don't block the entire path
            # We'll be more lenient with wall placement but ensure path exists
            border_points = set((x, y) for x, y in walls)
            
            # Check if there's a path from start to end
            if not self._has_valid_path(start, exit_pos, walls, size):
                return False
            
            # Ensure start and exit aren't blocked
            if (start[0], start[1]) in border_points or (exit_pos[0], exit_pos[1]) in border_points:
                return False

            # Check if path exists from start to exit
            if not self._has_valid_path(start, exit_pos, walls, size):
                return False

            return True

        except Exception:
            return False

    def _has_valid_path(self, start, end, walls, size):
        """Check if there's a valid path from start to end using BFS."""
        walls_set = {tuple(w) for w in walls}
        queue = deque([(start[0], start[1])])
        visited = {(start[0], start[1])}

        while queue:
            x, y = queue.popleft()
            if [x, y] == end:
                return True

            # Try all four directions
            for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
                new_x, new_y = x + dx, y + dy
                if (0 <= new_x < size and 0 <= new_y < size and 
                    (new_x, new_y) not in walls_set and 
                    (new_x, new_y) not in visited):
                    queue.append((new_x, new_y))
                    visited.add((new_x, new_y))

        return False

    def _generate_fallback_maze(self, level, size):
        """Generate a simple solvable maze as fallback."""
        walls = []
        coins = []
        
        # First, create a guaranteed path from start to exit
        path_points = set()
        x, y = 0, size-1  # Start position
        
        # Generate a simple path that goes up and right
        while x < size-1 or y > 0:
            path_points.add((x, y))
            if x < size-1 and (level == 1 or random.random() > 0.5):
                x += 1
            elif y > 0:
                y -= 1
            path_points.add((x, y))
        
        # Add some walls around the path
        for i in range(size):
            for j in range(size):
                if (i, j) not in path_points and random.random() < 0.3:
                    # Don't block start or exit
                    if not (i == 0 and j == size-1) and not (i == size-1 and j == 0):
                        walls.append([i, j])
        
        # Add coins near the path
        path_list = list(path_points)
        for _ in range(min(level + 3, len(path_list))):
            if path_list:
                point = random.choice(path_list)
                coins.append([point[0], point[1]])
                path_list.remove(point)
        
        return {
            "walls": walls,
            "coins": coins,
            "start": [0, size-1],
            "exit": [size-1, 0],
            "size": size
        }
