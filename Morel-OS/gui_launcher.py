import tkinter as tk
from tkinter import scrolledtext
import platform
import sys
import os 
import subprocess 
import re 

try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True 
    # Optional: print("DEBUG: pyperclip imported successfully in gui_launcher.py")
except ImportError:
    pyperclip = None 
    CLIPBOARD_AVAILABLE = False
    # Optional: print("DEBUG: pyperclip not found in gui_launcher.py. GUI clipboard features may be limited.")
    print("DEBUG: pyperclip module not found. GUI clipboard features will be limited. "
          "Install it with: pip install pyperclip")


# --- Global Constants (local to GUI Launcher) ---
MOREL_OS_VERSION = "0.3.1 (GUI Standalone)" # Indicate it's the GUI's version
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
INFO2_TEXT_CONTENT = (
    "This is Morel-OS (Graphical Launcher).\n"
    "Features include in-window info display and a basic terminal.\n\n"
    "[bold]Supported Commands (GUI Terminal):[/bold]\n"
    "  [cyan]info[/cyan]                 - display system and OS information\n"
    "  [cyan]info2[/cyan]                - display this help text\n"
    "  [cyan]femboy[/cyan]               - display special ASCII art\n"
    "  [cyan]pwd[/cyan]                  - print the current working directory (for the GUI)\n"
    "  [cyan]ls [path][/cyan]            - list directory contents (plain text)\n"
    "  [cyan]cd <directory>[/cyan]       - change current directory (for the GUI)\n"
    "  [cyan]run <script.py> [args][/cyan] - execute a Python script (output in GUI)\n"
    "  [cyan]echo [message][/cyan]       - display a message (built-in to GUI terminal)\n"
    "  [cyan]clear[/cyan]                - clear the GUI terminal screen (built-in)\n"
    "  [cyan]startgui[/cyan]             - (this GUI is already running)\n"
    "  [cyan]snake[/cyan]                - (unavailable directly in GUI terminal)\n"
    "  [cyan]exit / quit[/cyan]          - to hide the terminal input field (not to close GUI)\n"
    "\nUse the main 'Exit' button to close the GUI launcher."
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
# HIGHSCORE_FILE is not used directly by GUI, snake game manages its own.
RICH_AVAILABLE = False # GUI uses plain text display in its terminal area.

# --- Helper Functions (Local to GUI Launcher) ---
def strip_rich_markup(text: str) -> str:
    """Simple function to remove Rich-style markup tags."""
    # Improved regex to handle tags with values or spaces if they were to appear.
    return re.sub(r"\[/?[\w\s=\[\]#]+\]", "", text)

# --- Command Logic Functions (Local to GUI Launcher) ---
def info_command_string() -> str:
    python_version = sys.version.split()[0]
    platform_info = f"{platform.system()} {platform.release()}"
    cpu_info = platform.processor()

    lines = [
        ASCII_LOGO.strip(),
        "\nSystem Information:",
        f"  OS Name         : Morel OS (Graphical Launcher)",
        f"  OS Version      : {MOREL_OS_VERSION}",
        f"  Python Version  : {python_version}",
        f"  Platform        : {platform_info}",
    ]
    if cpu_info:
        lines.append(f"  CPU             : {cpu_info}")
    lines.append("\nType 'info2' in terminal for more commands and details.")
    return "\n".join(lines)

def info2_command_string() -> str:
    return INFO2_TEXT_CONTENT

def femboy_command_string() -> str:
    return FEMBOY_ASCII_ART

def pwd_command_string(current_path: str) -> str:
    return current_path

def ls_command_string(current_os_path: str, path_arg: str = None) -> str:
    output_lines = []
    target_path_display = path_arg if path_arg else "."
    if path_arg is None:
        resolved_target_path = current_os_path
    elif os.path.isabs(path_arg):
        resolved_target_path = path_arg
    else:
        resolved_target_path = os.path.abspath(os.path.join(current_os_path, path_arg))

    if not os.path.exists(resolved_target_path):
        return f"ls: cannot access '{target_path_display}': No such file or directory"
    if not os.path.isdir(resolved_target_path):
        return f"ls: cannot list contents of '{target_path_display}': Not a directory"
    try:
        entries = os.listdir(resolved_target_path)
        entries.sort()
        for entry in entries:
            full_path_to_entry = os.path.join(resolved_target_path, entry)
            if os.path.isdir(full_path_to_entry):
                output_lines.append(f"D: {entry}")
            else:
                output_lines.append(f"F: {entry}")
        if not output_lines: return f"Directory '{target_path_display}' is empty."
        return "\n".join(output_lines)
    except PermissionError:
        return f"ls: cannot open directory '{target_path_display}': Permission denied"
    except Exception as e:
        return f"ls: error accessing '{target_path_display}': {e}"

def cd_command_processor(current_path: str, target_path_arg: str = None) -> tuple[str, str]:
    if target_path_arg is None or target_path_arg == "" or target_path_arg == "~":
        resolved_new_path = os.path.expanduser("~")
        target_path_display = "~"
    elif os.path.isabs(target_path_arg):
        resolved_new_path = os.path.abspath(target_path_arg)
        target_path_display = target_path_arg
    else:
        resolved_new_path = os.path.abspath(os.path.join(current_path, target_path_arg))
        target_path_display = target_path_arg
    try:
        if not os.path.exists(resolved_new_path):
            return current_path, f"cd: no such file or directory: {target_path_display}"
        if not os.path.isdir(resolved_new_path):
            return current_path, f"cd: not a directory: {target_path_display}"
        os.listdir(resolved_new_path) 
        return resolved_new_path, ""
    except PermissionError:
        return current_path, f"cd: permission denied: {target_path_display}"
    except Exception as e:
        return current_path, f"cd: an error occurred: {e}"

def run_command_string(current_path: str, script_name_arg: str, script_args: list[str]) -> str:
    if not script_name_arg:
        return "run: missing script name"
    if os.path.isabs(script_name_arg):
        resolved_script_path = script_name_arg
    else:
        resolved_script_path = os.path.abspath(os.path.join(current_path, script_name_arg))
    if not resolved_script_path.endswith(".py"):
        return f"run: not a Python script: {script_name_arg}"
    if not os.path.exists(resolved_script_path) or not os.path.isfile(resolved_script_path):
        return f"run: script not found: {script_name_arg}"
    try:
        completed_process = subprocess.run(
            [sys.executable, resolved_script_path] + script_args,
            capture_output=True, text=True, check=False, cwd=current_path
        )
        output_parts = []
        if completed_process.stdout:
            output_parts.append(f"Output:\n{completed_process.stdout.strip()}")
        if completed_process.stderr:
            output_parts.append(f"Errors:\n{completed_process.stderr.strip()}")
        if not output_parts: return "[Script executed with no output]"
        return "\n\n".join(output_parts)
    except Exception as e:
        return f"run: failed to execute script '{script_name_arg}': {e}"

# --- Central Command Processor (Local to GUI Launcher) ---
def execute_morel_command(command_line_string: str, current_path: str) -> tuple[str, str, bool]:
    parts = command_line_string.strip().split()
    if not parts:
        return "", current_path, False 

    command = parts[0].lower()
    args = parts[1:]
    output_string = ""
    new_current_path = current_path
    should_exit_os = False 

    if command == "exit" or command == "quit": # Should be caught by process_terminal_command for GUI
        output_string = "Exiting Morel OS GUI..." 
        should_exit_os = True 
    elif command == "shutdown": # Add shutdown handling for GUI context
        output_string = "Morel OS GUI is shutting down..."
        should_exit_os = True
    elif command == "restart":
        output_string = "Morel OS is restarting... (Please re-launch the application manually)"
        should_exit_os = True
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
                # In GUI, we don't actually change the CWD of the GUI app itself
                # We just update our current_path_in_gui variable.
                # os.chdir(proposed_path) # No actual chdir for GUI's context
                new_current_path = proposed_path
            except Exception as e: # Should not happen if cd_command_processor is robust
                output_string = f"cd: error updating path to '{proposed_path}': {e}"
    elif command == "run":
        script_name = args[0] if args else None
        script_args_list = args[1:]
        if not script_name:
            output_string = "run: missing script name"
        else:
            output_string = run_command_string(current_path, script_name, script_args_list)
    elif command == "startgui": # This command is specific to the CLI morel_os.py
        output_string = "GUI is already running." # Or "Command not applicable in GUI."
    elif command == "snake": # This command is specific to the CLI morel_os.py
        # Launching snake game via subprocess as defined in the previous step
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            snake_script_path = os.path.join(script_dir, "snake_game.py")

            if not os.path.exists(snake_script_path):
                output_string = f"Error: snake_game.py not found in {script_dir}"
            else:
                python_executable = sys.executable
                cmd_list = [python_executable, snake_script_path]
                popen_kwargs = {'cwd': script_dir}
                if os.name == 'nt':
                    popen_kwargs['creationflags'] = subprocess.CREATE_NEW_CONSOLE
                
                process = subprocess.Popen(cmd_list, **popen_kwargs)
                output_string = (f"Attempting to launch Snake game in a new console window (PID: {process.pid})...\n"
                                 "Its output will appear in the new window, not in this GUI terminal.")
        except FileNotFoundError:
            output_string = "Error: Python interpreter not found. Cannot start Snake game."
        except Exception as e:
            import traceback
            output_string = f"An error occurred while trying to start the Snake game: {e}\n{traceback.format_exc()}"
    else:
        output_string = f"Unknown command: {command}"

    return output_string, new_current_path, should_exit_os


# --- Global Tkinter references ---
main_text_area = None
terminal_input_frame = None
terminal_input_entry = None
root = None 
current_path_in_gui = "" 

# --- Helper functions for Text Area ---
def clear_main_text_area():
    global main_text_area
    if main_text_area:
        main_text_area.config(state=tk.NORMAL)
        main_text_area.delete('1.0', tk.END)
        # State is left NORMAL by this helper

def append_to_main_text_area(text_to_append, style_tag="normal_output"): # Added style_tag
    global main_text_area
    if main_text_area:
        main_text_area.config(state=tk.NORMAL)
        main_text_area.insert(tk.END, text_to_append, style_tag) # Apply style_tag
        main_text_area.see(tk.END) 
        # State is left NORMAL by this helper

# --- Action functions ---
def action_show_info():
    global main_text_area
    print("DEBUG: 'Show Info' button clicked, updating text area.")
    
    info_content = info_command_string() # Calls local info_command_string

    if main_text_area:
        try:
            clear_main_text_area()
            # Use "normal_output" tag for info content. strip_rich_markup is still important.
            append_to_main_text_area(strip_rich_markup(info_content).strip() + "\n\n", style_tag="normal_output")
            main_text_area.config(state=tk.DISABLED) 
        except Exception as e:
            print(f"DEBUG: Error updating main_text_area in action_show_info: {e}")
    else:
        print("DEBUG_ERROR: main_text_area is None in action_show_info.")


def process_terminal_command(event=None): 
    global main_text_area, terminal_input_entry, current_path_in_gui, root
    
    if not terminal_input_entry or not main_text_area:
        print("DEBUG_ERROR: Terminal components not ready for processing command.")
        return

    command_str = terminal_input_entry.get().strip()
    terminal_input_entry.delete(0, tk.END)

    # Echo the command with the current path using "echoed_command" or "prompt_style"
    append_to_main_text_area(f"{current_path_in_gui}> ", "prompt_style")
    append_to_main_text_area(f"{command_str}\n", "echoed_command") # Or use normal_output

    if not command_str: 
        append_to_main_text_area(f"{current_path_in_gui}> ", "prompt_style") 
        return

    if command_str.lower() == "clear":
        clear_main_text_area()
        append_to_main_text_area(f"{current_path_in_gui}> ", "prompt_style") 
        return
    elif command_str.lower() in ["exit", "quit"]: 
        append_to_main_text_area("Terminal mode deactivated.\n", "normal_output")
        action_toggle_terminal() 
        return

    print(f"DEBUG: GUI calling LOCAL execute_morel_command with: '{command_str}', path: '{current_path_in_gui}'")
    output_str, new_path, should_exit_os = execute_morel_command(command_str, current_path_in_gui)
    print(f"DEBUG: GUI received from LOCAL execute_morel_command: output='{output_str[:50].replace('\n', ' ')}...', new_path='{new_path}', exit={should_exit_os}")
    
    current_path_in_gui = new_path 
    
    if output_str:
        plain_output = strip_rich_markup(output_str)
        current_style = "normal_output"
        # Heuristic for error messages from execute_morel_command
        stripped_output_for_check = plain_output.strip().lower()
        error_keywords = ["error:", "unknown command:", "cd:", "run:", "script not found", 
                          "no such file or directory", "not a python script", 
                          "missing script name", "not a directory", "permission denied"]
        if any(keyword in stripped_output_for_check for keyword in error_keywords):
            current_style = "error_output"
        
        if not plain_output.endswith("\n"):
            plain_output += "\n"
        append_to_main_text_area(plain_output, current_style)

    if should_exit_os: 
        append_to_main_text_area("Morel OS 'exit' command received. Closing GUI launcher.\n", "error_output")
        if root: 
            root.quit() 
        return 

    append_to_main_text_area(f"{current_path_in_gui}> ", "prompt_style") 

def action_toggle_terminal():
    global main_text_area, terminal_input_frame, terminal_input_entry, root, current_path_in_gui
    print("DEBUG: 'Toggle Terminal' button clicked.")

    if not root: 
        print("DEBUG_ERROR: Root window not available for terminal toggle.")
        return

    if terminal_input_frame is None: 
        print("DEBUG: Creating terminal UI elements for the first time.")
        terminal_input_frame = tk.Frame(root)
        terminal_input_frame.config(background="white") # Set frame background
        
        terminal_input_entry = tk.Entry(terminal_input_frame, width=60, font=("Arial", 10))
        terminal_input_entry.bind("<Return>", process_terminal_command)
        terminal_input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5))

        send_button = tk.Button(terminal_input_frame, text="Send", command=process_terminal_command, width=10)
        send_button.pack(side=tk.RIGHT)

        # --- Context Menu for terminal_input_entry ---
        entry_context_menu = tk.Menu(terminal_input_frame, tearoff=0)

        def entry_paste_text():
            global terminal_input_entry, root, CLIPBOARD_AVAILABLE, pyperclip # Access globals
            if not terminal_input_entry: return

            try:
                text_to_paste = ""
                if CLIPBOARD_AVAILABLE and pyperclip:
                    text_to_paste = pyperclip.paste()
                    print("DEBUG: Pasting from pyperclip.")
                elif root: # Fallback to Tkinter's clipboard if pyperclip not available
                    text_to_paste = root.clipboard_get()
                    print("DEBUG: Pasting from Tkinter clipboard.")
                else: # Should not happen if root exists
                    print("DEBUG: Root not available for Tkinter clipboard.")
                    return
                
                if text_to_paste:
                    terminal_input_entry.insert(tk.INSERT, text_to_paste)
                    print(f"DEBUG: Pasted: {text_to_paste[:50]}...") # Log a snippet

            except tk.TclError as e: 
                print(f"DEBUG: Tkinter clipboard paste error: {e}. Clipboard might be empty or content not text.")
            except Exception as e: 
                print(f"DEBUG: Error pasting text: {e}")

        entry_context_menu.add_command(label="Paste", command=entry_paste_text)

        def show_entry_context_menu(event):
            global CLIPBOARD_AVAILABLE, pyperclip, root # Access globals
            # Always enable Paste for now, let paste handler manage empty.
            # More complex checks could be added here if desired.
            entry_context_menu.entryconfig("Paste", state=tk.NORMAL)
            try:
                entry_context_menu.tk_popup(event.x_root, event.y_root)
            except tk.TclError as e:
                print(f"DEBUG: Error showing entry context menu: {e}")


        terminal_input_entry.bind("<Button-3>", show_entry_context_menu)

    if not terminal_input_frame.winfo_ismapped(): 
        print("DEBUG: Terminal is hidden, showing it.")
        terminal_input_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(5,10)) 
        
        clear_main_text_area()
        append_to_main_text_area("Terminal mode activated.\n", "normal_output")
        append_to_main_text_area(f"{current_path_in_gui}> ", "prompt_style")
        main_text_area.config(state=tk.NORMAL) 
        if terminal_input_entry:
            terminal_input_entry.focus_set()
    else: 
        print("DEBUG: Terminal is visible, hiding it.")
        terminal_input_frame.pack_forget()
        clear_main_text_area()
        append_to_main_text_area("Terminal hidden. Info mode active.\n"
                                 "Click 'Show Info' or 'Toggle Terminal' again.\n", "normal_output")
        main_text_area.config(state=tk.DISABLED) 


