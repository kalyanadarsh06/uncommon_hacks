import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file")
genai.configure(api_key=api_key)

class PuzzleGenerator:
    def __init__(self):
        # List available models
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"Found model: {m.name}")
        
        # Initialize with the correct model
        try:
            self.model = genai.GenerativeModel('gemini-pro')
        except Exception as e:
            print(f"Error initializing Gemini model: {e}")
            print("Available models:")
            for m in genai.list_models():
                print(f" - {m.name} (Methods: {m.supported_generation_methods})")
            raise
        
    def generate_puzzle(self, level):
        """Generate a puzzle based on the current level."""
        difficulty = "easy" if level <= 2 else "medium" if level <= 4 else "hard"
        
        prompt = f"""
        Create a {difficulty} puzzle for a dungeon escape game. The puzzle should:
        1. Be solvable within 2-3 minutes
        2. Use only ASCII characters for visualization
        3. Have clear instructions
        4. Return the following JSON format:
        {{
            "description": "Puzzle description and rules",
            "visualization": "ASCII art representation",
            "solution": "The correct solution",
            "hints": ["Hint 1", "Hint 2", "Hint 3"]
        }}
        
        For {difficulty} difficulty, focus on:
        - Easy: Simple pattern matching or sequence puzzles
        - Medium: Logic puzzles or simple riddles
        - Hard: Complex riddles or multi-step puzzles
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error generating puzzle: {e}")
            # Return a fallback puzzle for testing
            return '{"description": "Test puzzle: What number comes next? 2, 4, 6, __", "visualization": "2 -> 4 -> 6 -> ??", "solution": "8", "hints": ["Look at the pattern", "Each number increases by 2", "Add 2 to 6"]}'
    
    def verify_solution(self, puzzle_solution, player_answer):
        """Verify if the player's solution matches the puzzle solution."""
        # Clean up both strings and compare (case-insensitive)
        puzzle_solution = puzzle_solution.lower().strip()
        player_answer = player_answer.lower().strip()
        return puzzle_solution == player_answer
