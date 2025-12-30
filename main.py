import chess
from minimax import minimax
import heuristic  # this patches custom eval

SEARCH_DEPTH = 3


def play_game():
    board = chess.Board()

    while True:
        choice = input("Choose your side (w/b): ").strip().lower()
        if choice in ["w", "b"]:
            player_is_white = choice == "w"
            break
        else:
            print("Invalid choice. Type 'w' for White or 'b' for Black.")

    print(f"You are playing as {'White' if player_is_white else 'Black'}.")

    while not board.is_game_over():
        print("\nCurrent Board:\n")
        print(board)

        if board.turn == chess.WHITE:
            if player_is_white:
                move_uci = (
                    input("\nYour move (e7e5, a2a4, or 'undo'): ").strip().lower()
                )

                if move_uci == "undo":
                    if len(board.move_stack) >= 2:
                        board.pop()  # Undo AI move
                        board.pop()  # Undo player move
                        print("Last full turn undone.")
                    else:
                        print("Nothing to undo.")
                    continue

                try:
                    move = chess.Move.from_uci(move_uci)
                    if move in board.legal_moves:
                        board.push(move)
                    else:
                        print("Illegal move. Try again.")
                except:
                    print("Invalid format. Try again.")
            else:
                _, ai_move = minimax(board, SEARCH_DEPTH, True)
                print(f"AI plays: {ai_move}")
                board.push(ai_move)
        else:
            if not player_is_white:
                move_uci = (
                    input("\nYour move (e7e5, a2a4, or 'undo'): ").strip().lower()
                )

                if move_uci == "undo":
                    if len(board.move_stack) >= 2:
                        board.pop()  # Undo AI move
                        board.pop()  # Undo player move
                        print("Last full turn undone.")
                    else:
                        print("Nothing to undo.")
                    continue

                try:
                    move = chess.Move.from_uci(move_uci)
                    if move in board.legal_moves:
                        board.push(move)
                    else:
                        print("Illegal move. Try again.")
                except:
                    print("Invalid format. Try again.")
            else:
                _, ai_move = minimax(board, SEARCH_DEPTH, True)
                print(f"AI plays: {ai_move}")
                board.push(ai_move)

    print("\nGame Over!")
    print("Result:", board.result())


if __name__ == "__main__":
    play_game()
