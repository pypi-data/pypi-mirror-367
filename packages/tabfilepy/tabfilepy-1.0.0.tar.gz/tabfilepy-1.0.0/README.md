# TabFilePy

**TabFilePy** is a Python library that provides file path auto-completion functionality using shell scripts. It allows users to easily select file paths from the command line with tab completion.

## Features
- **Cross-platform support**: Works on Windows/CMD (`.cmd` script) and Linux/Bash (`.sh` script) environments.
- **Dynamic script location handling**: Finds and runs the appropriate script from the package directory.
- **Easy integration**: Simple API for retrieving file paths with tab completion.

## Dependencies
- Python 3.9 or higher
- Bash or Command Prompt (depending on OS)

## Usage
1. Install the library
```
pip install tabfilepy
```

2. Import and initialize the handler
```
# Example code
from tabfilepy import tabfilepy

# Create the instance
t = tabfilepy()

# Run tab completion and retrieve the selected file
filename = t.get_filename()
print(f"Selected file: {filename}")
```
