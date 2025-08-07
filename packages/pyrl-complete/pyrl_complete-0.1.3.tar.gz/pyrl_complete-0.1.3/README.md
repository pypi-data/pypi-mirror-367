# pyrl-complete
Python readline completer and command line parser

## What is pyrl-complete?

`pyrl-complete` is a Python library for building powerful, context-aware command-line autocompletion. It allows developers to define the grammar of a command-line interface (CLI) using a simple, human-readable syntax.

The library parses this grammar to understand all possible command structures, including commands, sub-commands, options, and arguments. It then uses this understanding to provide intelligent autocompletion suggestions and predictions as a user types.

## Key Features

- **Custom Grammar**: Define your CLI structure in a simple `.prl` file. The syntax supports:
    - Simple command sequences (`get status`)
    - Alternatives using `|` (`get (one | two)`)
    - Optional groups using `[]` (`command [optional_part]`)
    - Options with placeholder arguments (`-d ?`)
- **Completion Engine**: A prefix-tree-based engine that provides:
    - **Suggestions**: A list of all possible valid commands that match the current input.
    - **Predictions**: The most likely next word or token based on the current input.
- **Tester GUI**: A bundled Tkinter application that provides a live development environment. You can write your grammar, parse it, and test the completion behavior in real-time, making development and debugging fast and easy.

## Rules Syntax

The grammar for defining your command-line interface is designed to be simple and flexible. Rules are typically defined in a `.prl` file.

#### Statements

Each complete command path is a statement. Statements can be separated by a **newline** or a **semicolon (`;`)**.

```
# Separated by newline
get status
set user

# Separated by semicolon
get status; set user;
```

#### Alternatives (`|`) and Grouping (`()`)

The pipe character **`|`** is used to define a set of alternative tokens. Parentheses **`( ... )`** are used to group these alternatives, which is necessary when they appear in the middle of a command.

```
# Creates two valid paths: 'set user name ?' and 'set group name ?'
set (user | group) name ?;
```

#### Optional Groups (`[]`)

Square brackets **`[ ... ]`** define an optional part of a command. The command is valid with or without the tokens inside the brackets.

```
# Creates three valid paths: 'show config', 'show interfaces', and just 'show'
show [config | interfaces];
```

#### Options and Arguments (`-` and `?`)

Tokens starting with a hyphen **`-`** are treated as options. An option can be followed by a **`?`** to indicate that it takes an argument. The `?` acts as a placeholder for the completion engine.

```
# An option without an argument
get -h

# An option that requires an argument
set user -name ?
```

## How it Works

1.  **Define Rules**: You write your command structure in a text file (e.g., `rules.prl`).
    ```
    # Example Rules
    get status;
    set (user | group) name ?;
    show [config | interfaces];
    ```
2.  **Parse**: The library's parser (built with `ply`) reads your rules and generates a list of all valid command paths.
3.  **Complete**: As a user types a command, the completion engine queries a tree built from these paths to find and suggest the next valid tokens.

This library provides the core components to build a rich autocompletion experience for any Python-based CLI application.

## Usage with a Python CLI

To integrate `pyrl-complete` into a Python CLI application, you need to connect its completion engine to Python's built-in `readline` library. `readline` handles the user input loop and allows you to register a custom completer function.

Here's a basic example of how to set it up:

#### 1. Your Rules (`my_cli.prl`)

First, define your command grammar in a `.prl` file.

```
# my_cli.prl
get (status | version);
set user -name ?;
exit;
```

#### 2. Your Python Application (`my_cli.py`)

Next, write the Python code to load these rules and hook them into `readline`.

