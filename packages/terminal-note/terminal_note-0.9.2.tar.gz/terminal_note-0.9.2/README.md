[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/belousovsergey56/terminal-note/actions/workflows/Tests.yml/badge.svg?branch=main)](https://github.com/belousovsergey56/terminal-note/actions/workflows/Tests.yml)

[Русский](README-ru.md)

# terminal-note
A console utility for creating and managing notes without leaving the terminal.

# Contents
- [Motivation](#motivation)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Demo](#demo)
- [Dependencies](#dependencies)
- [Configuration file](#configuration-file)
- [Storage structure](#storage-structure)
- [Example template `template.md`](#example-template-templatemd)
- [Ideas](#ideas)


## Motivation
I mostly work in the terminal and use tools like `nvim`, `rg`, `fd`, and `fzf`. For note-taking, I use Obsidian — it stores notes locally in separate `.md` files, which is very convenient. However, launching Obsidian takes time, and constantly switching between the terminal and a GUI application disrupts my workflow.

To stay inside the terminal, I wrote `terminal-note` — a utility that allows you to quickly create, search, and manage notes directly from the console.

## Features
- Create notes with one command without opening an editor.
- Search, open, delete, and read notes using `fzf`.
- Notes are saved in Markdown (`.md`) format.
- Support for templates and flexible configuration through a config file.
- Works with a chosen directory — easily integrates with Obsidian.
- Write notes in your favorite console editor: nvim, micro, and others.


## Installation
1. Install via pip:

```bash
pip install terminal-note --user
```

2. Verify it works:

```bash
tn --help
```


# Usage
- `tn --config` or `tn -c` — open the configuration file.
- `tn "note text"` — create a quick note. The file will be named by a template (`2025-04-05 15:30:00.md`) and saved in the specified directory.
- `tn -o` — create or open a note. First, enter the file name, then the editor opens. If the file exists — it is edited; if not — created.
- `tn -d` — delete a note. The file is selected for deletion via `fzf`.
- `tn -r` — read a note. The file is selected through `fzf` and opened in `frogmouth` (which parses Markdown with navigation support).


### Demo

##### Displaying help
![Вызов справки](https://github.com/belousovsergey56/belousovsergey56/blob/main/assets/help.gif)

###### Editing the config file
![Конфиг файл](https://github.com/belousovsergey56/belousovsergey56/blob/main/assets/config.gif)

###### Inline note creation
![inline note](https://github.com/belousovsergey56/belousovsergey56/blob/main/assets/inlinenote.gif)

###### Editing a note
![edit](https://github.com/belousovsergey56/belousovsergey56/blob/main/assets/edit.gif)

###### Creating a new note
![new note](https://github.com/belousovsergey56/belousovsergey56/blob/main/assets/newfile.gif)

###### Deleting a note
![delete note](https://github.com/belousovsergey56/belousovsergey56/blob/main/assets/delete.gif)

###### Reading a note
![read](https://github.com/belousovsergey56/belousovsergey56/blob/main/assets/read.gif)

# Dependencies

- python >= 3.11
- iterfzf >= 1.8.0.62.0
- frogmouth >= 0.9.2


# Configuration file

```toml
# Storage mode (files only)
storage_mode = "files"

# Path to the directory where notes will be stored.
# The script parses only the $HOME variable. If a special path is needed, specify it fully.
path_to_storage_directory = "$HOME/terminal_note"

# File extension for notes: txt, md (without the dot .md)
file_extension = "md"

# Utility for reading non-md files: bat, cat, less
file_reader = "cat"

# Path to the template file.
path_to_template_note = "$HOME/terminal_note/Templates/template.md"

# Editor to write notes comfortably: vi, vim, nvim, micro, nano, etc.
editor = "vi"
```


### Storage structure

Example storage structure:

```bash
➜  ~ tree terminal_note
$HOME/terminal_note/
├── 2025-07-22 22:32:26.md
├── 2025-07-22 22:34:56.md
├── 2025-07-27 00:41:52.md
├── Gurtam
│   ├── 1. Vialon.md
│   ├── 2. Token authentication.md
│   └── 3. Searching elements.md
├── My Book.md
└── Templates
    └── template.md

3 directories, 8 files
```


### Example template (template.md)

```markdown
---
Creation date:
Modification date:
links:
tags:
---
```


# Ideas

- [ ] Git integration: `tn -g` will perform `pull`, `add`, `commit`, `push`.
- [ ] Support storage in a database (not sure yet — as it breaks compatibility with Obsidian).
- [ ] Possibly store inline quick notes in a separate directory for easier searching.

