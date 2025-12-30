import sys
import pygame
import chess
import os
import random

from minimax import minimax, minimax_ab
from heuristic import evaluate_board
import minimax as _minimax

SCREEN_SIZE = 640
BOARD_SIZE = 512
SQUARE_SIZE = BOARD_SIZE // 8
FPS = 30

COLOR_LIGHT = (245, 245, 245)
COLOR_DARK = (100, 100, 100)
COLOR_HIGHLIGHT = (70, 130, 180)
COLOR_BUTTON = (70, 130, 180)
COLOR_BG = (200, 200, 200)
COLOR_TEXT = (0, 0, 0)
COLOR_ERROR = (200, 0, 0)

UNICODE_PIECES = {
    chess.PAWN: {True: "♙", False: "♟"},
    chess.KNIGHT: {True: "♘", False: "♞"},
    chess.BISHOP: {True: "♗", False: "♝"},
    chess.ROOK: {True: "♖", False: "♜"},
    chess.QUEEN: {True: "♕", False: "♛"},
    chess.KING: {True: "♔", False: "♚"},
}

ASSET_DIR = os.path.join(os.path.dirname(__file__), "chess_piece_images")
PIECE_IMAGES = {}


def load_piece_images():
    """Load and scale chess piece images into the PIECE_IMAGES cache."""
    pieces = ["p", "n", "b", "r", "q", "k"]
    colors = {"w": True, "b": False}

    for color_code, color_bool in colors.items():
        for piece_code in pieces:
            filename = f"{color_code}{piece_code}.png"
            path = os.path.join(ASSET_DIR, filename)

            try:
                image = pygame.image.load(path).convert_alpha()
                image = pygame.transform.smoothscale(
                    image, (SQUARE_SIZE, SQUARE_SIZE)
                )
                piece_type = {
                    "p": chess.PAWN,
                    "n": chess.KNIGHT,
                    "b": chess.BISHOP,
                    "r": chess.ROOK,
                    "q": chess.QUEEN,
                    "k": chess.KING,
                }[piece_code]

                PIECE_IMAGES[(piece_type, color_bool)] = image
            except Exception as exc:
                print(f"Failed to load {path}: {exc}")


def clamp(value, low, high):
    """Restrict a value to the inclusive range [low, high]."""
    return max(low, min(value, high))