```python
import readline
from pyrl_complete.parser import Parser
from pyrl_complete.parser.tree import Tree

# --- 1. Load and Parse Rules ---
with open("my_cli.prl", "r") as f:
    rules_text = f.read()

parser = Parser()
parser.parse(rules_text)
completion_tree = Tree(parser.paths)

# --- 2. Create a Completer Class ---
class PyrlCompleter:
    def __init__(self, tree):
        self.tree = tree
        self.predictions = []

    def complete(self, text, state):
        # On the first Tab press, generate new predictions
        if state == 0:
            line_buffer = readline.get_line_buffer()
            self.predictions = self.tree.get_predictions(line_buffer)

        # Return the next prediction, or None if there are no more
        return self.predictions[state] if state < len(self.predictions) else None

# --- 3. Setup Readline ---
completer = PyrlCompleter(completion_tree)
readline.set_completer(completer.complete)
readline.parse_and_bind("tab: complete")

# --- 4. Main Application Loop ---
print("Welcome to the CLI. Type 'exit' to quit.")
while True:
    try:
        line = input(">> ")
        if line.strip() == 'exit':
            break
        print(f"You entered: {line}")
    except (EOFError, KeyboardInterrupt):
        break
print("\nGoodbye!")
```

### How the Example Works

1.  **Load and Parse Rules**: We load the rule file, create a `Parser`, and then a `Tree` which holds our completion logic.
2.  **Create a Completer Class**: The `PyrlCompleter` class holds the state for our completion. `readline` calls its `complete` method every time the user hits Tab.
    *   When `state` is `0` (the first Tab press for the current input), we get the full line from `readline.get_line_buffer()` and ask our `completion_tree` for new predictions.
    *   For subsequent Tab presses (`state > 0`), we simply return the next prediction from the list we already generated.
3.  **Setup Readline**: We instantiate our completer and tell `readline` to use it. `readline.parse_and_bind("tab: complete")` is crucial for making the Tab key trigger the completion function.
4.  **Main Loop**: A standard `input()` loop lets the user interact with the CLI, and `readline` automatically handles the autocompletion in the background.

## Using the Tester GUI

The library includes a graphical tester application built with Tkinter that provides a complete environment for writing, parsing, and testing your completion rules in real-time.

To run it, execute the `tester.py` script:
```bash
python pyrl_complete/apps/tester.py
```

### Workflow

1.  **Write or Load Rules**:
    *   Navigate to the **Write Rules** tab to write your grammar from scratch in the text editor.
    *   Alternatively, in the **Test Rules** tab, click **Load Rules** to open a `.prl` file from your computer. This will load its content into the editor and switch you to the **Write Rules** tab.

2.  **Parse Rules**:
    *   In the **Write Rules** tab, click the **Parse Rules** button.
    *   This will process the grammar in the editor, build the completion tree, and update the path count (e.g., "12 paths generated").
    *   The application will automatically switch you to the **Test Rules** tab.

3.  **Test Completion**:
    *   In the **Test Rules** tab, start typing a command in the **Command line input** field.
    *   As you type, the **Predictions** list on the right will update with all possible next tokens.
    *   Press the **Tab** key to cycle through the predictions and auto-populate the input field.

### Interface Overview

The application is organized into two main tabs and a log panel.

*   **Write Rules Tab**: This is your editor. It contains a large text area for writing rules and two primary buttons:
    *   `Save Rules`: Saves the content of the editor to a `.prl` file.
    *   `Parse Rules`: Processes the rules and prepares them for testing.

*   **Test Rules Tab**: This is your testing ground.
    *   **Rules View (Left)**: A read-only view of the currently parsed rules.
    *   **Predictions (Right)**: A list that shows potential completions for the current input.
    *   **Command line input**: The field where you type commands and use Tab completion.

*   **Log Activity Panel**: Located at the bottom of the window, this panel shows a running log of actions like loading files, parsing rules, and which completion was selected, which is useful for debugging.

## Dependencies

`pyrl-complete` has one core external dependency:

-   **ply**: Used for the Lex/Yacc-style parsing of the custom grammar rules.

The included Tester GUI application uses **Tkinter**, which is part of the Python standard library and should not require a separate installation. However on some linux systems a separate installation is required via the package mager, for example 
```
sudo apt install python3-tk 
```
for Debian/Ubuntu.
