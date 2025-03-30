import pyxel
import textwrap

class UIManager:
    def __init__(self):
        self.message = ""
        self.show_message_until = 0
        

    
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
