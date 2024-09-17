import chess.pgn
import chess
from board import ChessBoard
import random
import tkinter.simpledialog as simpledialog
import tkinter as tk
# from ai import AI

BOARD_SIZE = 500
SQUARE_SIZE = BOARD_SIZE // 8


class ChessGame:
    def __init__(self, canvas, images, root, pgn_file="game.pgn"):
        self.board = ChessBoard(canvas, images)
        self.player_color = random.choice([chess.WHITE, chess.BLACK])
        self.root = root
        self.pgn_game = chess.pgn.Game()
        self.current_node = self.pgn_game.add_variation(chess.Move.null())
        self.pgn_file = pgn_file
        self.pgn_moves = []
        self.ai_vs_ai = False

        self.ai_color = chess.BLACK if self.player_color == chess.WHITE else chess.WHITE
        self.ai = AI(self.ai_color, self.board)

        self.load_pgn()
        self.decide_first_turn()

        if canvas:
            self.status_label = tk.Label(
                root, text="1 = Player vs AI, 2 = AI vs AI", font=("Arial", 12), anchor="w")
            self.status_label.pack(side="bottom", fill="x")

            self.board.draw_board()
            self.bind_keys()

    def print_board(self):
        """Print the board state in a simple text format."""
        print(self.board.board)

    def bind_keys(self):
        self.root.bind("1", self.set_player_vs_ai)
        self.root.bind("2", self.set_ai_vs_ai)

    def set_player_vs_ai(self, event=None):
        self.ai_vs_ai = False
        self.player_color = random.choice([chess.WHITE, chess.BLACK])
        self.decide_first_turn()

    def set_ai_vs_ai(self, event=None):
        self.ai_vs_ai = True
        self.run_ai_vs_ai()

    def load_pgn(self):
        try:
            with open(self.pgn_file, 'r') as pgn:
                game = chess.pgn.read_game(pgn)
                if game is not None and game.mainline_moves():
                    self.pgn_moves = list(game.mainline_moves())
                else:
                    self.pgn_moves = []
        except FileNotFoundError:
            print(f"PGN file {self.pgn_file} not found.")
            self.pgn_moves = []

    def decide_first_turn(self):
        if self.player_color == chess.BLACK:
            self.make_random_opponent_move()

    def make_random_opponent_move(self):
        if self.board.is_game_over():
            return

        move = self.ai.make_move()

        if move:
            if self.board.is_pawn_promotion(move):
                move = chess.Move(move.from_square, move.to_square,
                                promotion=chess.QUEEN)

            self.board.push_move(move)
            self.log_move(move, "Opponent")
            self.check_game_over()

    def log_move(self, move, player):
        move_str = move.uci()
        if player == "Player":
            self.current_node = self.current_node.add_variation(move)
        elif player == "Opponent":
            self.current_node = self.current_node.add_variation(move)

    def save_game(self):
        with open(self.pgn_file, 'a') as f:
            f.write(self.pgn_game.accept(chess.pgn.StringExporter()) + '\n\n')

    def check_game_over(self):
        if self.board.is_game_over():
            print('Game ended')
            self.save_game()
            self.board.reset_board()
            self.ai_vs_ai = False

    def handle_click(self, event):
        if self.ai_vs_ai:
            return
        display_col = event.x // SQUARE_SIZE
        display_row = event.y // SQUARE_SIZE
        row, col = self.board.display_to_board(display_row, display_col)
        square = row * 8 + col

        if self.board.selected_piece == square:
            self.board.selected_piece = None
            self.board.possible_moves = set()
        elif self.board.selected_piece is None:
            piece = self.board.get_piece_at(square)
            if piece and (piece.color == self.board.get_turn()) and (piece.color == self.player_color):
                self.board.selected_piece = square
                self.board.possible_moves = {
                    move.to_square for move in self.board.get_legal_moves() if move.from_square == square}
        else:
            if square in self.board.possible_moves:
                promotion_piece = None
                if self.board.get_piece_at(self.board.selected_piece).piece_type == chess.PAWN and chess.square_rank(square) in [0, 7]:
                    promotion_choice = simpledialog.askstring(
                        "Promotion", "Promote to (q, r, b, n):", parent=self.root)
                    if promotion_choice:
                        promotion_map = {
                            'q': chess.QUEEN, 'r': chess.ROOK, 'b': chess.BISHOP, 'n': chess.KNIGHT}
                        promotion_piece = promotion_map.get(
                            promotion_choice.lower(), chess.QUEEN)

                if promotion_piece:
                    move = chess.Move(self.board.selected_piece,
                                      square, promotion=promotion_piece)
                else:
                    move = chess.Move(self.board.selected_piece, square)

                if move in self.board.get_legal_moves():
                    self.board.make_move(move)
                    self.log_move(move, "Player")
                    self.check_game_over()

                if self.board.get_turn() != self.player_color:
                    self.make_random_opponent_move()
                    self.board.selected_piece = None
                    self.board.possible_moves = set()
            else:
                self.board.selected_piece = None
                self.board.possible_moves = set()

        self.board.draw_board()

    def run_ai_vs_ai(self):
        while not self.board.is_game_over() and self.ai_vs_ai:
            if self.board.is_game_over():
                print("Game over detected in loop")
                break

            print(f"Current turn: {
                'White' if self.board.get_turn() == chess.WHITE else 'Black'}")

            if self.board.get_turn() == self.ai_color:
                move = self.ai.make_move()
                print(f"AI move: {move}")
            else:
                move = self.ai.make_move()
                print(f"Opponent AI move: {move}")

            if move and move in self.board.get_legal_moves():
                self.board.push_move(move)
                self.log_move(move, "AI")
                self.board.draw_board()
                self.root.update()
                self.root.after(400)
            else:
                print("No valid move found or move is not legal")
                break


