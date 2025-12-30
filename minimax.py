import chess
import numpy as np


def evaluate_board(board: chess.Board) -> int:
    """Evaluates the board position based on material.

    Args:
        board (chess.Board): The current chess board.

    Returns:
        int: Evaluation score (positive if White is better, negative if Black is better).
    """
    piece_values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
        chess.KING: 0,
    }

    value = 0
    for piece_type, piece_value in piece_values.items():
        value += len(board.pieces(piece_type, chess.WHITE)) * piece_value
        value -= len(board.pieces(piece_type, chess.BLACK)) * piece_value
    return value


def minimax(
    board: chess.Board, depth: int, maximizing_player: bool
) -> tuple[int, chess.Move]:
    """Performs the Minimax search algorithm.

    Args:
        board (chess.Board): The current chess board.
        depth (int): Search depth.
        maximizing_player (bool): True if maximizing player's turn, else False.

    Returns:
        tuple[int, chess.Move]: Evaluation score and the best move.
    """
    if depth == 0 or board.is_game_over():
        return evaluate_board(board), None

    best_move = None

    if maximizing_player:
        max_eval = -np.inf
        for move in board.legal_moves:
            board.push(move)
            evaluation, _ = minimax(board, depth - 1, False)
            board.pop()
            if evaluation > max_eval:
                max_eval = evaluation
                best_move = move
        return max_eval, best_move
    else:
        min_eval = np.inf
        for move in board.legal_moves:
            board.push(move)
            evaluation, _ = minimax(board, depth - 1, True)
            board.pop()
            if evaluation < min_eval:
                min_eval = evaluation
                best_move = move
        return min_eval, best_move


def maximize(board: chess.Board, depth: int, a: float, b: float):
    if depth == 0 or board.is_game_over():
        return evaluate_board(board), None

    best = None
    maxEval = -np.inf

    for move in board.legal_moves:
        board.push(move)
        score, _ = minimize(board, depth - 1, a, b)
        board.pop()

        if score > maxEval:
            maxEval, best = score, move
        a = max(a, score)
        if a >= b:
            break
    return maxEval, best

def minimize(board: chess.Board, depth: int, a: float, b: float):
    if depth == 0 or board.is_game_over():
        return evaluate_board(board), None

    best = None
    minEval = np.inf

    for move in board.legal_moves:
        board.push(move)
        score, _ = maximize(board, depth - 1, a, b)
        board.pop()

        if score < minEval:
            minEval, best = score, move
        b = min(b, score)
        if b <= a:
            break

    return minEval, best
    
def minimax_ab(
    board: chess.Board, depth: int, maximizingPlayer: bool,  alpha: float = -np.inf, beta: float = np.inf) -> tuple[int, chess.Move]:
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
    if (maximizingPlayer):
        return maximize(board, depth, alpha, beta)
    else:
        return minimize(board, depth, alpha, beta)