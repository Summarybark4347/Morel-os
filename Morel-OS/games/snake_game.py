import random
import time

try:
    import curses
    CURSES_AVAILABLE = True
    # Standard library import, should not fail if curses is available
    from curses import wrapper as curses_wrapper, error as curses_error
except ImportError:
    CURSES_AVAILABLE = False

    class MockCursesScreen:
        def getmaxyx(self): return (24, 80)  # Default mock size
        def border(self, *args): pass
        def addstr(self, *args): pass
        def addch(self, *args): pass
        def getch(self): return -1 # Simulate no key press
        def nodelay(self, flag): pass
        def timeout(self, delay): pass
        def keyp(self, key): pass # Not used but part of curses
        def clear(self): pass
        def refresh(self): pass
        # Add other methods if your draw_board_curses or game_loop uses them

    class MockCurses:
        # Key constants
        KEY_UP = 259
        KEY_DOWN = 258
        KEY_LEFT = 260
        KEY_RIGHT = 261
        error = type('curses_error', (Exception,), {}) # Mock curses.error exception

        def curs_set(self, visibility): pass
        def wrapper(self, func, *args, **kwargs):
            # In a real mock, you might call func with a MockCursesScreen instance
            print("MockCurses: wrapper called. Curses not available.")
            # To allow some non-curses testing if game_loop is adapted:
            # screen = MockCursesScreen()
            # return func(screen, *args, **kwargs)
        def endwin(self): pass # Important for cleanup in real curses
        # Add any other top-level curses functions used e.g. start_color, init_pair

    # Replace actual curses module with mock if not available
    # This allows the rest of the file to use `curses.` prefix transparently
    curses = MockCurses() 
    curses_wrapper = curses.wrapper # Make wrapper directly accessible if used like that
    curses_error = curses.error     # Make error directly accessible

# Define game constants
# BOARD_WIDTH and BOARD_HEIGHT will now be determined dynamically
MIN_BOARD_WIDTH = 10
MIN_BOARD_HEIGHT = 5
SNAKE_CHAR = "#"
APPLE_CHAR = "0"
EMPTY_CHAR = "." # Or use space ' '

# Conceptual Game State Variables are implicitly defined by the initialize_game function's return dict.

def initialize_game(term_height, term_width):
    """
    Resets the game to an initial state based on terminal dimensions.
    Returns a dictionary representing the game state.
    """
    # Calculate board dimensions
    # -2 for border (left/right or top/bottom), -1 for score line
    board_height = term_height - 3 
    board_width = term_width - 2

    if board_height < MIN_BOARD_HEIGHT or board_width < MIN_BOARD_WIDTH:
        raise Exception(f"Terminal too small. Minimum {MIN_BOARD_WIDTH+2}x{MIN_BOARD_HEIGHT+3} required. Current: {term_width}x{term_height}")

    snake_start_y = board_height // 2
    snake_start_x = board_width // 2
    
    # Initial snake:
    # Head is at (snake_start_y, snake_start_x)
    # Body extends to the left
    snake_body = [
        (snake_start_y, snake_start_x),
        (snake_start_y, snake_start_x - 1),
        (snake_start_y, snake_start_x - 2),
    ]
    
    current_direction = 'RIGHT'
    score = 0
    game_over = False
        
    # Create the game_state dictionary first
    game_state = {
        "snake_body": snake_body,
        "apple_pos": (0,0), # Placeholder, will be overwritten by place_apple
        "current_direction": current_direction,
        "score": score,
        "game_over": game_over,
        "board_width": board_width, # Use calculated board_width
        "board_height": board_height # Use calculated board_height
    }
    # Now place the apple using the formed game_state
    game_state["apple_pos"] = place_apple(game_state["snake_body"], game_state["board_width"], game_state["board_height"])
    return game_state

def place_apple(snake_body, board_width, board_height):
    """
    Randomly finds an empty spot on the board (not occupied by snake_body).
    Returns the (y, x) position for the new apple.
    """
    while True:
        y = random.randint(0, board_height - 1)
        x = random.randint(0, board_width - 1)
        if (y, x) not in snake_body:
            return (y, x)

