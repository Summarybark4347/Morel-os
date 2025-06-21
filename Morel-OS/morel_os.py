import os
import subprocess
import sys
import platform
import shlex # For robust command line parsing
import shutil # For copyfile command

try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
    # print("DEBUG: pyperclip imported successfully in morel_os.py")
except ImportError:
    pyperclip = None 
    CLIPBOARD_AVAILABLE = False
    print("DEBUG: pyperclip module not found. Clipboard commands (`copytext`, `pastetext`) will not be available. "
          "Install it with: pip install pyperclip")

try:
    from rich.console import Console
    from rich.text import Text
    from rich.panel import Panel
    from rich.prompt import Prompt
    from rich.style import Style
    RICH_AVAILABLE = True
    console = Console()
    # Define some styles
    error_style = Style(color="red", bold=True)
    prompt_style_base = "MorelOS"
    path_style = Style(color="blue", bold=True)
    info_label_style = Style(color="green")
    logo_style = Style(color="magenta", bold=True)
    file_style = Style(color="white")
    dir_style = Style(color="cyan", bold=True)
except ImportError:
    RICH_AVAILABLE = False
    console = None # Set to None if rich is not available initially
    # Define dummy print and input for graceful fallback
    class DummyConsoleFallback: # Renamed to avoid conflict if console is later defined
        def print(self, *args, **kwargs):
            # Remove style kwarg if present, as standard print doesn't use it
            kwargs.pop('style', None)
            kwargs.pop('Dim', None) # Assuming Dim might be a Rich-specific kwarg
            print(*args, **kwargs)
        def input(self, *args, **kwargs):
            return input(*args)
    
    if console is None: # If rich failed, use fallback
        console = DummyConsoleFallback()

    # Dummy Prompt class for fallback
    class Prompt: # This is okay as it's only used when RICH_AVAILABLE is true
        @staticmethod
        def ask(prompt_text):
            return input(prompt_text) # Fallback input

    # Define dummy styles if rich is not available
    error_style = "" 
    prompt_style_base = "MorelOS" # This is a string, not a Style object
    path_style = ""
    info_label_style = ""
    logo_style = ""
    file_style = ""
    dir_style = ""
    # Print this message only if console is the fallback, to avoid double print if rich is there but then fails later
    if isinstance(console, DummyConsoleFallback):
        print("Rich library not found. For a richer experience, please install it with: pip install rich")

# Attempt to import snake_game components
try:
    from snake_game import game_loop as snake_game_loop, CURSES_AVAILABLE as SNAKE_CURSES_AVAILABLE
    import curses # To use curses.wrapper if available
    # CURSES_AVAILABLE from Morel OS perspective, SNAKE_CURSES_AVAILABLE from snake_game's perspective
    # We primarily care about SNAKE_CURSES_AVAILABLE for running the game.
except ImportError as e:
    snake_game_loop = None
    SNAKE_CURSES_AVAILABLE = False
    # Define a placeholder for curses if it's not already defined in the main scope
    if 'curses' not in globals():
        class curses: # Minimal mock
            class error(Exception): pass
            @staticmethod
            def wrapper(func, *args, **kwargs):
                # Use Morel OS's console for printing errors, whether rich or dummy
                console.print("Error: Curses or snake_game module not fully available.", style=error_style if RICH_AVAILABLE else "")
                console.print("Snake game cannot be started.", style=error_style if RICH_AVAILABLE else "")
                if "curses" not in str(e).lower():
                    console.print(f"Import Error: {e}", style=error_style if RICH_AVAILABLE else "")
    # If snake_game itself failed to import curses, SNAKE_CURSES_AVAILABLE would be false.
    # If import curses here fails, then curses.wrapper will also fail.


MOREL_OS_VERSION = "0.1.0" # This should be updated if it's meant to reflect morel_os.py version

ASCII_LOGO = """
     /$$      /$$                               /$$          /$$$$$$   /$$$$$$ 
    | $$$    /$$$                              | $$         /$$__  $$ /$$__  $$
    | $$$$  /$$$$  /$$$$$$   /$$$$$$   /$$$$$$ | $$        | $$  \ $$| $$  \__/
    | $$ $$/$$ $$ /$$__  $$ /$$__  $$ /$$__  $$| $$ /$$$$$$| $$  | $$|  $$$$$$ 
    | $$  $$$| $$| $$  \ $$| $$  \__/| $$$$$$$$| $$|______/| $$  | $$ \____  $$
    | $$\  $ | $$| $$  | $$| $$      | $$_____/| $$        | $$  | $$ /$$  \ $$
    | $$ \/  | $$|  $$$$$$/| $$      |  $$$$$$$| $$        |  $$$$$$/|  $$$$$$/
    |__/     |__/ \______/ |__/       \_______/|__/         \______/  \______/ 
"""

