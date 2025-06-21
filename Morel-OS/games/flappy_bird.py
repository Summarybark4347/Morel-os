import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 288
SCREEN_HEIGHT = 512

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKY_BLUE = (135, 206, 235)
YELLOW = (255, 255, 0)  # For the bird placeholder
GREEN = (0, 255, 0)    # For the pipe placeholder

# Game Loop and Clock
clock = pygame.time.Clock()
FPS = 60
running = True

# Placeholder Asset Properties
BIRD_WIDTH = 34
BIRD_HEIGHT = 24

# Pipe Properties
PIPE_WIDTH = 60 # Slightly wider for better appearance
PIPE_COLOR = GREEN # Already defined as GREEN
PIPE_GAP_SIZE = 150
PIPE_SPEED = 2
PIPE_SPAWN_FREQUENCY = 120 # Spawn a new pipe every 120 frames (2 seconds at 60 FPS)
pipe_spawn_timer = 0

# List to store active pipes
pipes = []

# Game State
game_started = False # New state for start screen
game_over = False
score = 0

# Font for Score & Messages
pygame.font.init() # Ensure font module is initialized
score_font = pygame.font.Font(None, 56) 
game_over_font = pygame.font.Font(None, 72)
restart_font = pygame.font.Font(None, 36)
title_font = pygame.font.Font(None, 60) # Adjusted size
start_instruction_font = pygame.font.Font(None, 30) # Adjusted size


# Bird Properties
bird_x = SCREEN_WIDTH // 4 # bird_x remains constant for this version
bird_y = SCREEN_HEIGHT // 2
bird_velocity_y = 0
gravity = 0.5
flap_strength = -8

def create_pipe():
    """Generates a new pipe dictionary with random top pipe height."""
    # Minimum height for top pipe to ensure gap is visible and playable
    min_top_height = 50
    max_top_height = SCREEN_HEIGHT - PIPE_GAP_SIZE - 50 
    # Ensure bottom pipe also has a minimum height (implicitly handled by max_top_height)
    
    top_pipe_height = random.randint(min_top_height, max_top_height)
    return {'x': SCREEN_WIDTH, 'top_pipe_height': top_pipe_height, 'passed': False}

# Initialize with one pipe to start, or let timer spawn the first one.
# Let's use the timer for consistency.

def reset_game_state():
    global bird_y, bird_velocity_y, pipes, score, game_over, pipe_spawn_timer, game_started
    
    bird_y = SCREEN_HEIGHT // 2
    bird_velocity_y = 0
    pipes.clear()
    score = 0
    game_over = False
    game_started = False # Return to start screen after reset
    pipe_spawn_timer = 0 

# Call reset_game_state once before the main game loop to set initial state (shows start screen)
reset_game_state()

