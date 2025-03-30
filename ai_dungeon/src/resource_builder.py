import pyxel

# Initialize Pyxel with a temporary window (we only need it to create resources)
pyxel.init(32, 32, title="Resource Builder")

# Create sprites in image bank 0
# Colors: 
# 0: black, 1: dark-blue, 2: purple, 3: dark-green
# 4: brown, 5: dark-grey, 6: light-grey, 7: white
# 8: red, 9: orange, 10: yellow, 11: green
# 12: blue, 13: indigo, 14: pink, 15: peach

def create_explorer(x, y):
    # Brown hat (color 4)
    pyxel.rect(x+2, y, 4, 1, 4)
    pyxel.rect(x+1, y+1, 6, 1, 4)
    
    # Face (color 15 - peach)
    pyxel.rect(x+2, y+2, 4, 2, 15)
    
    # Eyes (color 0 - black)
    pyxel.pset(x+2, y+2, 0)
    pyxel.pset(x+5, y+2, 0)
    
    # Body (color 6 - light grey for shirt)
    pyxel.rect(x+2, y+4, 4, 3, 6)
    
    # Arms (color 15 - peach)
    pyxel.rect(x+1, y+4, 1, 2, 15)
    pyxel.rect(x+6, y+4, 1, 2, 15)
    
    # Legs (color 4 - brown pants)
    pyxel.rect(x+2, y+7, 2, 1, 4)
    pyxel.rect(x+4, y+7, 2, 1, 4)

def create_goblin(x, y):
    # Head (color 11 - green)
    pyxel.rect(x+2, y+1, 4, 3, 11)
    
    # Eyes (color 8 - red)
    pyxel.pset(x+2, y+2, 8)
    pyxel.pset(x+5, y+2, 8)
    
    # Ears (color 11 - green)
    pyxel.rect(x+1, y+2, 1, 2, 11)
    pyxel.rect(x+6, y+2, 1, 2, 11)
    
    # Body (color 11 - green)
    pyxel.rect(x+2, y+4, 4, 3, 11)
    
    # Arms (color 11 - green)
    pyxel.rect(x+1, y+4, 1, 2, 11)
    pyxel.rect(x+6, y+4, 1, 2, 11)
    
    # Legs (color 11 - green)
    pyxel.rect(x+2, y+7, 2, 1, 11)
    pyxel.rect(x+4, y+7, 2, 1, 11)

def create_sword(x, y):
    # Blade (color 7 - white)
    pyxel.rect(x+3, y, 2, 6, 7)
    # Handle (color 4 - brown)
    pyxel.rect(x+2, y+6, 4, 2, 4)

def create_bow(x, y):
    # Bow curve (color 4 - brown)
    pyxel.rect(x+1, y+1, 1, 6, 4)
    pyxel.rect(x+6, y+1, 1, 6, 4)
    # String (color 7 - white)
    pyxel.line(x+1, y+1, x+6, y+1, 7)
    pyxel.line(x+1, y+6, x+6, y+6, 7)

def create_staff(x, y):
    # Staff pole (color 4 - brown)
    pyxel.rect(x+3, y, 2, 7, 4)
    # Orb (color 12 - blue)
    pyxel.circ(x+4, y+1, 2, 12)

def create_arrow(x, y):
    # Arrow head (color 7 - white)
    pyxel.tri(x+6, y+3, x+4, y+2, x+4, y+4, 7)
    # Arrow shaft (color 4 - brown)
    pyxel.rect(x, y+3, 4, 1, 4)

def create_magic_bolt(x, y):
    # Magic orb (color 12 - blue with white center)
    pyxel.circb(x+3, y+3, 3, 12)
    pyxel.circb(x+3, y+3, 2, 12)
    pyxel.circ(x+3, y+3, 1, 7)

def create_dungeon_tiles(x, y):
    # Floor tiles (16x16 each)
    colors = [(5,7), (4,6), (3,5)]  # (base, highlight) color pairs
    
    for i, (base, highlight) in enumerate(colors):
        tile_x = x + (i * 16)
        
        # Base color
        pyxel.rect(tile_x, y, 16, 16, base)
        
        # Highlight pattern
        for j in range(4):
            for k in range(4):
                if (j + k) % 2 == 0:
                    pyxel.rect(tile_x + j*4, y + k*4, 2, 2, highlight)

    # Wall tiles (16x16 each)
    wall_x = x + 48  # Start walls after floor tiles
    
    # Create 3 wall variants
    for i in range(3):
        tile_x = wall_x + (i * 16)
        
        # Base wall
        pyxel.rect(tile_x, y, 16, 16, 5)
        
        # Add texture based on variant
        if i == 0:  # Stone wall
            for j in range(4):
                for k in range(4):
                    if (j + k) % 2 == 0:
                        pyxel.rect(tile_x + j*4, y + k*4, 3, 3, 6)
        elif i == 1:  # Brick wall
            for row in range(4):
                offset = (row % 2) * 8
                for col in range(2):
                    pyxel.rect(tile_x + offset + col*8, y + row*4, 7, 3, 4)
        else:  # Decorated wall
            for j in range(2):
                for k in range(2):
                    pyxel.circb(tile_x + 4 + j*8, y + 4 + k*8, 2, 7)
                    pyxel.pset(tile_x + 4 + j*8, y + 4 + k*8, 10)

def create_decorations(x, y):
    # Torch (8x8)
    pyxel.rect(x+3, y+2, 2, 4, 4)  # Handle
    pyxel.rect(x+2, y, 4, 2, 9)  # Base
    pyxel.circ(x+4, y-1, 2, 8)  # Flame
    
    # Skull (8x8)
    x += 8
    pyxel.circ(x+4, y+4, 3, 7)  # Skull base
    pyxel.pset(x+3, y+3, 0)  # Left eye
    pyxel.pset(x+5, y+3, 0)  # Right eye
    pyxel.rect(x+3, y+5, 3, 1, 0)  # Mouth

# Create all sprites and tiles in image bank 0
pyxel.image(0).cls(0)
create_explorer(0, 0)      # Player at (0,0)
create_goblin(8, 0)        # Enemy at (8,0)
create_sword(16, 0)        # Sword at (16,0)
create_bow(24, 0)          # Bow at (24,0)
create_staff(32, 0)        # Staff at (32,0)
create_arrow(40, 0)        # Arrow at (40,0)
create_magic_bolt(48, 0)   # Magic bolt at (48,0)

# Create tiles in image bank 1
pyxel.image(1).cls(0)
create_dungeon_tiles(0, 0)  # Tiles at (0,0) in bank 1
create_decorations(0, 32)   # Decorations at (0,32) in bank 1

# Save the resource file
pyxel.save("../assets/sprites.pyxres")