def strip_rich_markup(text):
    """A simple function to remove rich-style markup tags."""
    import re
    return re.sub(r"\[/?\w+\]", "", text)

INFO2_TEXT_CONTENT = (
    "This is Morel-OS, a free open source OS made with Jules AI, Python, and Henry Morel.\n"
    "This OS has a lot of cool features and commands. Down here I will show you some commands:\n\n"
    "[bold]Commands:[/bold]\n"
    "  [cyan]ls[/cyan]                     - to list files and directories\n"
    "  [cyan]ls <some_directory>[/cyan]  - to list contents of a specific directory\n"
    "  [cyan]cd <some_directory>[/cyan]  - to change the current directory\n"
    "  [cyan]cd ..[/cyan]                - to move to the parent directory\n"
    "  [cyan]pwd[/cyan]                  - to print the current working directory\n"
    "  [cyan]run <your_script.py>[/cyan] - to execute a Python script\n"
    "                           (e.g., a simple hello.py that prints 'Hello from script!')\n"
    "  [cyan]info[/cyan]                 - to display information about Morel OS\n"
    "  [cyan]info2[/cyan]                - to display this extended information and command list (alias: help, help2)\n"
    "  [cyan]femboy[/cyan]               - to display a special ASCII art\n"
    "  [cyan]snake[/cyan]                 - play Snake (WASD/arrows, high scores, requires curses)\n"
    "  [cyan]startgui[/cyan]              - launch graphical launcher (info, basic terminal with 'echo'/'clear')\n"
    "  [cyan]open <file_or_app> [args][/cyan] - open a file or run an executable (platform dependent)\n"
    "  [cyan]date[/cyan]                  - to display the current date and time\n"
    "  [cyan]help[/cyan]                  - to display this detailed help message (alias for info2)\n"
    "  [cyan]help2[/cyan]                 - to display this detailed help message (alias for info2)\n"
    # 'restart' command was removed, so its help text should be removed.
    "  [cyan]shutdown[/cyan]              - to shut down and exit Morel OS\n"
    # 'exit' and 'quit' commands were removed, so their help text should be removed.
    "  [cyan]copytext <text...>[/cyan]     - copies text to clipboard (requires 'pip install pyperclip')\n"
    "  [cyan]pastetext[/cyan]              - pastes text from clipboard (requires 'pip install pyperclip')"
)

FEMBOY_ASCII_ART = """
                                                             bbbbbbbb
    ffffffffffffffff                                         b::::::b
   f::::::::::::::::f                                        b::::::b
  f::::::::::::::::::f                                       b::::::b
  f::::::fffffff:::::f                                        b:::::b
  f:::::f       ffffffeeeeeeeeeeee       mmmmmmm    mmmmmmm   b:::::bbbbbbbbb       ooooooooooo yyyyyyy           yyyyyyy
  f:::::f           ee::::::::::::ee   mm:::::::m  m:::::::mm b::::::::::::::bb   oo:::::::::::ooy:::::y         y:::::y 
 f:::::::ffffff    e::::::eeeee:::::eem::::::::::mm::::::::::mb::::::::::::::::b o:::::::::::::::oy:::::y       y:::::y  
 f::::::::::::f   e::::::e     e:::::em::::::::::::::::::::::mb:::::bbbbb:::::::bo:::::ooooo:::::o y:::::y     y:::::y   
 f::::::::::::f   e:::::::eeeee::::::em:::::mmm::::::mmm:::::mb:::::b    b::::::bo::::o     o::::o  y:::::y   y:::::y    
 f:::::::ffffff   e:::::::::::::::::e m::::m   m::::m   m::::mb:::::b     b:::::bo::::o     o::::o   y:::::y y:::::y     
  f:::::f         e::::::eeeeeeeeeee  m::::m   m::::m   m::::mb:::::b     b:::::bo::::o     o::::o    y:::::y:::::y      
  f:::::f         e:::::::e           m::::m   m::::m   m::::mb:::::b     b:::::bo::::o     o::::o     y:::::::::y       
 f:::::::f        e::::::::e          m::::m   m::::m   m::::mb:::::bbbbbb::::::bo:::::ooooo:::::o      y:::::::y        
 f:::::::f         e::::::::eeeeeeee  m::::m   m::::m   m::::mb::::::::::::::::b o:::::::::::::::o       y:::::y         
 f:::::::f          ee:::::::::::::e  m::::m   m::::m   m::::mb:::::::::::::::b   oo:::::::::::oo       y:::::y          
 fffffffff            eeeeeeeeeeeeee  mmmmmm   mmmmmm   mmmmmmbbbbbbbbbbbbbbbb      ooooooooooo        y:::::y           
                                                                                                      y:::::y            
                                                                                                     y:::::y             
                                                                                                    y:::::y              
                                                                                                   y:::::y               
                                                                                                  yyyyyyy                
"""