def update_game_state(game_state, new_direction_intent):
    """
    Updates the game state based on the current direction and handles collisions.
    new_direction_intent is the direction player wants to move.
    """
    if game_state["game_over"]:
        return game_state

    snake_body = list(game_state["snake_body"]) # Make a mutable copy
    current_head_y, current_head_x = snake_body[0]
    current_direction = game_state["current_direction"]

    # Update current_direction based on new_direction_intent, preventing reversal
    if new_direction_intent:
        if new_direction_intent == 'UP' and current_direction != 'DOWN':
            current_direction = 'UP'
        elif new_direction_intent == 'DOWN' and current_direction != 'UP':
            current_direction = 'DOWN'
        elif new_direction_intent == 'LEFT' and current_direction != 'RIGHT':
            current_direction = 'LEFT'
        elif new_direction_intent == 'RIGHT' and current_direction != 'LEFT':
            current_direction = 'RIGHT'
    
    game_state["current_direction"] = current_direction # Store the possibly updated direction

    # Calculate new head position
    new_head_y, new_head_x = current_head_y, current_head_x
    if current_direction == 'UP':
        new_head_y -= 1
    elif current_direction == 'DOWN':
        new_head_y += 1
    elif current_direction == 'LEFT':
        new_head_x -= 1
    elif current_direction == 'RIGHT':
        new_head_x += 1
        
    new_head_pos = (new_head_y, new_head_x)

    # Check for wall collision
    if not (0 <= new_head_x < game_state["board_width"] and \
            0 <= new_head_y < game_state["board_height"]):
        game_state["game_over"] = True
        return game_state

    # Check for self-collision (new head is in the rest of the body)
    # This check must be done BEFORE adding the new head to the body list
    if new_head_pos in snake_body: # If snake is length 1, this won't be true, which is fine
        game_state["game_over"] = True
        return game_state

    # Add new head
    snake_body.insert(0, new_head_pos)

    # Check for apple collision
    ate_apple = False
    if new_head_pos == game_state["apple_pos"]:
        game_state["score"] += 1
        game_state["apple_pos"] = place_apple(snake_body, game_state["board_width"], game_state["board_height"])
        ate_apple = True
    
    if not ate_apple:
        snake_body.pop() # Remove tail if no apple was eaten

    game_state["snake_body"] = snake_body
    return game_state

# This function is now replaced by draw_board_curses
# def draw_board(game_state, stdscr=None): ...

def draw_board_curses(stdscr, game_state):
    """Draws the game board, snake, apple, and score using curses."""
    # Use stdscr.border() for a standard border if available and preferred.
    # Or draw manually like this:
    # Top border
    stdscr.addstr(0, 0, "+" + "-" * game_state["board_width"] + "+")
    # Side borders
    for y_idx in range(game_state["board_height"]):
        stdscr.addstr(y_idx + 1, 0, "|")
        stdscr.addstr(y_idx + 1, game_state["board_width"] + 1, "|")
    # Bottom border
    stdscr.addstr(game_state["board_height"] + 1, 0, "+" + "-" * game_state["board_width"] + "+")

    # Draw empty characters for the play area (within border)
    for y in range(game_state["board_height"]):
        for x in range(game_state["board_width"]):
            stdscr.addstr(y + 1, x + 1, EMPTY_CHAR)

    # Draw apple
    apple_y, apple_x = game_state["apple_pos"]
    if 0 <= apple_y < game_state["board_height"] and 0 <= apple_x < game_state["board_width"]:
        stdscr.addstr(apple_y + 1, apple_x + 1, APPLE_CHAR)

    # Draw snake
    for y, x in game_state["snake_body"]:
        if 0 <= y < game_state["board_height"] and 0 <= x < game_state["board_width"]:
            stdscr.addstr(y + 1, x + 1, SNAKE_CHAR)
            
    # Display score
    score_text = f"Score: {game_state['score']}"
    stdscr.addstr(game_state["board_height"] + 2, 1, score_text) # Below border


