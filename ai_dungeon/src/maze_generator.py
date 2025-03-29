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
        1. Create strategic wall placement:
           - Place walls to prevent easy edge-walking
           - Create bottlenecks and corridors
           - Leave multiple possible paths but make them challenging
        2. Include AT LEAST {min_walls} wall blocks to create a complex maze
        3. The path from start to exit MUST:
           - Be at least {path_length} steps long
           - Require at least {min_turns} changes in direction
           - Have multiple possible routes of varying difficulty
        4. Add {level} strategic obstacles:
           - Create challenging pathways
           - Add optional exploration routes for coins
           - Make shortcuts risky or costly
        5. Place {level + 3} coins in positions that require exploration
        6. The maze MUST be different from all previous levels
        7. Make it feel like a level {level} challenge

        CRITICAL RULES:
        - All coordinates must be within 0 to {size-1}
        - There MUST be at least one valid path from start to exit
        - Start is fixed at [0,{size-1}] and exit at [{size-1},0]
        - Balance challenge with solvability
        - Create multiple paths but make them all require skill
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

            # Validate wall density near edges
            edge_density = 0
            total_edges = (size - 1) * 4  # Total possible edge cells excluding corners
            
            # Count walls along edges
            for x in range(1, size-1):
                if (x, 0) in border_points: edge_density += 1  # Top edge
                if (x, size-1) in border_points: edge_density += 1  # Bottom edge
            for y in range(1, size-1):
                if (0, y) in border_points: edge_density += 1  # Left edge
                if (size-1, y) in border_points: edge_density += 1  # Right edge
                
            # Ensure some edge walls (30-70% coverage) but not complete blockage
            if not (0.3 * total_edges <= edge_density <= 0.7 * total_edges):
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
        
        # Create a zigzag pattern that prevents straight paths
        for i in range(1, size-1):
            if i % 2 == 0:
                # Create partial walls that force turns
                for j in range(0, size-2):
                    walls.append([i, j])
            else:
                # Create gaps for passage but prevent straight paths
                for j in range(2, size):
                    walls.append([i, j])
        
        # Add some strategic edge walls
        for i in range(2, size-2):
            if i % 3 == 0:
                walls.append([0, i])  # Left edge
                walls.append([size-1, i])  # Right edge
                walls.append([i, 0])  # Top edge
                walls.append([i, size-1])  # Bottom edge
        
        # Add coins in challenging positions
        coins = []
        for i in range(min(level+3, size-2)):
            if i % 2 == 0:
                coins.append([i+1, i+1])
            else:
                coins.append([i+1, size-2-i])
        
        return {
            "walls": walls,
            "coins": coins,
            "start": [0, size-1],
            "exit": [size-1, 0],
            "size": size
        }