class AI:
    def __init__(self, color, board, max_depth=2):
        self.board = board
        self.color = color
        self.max_depth = max_depth
        self.successful_moves = []
        self.load_successful_moves()

    def evaluate_board(self):
        score = 0
        piece_values = {
            chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9,
            chess.KING: 0
        }

        for square in chess.SQUARES:
            piece = self.board.get_piece_at(square)
            if piece is not None:
                piece_value = piece_values.get(piece.piece_type, 0)
                if self.board.is_square_attacked(square, not piece.color):
                    attackers = self.board.get_attackers(
                        square, not piece.color)
                    defenders = self.board.get_attackers(square, piece.color)

                    if attackers:
                        attacker_values = [
                            piece_values.get(self.board.get_piece_at(
                                attacker).piece_type, 0)
                            for attacker in attackers if self.board.get_piece_at(attacker) is not None
                        ]

                        if attacker_values:
                            lowest_attacker_value = min(attacker_values)

                            if not defenders or (defenders and lowest_attacker_value < piece_value):
                                score -= piece_value  # Penalize if attacked by a stronger piece
                            else:
                                score += piece_value  # Reward if defended successfully
                else:
                    if piece.color == self.color:
                        score += piece_value
                    else:
                        score -= piece_value
            print(square, score)
        return score

    def minimax(self, depth, alpha, beta, maximizing_player):
        if depth == 0 or self.board.is_game_over():
            return self.evaluate_board(), None

        legal_moves = list(self.board.get_legal_moves())
        best_move = None

        if maximizing_player:
            max_eval = -float('inf')
            for move in legal_moves:
                self.board.push_move(move)
                evaluation, _ = self.minimax(depth - 1, alpha, beta, False)
                self.board.pop_move()
                if evaluation > max_eval:
                    max_eval = evaluation
                    best_move = move
                alpha = max(alpha, evaluation)
                if beta <= alpha:
                    break  # Beta cut-off
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for move in legal_moves:
                self.board.push_move(move)
                evaluation, _ = self.minimax(depth - 1, alpha, beta, True)
                self.board.pop_move()
                if evaluation < min_eval:
                    min_eval = evaluation
                    best_move = move
                beta = min(beta, evaluation)
                if beta <= alpha:
                    break 
            return min_eval, best_move

    def make_best_move(self):
        _, best_move = self.minimax(
            self.max_depth, -float('inf'), float('inf'), True)
        if best_move:
            return best_move
        else:
            return random.choice(list(self.board.get_legal_moves()))

    def load_successful_moves(self):
        self.successful_moves = [
            (chess.D2, chess.D4),
            (chess.D7, chess.D5)
        ]

    def translate_move(self, move):
        if self.color == chess.BLACK:
            return chess.Move(chess.square_mirror(move.from_square), chess.square_mirror(move.to_square))
        return move

    def make_move(self):
        legal_moves = list(self.board.get_legal_moves())

        for move in self.successful_moves:
            translated_move = self.translate_move(chess.Move(move[0], move[1]))
            if translated_move in legal_moves:
                print(f"Making successful move: {translated_move}")
                return translated_move

        print("No successful move found, evaluating best move.")
        return self.make_best_move()