# femboy_command() is now replaced by femboy_command_string() below
# info2_command() is now replaced by info2_command_string() below

import time # For date command

# --- String-returning command functions ---

def get_current_datetime_string() -> str:
    """Returns the current date and time as a formatted string."""
    return time.strftime("%Y-%m-%d %H:%M:%S")

def femboy_command_string() -> str:
    """Returns the FEMBOY_ASCII_ART string."""
    return FEMBOY_ASCII_ART

def info2_command_string() -> str:
    """
    Prepares the string for the 'info2' command.
    Returns INFO2_TEXT_CONTENT, possibly stripped of Rich markup if Rich is not available
    (though the processor will handle actual printing).
    For now, it returns the raw string with markup, and the caller (main loop) decides.
    If we want the processor to always get plain text unless Rich is printing,
    this function would need to be:
    return strip_rich_markup(INFO2_TEXT_CONTENT) if not RICH_AVAILABLE else INFO2_TEXT_CONTENT
    However, INFO2_TEXT_CONTENT is already a plain string with markup tags.
    The console.print function handles rendering or not. So just return it.
    """
    return INFO2_TEXT_CONTENT


def info_command_string() -> str:
    """Prepares the informational string for the 'info' command."""
    python_version = sys.version.split()[0]
    # platform.platform() can be quite verbose, let's use system and release
    platform_info = f"{platform.system()} {platform.release()}"
    cpu_info = platform.processor() # This can be empty on some systems/Python builds

    lines = [
        ASCII_LOGO.strip(), # Remove leading/trailing newlines from the art
        "\nSystem Information:",
        f"  OS Name         : Morel OS",
        f"  OS Version      : {MOREL_OS_VERSION}",
        f"  Python Version  : {python_version}",
        f"  Platform        : {platform_info}",
    ]
    if cpu_info: # Only add CPU if available
        lines.append(f"  CPU             : {cpu_info}")
    lines.append("\nFor a list of commands, type: info2")
    
    return "\n".join(lines)

def pwd_command_string(current_path: str) -> str:
    """Prepares the string for the 'pwd' command."""
    return current_path

def cd_command_processor(current_path: str, target_path_arg: str = None) -> tuple[str, str]:
    """
    Processes the 'cd' command, resolves paths, and validates.
    Does NOT change the directory itself.
    Returns: (new_potential_path, error_message_string)
             If successful, error_message_string is empty.
    """
    if target_path_arg is None or target_path_arg == "" or target_path_arg == "~":
        # If no argument or "~", target home directory
        resolved_new_path = os.path.expanduser("~")
        # For display in error messages, show what user typed or implies
        target_path_display = target_path_arg if target_path_arg is not None else "~" 
    elif os.path.isabs(target_path_arg):
        resolved_new_path = os.path.abspath(target_path_arg) # Normalize like .. in abs paths
        target_path_display = target_path_arg
    else:
        # Relative path
        resolved_new_path = os.path.abspath(os.path.join(current_path, target_path_arg))
        target_path_display = target_path_arg

    try:
        if not os.path.exists(resolved_new_path):
            return current_path, f"cd: no such file or directory: {target_path_display}"
        if not os.path.isdir(resolved_new_path):
            return current_path, f"cd: not a directory: {target_path_display}"
        
        # Attempt to list dir contents as a proxy for readability/permission for cd
        # This is not a perfect check for all systems/permissions but a common one.
        # os.access(resolved_new_path, os.R_OK | os.X_OK) is another option but can be complex with X_OK on dirs.
        os.listdir(resolved_new_path) 

        return resolved_new_path, "" # Success: new path, no error message
    except PermissionError:
        return current_path, f"cd: permission denied: {target_path_display}"
    except Exception as e: # Catch other potential errors during path validation
        return current_path, f"cd: an error occurred with path '{target_path_display}': {e}"


