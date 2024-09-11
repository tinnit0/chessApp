import chess.pgn
import chess
from board import ChessBoard
import random
import tkinter.simpledialog as simpledialog

BOARD_SIZE = 500
SQUARE_SIZE = BOARD_SIZE // 8


class ChessGame:
    def __init__(self, canvas, images, pgn_file="game.pgn"):
        self.board = ChessBoard(canvas, images)
        self.player_color = random.choice([chess.WHITE, chess.BLACK])
        self.board.draw_board()


        self.pgn_game = chess.pgn.Game()
        self.current_node = self.pgn_game.add_variation(chess.Move.null())
        self.pgn_file = pgn_file
        self.decide_first_turn()

        # with open(self.pgn_file, 'w') as f:
        #     f.write(self.pgn_game.headers_to_string() + '\n')

    def decide_first_turn(self):
        if self.player_color == chess.BLACK:
            self.make_random_opponent_move()

    def make_random_opponent_move(self):
        legal_moves = self.board.get_legal_moves()
        if legal_moves:
            random_move = random.choice(legal_moves)
            if self.board.is_pawn_promotion(random_move):
                random_move = chess.Move(
                    random_move.from_square, random_move.to_square, promotion=chess.QUEEN)
            self.board.push_move(random_move)
            self.log_move(random_move, "Opponent")
            self.check_game_over()

    def log_move(self, move, player):
        move_str = move.uci()
        if player == "Player":
            self.current_node = self.current_node.add_variation(move)
        elif player == "Opponent":
            self.current_node = self.current_node.add_variation(move)

    def save_game(self):
        with open(self.pgn_file, 'a') as f:
            f.write(self.pgn_game.accept(chess.pgn.StringExporter()) +
                    '\n\n')

    def check_game_over(self):
        if self.board.is_game_over() == True:
            print('game ended')
            self.save_game()
            self.board.reset_board()

    def handle_click(self, event):
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
                        promotion_map = {'q': chess.QUEEN, 'r': chess.ROOK,
                                         'b': chess.BISHOP, 'n': chess.KNIGHT}
                        promotion_piece = promotion_map.get(
                            promotion_choice.lower(), chess.QUEEN)

                if promotion_piece:
                    move = chess.Move(self.board.selected_piece, square,
                                      promotion=promotion_piece)
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