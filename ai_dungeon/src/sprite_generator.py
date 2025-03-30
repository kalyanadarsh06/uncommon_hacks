import pygame
import os
from PIL import Image, ImageDraw

# Initialize Pygame
pygame.init()

# Constants
TILE_SIZE = 32  # Increased size for better visibility
SPRITE_SIZE = 32
DECORATION_SIZE = 16

# Colors
COLORS = {
    'black': (0, 0, 0),
    'white': (255, 255, 255),
    'red': (255, 0, 0),
    'green': (0, 255, 0),
    'blue': (0, 0, 255),
    'brown': (139, 69, 19),
    'gray': (128, 128, 128),
    'dark_gray': (64, 64, 64),
    'yellow': (255, 255, 0),
    'orange': (255, 165, 0),
    'purple': (128, 0, 128),
    'peach': (255, 218, 185)
}

def create_sprite_surface(width, height, color_key=(0, 0, 0)):
    """Create a new sprite surface with transparency."""
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    surface.fill((0, 0, 0, 0))  # Transparent background
    return surface

def save_surface(surface, filename):
    """Save a pygame surface as a PNG file."""
    pygame.image.save(surface, filename)

def create_player():
    """Create the player character sprite."""
    surface = create_sprite_surface(SPRITE_SIZE, SPRITE_SIZE)
    
    # Draw body
    pygame.draw.rect(surface, COLORS['brown'], (12, 8, 8, 12))  # Torso
    pygame.draw.rect(surface, COLORS['peach'], (10, 4, 12, 8))  # Head
    pygame.draw.rect(surface, COLORS['blue'], (10, 20, 4, 8))   # Left leg
    pygame.draw.rect(surface, COLORS['blue'], (18, 20, 4, 8))   # Right leg
    pygame.draw.rect(surface, COLORS['peach'], (6, 12, 4, 8))   # Left arm
    pygame.draw.rect(surface, COLORS['peach'], (22, 12, 4, 8))  # Right arm
    
    # Eyes
    pygame.draw.rect(surface, COLORS['black'], (12, 8, 2, 2))   # Left eye
    pygame.draw.rect(surface, COLORS['black'], (18, 8, 2, 2))   # Right eye
    
    return surface

def create_enemy():
    """Create the enemy sprite."""
    surface = create_sprite_surface(SPRITE_SIZE, SPRITE_SIZE)
    
    # Draw body
    pygame.draw.rect(surface, COLORS['green'], (12, 8, 8, 12))  # Torso
    pygame.draw.rect(surface, COLORS['green'], (10, 4, 12, 8))  # Head
    pygame.draw.rect(surface, COLORS['dark_gray'], (10, 20, 4, 8))   # Left leg
    pygame.draw.rect(surface, COLORS['dark_gray'], (18, 20, 4, 8))   # Right leg
    pygame.draw.rect(surface, COLORS['green'], (6, 12, 4, 8))   # Left arm
    pygame.draw.rect(surface, COLORS['green'], (22, 12, 4, 8))  # Right arm
    
    # Red eyes
    pygame.draw.rect(surface, COLORS['red'], (12, 8, 2, 2))   # Left eye
    pygame.draw.rect(surface, COLORS['red'], (18, 8, 2, 2))   # Right eye
    
    return surface

def create_floor_tile(variant=0):
    """Create a floor tile with different variants."""
    surface = create_sprite_surface(TILE_SIZE, TILE_SIZE)
    base_color = COLORS['gray']
    pattern_color = COLORS['dark_gray']
    
    # Fill base
    pygame.draw.rect(surface, base_color, (0, 0, TILE_SIZE, TILE_SIZE))
    
    # Add pattern based on variant
    if variant == 0:
        # Checkered pattern
        for i in range(0, TILE_SIZE, 8):
            for j in range(0, TILE_SIZE, 8):
                if (i + j) % 16 == 0:
                    pygame.draw.rect(surface, pattern_color, (i, j, 8, 8))
    elif variant == 1:
        # Diagonal lines
        for i in range(0, TILE_SIZE * 2, 8):
            pygame.draw.line(surface, pattern_color, (0, i), (i, 0), 2)
    else:
        # Dots pattern
        for i in range(4, TILE_SIZE, 8):
            for j in range(4, TILE_SIZE, 8):
                pygame.draw.circle(surface, pattern_color, (i, j), 2)
    
    return surface