def ls_command_string(current_os_path: str, path_arg: str = None) -> str:
    """
    Prepares the string for the 'ls' command.
    Lists files and directories in the specified path.
    current_os_path is the CWD of Morel OS.
    path_arg is the argument given to ls (can be None, relative, or absolute).
    """
    output_lines = []
    target_path_display = path_arg if path_arg else "." # For error messages

    if path_arg is None:
        # No argument, list current_os_path
        resolved_target_path = current_os_path
    elif os.path.isabs(path_arg):
        # Absolute path argument
        resolved_target_path = path_arg
    else:
        # Relative path argument
        resolved_target_path = os.path.abspath(os.path.join(current_os_path, path_arg))

    if not os.path.exists(resolved_target_path):
        return f"ls: cannot access '{target_path_display}': No such file or directory"
    
    if not os.path.isdir(resolved_target_path):
        # If it exists but is not a directory, behavior can vary.
        # Standard 'ls' would list info about the file.
        # For this version, let's treat it as an error similar to "not a directory" if used as a path for listing.
        # Or, if it's a file and path_arg was given, just list that file.
        # For now, simplifying: if it's not a dir, can't list its contents.
        # If path_arg pointed directly to a file, we could just show that file.
        # Let's assume 'ls' is primarily for listing directory contents.
        if path_arg is not None: # Only error if they tried to list contents of a file path
             return f"ls: cannot list contents of '{target_path_display}': Not a directory"
        else: # if path_arg was None, this means current_os_path is somehow a file, which is odd.
             return f"ls: current path '{target_path_display}' is not a directory."


    try:
        entries = os.listdir(resolved_target_path)
        entries.sort() # Sort for consistent output

        for entry in entries:
            full_path_to_entry = os.path.join(resolved_target_path, entry)
            if RICH_AVAILABLE:
                # These style tags will be interpreted by console.print() if it's the Rich console
                if os.path.isdir(full_path_to_entry):
                    output_lines.append(f"[bold cyan]📁 {entry}[/bold cyan]")
                else: # Must be a file or link, treat as file for simplicity
                    output_lines.append(f"[white]📄 {entry}[/white]")
            else:
                if os.path.isdir(full_path_to_entry):
                    output_lines.append(f"D: {entry}")
                else:
                    output_lines.append(f"F: {entry}")
        
        if not output_lines:
            return f"Directory '{target_path_display}' is empty." # Or just an empty string
            
        return "\n".join(output_lines)

    except PermissionError:
        return f"ls: cannot open directory '{target_path_display}': Permission denied"
    except Exception as e: # Catch other potential OS errors
        return f"ls: error accessing '{target_path_display}': {e}"

def run_command_string(current_path: str, script_name_arg: str, script_args: list[str]) -> str:
    """
    Prepares the string output for the 'run' command by executing a Python script.
    """
    if not script_name_arg:
        return "run: missing script name"

    # Resolve script path
    if os.path.isabs(script_name_arg):
        resolved_script_path = script_name_arg
    else:
        resolved_script_path = os.path.abspath(os.path.join(current_path, script_name_arg))

    if not resolved_script_path.endswith(".py"):
        return f"run: not a Python script: {script_name_arg}"

    if not os.path.exists(resolved_script_path) or not os.path.isfile(resolved_script_path):
        return f"run: script not found: {script_name_arg}"

    try:
        # sys.executable ensures using the same Python interpreter
        completed_process = subprocess.run(
            [sys.executable, resolved_script_path] + script_args,
            capture_output=True,
            text=True,
            check=False, # Do not raise exception for non-zero exit codes
            cwd=current_path # Run script in the context of Morel OS's current directory
        )
        
        output_parts = []
        if completed_process.stdout:
            # For Rich, we might want to avoid prefix if the output itself is Rich-formatted.
            # For now, simple prefixing.
            # If RICH_AVAILABLE, could use f"[green]Output:[/green]\n{completed_process.stdout.strip()}"
            output_parts.append(f"Output:\n{completed_process.stdout.strip()}")
            
        if completed_process.stderr:
            # If RICH_AVAILABLE, could use f"[red]Errors:[/red]\n{completed_process.stderr.strip()}"
            output_parts.append(f"Errors:\n{completed_process.stderr.strip()}")
            
        if not output_parts:
            return "[Script executed with no output]"
            
        return "\n\n".join(output_parts)

    except Exception as e:
        return f"run: failed to execute script '{script_name_arg}': {e}"


