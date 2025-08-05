<div align="center">

# 🐧 LinAIx

**AI-Powered Linux Command Assistant**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux-orange.svg)](https://www.linux.org/)
[![AI](https://img.shields.io/badge/AI-Gemini-purple.svg)](https://aistudio.google.com/)

> **Improve your Linux experience with natural language commands powered by Google Gemini AI**

[Features](#-features) • [Installation](#-installation) • [Quick Start](#-quick-start) • [Usage](#-usage) • [Configuration](#-configuration) • [Contributing](#-contributing)

</div>

<div align='center'>

![LinAIx Demo Video](linaix_demo.gif)

*Recording showing Linaix generating different linux command based on user natural language input*
</div>
---

## 🎯 What is LinAIx?

LinAIx is a  command-line tool bridging the gap between human language and Linux system shell command. Instead of memorizing complex shell commands, simply describe what you want to do in plain English, and LinAIx will generate and execute the appropriate Linux commands for you.

### 🌟 Why LinAIx?

- **🚀 Productivity Boost**: No more Googling commands or reading man pages
- **🛡️ Safety First**: Built-in protection against destructive operations
- **🧠 AI-Powered**: Leverages Google Gemini for intelligent command generation
- **📚 Learning Tool**: Understand what commands do with detailed explanations
- **⚡ Interactive Mode**: Full AI-powered terminal experience

---

## ✨ Features

### 🤖 **Natural Language Processing**
Turn everyday language into precise Linux commands:
```bash
"Show me all Python files in the current directory"
# Generates: ls *.py

"Create a backup of my documents folder"
# Generates: cp -r ~/Documents ~/Documents_backup_$(date +%Y%m%d)
```

### 🖥️ **Interactive AI Terminal**
Launch a full-featured AI-powered terminal session:
```bash
linaix --interactive
```
- **Smart Context Awareness**: Understands your current directory and system state
- **Real-time Command Generation**: Instantly converts your requests to commands
- **Error Recovery**: Automatically suggests fixes when commands fail
- **Natural Exit**: Simply type `exit` or `quit` to close

### 📚 **Command History & Learning**
- **Persistent History**: All your commands are saved for future reference
- **Command Reuse**: Replay previous commands with `--reuse <index>`
- **Learning Insights**: Understand what each command does with `--verbose`

### 🏷️ **Smart Aliases**
Create custom shortcuts for your most common tasks:
```bash
# Create an alias
linaix --add-alias listpy "list all python files"

# Use the alias
linaix listpy
```

### 🛡️ **Safety Features**
- **Destructive Command Warnings**: Confirmation prompts for dangerous operations
- **Safe Command Generation**: AI prioritizes non-destructive solutions
- **Error Handling**: Graceful handling of command failures with alternative suggestions

### ⚙️ **Flexible Configuration**
- **Interactive Setup**: Easy setup with `--setup` command
- **JSON Configuration**: Easy-to-edit settings file at `~/.linaix/config.json`
- **Environment Variables**: Support for `GOOGLE_API_KEY` environment variable
- **Model Selection**: Choose your preferred Gemini model during setup
- **Custom Aliases**: Persistent alias management

---

## 🚀 Installation

### Prerequisites

- **Python 3.8+**
- **Linux Distribution** (Ubuntu, Debian, Fedora, etc.)
- **Google Gemini API Key** ([Get one here](https://aistudio.google.com/app/apikey))

### Step 1: Clone the Repository
```bash
git clone https://github.com/AdirAli/linaix.git
cd linaix
```

### Step 2: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Install Linux Dependencies

#### For Ubuntu/Debian:
```bash
sudo apt update
sudo apt install gnome-terminal python3-pip
```

#### For Fedora/RHEL/CentOS:
```bash
sudo dnf install gnome-terminal python3-pip
# or for older versions:
sudo yum install gnome-terminal python3-pip
```

#### For Arch Linux:
```bash
sudo pacman -S gnome-terminal python-pip
```

### Step 4: Configure Your API Key

**Option A: Interactive Setup (Recommended)**
```bash
python3 linaix.py --setup
```
This will guide you through setting up your API key and choosing your preferred Gemini model interactively.

**Option B: Environment Variable**
```bash
export GOOGLE_API_KEY='your-api-key-here'
```

**Option C: Manual Configuration**
```bash
# The config file will be created automatically at ~/.linaix/config.json
# You can edit it manually if needed
nano ~/.linaix/config.json
```

**Available Models:**
- `gemini-1.5-flash` (fast, good for most tasks) - **Default**
- `gemini-1.5-pro` (more capable, slower)
- `gemini-pro` (legacy model)

### Step 5: Set Up Global Access (Optional but Recommended)

Make the `linaix` command available globally so you can run it from any directory:

**Create a Symbolic Link**
```bash
# Make the script executable
chmod +x linaix.py

# Create a symbolic link in /usr/local/bin (requires sudo)
sudo ln -s $(pwd)/linaix.py /usr/local/bin/linaix

# Now you can run linaix from anywhere
linaix --interactive
```

---

## 🎮 Quick Start

### 1. **Generate Your First Command**
```bash
linaix "list all files in the current directory"
```

### 2. **Launch Interactive Mode**
```bash
linaix --interactive
```

### 3. **Create Your First Alias**
```bash
linaix --add-alias cleanup "remove all temporary files"
```

---

## 📖 Usage Guide

### **Interactive Mode** 🖥️
Run LinAIx in interactive mode for a natural language terminal experience:

```bash
python3 linaix.py --interactive
```

This will run the LinAIx natural language terminal directly in your current terminal window.

**Interactive Mode Features:**
- 🎯 **Natural Language Input**: Type what you want to do in plain English
- 🔄 **Real-time Execution**: Commands are generated and executed immediately
- 📊 **Visual Feedback**: Clear success/error indicators
- 🧠 **Context Awareness**: AI understands your current directory and system state
- 🔧 **Error Recovery**: Automatic suggestions when commands fail
- 🖥️ **Current Terminal**: Runs in your current terminal session (no new windows)

**Example Interactive Session:**
```
user@host:/home/user $ create a new project folder called myapp
Generated Command: mkdir -p myapp
✓ Success

user@host:/home/user $ list all files in the project
Generated Command: ls -la myapp/
✓ Success

user@host:/home/user $ install git if it's not already installed
Generated Command: sudo apt update && sudo apt install -y git
✓ Success
```

### **One-off Commands** ⚡
Generate commands for specific tasks:

```bash
# Basic command generation
linaix "find all PDF files in the current directory"

# With explanation
linaix --verbose "create a backup of my documents"

# Complex tasks
linaix "install the latest version of Node.js and npm"
```

### **Alias Management** 🏷️
Create and manage custom shortcuts:

```bash
# Add an alias
linaix --add-alias listpy "list all python files"
linaix --add-alias cleanup "remove all .tmp files"

# Use aliases
linaix listpy
linaix cleanup

# List all aliases
linaix --list-aliases

# Remove an alias
linaix --remove-alias cleanup
```

### **Command History** 📚
Access and reuse previous commands:

```bash
# View command history
linaix --history

# Reuse a specific command
linaix --reuse 2
```

---

## ⚙️ Configuration

### **Configuration File Location**
```
~/.linaix/config.json
```

The configuration file is automatically created on first run with sensible defaults. You can modify it manually or use the interactive setup command.

### **Configuration Options**
```json
{
  "api_key": "your-gemini-api-key",
  "model": "gemini-1.5-flash",
  "auto_run_safe": false,
  "aliases": {
    "listpy": "list all python files",
    "cleanup": "remove temporary files"
  }
}
```

### **Setup Commands**
```bash
# Interactive setup (recommended)
linaix --setup

# Set API key directly
linaix --set-api-key "your-api-key-here"
```

### **Environment Variables**
```bash
export GOOGLE_API_KEY="your-api-key-here"
```

---

## 🖼️ Screenshots

<div align="center">

### Interactive Mode Demo
![LinAIx Interactive Mode](Interactivemode.png)

*Screenshot showing the AI-powered terminal interface with natural language input and command generation*

</div>

---

## 🔧 Troubleshooting

### **Common Issues**

#### **"No Google API key found"**
```bash
# Use the interactive setup (recommended)
linaix --setup

# Or set your API key via environment variable
export GOOGLE_API_KEY="your-api-key-here"

# Or set API key directly
linaix --set-api-key "your-api-key-here"
```

#### **"Permission denied"**
```bash
# Make the script executable
chmod +x linaix.py

# Or run with python explicitly
python3 linaix.py --interactive
```

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### **Getting Started**
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Test thoroughly
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

### **Development Setup**
```bash
git clone https://github.com/AdirAli/linaix.git
cd linaix
pip install -r requirements.txt
```

### **Code Style**
- Follow PEP 8 guidelines
- Add type hints where appropriate
- Include docstrings for new functions
- Write tests for new features

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


<div align="center">

**Made wit for the Linux community**

[![GitHub stars](https://img.shields.io/github/stars/AdirAli/linaix?style=social)](https://github.com/yourusername/linaix)
[![GitHub forks](https://img.shields.io/github/forks/AdirAli/linaix?style=social)](https://github.com/yourusername/linaix)
[![GitHub issues](https://img.shields.io/github/issues/AdirAli/linaix)](https://github.com/yourusername/linaix/issues)

</div>
