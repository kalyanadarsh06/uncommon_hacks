import pyxel
import textwrap

class UIManager:
    def __init__(self):
        self.message = ""
        self.show_message_until = 0
        self.puzzle_input = ""
        self.puzzle_data = None
        self.show_hints = False
        self.current_hint = 0
        
    def show_puzzle(self, puzzle_data):
        """Display the current puzzle."""
        self.puzzle_data = puzzle_data
        
        # Clear screen
        pyxel.cls(0)
        
        # Draw puzzle description
        # Draw title
        pyxel.text(5, 5, "LEVEL PUZZLE", 7)
        
        # Draw description with more width
        lines = textwrap.wrap(puzzle_data["description"], width=45)
        for i, line in enumerate(lines):
            pyxel.text(5, 20 + i*8, line, 7)
        
        # Draw visualization (centered)
        vis_lines = puzzle_data["visualization"].split('\n')
        start_y = 80
        for i, line in enumerate(vis_lines):
            x = (pyxel.width - len(line) * 4) // 2
            pyxel.text(x, start_y + i*8, line, 11)
        
        # Draw input box with border
        pyxel.rectb(10, 140, 220, 12, 7)  # White border
        pyxel.rect(11, 141, 218, 10, 5)    # Dark background
        # Show input with cursor blink
        cursor = "_" if (pyxel.frame_count // 8) % 2 == 0 else " "
        pyxel.text(15, 143, f"Answer: {self.puzzle_input}{cursor}", 7)
        # Show current input length
        pyxel.text(200, 143, f"[{len(self.puzzle_input)}]", 6)
        
        # Draw hints button
        pyxel.rect(10, 160, 40, 12, 5)
        pyxel.text(15, 163, "HINT", 7)
        
        # Show current hint if requested
        if self.show_hints and self.current_hint < len(puzzle_data["hints"]):
            hint_text = puzzle_data["hints"][self.current_hint]
            hint_lines = textwrap.wrap(hint_text, width=45)
            for i, line in enumerate(hint_lines):
                pyxel.text(60, 163 + i*8, line, 8)
    
    def show_combat(self, player_health, level_num):
        """Display combat UI elements."""
        # Draw frame
        pyxel.rectb(5, 5, 230, 30, 5)
        
        # Left side - Level and Health
        pyxel.text(10, 10, f"LEVEL {level_num}", 7)
        pyxel.text(10, 20, f"HP: {player_health}", 11)
        
        # Right side - Weapons
        pyxel.text(120, 10, "WEAPONS:", 7)
        pyxel.text(120, 20, "1:SWORD 2:BOW 3:STAFF", 6)
        
    def show_message(self, text, duration=30):
        """Show a temporary message."""
        self.message = text
        self.show_message_until = pyxel.frame_count + duration
        
    def update(self):
        """Update UI state."""
        # Clear temporary messages
        if self.show_message_until > 0 and pyxel.frame_count > self.show_message_until:
            self.message = ""
            self.show_message_until = 0
            
    def draw_message(self):
        """Draw any active temporary message."""
        if self.message and self.show_message_until > pyxel.frame_count:
            # Draw centered message with background
            text_width = len(self.message) * 4
            x = (pyxel.width - text_width) // 2
            y = 60
            
            # Background
            pyxel.rect(x-2, y-2, text_width+4, 12, 5)
            # Text
            pyxel.text(x, y, self.message, 7)
