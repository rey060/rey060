"""heuristic.py
Importing it once will
patch   `minmax.evaluate_board`   so every subsequent minimax search uses the
new heuristic.

Key features implemented
• Material with bishop‑pair bonus
• Center control bonus (16‑square extended center)
• King safety: pawn shield + (semi)‑open files for both short and long castle
• Pawn structure: isolated & doubled pawns penalties
• Piece mobility: weighted move count per side

All weights are in **centipawns**.
"""

import chess
import minimax

ORIG_EVAL = minimax.evaluate_board

#   Piece values (centipawns)
PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 0,  # handled separately
}
BISHOP_PAIR_BONUS = 30


#   Center control
#   Extended center = squares c3–f6 (files 2‑5, ranks 2‑5)
EXT_CENTER = [
    chess.square(file, rank)
    for file in range(2, 6)  # c‑f files (0=a)
    for rank in range(2, 6)
]  # 3‑6 ranks (0=1st rank)
CENTER_BONUS = 10  # cp per square occupied in extended center


#   King‑safety parameters
PAWN_SHIELD_PENALTY = 15  # missing shield pawn
SEMI_OPEN_PENALTY = 10  # enemy pawn on file
OPEN_FILE_PENALTY = 20  # completely open file

# map castle square → (shield squares, files to check)
_KING_DEF = {
    chess.G1: ([chess.F2, chess.G2, chess.H2], (5, 6, 7)),  # O‑O white
    chess.C1: ([chess.B2, chess.C2, chess.D2], (1, 2, 3)),  # O‑O‑O white
    chess.G8: ([chess.F7, chess.G7, chess.H7], (5, 6, 7)),  # O‑O black
    chess.C8: ([chess.B7, chess.C7, chess.D7], (1, 2, 3)),  # O‑O‑O black
}

#   Mobility parameters
MOBILITY_WEIGHTS = {
    chess.KNIGHT: 1.0,
    chess.BISHOP: 1.0,
    chess.ROOK: 0.5,
    chess.QUEEN: 0.1,
}
MOBILITY_UNIT = 5  # cp per weighted move

#   Helper: legal moves for a given colour without altering board.turn


def _moves_for(board: chess.Board, colour: chess.Color):
    old_turn = board.turn
    board.turn = colour
    moves = list(board.legal_moves)
    board.turn = old_turn
    return moves


#   Evaluation components


def _material(board: chess.Board):
    score = 0
    for ptype, val in PIECE_VALUES.items():
        score += (
            len(board.pieces(ptype, chess.WHITE))
            - len(board.pieces(ptype, chess.BLACK))
        ) * val
    # bishop pair
    if len(board.pieces(chess.BISHOP, chess.WHITE)) >= 2:
        score += BISHOP_PAIR_BONUS
    if len(board.pieces(chess.BISHOP, chess.BLACK)) >= 2:
        score -= BISHOP_PAIR_BONUS
    return score


def _center(board: chess.Board):
    score = 0
    for sq in EXT_CENTER:
        piece = board.piece_at(sq)
        if piece is None:
            continue
        score += CENTER_BONUS if piece.color == chess.WHITE else -CENTER_BONUS
    return score


def _king_safety(board: chess.Board):
    score = 0
    for colour, sign in ((chess.WHITE, +1), (chess.BLACK, -1)):
        ksq = board.king(colour)
        if ksq not in _KING_DEF:
            continue  # uncastled king not handled yet
        shields, files_to_check = _KING_DEF[ksq]
        # pawn shield
        for sq in shields:
            piece = board.piece_at(sq)
            if piece is None or piece.piece_type != chess.PAWN or piece.color != colour:
                score -= sign * PAWN_SHIELD_PENALTY
        # open / semi‑open files
        for f in files_to_check:
            own_pawn = any(
                chess.square_file(sq) == f for sq in board.pieces(chess.PAWN, colour)
            )
            opp_pawn = any(
                chess.square_file(sq) == f
                for sq in board.pieces(chess.PAWN, not colour)
            )
            if not own_pawn:
                score -= sign * (
                    OPEN_FILE_PENALTY if not opp_pawn else SEMI_OPEN_PENALTY
                )
    return score


def _pawn_structure(board: chess.Board):
    score = 0
    for colour, sign in ((chess.WHITE, +1), (chess.BLACK, -1)):
        pawns_by_file = {f: [] for f in range(8)}
        for sq in board.pieces(chess.PAWN, colour):
            pawns_by_file[chess.square_file(sq)].append(sq)
        for f, pawns in pawns_by_file.items():
            if len(pawns) > 1:
                score -= sign * 7 * (len(pawns) - 1)  # doubled pawn penalty
            left, right = f - 1, f + 1
            if (
                pawns
                and (left < 0 or not pawns_by_file[left])
                and (right > 7 or not pawns_by_file[right])
            ):
                score -= sign * 10 * len(pawns)  # isolated pawn penalty
    return score


def _mobility(board: chess.Board):
    score = 0
    for colour, sign in ((chess.WHITE, +1), (chess.BLACK, -1)):
        moves = _moves_for(board, colour)
        for ptype, weight in MOBILITY_WEIGHTS.items():
            count = sum(1 for m in moves if board.piece_type_at(m.from_square) == ptype)
            score += sign * int(count * weight * MOBILITY_UNIT)
    return score


#   Top‑level evaluation


def evaluate_board(board: chess.Board) -> int:
    # Terminal checks first
    if board.is_checkmate():
        return -10_000 if board.turn == chess.WHITE else 10_000
    if board.is_stalemate() or board.is_insufficient_material():
        return 0

    score = 0
    score += _material(board)
    score += _center(board)
    score += _king_safety(board)
    score += _pawn_structure(board)
    score += _mobility(board)
    return score


# patch minimax
minimax.evaluate_board = evaluate_board

#   Basic test


def _test():
    b = chess.Board()
    print("Initial:", evaluate_board(b))
    b.push_san("e4")
    b.push_san("e5")
    print("After 1.e4 e5:", evaluate_board(b))
    b.set_fen("rnbqkbnr/pppppppp/8/8/4Q3/8/PPPPPPPP/RNB1KBNR b KQkq - 0 4")
    print("Queen up:", evaluate_board(b))


if __name__ == "__main__":
    _test()
