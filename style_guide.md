# B351 Project Style Guide

## Code Formatting (Black)

- Always format code with [`black`](https://black.readthedocs.io/).
- Use default settings (88-character line length).
- Do not manually tweak spacing, alignment, or indentation.
- No trailing commas needed unless Black adds them.
- **Always autoformat** before committing code.

```bash
black .
```

## Docstrings (Google Style)

Use [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) format for all public modules, classes, and functions.

### Function Example

```python
def minimax_ab(board: chess.Board, depth: int, alpha: float, beta: float, maximizing_player: bool) -> tuple[int, chess.Move]:
    """Performs the Minimax search algorithm with Alpha-Beta pruning.

    Args:
        board (chess.Board): The current chess board.
        depth (int): Search depth.
        alpha (float): Alpha value.
        beta (float): Beta value.
        maximizing_player (bool): True if maximizing player's turn, otherwise False.

    Returns:
        tuple[int, chess.Move]: Evaluation score and the best move.
    """
```
## Naming Conventions

We are using PEP 8 for naming conventions: https://www.python.org/dev/peps/pep-0008/#naming-conventions

 - Follow snake_case for functions and variable names.

 - Use PascalCase (CapWords) for class names.

 - Constants should be UPPER_CASE_WITH_UNDERSCORES
---
