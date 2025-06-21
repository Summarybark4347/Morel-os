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
    *   Integration with the `rich` library for a more colorful and user-friendly terminal experience (e.g., styled prompts, icons for files/directories, colored error messages).
*   **Basic Commands:**
    *   `exit`, `quit`: Terminate Morel OS.

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
    *   `info2`: Displays more detailed information about Morel OS, its creation, and a list of all commands.
    *   `femboy`: Displays a special ASCII art.
    *   `exit` or `quit`: Exit Morel OS.

## Contributing

Contributions are welcome! Please feel free to fork the repository, make changes, and submit a pull request.

## License

This project is licensed under the MIT License. (Assuming MIT, update if different)