def game_loop(stdscr):
    """Main game loop using curses."""
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(150) # Adjust for game speed

    term_height, term_width = stdscr.getmaxyx()
    try:
        game_state = initialize_game(term_height, term_width)
    except Exception as e: # Catch "Terminal too small"
        stdscr.clear()
        # Check if terminal is large enough to even print the error
        if term_height > 0 and term_width > len(str(e)) + 2 :
            stdscr.addstr(0, 0, str(e))
        else: # Fallback to console if terminal is extremely small
            # This print might not be visible if curses is still active without wrapper cleanup
            # but wrapper should handle it.
            print(str(e)) 
        stdscr.refresh()
        time.sleep(3)
        return # Exit game_loop

    while not game_state['game_over']:
        try:
            key = stdscr.getch() 
            
            
            new_direction_intent = None 

            # Check for arrow keys or WASD keys
            # Important: game_state['current_direction'] is the snake's actual current heading
            if (key == curses.KEY_UP or key == ord('w')) and game_state['current_direction'] != 'DOWN':
                new_direction_intent = 'UP'
            elif (key == curses.KEY_DOWN or key == ord('s')) and game_state['current_direction'] != 'UP':
                new_direction_intent = 'DOWN'
            elif (key == curses.KEY_LEFT or key == ord('a')) and game_state['current_direction'] != 'RIGHT':
                new_direction_intent = 'LEFT'
            elif (key == curses.KEY_RIGHT or key == ord('d')) and game_state['current_direction'] != 'LEFT':
                new_direction_intent = 'RIGHT'
            elif key == ord('q') or key == 27: # 'q' or ESC
                break 

            game_state = update_game_state(game_state, new_direction_intent)

            stdscr.clear()
            draw_board_curses(stdscr, game_state)
            stdscr.refresh()

            if game_state['game_over']:
                msg_y = (game_state['board_height'] + 2) // 2 # Center within bordered area
                msg_x_offset = (game_state['board_width'] + 2) // 2
                
                game_over_msg = "GAME OVER!"
                score_msg = f"Final Score: {game_state['score']}"
                
                # Ensure messages fit, otherwise they might cause error or wrap badly
                if msg_x_offset - len(game_over_msg)//2 >=0 and msg_x_offset + len(game_over_msg)//2 < term_width and msg_y < term_height :
                     stdscr.addstr(msg_y, msg_x_offset - len(game_over_msg)//2, game_over_msg)
                if msg_x_offset - len(score_msg)//2 >=0 and msg_x_offset + len(score_msg)//2 < term_width and msg_y + 1 < term_height :
                     stdscr.addstr(msg_y + 1, msg_x_offset - len(score_msg)//2, score_msg)
                
                stdscr.refresh()
                time.sleep(2)
                break
        
        except curses.error as e: # Catch curses errors during the loop (e.g. terminal resize)
            # Clean up curses before printing error that might be outside screen
            # stdscr.nodelay(0)
            # stdscr.keypad(0)
            # curses.echo()
            # curses.endwin() # Wrapper should handle this, but can be explicit
            print(f"Curses error during game: {e}. Terminal might have been resized.")
            # It's tricky to recover from this gracefully without restarting the curses session.
            # For now, just exit the game loop.
            break 
        except Exception as e: # Catch other unexpected errors
            print(f"Unexpected error in game loop: {e}")
            break


if __name__ == "__main__":
    if CURSES_AVAILABLE:
        try:
            curses_wrapper(game_loop) # Use the imported curses_wrapper
        except Exception as e:
            # This top-level catch is for errors outside curses.wrapper's own handling,
            # or if curses itself is not available and the mock wrapper has an issue.
            # If curses was active, curses.endwin() should ideally be called.
            # However, curses.wrapper is very good at ensuring this.
            # If curses is truly available, wrapper handles endwin.
            # If curses is not available, our mock wrapper doesn't init curses.
            print(f"An unexpected error occurred: {e}")
            if CURSES_AVAILABLE: # If real curses was thought to be in use
                try:
                    curses.endwin() # Attempt cleanup if not done by wrapper
                except Exception as ce:
                    print(f"Failed to call curses.endwin(): {ce}")
            print("Exited Snake game due to an error.")
    else:
        print("Curses library is not available on this system.")
        print("Please install it (e.g., 'pip install windows-curses' on Windows) to play Snake interactively.")
        print("You can try running the game logic tests if available in a non-curses mode (not implemented here).")
