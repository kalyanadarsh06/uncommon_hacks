import google.generativeai as genai
import os
import random
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from collections import deque

class MazeGenerator:
    def __init__(self):
        """Initialize the maze generator with Gemini API."""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        genai.configure(api_key=api_key)
        try:
            self.model = genai.GenerativeModel('gemini-pro')
        except Exception as e:
            print(f"Warning: Could not initialize Gemini model: {e}")
            self.model = None

    def generate_maze(self, level, size=10):
        """Generate a maze with walls, coins, and start/exit positions."""
        # Scale difficulty with level
        min_coins = min(3, level)  # Cap coins at 3 per level
        min_walls = 10 + (level * 2)  # More walls per level
        
        # Try to generate maze with Gemini
        try:
            prompt = f"""Generate a {size}x{size} maze with:
            - At least {min_walls} walls
            - At least {min_coins} coins
            - One start position at bottom-left [0, {size-1}]
            - Ensure at least one coin is reachable from start
            - DO NOT include an exit position
            Format as JSON with 'walls', 'coins', 'start' lists of [x,y] coordinates"""
            
            if self.model is not None:
                response = self.model.generate_content(prompt)
                
                if response.text:
                    try:
                        maze_data = json.loads(response.text)
                        if self._validate_maze(maze_data, min_coins, min_walls):
                            maze_data['size'] = size
                            return maze_data
                    except json.JSONDecodeError:
                        pass
                    
        except Exception as e:
            print(f"Error generating maze with Gemini: {e}")
            
        # Fallback to manual generation if Gemini fails
        return self.generate_fallback_maze(level, size)
        
    def _validate_maze(self, maze_data, min_coins, min_walls):
        """Validate maze data meets requirements."""
        if not isinstance(maze_data, dict):
            return False
            
        required_keys = ['walls', 'coins', 'start']
        if not all(key in maze_data for key in required_keys):
            return False
            
        size = 10  # Default size
        
        # Check start position is valid
        start = maze_data['start']
        if not (isinstance(start, list) and len(start) == 2 and
                0 <= start[0] < size and 0 <= start[1] < size):
            return False
            
        # Check walls are valid and don't block start
        walls = maze_data['walls']
        if not isinstance(walls, list) or len(walls) < min_walls:
            return False
            
        # Ensure walls don't trap start position or block goal access
        goal_pos = [size - 1, 0]  # Top-right corner
        goal_adjacent = [
            [size - 2, 0],  # Left of goal
            [size - 1, 1]   # Below goal
        ]
        
        # Remove any walls at goal-adjacent positions
        walls = [wall for wall in walls if wall not in goal_adjacent]
        maze_data['walls'] = walls
            
        # Check coins are valid
        coins = maze_data['coins']
        if not isinstance(coins, list) or len(coins) < min_coins:
            return False
            
        return True

    def generate_fallback_maze(self, level, size=10):
        """Generate a fallback maze when API fails."""
        # Initialize empty maze
        maze = {
            'walls': [],
            'coins': [],
            'start': [0, size-1],  # Bottom-left corner
            'size': size
        }
        
        # Add walls (avoiding start, goal, and adjacent to goal)
        num_walls = 10 + (level * 2)
        goal_pos = [size - 1, 0]
        goal_adjacent = [
            [size - 2, 0],  # Left of goal
            [size - 1, 1]   # Below goal
        ]
        
        while len(maze['walls']) < num_walls:
            x = random.randint(0, size-1)
            y = random.randint(0, size-1)
            pos = [x, y]
            
            # Don't place walls at start, goal, or adjacent to goal
            if (pos != maze['start'] and 
                pos != goal_pos and 
                pos not in goal_adjacent and
                pos not in maze['walls']):
                maze['walls'].append(pos)
        
        # Add coins (avoiding walls and other coins)
        num_coins = min(3, level)  # Cap coins at 3 per level
        while len(maze['coins']) < num_coins:
            x = random.randint(0, size-1)
            y = random.randint(0, size-1)
            pos = [x, y]
            
            if (pos not in maze['walls'] and 
                pos != maze['start'] and
                pos != goal_pos and
                pos not in maze['coins']):
                maze['coins'].append(pos)
        
        return maze
