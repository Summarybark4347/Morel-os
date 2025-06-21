# Morel OS

Morel OS is a simple, simulated command-line operating system environment written in Python. It provides basic file system navigation, script execution, and system information display.

## Features

*   **File System Navigation:**
    *   `ls [path]`: List files and directories.
    *   `cd <path>`: Change current directory. Supports relative/absolute paths and `~`.
    *   `pwd`: Print current working directory.
*   **Script Execution:**
    *   `run <script.py> [args...]`: Execute a Python script and see its output.
*   **System Information:**
    *   `info`: Display OS details, Python version, platform, and CPU.
*   **Visual Flair (Optional):**
    *   Integration with the `rich` library for a more colorful and user-friendly terminal experience in the command-line version.
*   **Graphical Launcher (Basic):**
    *   A simple Tkinter-based GUI providing buttons for displaying information (with an updated application logo) and a basic interactive terminal. The GUI terminal now features a light theme (white background with black text, red for errors, and other specific colors for prompts/echoed commands).
*   **Application Launching:**
    *   `open` command in the CLI to open files with default applications or run executables.
*   **Core System Commands:**
    *   Includes essential commands like `shutdown` to exit the OS.

## Graphical Launcher

Morel OS includes a basic graphical launcher built with Tkinter (Python's standard GUI library).
This launcher features a main text area where information (like OS details) can be displayed using the "Show Info" button.
It also includes a "Toggle Terminal" button, which reveals an input field and a send button. In this terminal view, users can type basic commands like:
-   `echo [message]` - to display the message in the text area.
-   `clear` - to clear the text area.
-   `exit` or `quit` - to hide the terminal input field and return to info display mode (does not close the GUI app).
The GUI's terminal display now uses a light theme (white background with black text for general output, dark gray for prompts, dark blue for echoed commands, and red text for errors), improving readability.
Clipboard operations (Copy from output area, Paste into input field via right-click context menus) are available and work best if the `pyperclip` library is installed (`pip install pyperclip`).

You can run the graphical launcher in two ways:

1.  **Directly from your system terminal:**
    ```bash
    python gui_launcher.py
    ```
    (Ensure you are in the Morel OS project directory.)

2.  **From within Morel OS (command-line version):**
    Type the following command at the Morel OS prompt:
    ```
    MorelOS> startgui
    ```

## Usage

1.  **Prerequisites:**
    *   Python 3.x

2.  **Optional - Enhanced Visuals:**
    For the best experience, install the `rich` library:
    ```bash
    pip install rich
    ```
    Morel OS will function without `rich`, but the visual enhancements will be disabled.

3.  **Running Morel OS:**
    Navigate to the directory containing `morel_os.py` and run:
    ```bash
    python morel_os.py
    ```

4.  **Available Commands:**
    Once Morel OS is running, you can use the following commands:
    *   `ls [path]`: List directory contents. If `path` is omitted, lists current directory.
    *   `cd <directory>`: Change to the specified directory.
    *   `pwd`: Show the current directory path.
    *   `run <filename.py> [arguments...]`: Execute the Python script `filename.py`. Any additional `arguments` will be passed to the script.
    *   `info`: Display information about Morel OS and the system.
    *   `info2`: Displays a detailed list of all commands and more info (aliased by `help` and `help2`).
    *   `help`: Displays a detailed list of all available commands (alias for `info2`).
    *   `help2`: Displays a detailed list of all available commands (alias for `info2`).
    *   `date`: Displays the current system date and time.
    *   `open <file_or_app> [args...]`: Opens a file with its default system application or runs an executable (platform-dependent behavior).
    *   `copytext <text...>`: Copies the provided text to the system clipboard. (Requires `pyperclip` library: `pip install pyperclip`)
    *   `pastetext`: Pastes text from the system clipboard. (Requires `pyperclip` library)
    *   `femboy`: Displays a special ASCII art.
    *   `snake`: Plays a classic Snake game (WASD or arrow keys) with high scores. (Requires a curses-compatible terminal; on Windows, you may need to install `windows-curses` via pip.)
    *   `startgui`: Launches a graphical interface with in-window info display and a basic terminal (supports 'echo', 'clear').
    *   `shutdown`: Exits/terminates Morel OS.

## Contributing

Contributions are welcome! Please feel free to fork the repository, make changes, and submit a pull request.

## License

This project is licensed under the MIT License. 
