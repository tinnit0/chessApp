import chess.pgn
import chess
from board import ChessBoard
import random
import tkinter.simpledialog as simpledialog
import tkinter as tk

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
        self.ai_color = None
        
        self.load_pgn()
        self.decide_first_turn()

        self.status_label = tk.Label(
            root, text="1 = Player vs AI, 2 = AI vs AI", font=("Arial", 12), anchor="w")
        self.status_label.pack(side="bottom", fill="x")

        self.board.draw_board()
        self.bind_keys()

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
        
        print(f"Current FEN: {self.board.board.fen()}")
        legal_moves = self.board.get_legal_moves()
        print(f"Legal Moves: {legal_moves}")

        if self.pgn_moves:
            next_pgn_move = self.pgn_moves.pop(0)
            if next_pgn_move in legal_moves:
                move = next_pgn_move
            else:
                print(f"PGN move {
                      next_pgn_move} not legal, picking a random move.")
                move = random.choice(legal_moves)
        else:
            move = random.choice(legal_moves)

        if move:
            if self.board.is_pawn_promotion(move):
                move = chess.Move(move.from_square,
                                  move.to_square, promotion=chess.QUEEN)
            self.board.push_move(move)
            print(f"Move made: {move}")
            print(f"New FEN: {self.board.board.fen()}")
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
                break
            self.make_random_opponent_move()
            self.board.draw_board()
            self.root.update()
            self.root.after(10)
