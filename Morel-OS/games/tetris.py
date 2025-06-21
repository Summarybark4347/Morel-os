import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_COLS = 10
GRID_ROWS = 20
BLOCK_SIZE = 30

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
GRID_COLOR = GRAY  # Color for the grid lines
EMPTY_CELL_COLOR = BLACK # Color for empty cells

# Tetromino shapes (list of lists of (row, col) offsets)
TETROMINOES = {
    'I': [[(0, 0), (1, 0), (2, 0), (3, 0)], [(0,0), (0,1), (0,2), (0,3)]], # Simplified for now, only first orientation
    'O': [[(0, 0), (0, 1), (1, 0), (1, 1)]],
    'T': [[(0, 1), (1, 0), (1, 1), (1, 2)], [(0,0),(1,0),(2,0),(1,1)]],
    'S': [[(0, 1), (0, 2), (1, 0), (1, 1)], [(0,0),(1,0),(1,1),(2,1)]],
    'Z': [[(0, 0), (0, 1), (1, 1), (1, 2)], [(0,1),(1,1),(1,0),(2,0)]],
    'J': [[(0, 0), (1, 0), (2, 0), (2, 1)], [(0,1),(1,1),(2,1),(0,0)]],
    'L': [[(0, 1), (1, 1), (2, 1), (2, 0)], [(0,0),(1,0),(2,0),(0,1)]]
}

TETROMINO_COLORS = {
    'I': (0, 255, 255),   # Cyan
    'O': (255, 255, 0),   # Yellow
    'T': (128, 0, 128),   # Purple
    'S': (0, 255, 0),     # Green
    'Z': (255, 0, 0),     # Red
    'J': (0, 0, 255),     # Blue
    'L': (255, 165, 0)    # Orange
}