class Button:
    """Represents a clickable UI button."""

    def __init__(self, rect, text, font):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.selected = False

    def handle_event(self, event):
        """Check for mouse click within the button area.

        Args:
            event (pygame.event.Event): The event to check.

        Returns:
            bool: True if this button was clicked.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(
            event.pos
        ):
            return True
        return False

    def draw(self, surface):
        """Render the button on the given surface."""
        background_color = COLOR_BUTTON if self.selected else COLOR_LIGHT
        pygame.draw.rect(surface, background_color, self.rect)
        text_surface = self.font.render(self.text, True, COLOR_TEXT)
        surface.blit(text_surface, text_surface.get_rect(center=self.rect.center))


class GameUI:
    """Main class managing the game UI, input handling, and game loop."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
        pygame.display.set_caption("Chess AI UI")
        self.clock = pygame.time.Clock()
        self.font_small = pygame.font.SysFont(None, 24)
        self.font_medium = pygame.font.SysFont(None, 32)
        self.game_over = False
        self.endgame_message = ""

        load_piece_images()

        button_width, button_height, padding = 150, 50, 20
        vertical_group_spacing = 80
        center_x = SCREEN_SIZE // 2

        side_y = 120
        algo_y = side_y + vertical_group_spacing
        difficulty_y = algo_y + vertical_group_spacing

        self.side_buttons = [
            Button(
                (center_x - button_width - padding // 2, side_y, button_width, button_height),
                "Play as White",
                self.font_medium,
            ),
            Button(
                (center_x + padding // 2, side_y, button_width, button_height),
                "Play as Black",
                self.font_medium,
            ),
        ]

        self.algo_buttons = [
            Button(
                (center_x - button_width - padding // 2, algo_y, button_width, button_height),
                "Minimax",
                self.font_medium,
            ),
            Button(
                (center_x + padding // 2, algo_y, button_width, button_height),
                "AlphaBeta",
                self.font_medium,
            ),
        ]

        self.diff_buttons = [
            Button(
                (
                    center_x - button_width - padding - button_width // 2,
                    difficulty_y,
                    button_width,
                    button_height,
                ),
                "Easy",
                self.font_medium,
            ),
            Button((center_x - button_width // 2, difficulty_y, button_width, button_height),
                   "Medium",
                   self.font_medium),
            Button(
                (
                    center_x + button_width // 2 + padding,
                    difficulty_y,
                    button_width,
                    button_height,
                ),
                "Hard",
                self.font_medium,
            ),
        ]

        self.diff_buttons[1].selected = True
        self.selecting = True
        self.paused = False

        _minimax.evaluate_board = evaluate_board

        self.board = None
        self.player_side = True
        self.algo = "minimax"
        self.search_depth = 3
        self.selected_square = None
        self.valid_moves = []
        self.message = ""
        self.message_time = 0
        self.illegal_animation = None

        self.player_color = chess.WHITE if self.player_side else chess.BLACK
        self.ai_color = not self.player_color

        if self.diff_buttons[0].selected:
            self.search_depth = 2
        elif self.diff_buttons[1].selected:
            self.search_depth = 3
        else:
            self.search_depth = 4

        icon_size = 32
        self.player_icon = pygame.transform.smoothscale(
            PIECE_IMAGES[(chess.KING, self.player_color)], (icon_size, icon_size)
        )
        self.ai_icon = pygame.transform.smoothscale(
            PIECE_IMAGES[(chess.KING, self.ai_color)], (icon_size, icon_size)
        )

    def draw_side_info(self):
        """Draw player and AI icons with turn indicator."""
        x0, y0 = 10, 10  # Top-left corner
        self.screen.blit(self.player_icon, (x0, y0))
        lbl = self.font_small.render("You", True, COLOR_TEXT)
        self.screen.blit(lbl, (x0 + self.player_icon.get_width() + 5, y0 + 8))

        x1 = SCREEN_SIZE - self.ai_icon.get_width() - 10  # Top-right
        self.screen.blit(self.ai_icon, (x1, y0))
        lbl2 = self.font_small.render("AI", True, COLOR_TEXT)
        self.screen.blit(lbl2, (x1 - lbl2.get_width() - 5, y0 + 8))

    def show_menu(self):
        """Display the start menu and handle user selections."""
        while self.selecting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                for group in (
                    self.side_buttons,
                    self.algo_buttons,
                    self.diff_buttons,
                ):
                    for button in group:
                        if button.handle_event(event):
                            for btn in group:
                                btn.selected = False
                            button.selected = True

                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    self.selecting = False

            self.screen.fill(COLOR_BG)
            for buttons in (
                self.side_buttons,
                self.algo_buttons,
                self.diff_buttons,
            ):
                for button in buttons:
                    button.draw(self.screen)

            prompt_surface = self.font_medium.render(
                "Press Enter to Start", True, COLOR_TEXT
            )
            self.screen.blit(
                prompt_surface,
                prompt_surface.get_rect(
                    center=(SCREEN_SIZE // 2, SCREEN_SIZE // 2 + 250)
                ),
            )

            pygame.display.flip()
            self.clock.tick(FPS)

        self.board = chess.Board()
        self.player_side = self.side_buttons[0].selected
        self.algo = (
            "minimax"
            if self.algo_buttons[0].selected
            else "alphabeta"
        )
        if self.diff_buttons[0].selected:
            self.search_depth = 2
        elif self.diff_buttons[1].selected:
            self.search_depth = 3
        else:
            self.search_depth = 4

    def show_pause_overlay(self):
        """Render the paused state overlay."""
        overlay = pygame.Surface((SCREEN_SIZE, SCREEN_SIZE))
        overlay.set_alpha(180)
        overlay.fill((50, 50, 50))
        self.screen.blit(overlay, (0, 0))
        paused_surface = self.font_medium.render(
            "Paused - Press ESC to resume", True, COLOR_TEXT
        )
        self.screen.blit(
            paused_surface,
            paused_surface.get_rect(
                center=(SCREEN_SIZE // 2, SCREEN_SIZE // 2)
            ),
        )

    def ai_move(self):
        """Compute and apply the AI's next move."""
        try:
            if self.algo == "minimax":
                _, move = minimax(
                    self.board, self.search_depth, self.board.turn == chess.WHITE
                )
            else:
                _, move = minimax_ab(
                    self.board,
                    self.search_depth,
                    self.board.turn == chess.WHITE,
                    float("-inf"),
                    float("inf"),
                    
                )
            self.board.push(move)
        except Exception as exc:
            print(f"AI error: {exc}")

    def check_game_over(self):
        """Check and handle all game-over conditions.

        Returns:
            bool: True if the game has ended.
        """
        if self.board.is_checkmate():
            winner = "Black" if self.board.turn else "White"
            self.endgame_message = f"Checkmate! {winner} wins."
        elif self.board.is_stalemate():
            self.endgame_message = "Stalemate! Draw."
        elif self.board.is_insufficient_material():
            self.endgame_message = "Draw by insufficient material."
        elif self.board.can_claim_threefold_repetition():
            self.endgame_message = "Draw by threefold repetition."
        elif self.board.can_claim_fifty_moves():
            self.endgame_message = "Draw by fifty-move rule."
        else:
            return False

        self.paused = True
        self.game_over = True
        return True

    def show_endgame_overlay(self):
        """Render the end-of-game overlay with result and restart prompt."""
        overlay = pygame.Surface((SCREEN_SIZE, SCREEN_SIZE))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        big_font = pygame.font.SysFont(None, 48)
        text_surface = big_font.render(self.endgame_message, True, COLOR_LIGHT)
        self.screen.blit(
            text_surface,
            text_surface.get_rect(center=(SCREEN_SIZE // 2, SCREEN_SIZE // 2 - 20)),
        )

        prompt_surface = pygame.font.SysFont(None, 32).render(
            "Press R to restart", True, COLOR_LIGHT
        )
        self.screen.blit(
            prompt_surface,
            prompt_surface.get_rect(
                center=(SCREEN_SIZE // 2, SCREEN_SIZE // 2 + 30)
            ),
        )

    def run(self):
        """Main loop: handle events, update state, and render frames."""
        self.show_menu()

        if not self.player_side:
            self._show_loading()
            self.ai_move()

        while True:
            now_ticks = pygame.time.get_ticks()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if self.game_over:
                    if (
                        event.type == pygame.KEYDOWN
                        and event.key == pygame.K_r
                    ):
                        self.board = chess.Board()
                        self.selected_square = None
                        self.valid_moves = []
                        self.paused = False
                        self.game_over = False
                        self.endgame_message = ""
                    continue

                if (
                    event.type == pygame.KEYDOWN
                    and event.key == pygame.K_ESCAPE
                ):
                    self.paused = not self.paused

                if self.paused:
                    continue

                if (
                    self.board.turn == self.player_side
                    and event.type == pygame.MOUSEBUTTONDOWN
                ):
                    x, y = event.pos
                    board_rect = pygame.Rect(
                        (SCREEN_SIZE - BOARD_SIZE) // 2,
                        (SCREEN_SIZE - BOARD_SIZE) // 2,
                        BOARD_SIZE,
                        BOARD_SIZE,
                    )
                    if board_rect.collidepoint(x, y):
                        file_index = clamp(
                            (x - board_rect.x) // SQUARE_SIZE, 0, 7
                        )
                        rank_index = clamp(
                            (y - board_rect.y) // SQUARE_SIZE, 0, 7
                        )
                        square = self.flip_board(file_index, rank_index)
                        piece = self.board.piece_at(square)

                        if self.selected_square == square:
                            self.selected_square = None
                            self.valid_moves = []
                            continue

                        if self.selected_square is None:
                            if piece and piece.color == self.player_side:
                                self.selected_square = square
                                self.valid_moves = [
                                    move.to_square
                                    for move in self.board.legal_moves
                                    if move.from_square == square
                                ]
                            else:
                                self._show_message("Select your piece")
                        else:
                            move = chess.Move(
                                self.selected_square, square
                            )
                            if move in self.board.legal_moves:
                                self.board.push(move)
                                self.selected_square = None
                                self.valid_moves = []

                                if self.check_game_over():
                                    break

                                self._show_loading()
                                self.ai_move()

                                self.check_game_over()
                            else:
                                self.illegal_animation = {
                                    "sq": self.selected_square,
                                    "start": now_ticks,
                                }
                                self.selected_square = None
                                self.valid_moves = []

            self.draw_board()

            if self.game_over:
                self.show_endgame_overlay()
            elif self.paused:
                self.show_pause_overlay()

            pygame.display.flip()
            self.clock.tick(FPS)

    def _show_message(self, text):
        """Display a transient error or info message at bottom of screen."""
        self.message = text
        self.message_time = pygame.time.get_ticks()

    def _show_loading(self):
        """Render a loading indicator for AI thinking."""
        loading_surface = self.font_medium.render(
            "AI is thinking...", True, COLOR_TEXT
        )
        self.screen.blit(
            loading_surface,
            loading_surface.get_rect(center=(SCREEN_SIZE // 2, 40)),
        )
        pygame.display.flip()
    
    def flip_board(self, f, r) -> chess.Square:
        if self.player_side:
            return chess.square(f, 7 - r)
        else:
            return chess.square(7 - f, r)

    def draw_board(self):
        """Draw the chess board, pieces, highlights, and messages."""
        self.screen.fill(COLOR_BG)
        self.draw_side_info()
        board_surface = pygame.Surface((BOARD_SIZE, BOARD_SIZE))
        current_ticks = pygame.time.get_ticks()

        for rank in range(8):
            for file in range(8):
                light_square = (file + rank) % 2 == 0
                square_rect = pygame.Rect(
                    file * SQUARE_SIZE, rank * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE
                )
                square_color = COLOR_LIGHT if light_square else COLOR_DARK
                pygame.draw.rect(board_surface, square_color, square_rect)

                square_index = self.flip_board(file, rank)
                if square_index in self.valid_moves:
                    pygame.draw.rect(board_surface, COLOR_HIGHLIGHT, square_rect, 3)

                dx = dy = 0
                if (
                    self.illegal_animation
                    and self.illegal_animation["sq"] == square_index
                ):
                    elapsed = current_ticks - self.illegal_animation["start"]
                    if elapsed < 500:
                        if (elapsed // 100) % 2 == 0:
                            pygame.draw.rect(
                                board_surface, COLOR_ERROR, square_rect, 3
                            )
                        offset = random.randint(-5, 5)
                        dx = dy = offset
                    else:
                        self.illegal_animation = None

                piece = self.board.piece_at(square_index)
                if piece:
                    image = PIECE_IMAGES.get((piece.piece_type, piece.color))
                    if image:
                        board_surface.blit(image, square_rect.move(dx, dy))
                    else:
                        glyph = UNICODE_PIECES[piece.piece_type][piece.color]
                        font = pygame.font.SysFont("dejavusans", SQUARE_SIZE)
                        text_img = font.render(glyph, True, COLOR_TEXT)
                        board_surface.blit(
                            text_img, text_img.get_rect(center=square_rect.center)
                        )

        if self.message and current_ticks - self.message_time < 2000:
            message_surface = self.font_small.render(
                self.message, True, COLOR_ERROR
            )
            self.screen.blit(message_surface, (10, SCREEN_SIZE - 30))

        self.screen.blit(
            board_surface,
            board_surface.get_rect(
                center=(SCREEN_SIZE // 2, SCREEN_SIZE // 2)
            ),
        )


def main():
    ui = GameUI()
    ui.run()


if __name__ == "__main__":
    main()
