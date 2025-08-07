

### README.md


# PyHider

PyHider is a Python tool to obfuscate, compile, and hide Python scripts easily.  
It supports options like obfuscation via marshal, compiling with PyInstaller, hiding console windows, hiding webhooks, URLs, and functions in the code.

## Features

- Obfuscate Python scripts using marshal
- Compile scripts to executables with or without console windows
- Hide webhooks and URLs by encoding them in base64 with custom ASCII encoding
- Obfuscate functions to protect your code
- Clean temporary files after compilation
- Detailed debug output available
- Simple CLI interface



## Installation

```bash
pip install pyhider
````

## Usage

```bash
pyhider --file your_script.py --compile --hideconsole --obfuscate
```

## Commands

* `--file` or `-f` : Specify the file to process
* `--compile` or `-c` : Compile the file into an executable
* `--ico` : Set a custom icon for the executable
* `--name` : Set the name of the output executable
* `--obfuscate` : Obfuscate the Python source code
* `--ascii` : Show the PyHider ASCII banner
* `--hideconsole` : Hide the console window when running the executable
* `--debug` : Show detailed debug info
* `--clear` : Remove temporary files after compiling
* `--hidewebhook` : Obfuscate detected webhooks in the code
* `--hideurl` : Obfuscate detected URLs in the code
* `--hidefunctions` : Obfuscate functions in the code
* `--version` : Show the current version


## License

This project is licensed under the MIT License. See LICENSE file for details.

## Developer

Kalom



