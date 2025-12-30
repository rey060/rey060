import chess
from minimax import minimax, minimax_ab


def play_game() -> None:
    """Runs an interactive chess game utilzing the chess library."""
    board = chess.Board()

    player_is_white = _choose_player_side()
    ai_algorithm = _choose_ai_algorithm()

    print(f"You are playing as {'White' if player_is_white else 'Black'}.")

    while not board.is_game_over():
        print("\nCurrent Board:\n")
        print(board)

        if board.turn == chess.WHITE:
            if player_is_white:
                _player_move(board)
            else:
                _ai_move(board, ai_algorithm)
        else:
            if not player_is_white:
                _player_move(board)
            else:
                _ai_move(board, ai_algorithm)

    print("\nGame Over!")
    print("Result:", board.result())


def _choose_player_side() -> bool:
    """Prompts the user to choose a side.

    Returns:
        bool: True if player chooses White, False otherwise.
    """
    while True:
        choice = input("Choose your side (w/b): ").strip().lower()
        if choice in ["w", "b"]:
            return choice == "w"
        print("Invalid choice. Type 'w' for White or 'b' for Black.")


def _choose_ai_algorithm() -> str:
    """Prompts the user to choose the AI algorithm.

    Returns:
        str: The name of the chosen algorithm ('minimax' or 'alphabeta').
    """
    while True:
        algo = input("Choose AI algorithm (minimax/alphabeta): ").strip().lower()
        if algo in ["minimax", "alphabeta"]:
            return algo
        print("Invalid choice. Type 'minimax' or 'alphabeta'.")


def _player_move(board: chess.Board) -> None:
    """Prompts the player to make a move.

    Args:
        board (chess.Board): The current chess board.
    """
    move_uci = input("\nYour move (e.g., e7e5, a2a4): ").strip()
    try:
        move = chess.Move.from_uci(move_uci)
        if move in board.legal_moves:
            board.push(move)
        else:
            print("Illegal move. Try again.")
    except ValueError:
        print("Invalid move format. Try again.")


def _ai_move(board: chess.Board, algorithm: str) -> None:
    """Makes a move for the AI using the selected algorithm.

    Args:
        board (chess.Board): The current chess board.
        algorithm (str): The AI algorithm to use ('minimax' or 'alphabeta').
    """
    if algorithm == "minmax":
        _, ai_move = minimax(board, 2, True)
    else:
        _, ai_move = minimax_ab(board, 2, float("-inf"), float("inf"), True)

    print(f"AI plays: {ai_move}")
    board.push(ai_move)


if __name__ == "__main__":
    play_game()