# Helper function to print messages within Morel OS, adapted from existing style
def message_user_internal(message, style_error=False, style_info=False):
    # Uses global 'console' and 'RICH_AVAILABLE'
    # Also uses global 'error_style' and 'info_label_style' (both are Style objects)

    if RICH_AVAILABLE and console:
        style_to_apply = None
        if style_error:
            style_to_apply = error_style 
        elif style_info:
            style_to_apply = info_label_style 
        
        # console.print can take Style objects directly
        if style_to_apply:
            console.print(message, style=style_to_apply)
        else:
            console.print(message)
    else:
        # Basic print, style information is lost but message is conveyed
        print(message)


# --- Commands that have side effects or don't fit the string-return model well ---
# These will be called directly by execute_morel_command but their primary output 
# might not be a simple string, or they manage their own user interaction.

def startgui_command_action(): # Renamed to avoid conflict if we wanted a string version
    """Handles the logic for the startgui command (launching GUI)."""
    # This function will print its own messages using message_user_internal
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        gui_script_path = os.path.join(script_dir, "gui_launcher.py")

        if not os.path.exists(gui_script_path):
            message_user_internal("Error: gui_launcher.py not found in the same directory.", style_error=True)
            return

        python_executable = sys.executable
        
        # Keep this basic print for now, or integrate with message_user_internal if preferred
        print(f"DEBUG: Attempting to launch GUI: {python_executable} {gui_script_path}") 
        process = subprocess.Popen([python_executable, gui_script_path])
        message_user_internal(f"GUI launcher started (PID: {process.pid}). Check your desktop for the window.", style_info=True)
        return # This action command doesn't return a string for main loop to print

    except FileNotFoundError: 
        message_user_internal("Error: Python interpreter not found. Cannot start GUI.", style_error=True)
    except Exception as e:
        message_user_internal(f"An error occurred while trying to start the GUI: {e}", style_error=True)
    return # Ensure return in all paths

def snake_command_action(): # Renamed
    """Handles the logic for the snake command (launching game)."""
    # This function will print its own messages using message_user_internal or direct console
    if not SNAKE_CURSES_AVAILABLE or not snake_game_loop:
        if RICH_AVAILABLE and console: 
            console.print("[bold red]Error: Snake game module or its curses dependency is not available.[/bold red]")
            console.print("On Linux/macOS, ensure 'curses' is available (often part of standard Python).")
            console.print("On Windows, you might need to install 'windows-curses': [italic]pip install windows-curses[/italic]")
        else: 
            print("Error: Snake game module or its curses dependency is not available.")
            print("On Linux/macOS, ensure 'curses' is available (often part of standard Python).")
            print("On Windows, you might need to install 'windows-curses': pip install windows-curses")
        return

    if RICH_AVAILABLE and console:
        console.print("Starting Snake game... (Press 'q' or ESC to quit the game)", style="yellow")
    else:
        print("Starting Snake game... (Press 'q' or ESC to quit the game)")
    
    try:
        curses.wrapper(snake_game_loop) # 'curses' here refers to the one imported/mocked in morel_os.py
    except curses.error as e: 
        message_user_internal(f"A problem occurred while running the Snake game: {e}", style_error=True)
    except Exception as e: 
         message_user_internal(f"An unexpected error occurred in the Snake game: {e}", style_error=True)

    if RICH_AVAILABLE and console: # This message will be printed by the main loop after execute_morel_command returns
        # For now, let snake_command_action handle its own "Returned to Morel OS" if needed, or remove it.
        # The command processor will return a generic message.
        pass # console.print("Returned to Morel OS.", style="yellow") 
    else:
        pass # print("Returned to Morel OS.")
    return # This action command doesn't return a string for main loop to print