while running:
    if game_started and not game_over: # Only increment timer if game is active and started
      pipe_spawn_timer += 1

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if not game_started: # Handle input for starting the game
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE or \
               event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                reset_game_state() # Reset everything for a fresh start
                game_started = True # Then start the game
                game_over = False # Ensure game_over is false if reset_game_state didn't set it (it does)
                # Flap on first input to prevent immediate fall if desired, or not.
                # bird_velocity_y = flap_strength 
        elif not game_over: # Process game input only if started and not game over
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bird_velocity_y = flap_strength
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: 
                    bird_velocity_y = flap_strength
        else: # Process restart input only if game is over (and implicitly, game_started was true)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    reset_game_state() # This will set game_started = False, returning to start screen

    # --- Game Logic (only if game_started and not game_over) ---
    if game_started and not game_over:
        # Bird Movement
        bird_velocity_y += gravity
        bird_y += bird_velocity_y

        # Update bird_rect for current frame
        bird_rect = pygame.Rect(bird_x, bird_y, BIRD_WIDTH, BIRD_HEIGHT)

        # Collision with Top/Bottom Boundaries
        if bird_rect.top < 0:
            game_over = True
            print("Collision with top boundary!")
            # bird_y = 0 # Optional: Keep bird visible
            # bird_velocity_y = 0
        
        if bird_rect.bottom > SCREEN_HEIGHT:
            game_over = True
            print("Collision with bottom boundary!")
            # bird_y = SCREEN_HEIGHT - BIRD_HEIGHT # Optional: Keep bird visible
            # bird_velocity_y = 0

        # Pipe Logic
        # Spawning new pipes
        if pipe_spawn_timer >= PIPE_SPAWN_FREQUENCY:
            pipes.append(create_pipe())
            pipe_spawn_timer = 0

        # Moving Pipes
        for pipe in pipes:
            pipe['x'] -= PIPE_SPEED

        # Removing Off-Screen Pipes (do this before drawing and collision for slight efficiency)
        pipes = [p for p in pipes if p['x'] + PIPE_WIDTH > 0]
        
        # Scoring and Collision with Pipes
        for pipe in pipes:
            # Scoring: Check if bird passed the pipe
            if not pipe['passed'] and pipe['x'] + PIPE_WIDTH < bird_x:
                score += 1
                pipe['passed'] = True
                print(f"Score: {score}")

            # Collision
            top_pipe_rect = pygame.Rect(pipe['x'], 0, PIPE_WIDTH, pipe['top_pipe_height'])
            bottom_pipe_y = pipe['top_pipe_height'] + PIPE_GAP_SIZE
            bottom_pipe_height = SCREEN_HEIGHT - bottom_pipe_y
            bottom_pipe_rect = pygame.Rect(pipe['x'], bottom_pipe_y, PIPE_WIDTH, bottom_pipe_height)

            if bird_rect.colliderect(top_pipe_rect) or bird_rect.colliderect(bottom_pipe_rect):
                game_over = True
                print("Collision with pipe!")
                break 

    # --- Drawing (happens regardless of game_over state) ---
    screen.fill(SKY_BLUE)  # Fill screen with sky blue

    # Draw Pipes (before bird, so bird is on top)
    for pipe in pipes:
        # Top Pipe
        top_pipe_rect_draw = pygame.Rect(pipe['x'], 0, PIPE_WIDTH, pipe['top_pipe_height'])
        pygame.draw.rect(screen, PIPE_COLOR, top_pipe_rect_draw)
        # Bottom Pipe
        bottom_pipe_y_draw = pipe['top_pipe_height'] + PIPE_GAP_SIZE
        bottom_pipe_height_draw = SCREEN_HEIGHT - bottom_pipe_y_draw
        bottom_pipe_rect_draw = pygame.Rect(pipe['x'], bottom_pipe_y_draw, PIPE_WIDTH, bottom_pipe_height_draw)
        pygame.draw.rect(screen, PIPE_COLOR, bottom_pipe_rect_draw)

    # Draw the bird (using the last valid bird_rect if game_over, or updated one)
    # For simplicity, bird_rect is defined/updated once per frame if not game_over
    # If game_over, we use the bird_rect from the frame of collision.
    # If game just started and bird_rect not defined yet, create a default one for drawing.
    # Draw Pipes, Bird, and Score (only if game has started)
    if game_started:
        for pipe in pipes:
            # Top Pipe
            top_pipe_rect_draw = pygame.Rect(pipe['x'], 0, PIPE_WIDTH, pipe['top_pipe_height'])
            pygame.draw.rect(screen, PIPE_COLOR, top_pipe_rect_draw)
            # Bottom Pipe
            bottom_pipe_y_draw = pipe['top_pipe_height'] + PIPE_GAP_SIZE
            bottom_pipe_height_draw = SCREEN_HEIGHT - bottom_pipe_y_draw
            bottom_pipe_rect_draw = pygame.Rect(pipe['x'], bottom_pipe_y_draw, PIPE_WIDTH, bottom_pipe_height_draw)
            pygame.draw.rect(screen, PIPE_COLOR, bottom_pipe_rect_draw)

        current_bird_rect = pygame.Rect(bird_x, bird_y, BIRD_WIDTH, BIRD_HEIGHT) 
        pygame.draw.rect(screen, YELLOW, current_bird_rect)
        
        score_text_surface = score_font.render(str(score), True, WHITE)
        score_text_rect = score_text_surface.get_rect(center=(SCREEN_WIDTH // 2, 50))
        screen.blit(score_text_surface, score_text_rect)
    
    # Display Start Screen or Game Over Screen
    if not game_started:
        # Display Start Screen Message
        title_surface = title_font.render("Flappy Bird", True, BLACK)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
        screen.blit(title_surface, title_rect)

        start_text_surface = start_instruction_font.render("Press Space or Click to Start", True, BLACK)
        start_text_rect = start_text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        screen.blit(start_text_surface, start_text_rect)

    elif game_over: # game_started must be true here
        # Display Game Over Message
        go_text_surface = game_over_font.render("Game Over", True, BLACK)
        go_text_rect = go_text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(go_text_surface, go_text_rect)

        # Display Restart Instructions
        restart_text_surface = restart_font.render("Press 'R' to Restart", True, BLACK)
        restart_text_rect = restart_text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30)) 
        screen.blit(restart_text_surface, restart_text_rect)
        
        # Final score is already displayed by the score display logic that runs if game_started

    pygame.display.flip()  # Update the full display

    # Clock tick
    clock.tick(FPS)

# Quit Pygame
pygame.quit()