# --- Game State Variables ---
grid = [[0 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
score = 0
game_over = False
# fall_time will be initialized in reset_game_state or before game loop
# Current block state variables will also be initialized/reset
current_tetromino_key = None
current_tetromino_shapes = None 
current_rotation_index = 0
current_tetromino_color = None
current_block_row = 0
current_block_col = 0
next_tetromino_key = None # For the upcoming block

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tetris")

# --- Next Block Preview Area ---
NEXT_BLOCK_AREA_X = SCREEN_WIDTH - 200 # Example X position
NEXT_BLOCK_AREA_Y = 50                 # Example Y position
NEXT_BLOCK_AREA_WIDTH = 160
NEXT_BLOCK_AREA_HEIGHT = 120
PREVIEW_BLOCK_SIZE = 20 # Potentially smaller size for preview blocks

def draw_grid(surface, game_grid):
    """Draws the Tetris grid lines and filled cells."""
    grid_surface_width = GRID_COLS * BLOCK_SIZE
    grid_surface_height = GRID_ROWS * BLOCK_SIZE
    start_x = (SCREEN_WIDTH - grid_surface_width) // 2
    start_y = (SCREEN_HEIGHT - grid_surface_height) // 2

    for r_idx, row in enumerate(game_grid):
        for c_idx, cell_value in enumerate(row):
            cell_rect = pygame.Rect(
                start_x + c_idx * BLOCK_SIZE,
                start_y + r_idx * BLOCK_SIZE,
                BLOCK_SIZE,
                BLOCK_SIZE
            )
            # Draw the cell based on its value
            fill_color = EMPTY_CELL_COLOR
            if cell_value != 0: # If it's a filled cell
                # Assuming cell_value is a key like 'L', 'T', etc.
                # This part is more for when blocks are locked into the grid
                if cell_value in TETROMINO_COLORS:
                    fill_color = TETROMINO_COLORS[cell_value]
                else:
                    fill_color = WHITE # Fallback for unexpected values
            
            pygame.draw.rect(surface, fill_color, cell_rect)

            # Draw grid lines
            pygame.draw.rect(surface, GRID_COLOR, cell_rect, 1) # The '1' makes it draw only the border

def draw_block(surface, shape_coords, block_color, position_on_grid, block_size_val):
    """
    Draws a tetromino block on the grid.
    shape_coords: List of (row, col) offsets for the block's shape.
    block_color: The color of the block.
    position_on_grid: (row, col) of the top-left of the block's bounding box on the grid.
    block_size_val: The size of a single cell in pixels.
    """
    grid_surface_width = GRID_COLS * BLOCK_SIZE
    grid_surface_height = GRID_ROWS * BLOCK_SIZE
    start_x = (SCREEN_WIDTH - grid_surface_width) // 2
    start_y = (SCREEN_HEIGHT - grid_surface_height) // 2

    base_row, base_col = position_on_grid
    # Ensure shape_coords is not None and is iterable
    if shape_coords and isinstance(shape_coords, list):
        for r_offset, c_offset in shape_coords:
            # Calculate actual screen coordinates
            cell_x = start_x + (base_col + c_offset) * block_size_val
            cell_y = start_y + (base_row + r_offset) * block_size_val
            
            block_rect = pygame.Rect(cell_x, cell_y, block_size_val, block_size_val)
            pygame.draw.rect(surface, block_color, block_rect)
            pygame.draw.rect(surface, GRAY, block_rect, 1) # Border for each cell of the block
    else:
        # Optionally, log an error or handle the case where shape_coords is invalid
        # print(f"Warning: draw_block called with invalid shape_coords: {shape_coords}")
        pass


def spawn_new_block():
    global current_tetromino_key, current_tetromino_shapes, current_rotation_index
    global current_tetromino_color, current_block_row, current_block_col, game_over
    global next_tetromino_key # Added next_tetromino_key
    
    if next_tetromino_key is None: # Should only happen on very first spawn
        # This case will be handled by reset_game_state pre-seeding next_tetromino_key
        # For safety, pick a random one if somehow missed.
        available_keys = list(TETROMINOES.keys())
        next_tetromino_key = random.choice(available_keys)

    current_tetromino_key = next_tetromino_key # The 'next' block becomes current
    current_tetromino_shapes = TETROMINOES[current_tetromino_key]
    current_rotation_index = 0 
    current_tetromino_color = TETROMINO_COLORS[current_tetromino_key]
    current_block_row = 0 
    
    # Generate the *new* next block
    available_keys_for_next = list(TETROMINOES.keys())
    next_tetromino_key = random.choice(available_keys_for_next)
    
    shape_to_center = current_tetromino_shapes[current_rotation_index]
    if not shape_to_center or not all(isinstance(item, tuple) and len(item) == 2 for item in shape_to_center):
        print(f"Error: Invalid shape for {current_tetromino_key} during spawn.")
        game_over = True # Critical error if shape is bad
        return

    min_col_offset = min(c_offset for r_offset, c_offset in shape_to_center)
    max_col_offset = max(c_offset for r_offset, c_offset in shape_to_center)
    block_width_in_cells = max_col_offset - min_col_offset + 1
    current_block_col = (GRID_COLS - block_width_in_cells) // 2 - min_col_offset

    # Game Over Check: If the new block is immediately invalid
    if not is_valid_position(shape_to_center, current_block_row, current_block_col, grid):
        game_over = True
        # The print statement from previous step can be removed or kept for debugging
        # print(f"Game Over! Spawn collision. Final Score: {score}")


def is_valid_position(shape_coords, grid_row, grid_col, game_grid_state):
    """
    Checks if the given tetromino shape at the specified grid position is valid.
    - shape_coords: List of (row_offset, col_offset) for the block's cells.
    - grid_row: The base row of the block on the grid.
    - grid_col: The base column of the block on the grid.
    - game_grid_state: The current state of the main game grid.
    """
    if not shape_coords: # Should not happen with current setup
        return False

    for r_offset, c_offset in shape_coords:
        actual_row = grid_row + r_offset
        actual_col = grid_col + c_offset

        # Check boundaries
        if not (0 <= actual_row < GRID_ROWS and 0 <= actual_col < GRID_COLS):
            return False # Out of bounds

        # Check collision with existing blocks on the grid
        # This check is only needed if actual_row is within the grid's visible part
        if game_grid_state[actual_row][actual_col] != 0: # Cell is already occupied
            return False
            
    return True

def lock_block(shape_coords, grid_row, grid_col, color_key, game_grid_state):
    """
    Locks the current block into the game grid.
    - shape_coords: List of (row_offset, col_offset) for the block's cells.
    - grid_row: The base row of the block on the grid.
    - grid_col: The base column of the block on the grid.
    - color_key: The key representing the block's color (e.g., 'L', 'T').
    - game_grid_state: The main game grid to update.
    """
    if not shape_coords:
        return

    for r_offset, c_offset in shape_coords:
        actual_row = grid_row + r_offset
        actual_col = grid_col + c_offset
        # Ensure the part of the block being locked is within bounds
        # This should ideally be guaranteed by is_valid_position checks before locking
        if 0 <= actual_row < GRID_ROWS and 0 <= actual_col < GRID_COLS:
            game_grid_state[actual_row][actual_col] = color_key # Use the color key

# --- Score and Font (font init remains here, score is global) ---
# score = 0 # Moved to global game state variables
try:
    pygame.font.init() # Ensure font module is initialized
    score_font = pygame.font.Font(None, 36) # Default font, size 36
except Exception as e:
    print(f"Could not initialize font: {e}")
    score_font = None # Fallback if font loading fails

# Points for clearing lines
LINE_SCORES = {
    1: 40,
    2: 100,
    3: 300,
    4: 1200
}

def check_and_clear_lines(game_grid_state):
    """
    Checks for completed lines, clears them, and shifts blocks down.
    Returns the number of lines cleared.
    """
    lines_cleared = 0
    row_idx = GRID_ROWS - 1 # Start checking from the bottom

    while row_idx >= 0:
        is_line_full = True
        for col_idx in range(GRID_COLS):
            if game_grid_state[row_idx][col_idx] == 0: # If any cell is empty
                is_line_full = False
                break
        
        if is_line_full:
            lines_cleared += 1
            # Remove the full line
            del game_grid_state[row_idx]
            # Add a new empty line at the top
            game_grid_state.insert(0, [0 for _ in range(GRID_COLS)])
            # Since a line was removed, the next line to check is at the same row_idx
            # No change to row_idx here, as the rows above have shifted down.
        else:
            row_idx -= 1 # Move to check the line above
            
    return lines_cleared

def reset_game_state():
    global grid, score, game_over, fall_time, next_tetromino_key
    # No need to global current_block variables here as spawn_new_block handles them
    
    grid = [[0 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
    score = 0
    game_over = False
    fall_time = 0
    
    # Initialize the very first 'next' block
    available_keys = list(TETROMINOES.keys())
    next_tetromino_key = random.choice(available_keys)
    
    spawn_new_block() # This will make the initial 'next' current and generate a new 'next'

# Initialize game for the first time
reset_game_state()

def draw_preview_block(surface, shape_coords, block_color, area_rect):
    """
    Draws a tetromino block shape centered within a given rectangular area.
    surface: The pygame surface to draw on.
    shape_coords: List of (row, col) offsets for the block's shape.
    block_color: The color of the block.
    area_rect: A pygame.Rect defining the area for the preview.
    """
    if not shape_coords or not isinstance(shape_coords, list):
        return

    # Determine bounds of the shape itself to help with centering
    min_r_offset = min(r for r, c in shape_coords)
    max_r_offset = max(r for r, c in shape_coords)
    min_c_offset = min(c for r, c in shape_coords)
    max_c_offset = max(c for r, c in shape_coords)
    
    shape_height_cells = max_r_offset - min_r_offset + 1
    shape_width_cells = max_c_offset - min_c_offset + 1

    # Calculate total pixel dimensions of the shape using PREVIEW_BLOCK_SIZE
    shape_width_pixels = shape_width_cells * PREVIEW_BLOCK_SIZE
    shape_height_pixels = shape_height_cells * PREVIEW_BLOCK_SIZE

    # Calculate top-left position to center the shape within area_rect
    start_x = area_rect.x + (area_rect.width - shape_width_pixels) // 2
    start_y = area_rect.y + (area_rect.height - shape_height_pixels) // 2

    # Adjust start_x and start_y to account for the shape's own internal origin (min_c_offset, min_r_offset)
    draw_origin_x = start_x - (min_c_offset * PREVIEW_BLOCK_SIZE)
    draw_origin_y = start_y - (min_r_offset * PREVIEW_BLOCK_SIZE)

    for r_offset, c_offset in shape_coords:
        cell_x = draw_origin_x + c_offset * PREVIEW_BLOCK_SIZE
        cell_y = draw_origin_y + r_offset * PREVIEW_BLOCK_SIZE
        
        block_rect = pygame.Rect(cell_x, cell_y, PREVIEW_BLOCK_SIZE, PREVIEW_BLOCK_SIZE)
        pygame.draw.rect(surface, block_color, block_rect)
        pygame.draw.rect(surface, GRAY, block_rect, 1) # Border for each cell

# Game loop
running = True
clock = pygame.time.Clock()
# fall_time is now part of game state, initialized in reset_game_state
fall_speed = 500 # Milliseconds per step down 

while running:
    dt = clock.tick(60) 

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if game_over: # Only check for restart key if game is over
                if event.key == pygame.K_r:
                    reset_game_state()
            else: # Active game input processing (if not game_over)
                if current_tetromino_shapes: 
                    current_shape_coords = current_tetromino_shapes[current_rotation_index]
                    if event.key == pygame.K_LEFT:
                        if is_valid_position(current_shape_coords, current_block_row, current_block_col - 1, grid):
                            current_block_col -= 1
                    elif event.key == pygame.K_RIGHT:
                        if is_valid_position(current_shape_coords, current_block_row, current_block_col + 1, grid):
                            current_block_col += 1
                    elif event.key == pygame.K_DOWN: 
                        if is_valid_position(current_shape_coords, current_block_row + 1, current_block_col, grid):
                            current_block_row += 1
                            fall_time = 0 # Reset gravity timer on soft drop
                    elif event.key == pygame.K_UP: 
                        next_rotation_index = (current_rotation_index + 1) % len(current_tetromino_shapes)
                        next_shape_coords = current_tetromino_shapes[next_rotation_index]
                        if is_valid_position(next_shape_coords, current_block_row, current_block_col, grid):
                            current_rotation_index = next_rotation_index
                        else: # Basic wall kick
                            if is_valid_position(next_shape_coords, current_block_row, current_block_col + 1, grid):
                                current_block_col +=1
                                current_rotation_index = next_rotation_index
                            elif is_valid_position(next_shape_coords, current_block_row, current_block_col - 1, grid):
                                current_block_col -=1
                                current_rotation_index = next_rotation_index
    
    # --- Game Logic (only if not game_over) ---
    if not game_over:
        fall_time += dt 
        if fall_time >= fall_speed:
            fall_time = 0 
            if current_tetromino_shapes: 
                current_shape_coords = current_tetromino_shapes[current_rotation_index]
                if is_valid_position(current_shape_coords, current_block_row + 1, current_block_col, grid):
                    current_block_row += 1
                else:
                    lock_block(current_shape_coords, current_block_row, current_block_col, current_tetromino_key, grid)
                    lines_cleared_count = check_and_clear_lines(grid)
                    if lines_cleared_count > 0:
                        score += LINE_SCORES.get(lines_cleared_count, 0)
                    spawn_new_block() # game_over will be set here if spawn fails

    # --- Drawing ---
    screen.fill(BLACK)
    draw_grid(screen, grid)
    
    if not game_over and current_tetromino_shapes: 
        current_shape_coords = current_tetromino_shapes[current_rotation_index]
        draw_block(screen, current_shape_coords, current_tetromino_color, 
                   (current_block_row, current_block_col), BLOCK_SIZE)
    
    if score_font: # Always draw score
        score_text_surface = score_font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text_surface, (10, 10))
    
    # Draw Next Block Area and Preview
    if score_font: # Using score_font for "Next:" label as well
        # Draw border for the next block area
        next_area_border_rect = pygame.Rect(NEXT_BLOCK_AREA_X - 2, NEXT_BLOCK_AREA_Y - 2, 
                                            NEXT_BLOCK_AREA_WIDTH + 4, NEXT_BLOCK_AREA_HEIGHT + 4 + 30) # +30 for text
        pygame.draw.rect(screen, GRID_COLOR, next_area_border_rect, 2) # Border

        next_text_surface = score_font.render("Next:", True, WHITE)
        screen.blit(next_text_surface, (NEXT_BLOCK_AREA_X + 5, NEXT_BLOCK_AREA_Y)) # Position text

        if next_tetromino_key and not game_over: # Only show if there is a next block and game is not over
            preview_shape_coords = TETROMINOES[next_tetromino_key][0] # Use first orientation
            preview_color = TETROMINO_COLORS[next_tetromino_key]
            # Define the actual drawing area for the block itself (below the text)
            preview_block_display_rect = pygame.Rect(NEXT_BLOCK_AREA_X, NEXT_BLOCK_AREA_Y + 30, 
                                                     NEXT_BLOCK_AREA_WIDTH, NEXT_BLOCK_AREA_HEIGHT)
            draw_preview_block(screen, preview_shape_coords, preview_color, preview_block_display_rect)


    if game_over: # Display Game Over messages
        if score_font:
            game_over_msg = score_font.render("GAME OVER", True, (255,0,0))
            msg_rect = game_over_msg.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
            screen.blit(game_over_msg, msg_rect)

            final_score_msg = score_font.render(f"Final Score: {score}", True, WHITE)
            final_score_rect = final_score_msg.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(final_score_msg, final_score_rect)
            
            restart_msg = score_font.render("Press 'R' to Restart", True, WHITE)
            restart_rect = restart_msg.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
            screen.blit(restart_msg, restart_rect)

    pygame.display.flip()

pygame.quit()