# --- Central Command Processor ---
def execute_morel_command(command_line_string: str, current_path: str) -> tuple[str, str, bool]:
    """
    Processes a command line string and returns output, new path, and exit status.
    """
    try:
        parts = shlex.split(command_line_string.strip())
    except ValueError as e: # Handle shlex parsing errors (e.g., unmatched quotes)
        return f"Error parsing command: {e}", current_path, False

    if not parts:
        return "", current_path, False

    command = parts[0].lower()
    args = parts[1:]

    output_string = ""
    new_current_path = current_path
    should_exit = False

    # The 'exit' and 'quit' commands are removed. 
    # 'shutdown' and 'restart' are the primary ways to exit.
    if command == "shutdown":
        output_string = "Morel OS is shutting down..."
        should_exit = True
    # All other commands follow
    elif command == "date":
        output_string = get_current_datetime_string()
    elif command == "help":
        output_string = info2_command_string()
    elif command == "help2": 
        output_string = info2_command_string() 
    elif command == "info":
        output_string = info_command_string()
    elif command == "info2":
        output_string = info2_command_string() 
    elif command == "femboy":
        output_string = femboy_command_string()
    elif command == "pwd":
        output_string = pwd_command_string(current_path)
    elif command == "ls":
        path_arg = args[0] if args else None
        output_string = ls_command_string(current_path, path_arg)
    elif command == "cd":
        target_arg = args[0] if args else None
        proposed_path, message = cd_command_processor(current_path, target_arg)
        if message:
            output_string = message 
        else:
            try:
                os.chdir(proposed_path)
                new_current_path = proposed_path 
            except Exception as e:
                output_string = f"cd: error changing directory to '{proposed_path}': {e}"
    elif command == "run":
        script_name = args[0] if args else None
        script_args_list = args[1:] 
        if not script_name:
            output_string = "run: missing script name"
        else:
            output_string = run_command_string(current_path, script_name, script_args_list)
    elif command == "copytext":
        if not CLIPBOARD_AVAILABLE:
            output_string = "copytext: pyperclip library not available. Please install it using 'pip install pyperclip'."
        elif not args:
            output_string = "copytext: no text provided to copy."
        else:
            text_to_copy = " ".join(args)
            try:
                pyperclip.copy(text_to_copy) # pyperclip should be available if CLIPBOARD_AVAILABLE is True
                output_string = "Text copied to clipboard."
            except pyperclip.PyperclipException as e: 
                output_string = f"copytext: error copying to clipboard - {e}"
            except Exception as e: 
                output_string = f"copytext: unexpected error during copy - {e}"
    elif command == "copyfile":
        if len(args) != 2:
            output_string = "copyfile: incorrect number of arguments. Usage: copyfile <source_file> <destination_file_or_directory>"
        else:
            source_file_arg = args[0]
            destination_arg = args[1]

            source_file_path = os.path.abspath(os.path.join(current_path, source_file_arg) if not os.path.isabs(source_file_arg) else source_file_arg)
            
            if not os.path.exists(source_file_path):
                output_string = f"copyfile: source file '{source_file_arg}' not found at '{source_file_path}'."
            elif not os.path.isfile(source_file_path):
                output_string = f"copyfile: source '{source_file_arg}' is not a file."
            else:
                resolved_destination_path = os.path.abspath(os.path.join(current_path, destination_arg) if not os.path.isabs(destination_arg) else destination_arg)
                
                final_dest_path_for_shutil = resolved_destination_path
                
                try:
                    if os.path.isdir(resolved_destination_path):
                        # shutil.copy2 handles copying into an existing directory
                        pass # No change to final_dest_path_for_shutil needed
                    else: 
                        dest_parent_dir = os.path.dirname(resolved_destination_path)
                        if not os.path.exists(dest_parent_dir):
                             output_string = f"copyfile: destination directory '{dest_parent_dir}' does not exist."
                             # Early return for this specific error before shutil.copy2
                             return (output_string, current_path, False) 
                        # If resolved_destination_path is an existing file, shutil.copy2 will overwrite it.

                    shutil.copy2(source_file_path, final_dest_path_for_shutil)
                    
                    if os.path.isdir(final_dest_path_for_shutil): # If copied into a directory
                         output_string = f"File '{os.path.basename(source_file_path)}' copied into directory '{final_dest_path_for_shutil}'."
                    else:
                         output_string = f"File '{os.path.basename(source_file_path)}' copied to '{final_dest_path_for_shutil}'."

                except shutil.SameFileError:
                    output_string = "copyfile: source and destination are the same file."
                except PermissionError:
                    output_string = f"copyfile: permission denied for '{destination_arg}'."
                except Exception as e:
                    output_string = f"copyfile: error copying file - {e}"
    elif command == "pastetext":
        if not CLIPBOARD_AVAILABLE:
            output_string = "pastetext: pyperclip library not available. Please install it using 'pip install pyperclip'."
        else:
            try:
                pasted_text = pyperclip.paste() if pyperclip else None # Check if pyperclip is not None
                if pasted_text:
                    output_string = pasted_text
                else:
                    output_string = "pastetext: clipboard is empty or does not contain plain text."
            except pyperclip.PyperclipException as e:
                output_string = f"pastetext: error pasting from clipboard - {e}"
            except Exception as e:
                output_string = f"pastetext: unexpected error during paste - {e}"
    elif command == "open":
        if not args:
            output_string = "open: missing application name or path"
        else:
            app_to_open = args[0]
            app_args_for_open = args[1:]
            output_string = f"Attempting to open '{app_to_open}'..."
            try:
                if os.name == 'nt': # For Windows
                    try:
                        os.startfile(app_to_open) 
                        output_string = f"Attempting to open '{app_to_open}' with default application..."
                    except OSError: # Catch specific error from startfile
                        # If startfile fails, try Popen for executables or commands in PATH
                        subprocess.Popen([app_to_open] + app_args_for_open, creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP, close_fds=True)
                        output_string = f"Attempting to launch '{app_to_open}' as a command..."
                elif sys.platform == 'darwin': # For macOS
                    subprocess.Popen(['open', app_to_open] + app_args_for_open)
                elif sys.platform.startswith('linux'): # For Linux
                    subprocess.Popen(['xdg-open', app_to_open] + app_args_for_open)
                else:
                    output_string = f"open: unsupported operating system '{sys.platform}'"
            except FileNotFoundError:
                output_string = f"open: command or application '{app_to_open}' not found."
            except Exception as e:
                output_string = f"open: failed to open '{app_to_open}'. Error: {e}"
    elif command == "startgui":
        startgui_command_action() 
        output_string = "GUI launcher initiated. Check your desktop." 
    elif command == "snake":
        snake_command_action() 
        output_string = "Snake game session ended. Returned to Morel OS." 
    else:
        output_string = f"Unknown command: {command}"

    return output_string, new_current_path, should_exit


