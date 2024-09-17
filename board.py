import chess
import tkinter as tk

BOARD_SIZE = 500
SQUARE_SIZE = BOARD_SIZE // 8


class ChessBoard:
    def __init__(self, canvas, images):
        self.board = chess.Board()
        self.selected_piece = None
        self.possible_moves = set()
        self.canvas = canvas
        self.images = images
        print(self.board)

    def draw_board(self):
        self.canvas.delete('all')
        for row in range(8):
            for col in range(8):
                display_row, display_col = self.board_to_display(row, col)
                x1, y1 = display_col * SQUARE_SIZE, display_row * SQUARE_SIZE
                x2, y2 = x1 + SQUARE_SIZE, y1 + SQUARE_SIZE
                color = '#eee' if (
                    display_row + display_col) % 2 == 0 else '#964B00'
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color)

                square = row * 8 + col
                piece = self.get_piece_at(square)
                if piece:
                    self.canvas.create_image(
                        x1, y1, anchor=tk.NW, image=self.images[piece.symbol()]
                    )

        for move_square in self.possible_moves:
            row, col = divmod(move_square, 8)
            display_row, display_col = self.board_to_display(row, col)
            x1, y1 = display_col * SQUARE_SIZE, display_row * SQUARE_SIZE
            x2, y2 = x1 + SQUARE_SIZE, y1 + SQUARE_SIZE
            self.canvas.create_rectangle(
                x1, y1, x2, y2, outline='yellow', width=2
            )

    def board_to_display(self, row, col):
        if self.get_turn() == chess.WHITE:
            return 7 - row, col
        else:
            return row, col

    def is_square_attacked(self, square, color):
        opponent_color = not color
        return self.board.is_attacked_by(opponent_color, square)

    def display_to_board(self, display_row, display_col):
        if self.get_turn() == chess.WHITE:
            return 7 - display_row, display_col
        else:
            return display_row, display_col

    def get_piece_at(self, square):
        return self.board.piece_at(square)

    def make_move(self, move):
        if move in self.board.legal_moves:
            self.board.push(move)

    def get_legal_moves(self):
        return list(self.board.legal_moves)

    def get_turn(self):
        return self.board.turn

    def is_game_over(self):
        return self.board.is_game_over()

    def is_stalemate(self):
        return self.board.is_stalemate()

    def reset_board(self):
        return self.board.reset()

    def push_move(self, move):
        self.board.push(move)

    def pop_move(self):
        self.board.pop()

    def is_pawn_promotion(self, move):
        return self.board.piece_at(move.from_square).piece_type == chess.PAWN and chess.square_rank(move.to_square) in [0, 7]

    def get_material_score(self, color):
        piece_values = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3,
                        chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 0}
        score = 0
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece and piece.color == color:
                score += piece_values[piece.piece_type]
        return score

    def get_attackers(self, square, attacking_color):
        return [sq for sq in chess.SQUARES if self.board.is_attacked_by(attacking_color, square)]

    def evaluate_position(self, color):
        print('evaluate')
        material_score = self.get_material_score(color)
        opponent_score = self.get_material_score(not color)

        evaluation = material_score - opponent_score

        return evaluation

    def __str__(self):
        return str(self.board)
