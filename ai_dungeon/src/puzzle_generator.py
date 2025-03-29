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
        
        # Define puzzle types based on difficulty
        puzzle_types = {
            "easy": [
                "Complete the number sequence",
                "Find the missing letter",
                "Simple math problem",
                "Pattern recognition",
                "Count the shapes"
            ],
            "medium": [
                "Word riddle",
                "Logic puzzle",
                "Mathematical pattern",
                "Symbol substitution",
                "Visual sequence"
            ],
            "hard": [
                "Multi-step riddle",
                "Complex pattern",
                "Code breaking",
                "Mathematical series",
                "Visual transformation"
            ]
        }
        
        # Select a random puzzle type for this level
        import random
        puzzle_type = random.choice(puzzle_types[difficulty])
        
        prompt = f"""
        You are a puzzle generator for a dungeon escape game. Generate a {difficulty} {puzzle_type.lower()} puzzle.
        
        CRITICAL: Your entire response must be a single, valid JSON object. No other text, no markdown, no explanations.
        The JSON must exactly match this structure:
        {{
            "description": "Clear instructions for solving the puzzle",
            "visualization": "ASCII art or diagram using only basic characters",
            "solution": "EXACT answer player must type (keep it simple)",
            "hints": ["Subtle hint", "More direct hint", "Almost gives it away"]
        }}
        
        Rules for each field:
        - description: Clear text explaining the puzzle rules
        - visualization: Only use basic ASCII (no special chars)
        - solution: Single word or number, no punctuation
        - hints: Array of 3 strings, getting more helpful
        
        Make the puzzle:
        - {difficulty} difficulty
        - Themed around {puzzle_type.lower()}
        - Solvable in 2-3 minutes
        - Have an unambiguous solution
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Try to extract JSON from the response
            text = response.text.strip()
            
            # Find the JSON object
            import re
            json_match = re.search(r'\{[^{}]*\}', text)
            if not json_match:
                print("No JSON found in response")
                raise ValueError("No JSON in response")
                
            json_str = json_match.group(0)
            
            # Clean the JSON string
            # Remove any control characters and escape sequences
            json_str = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', json_str)
            json_str = json_str.replace('\\n', '\n').replace('\\"', '"')
            
            # Validate JSON structure
            import json
            try:
                puzzle_data = json.loads(json_str)
                required_keys = ['description', 'visualization', 'solution', 'hints']
                if not all(key in puzzle_data for key in required_keys):
                    raise ValueError("Missing required keys in puzzle data")
                if not isinstance(puzzle_data['hints'], list):
                    raise ValueError("Hints must be a list")
                
                # Ensure the solution is clean
                puzzle_data['solution'] = puzzle_data['solution'].strip()
                
                # Convert back to JSON string
                return json.dumps(puzzle_data)
            except json.JSONDecodeError as e:
                print(f"Invalid JSON: {e}")
                raise
            except Exception as e:
                print(f"Error validating puzzle data: {e}")
                raise
                
        except Exception as e:
            print(f"Error generating puzzle: {e}")
            # Return a fallback puzzle
            fallback_puzzles = [
                '{"description": "What number comes next? 2, 4, 6, __", "visualization": "2 -> 4 -> 6 -> ??", "solution": "8", "hints": ["Look at the pattern", "Each number increases by 2", "Add 2 to 6"]}',
                '{"description": "Unscramble the word: NGUDENO", "visualization": "D _ _ G _ _ _", "solution": "DUNGEON", "hints": ["It\'s where you are", "Think about the game setting", "DUNGEON scrambled"]}',
                '{"description": "Solve: If a sword is 5 and a bow is 3, what is a staff?", "visualization": "SWORD = 5\nBOW = 3\nSTAFF = ?", "solution": "5", "hints": ["Count something", "Look at the letters", "Count consonants"]}'
            ]
            return fallback_puzzles[level % len(fallback_puzzles)]
    
    def verify_solution(self, puzzle_solution, player_answer):
        """Verify if the player's solution matches the puzzle solution."""
        # Clean up both strings and compare (case-insensitive)
        puzzle_solution = puzzle_solution.lower().strip()
        player_answer = player_answer.lower().strip()
        return puzzle_solution == player_answer