if __name__ == "__main__":
    root = tk.Tk() 
    root.title("Morel OS - Graphical Launcher")
    root.config(background="white") # Set root window background
    
    command_button_frame = tk.Frame(root)
    command_button_frame.config(background="white") # Set frame background
    command_button_frame.pack(pady=5, padx=10, fill=tk.X)

    button_width = 15 

    info_button = tk.Button(command_button_frame, text="Show Info", command=action_show_info, width=button_width)
    info_button.pack(side=tk.LEFT, padx=5)

    terminal_button = tk.Button(command_button_frame, text="Toggle Terminal", command=action_toggle_terminal, width=button_width)
    terminal_button.pack(side=tk.LEFT, padx=5)
    
    exit_button = tk.Button(command_button_frame, text="Exit", command=root.quit, width=button_width)
    exit_button.pack(side=tk.RIGHT, padx=5)

    main_text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=15, width=70)
    # Configure default appearance and tags for light theme
    main_text_area.config(background="white", foreground="black", insertbackground="black", font=("Arial", 10)) # Added font
    main_text_area.tag_configure("normal_output", foreground="black")
    main_text_area.tag_configure("error_output", foreground="red")
    main_text_area.tag_configure("prompt_style", foreground="darkgray", font=("Arial", 10, "bold")) # Bold prompt
    main_text_area.tag_configure("echoed_command", foreground="darkblue") # Echoed command

    main_text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
    
    initial_message = """Welcome to Morel OS Graphical Launcher!

Click 'Show Info' to display system information in this area.
Click 'Toggle Terminal' to activate a basic command line interface here.
When terminal is active, you can type commands like 'echo [your message]' or 'clear'.
Type 'exit' or 'quit' in the terminal to hide it.

Use the main 'Exit' button to close this launcher.
"""
    # Insert initial message with "normal_output" tag
    main_text_area.config(state=tk.NORMAL)
    main_text_area.insert(tk.END, initial_message, "normal_output") # Apply normal_output tag
    main_text_area.config(state=tk.DISABLED)

    current_path_in_gui = os.getcwd()
    print(f"DEBUG: Initial current_path_in_gui: {current_path_in_gui}")

    # --- Context Menu for main_text_area ---
    text_area_context_menu = tk.Menu(root, tearoff=0)

    def text_area_copy_selection():
        global main_text_area, root # Ensure access to root for clipboard
        if not main_text_area: return
        try:
            if main_text_area.tag_ranges(tk.SEL): # Check if text is selected
                selected_text = main_text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
                if CLIPBOARD_AVAILABLE and pyperclip:
                    try:
                        pyperclip.copy(selected_text)
                        print("DEBUG: Selected text copied to clipboard via pyperclip.")
                    except Exception as e: # Catch Pyperclip specific exceptions if possible
                        print(f"DEBUG: Error copying with pyperclip: {e}")
                        # Attempt Tkinter fallback if pyperclip fails unexpectedly
                        if root: # Check if root is available
                            root.clipboard_clear()
                            root.clipboard_append(selected_text)
                            print("DEBUG: Pyperclip failed, selected text copied via Tkinter clipboard as fallback.")
                elif root: # pyperclip not available, use Tkinter's clipboard
                    root.clipboard_clear()
                    root.clipboard_append(selected_text)
                    print("DEBUG: Selected text copied to clipboard via Tkinter clipboard.")
        except tk.TclError as e:
            # This can happen if selection is attempted on an empty range or other Tcl errors
            print(f"DEBUG: Tkinter clipboard/selection error: {e}")

    text_area_context_menu.add_command(label="Copy", command=text_area_copy_selection)

    def show_text_area_context_menu(event):
        global main_text_area # Ensure access
        if not main_text_area: return
        # Display the menu at the click position
        # Disable "Copy" if no text is selected
        try:
            if main_text_area.tag_ranges(tk.SEL):
                text_area_context_menu.entryconfig("Copy", state=tk.NORMAL)
            else:
                text_area_context_menu.entryconfig("Copy", state=tk.DISABLED)
        except tk.TclError: # If selection check fails (e.g. widget disposed)
                text_area_context_menu.entryconfig("Copy", state=tk.DISABLED)
        
        text_area_context_menu.tk_popup(event.x_root, event.y_root)

    main_text_area.bind("<Button-3>", show_text_area_context_menu) # Button-3 is usually right-click


    root.minsize(600, 450) 
    
    root.mainloop()
