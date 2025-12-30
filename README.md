# Chess Visualization Engine

**B351 / Q351 Final Project**  
A visual and interactive chess AI built in Python using Pygame and python-chess.

---

## Overview

This project is a chess engine and GUI that allows a human to play against an AI. The AI uses:
- **Minimax** and **Alpha-Beta Pruning** 
- A **custom heuristic** for board evaluation 
- A Pygame-powered GUI for a visual chess experience
- Full support for piece movement, game rules, and endgame detection
  
---

## Team Members & Contributions

- Aadi Khanna: Minimax algorithm and alpha-beta pruning logic
- Colton Romines: Custom heuristic evaluator for board evaluation
- Rey Chaudhary: GUI implementation and game flow
- Ethan Parr: GUI and CLI implementation and integration with core engine

---

## Features

-  Play as White or Black
-  Choose between Minimax and Alpha-Beta Pruning
-  Select difficulty (Easy / Medium / Hard)
-  GUI board with click-to-move controls
-  Undo functionality
-  Full legal move enforcement
-  Custom board evaluation logic

---

## AI Logic

The AI decision-making is based on:
- **Minimax search** with configurable depth
- **Alpha-beta pruning** to reduce computation
- **Heuristic evaluation** that considers:
  - Material balance
  - Positional values (via piece-square tables)
  - Game phase
  - king safety

---

## Directory

- **heuristic.py** Contains code used for heuristic, replaces board evaluation function in minimax.py
- **main_cli.py** Component has CLI based game logic, run using python/python3 main.py (driver)
- **main_ui.py** Component to launch full game with UI, run using python/python3 main_ui.py
- **main.py** Driver component for main_cli.p, run using python/python3 main.py.
- **minimax.py** Contains the search algorithm logic for the minimax and minimax_ab functions, along with the helper "minimize" and "maximize" functions.
- **requirements.txt** Contains list of all required libraries to run project.

---


To run with the visualized UI, please run the command:

`python3 main_ui.py` for macOS
`python main_ui.py` for Windows

To install necessary libraries **prefix pip3 for macOS and pip for Windows**
`pip install -r requirements.txt`

#### [Style Guide](style_guide.md)