def main():
    # Ensure console is defined, especially if RICH_AVAILABLE might be true
    # but the initial 'console = Console()' failed for some reason (though unlikely with current structure)
    # This is more of a safeguard. The current try-except for rich import handles it.
    global console
    # Initialize current_path once
    current_path = os.getcwd() 
    
    if RICH_AVAILABLE and not isinstance(console, Console): 
        console = Console() 
    elif not RICH_AVAILABLE and not hasattr(console, 'print'): 
        console = DummyConsoleFallback()

    while True:
        try:
            # Prompt construction
            if RICH_AVAILABLE:
                prompt_text = Text(f"{prompt_style_base}:")
                prompt_text.append(current_path, style=path_style)
                prompt_text.append("> ")
                user_input_str = console.input(prompt_text)
            else:
                # Basic prompt for non-Rich environments
                plain_prompt = f"{prompt_style_base}:{current_path}> "
                user_input_str = input(plain_prompt)

            if not user_input_str.strip(): # Handle empty input by continuing to next prompt
                continue

            output_str, new_path, should_exit = execute_morel_command(user_input_str, current_path)
            
            current_path = new_path # Update current path regardless of output or exit status

            if output_str: # Only print if there's something to print
                # console.print handles Rich markup if RICH_AVAILABLE is true
                # and DummyConsoleFallback.print handles plain text (though it doesn't strip Rich tags)
                console.print(output_str)

            if should_exit:
                break # Exit the main loop
            
        except KeyboardInterrupt:
            # Use message_user_internal for styled exit message if possible
            message_user_internal("\nExiting MorelOS... (Ctrl+C)", style_info=True)
            break
        except EOFError: # Ctrl+D
            message_user_internal("\nExiting MorelOS... (EOF)", style_info=True)
            break
        except Exception as e:
            # General error reporting for unexpected issues in the main loop
            if RICH_AVAILABLE:
                console.print(f"An unexpected error occurred in the main loop: {e}", style=error_style)
                console.print_exception(show_locals=True) # Rich traceback
            else:
                print(f"An unexpected error occurred in the main loop: {e}")
                import traceback
                traceback.print_exc()
            # Decide if such an error should terminate the OS or try to continue
            # For now, let's try to continue, but this could be changed.


if __name__ == "__main__":
    main()
