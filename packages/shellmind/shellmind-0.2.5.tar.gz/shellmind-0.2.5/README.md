# ShellMind 🤖💻

[![PyPI version](https://img.shields.io/pypi/v/shellmind)](https://pypi.org/project/shellmind/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## Table of Contents
- [Features](#features-)
- [Why ShellMind?](#why-shellmind-)
- [Installation](#installation-)
- [Configuration](#configuration-)
- [Usage](#usage-)
- [Contributing](#contributing-)
- [Roadmap](#roadmap-)
- [License](#license-)
- [Acknowledgments](#acknowledgments-)

**ShellMind** is your AI-powered terminal companion. It helps you generate, understand, and debug command-line instructions using natural language. Never struggle with terminal commands or flags again!

![Demo](https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExcmQzZGFvdWI0d2E3MTJkbDV2bnVybWg0dmY5d3RnbHUwc3J1bmM0OCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3NtY188QaxDdC/giphy.gif)  

---

## Features ✨

- **Natural Language to Commands**: Convert questions like *"How do I find large files?"* into terminal commands, making it accessible even for beginners.
- **Command Explanations**: Understand flags and syntax with `--explain`, helping users learn as they go.
- **Error Diagnosis**: Get suggestions for common CLI errors, reducing frustration and improving productivity.
- **Safety Checks**: AI-powered warnings for destructive or risky commands (e.g., `rm -rf`, `chmod 777`), ensuring safe usage.
- **OpenAI Integration**: Powered by OpenAI API compatible endpoints, with support for local models like Ollama for added flexibility.
- **System-Specific Commands**: Automatically detect or specify your system type (e.g., Fedora, Debian, Ubuntu) for accurate, system-specific command generation.
- **Real-Time Execution**: Execute commands directly with real-time output using the `-x` flag, ideal for long-running processes like system upgrades.
- **Interactive Mode**: Ask multiple questions in a continuous session with `-i`, perfect for complex workflows.
- **Command History**: View previously generated commands with `--history`, making it easy to reuse or review past queries.
- **JSON Output**: All responses are structured as valid JSON, making it easy to integrate with other tools or scripts.
- **Customizable Configuration**: Specify your system type, API key, and base URL in a config file for a personalized experience.

---

## Why ShellMind? 🚀

ShellMind is designed to make terminal usage **easier**, **safer**, and **more efficient** for everyone. Here's what makes it special:

- **User-Friendly**: Whether you're a beginner or an advanced user, ShellMind bridges the gap between natural language and terminal commands.
- **Educational**: Explanations and safety checks help you learn terminal commands while avoiding common pitfalls.
- **Efficient**: Real-time execution and interactive mode streamline workflows, saving you time and effort.
- **Extensible**: The modular design makes it easy to add new features or integrate with other tools.
- **Cross-Platform**: Works with OpenAI and local models (e.g., Ollama), giving you flexibility in how you use the tool.

---

## Installation 🛠️

### From PyPI
```bash
pip install shellmind
```

### From Source
```bash
git clone https://github.com/k-mktr/shellmind.git
cd shellmind
pip install .
```

---

## Configuration ⚙️

### Base URL and API Key

You can specify your base URL, model and API key in the configuration file:

```bash
mkdir ~/.config/shellmind
touch ~/.config/shellmind/config.ini
```

```ini
[default]
base_url = http://localhost:11434/v1 # or your OpenAI API base URL
model = llama3.2:3b-instruct-q8_0 # or your OpenAI API model
api_key = ollama # or your OpenAI API key
```

### System Type


You can specify your system type in the configuration file to ensure ShellMind generates system-specific commands:
```ini
[default]
system_type = Fedora  # or Debian, Ubuntu, Arch, etc.
```

If not specified, ShellMind will automatically detect your system type.

---

## Usage 🚀

### Basic Query
```bash
shellmind -a "How to search for 'error' in all .log files?"
```
**Output**:
```
Command: grep -r "error" *.log
Explanation:
  - `-r`: Recursively search subdirectories.
```

### Interactive Mode
Start an interactive session where you can ask multiple questions:
```bash
shellmind -i
> How to check disk usage?
> How to find large files?
> exit
```

### Detailed Explanations
```bash
shellmind -a "Explain tar -xzvf" --explain
```
**Output**:
```
Command: tar -xzvf archive.tar.gz
Explanation:
  - `-x`: Extract files.
  - `-z`: Decompress using gzip.
  - `-v`: Verbose output (show progress).
  - `-f`: Specify filename.
```

### Safety Checks
ShellMind now uses AI-powered safety checks to warn about destructive commands:
```bash
shellmind -a "Delete everything in /tmp"
```
**Output**:
```
Command: rm -rf /tmp/*
⚠️  Warning: This command will delete all files in /tmp. Use with caution!
```

### Command Execution
Execute the generated command directly (with confirmation for destructive commands):
```bash
shellmind -a "List files in /tmp" -x
```

### System-Specific Commands
Generate commands specific to your system type:
```bash
shellmind -a "Update my system"
```

**Output**:
```
Command: sudo dnf upgrade  # or sudo apt-get upgrade, depending on your system
Explanation:
  - `sudo`: Run as superuser.
  - `dnf`: Package manager for Fedora.
  - `upgrade`: Upgrade all installed packages.
```

**Real-Time Output**:  
When using the `-x` flag, ShellMind streams the command's output directly to the terminal, allowing you to see progress in real-time. This is especially useful for commands like `dnf upgrade` or `apt-get upgrade`.

### Command History
View previously generated commands:
```bash
shellmind --history
```

### Error Diagnosis
ShellMind can diagnose and suggest fixes for common CLI errors:
```bash
shellmind -a "Invalid command" -x
```

### JSON Output
ShellMind ensures that all responses are structured as valid JSON, making it easier to parse and integrate with other tools.
```bash
shellmind -a "How to check disk usage?"
```

### Enhanced System Prompt
ShellMind uses a detailed system prompt to ensure accurate, safe, and efficient command generation. The prompt includes:
- Role definition (Linux terminal expert).
- Safety guidelines.
- Output format requirements.

Example:
```bash
shellmind -a "Delete all files in /tmp"
```

### Advanced Usage Examples

#### Safe Command Alternatives
For potentially dangerous operations, ShellMind suggests safer alternatives:
```bash
shellmind -a "How to move files with backup?"
```
**Output**:
```
Command: cp -r source_dir/* destination_dir/ && rm -rf source_dir/*
Explanation:
  - `cp -r`: Copy directories recursively
  - `rm -rf`: Remove directories recursively (after copying)
Warning: This command will first copy files and then remove the originals. Use with caution.
```

#### Custom Configuration
You can create a custom configuration file for your specific needs:
```bash
mkdir ~/.config/shellmind
cat > ~/.config/shellmind/config.ini << EOF
[default]
base_url = http://localhost:11434/v1
model = llama3.2:3b-instruct-q8_0
system_type = Ubuntu
EOF
```

#### API Integration
For OpenAI-compatible APIs:
```bash
shellmind -a "How to list all running processes?" --base-url https://api.openai.com/v1 --model gpt-4o-mini
```

#### Error Recovery
When a command fails, ShellMind can help diagnose the issue:
```bash
shellmind -a "Try to access non-existent file" -x
```
**Output**:
```
Command: cat /nonexistent/file.txt
❌ Command failed with exit code 1
Diagnosis: The file '/nonexistent/file.txt' does not exist. 
Explanation:
  - `cat`: Display file contents
Warning: This command will fail because the file doesn't exist.
```

### Help
Get help and see all available options:
```bash
shellmind -h
```

---

## Contributing 🤝

Contributions are welcome! Here's how you can help:

1. **Report Issues**: Found a bug or have a feature request? [Open an issue](https://github.com/k-mktr/shellmind/issues).
2. **Submit Pull Requests**: Want to contribute code? Fork the repository, make your changes, and submit a pull request.
3. **Improve Documentation**: Help improve the README, add examples, or write tutorials.

Before contributing, please read our [Contributing Guidelines](CONTRIBUTING.md).

---

## Roadmap 🌟

Here are some planned features and improvements:

- **Plugin System**: Add support for custom plugins to extend functionality.
- **Command Aliases**: Support user-defined aliases for frequently used commands.
- **Enhanced Error Handling**: Provide more detailed error messages and recovery suggestions.

Have an idea? [Open an issue](https://github.com/k-mktr/shellmind/issues) or submit a pull request!

---

## License 📜

ShellMind is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Acknowledgments 🙏

- **DeepSeek**: For providing the powerful language models that make ShellMind possible.
- **Ollama**: For enabling local model support.
- **CLI Warriors**: Inspired by the countless developers and sysadmins who make the terminal their home.

---

Made with ❤️ by Karl Danisz | Inspired by CLI warriors everywhere.
