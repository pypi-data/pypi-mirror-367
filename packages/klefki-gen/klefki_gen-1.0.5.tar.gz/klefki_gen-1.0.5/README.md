# Klefki - Secure Password Generator

Klefki is a highly secure and customizable password generator written in Python. It allows users to generate strong passwords with varying levels of complexity and even integrate a custom **base word** into the password. Klefki supports both interactive and command-line interfaces for maximum flexibility.

## Features
- **Dual Interface**: Interactive menu or command-line arguments
- **Clipboard Integration**: Automatically copy passwords to clipboard with `--copy` flag
- **Customizable Complexity**: Choose from 4 levels of complexity:
  - **Level 1**: Lowercase letters only
  - **Level 2**: Letters and digits
  - **Level 3**: Letters, digits, and symbols
  - **Level 4**: Max complexity (guarantees all character types)
- **Custom Base Word**: Optionally embed a base word into the password
- **Randomized Character Shuffling**: Characters are randomly shuffled to prevent predictability
- **Security**: Uses Python's `secrets` module for cryptographically secure randomization

## Installation
Install the required dependency for clipboard functionality:

```bash
pip install pyperclip
```

Requirements:
- **Python 3.6+**
- **pyperclip** (for clipboard functionality)

You can install Klefki directly via pip after cloning the repository:

```bash
pip install .
```

Or, after publication on PyPI:

```bash
pip install klefki-gen
```

## Usage

After installation, simply run:

```bash
klefki
```

Or use via CLI:

```bash
klefki -l 16 -c 4 --copy
```

### Interactive Mode
Run without arguments to enter interactive mode:

```bash
python3 main.py
```

### Command-Line Interface
Generate passwords directly from command line:

```bash
# Basic usage
python3 main.py -l 16 -c 3

# With base word
python3 main.py -l 20 -c 4 -b "secure"

# Copy to clipboard automatically
python3 main.py -l 12 -c 3 --copy
```

#### CLI Arguments
- `-l, --length`: Password length (required for CLI mode)
- `-c, --complexity`: Complexity level 1-4 (required for CLI mode)
- `-b, --base`: Base word to include (optional)
- `--copy`: Copy password to clipboard automatically

### Example Usage

#### Interactive Mode
```
Welcome to the Interactive Password Generator!
Enter password length: 12

Complexity levels:
1 - Lowercase letters
2 - Letters and digits
3 - Letters, digits, symbols
4 - Max complexity (guarantees all types)
Choose complexity (1-4): 3
Optional base word: secure

Your password: a9$ecurelP!#

Copy to clipboard? (y/n): y
Password copied to clipboard!
Generate another? (y/n): n
Goodbye!
```

#### Command-Line Mode
```bash
$ python3 main.py -l 16 -c 4 -b "test" --copy
K8#testM2@pL9$vX
Password copied to clipboard!
```

## Code Overview
- **`generate_password()`**: Core password generation with complexity levels and base word integration
- **`display_menu()`**: Interactive user interface with improved UX
- **`cli()`**: Command-line argument parsing and execution
- Uses `argparse` for robust CLI argument handling
- Integrates `pyperclip` for seamless clipboard operations

## Security Notes
Klefki prioritizes security by:
- Using Python's `secrets` module for cryptographically secure randomization
- Shuffling characters to prevent base word pattern detection
- Supporting maximum complexity mode that guarantees character type diversity

## Possible Improvements
- Add a graphical user interface (GUI) using `tkinter`.
- Add command-line arguments to allow non-interactive usage.
- Include more advanced password strength analysis and feedback.

## Contributing
Contributions are welcome! If you'd like to add features or fix issues, feel free to open a pull request.

## License
This project is open-source and licensed under the **MIT License**.