def create_wall_tile(variant=0):
    """Create a wall tile with different variants."""
    surface = create_sprite_surface(TILE_SIZE, TILE_SIZE)
    base_color = COLORS['dark_gray']
    pattern_color = COLORS['gray']
    
    # Fill base
    pygame.draw.rect(surface, base_color, (0, 0, TILE_SIZE, TILE_SIZE))
    
    # Add pattern based on variant
    if variant == 0:
        # Stone wall
        for i in range(0, TILE_SIZE, 8):
            for j in range(0, TILE_SIZE, 8):
                pygame.draw.rect(surface, pattern_color, (i+1, j+1, 6, 6))
    elif variant == 1:
        # Brick wall
        for i in range(0, TILE_SIZE, 16):
            for j in range(0, TILE_SIZE, 8):
                offset = 8 if j % 16 == 0 else 0
                pygame.draw.rect(surface, pattern_color, (offset+i, j, 14, 6))
    else:
        # Decorated wall
        pygame.draw.rect(surface, pattern_color, (0, 0, TILE_SIZE, TILE_SIZE))
        for i in range(8, TILE_SIZE, 16):
            for j in range(8, TILE_SIZE, 16):
                pygame.draw.circle(surface, base_color, (i, j), 4)
    
    return surface

def create_decoration(type='torch'):
    """Create decoration sprites (torch, skull)."""
    surface = create_sprite_surface(DECORATION_SIZE, DECORATION_SIZE)
    
    if type == 'torch':
        # Handle
        pygame.draw.rect(surface, COLORS['brown'], (7, 8, 2, 6))
        # Base
        pygame.draw.rect(surface, COLORS['orange'], (6, 6, 4, 2))
        # Flame
        pygame.draw.circle(surface, COLORS['yellow'], (8, 4), 3)
    else:  # skull
        # Base
        pygame.draw.circle(surface, COLORS['white'], (8, 8), 6)
        # Eyes
        pygame.draw.rect(surface, COLORS['black'], (5, 7, 2, 2))
        pygame.draw.rect(surface, COLORS['black'], (9, 7, 2, 2))
        # Mouth
        pygame.draw.rect(surface, COLORS['black'], (6, 10, 4, 1))
    
    return surface

def create_weapon(type='sword'):
    """Create weapon sprites."""
    surface = create_sprite_surface(SPRITE_SIZE, SPRITE_SIZE)
    
    if type == 'sword':
        # Blade
        pygame.draw.rect(surface, COLORS['white'], (14, 4, 4, 20))
        # Handle
        pygame.draw.rect(surface, COLORS['brown'], (13, 24, 6, 4))
        # Guard
        pygame.draw.rect(surface, COLORS['yellow'], (11, 22, 10, 2))
    elif type == 'bow':
        # Bow curve
        pygame.draw.arc(surface, COLORS['brown'], (8, 4, 16, 24), 0.5, 5.5, 2)
        # String
        pygame.draw.line(surface, COLORS['white'], (12, 6), (12, 26), 1)
    else:  # staff
        # Staff pole
        pygame.draw.rect(surface, COLORS['brown'], (14, 4, 4, 24))
        # Orb
        pygame.draw.circle(surface, COLORS['purple'], (16, 6), 6)
    
    return surface

def generate_all_sprites():
    """Generate and save all game sprites."""
    # Create directories if they don't exist
    os.makedirs('../assets/images/sprites', exist_ok=True)
    os.makedirs('../assets/images/tiles', exist_ok=True)
    os.makedirs('../assets/images/ui', exist_ok=True)
    
    # Generate character sprites
    save_surface(create_player(), '../assets/images/sprites/player.png')
    save_surface(create_enemy(), '../assets/images/sprites/enemy.png')
    
    # Generate tiles
    for i in range(3):
        save_surface(create_floor_tile(i), f'../assets/images/tiles/floor_{i}.png')
        save_surface(create_wall_tile(i), f'../assets/images/tiles/wall_{i}.png')
    
    # Generate decorations
    save_surface(create_decoration('torch'), '../assets/images/tiles/torch.png')
    save_surface(create_decoration('skull'), '../assets/images/tiles/skull.png')
    
    # Generate weapons
    save_surface(create_weapon('sword'), '../assets/images/sprites/sword.png')
    save_surface(create_weapon('bow'), '../assets/images/sprites/bow.png')
    save_surface(create_weapon('staff'), '../assets/images/sprites/staff.png')

if __name__ == '__main__':
    generate_all_sprites()
    pygame.quit()
