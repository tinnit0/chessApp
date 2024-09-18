import chess
import tkinter as tk
import tkinter.simpledialog as simpledialog
from PIL import Image, ImageTk

class ChessBoard:
    def __init__(self, canvas, images, starting_color, root=None):
        self.board = chess.Board()
        self.selected_piece = None
        self.possible_moves = set()
        self.canvas = canvas
        self.images = images
        self.starting_color = starting_color
        self.flip_board = (self.starting_color == chess.BLACK)
        self.root = root
        print(self.board)

    def draw_board(self):
        self.canvas.delete('all')
        for row in range(8):
            for col in range(8):
                display_row, display_col = self.board_to_display(row, col)
                x1, y1 = display_col * SQUARE_SIZE, display_row * SQUARE_SIZE
                x2, y2 = x1 + SQUARE_SIZE, y1 + SQUARE_SIZE
                color = '#eee' if (display_row + display_col) % 2 == 0 else '#964B00'
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
        if self.starting_color == chess.WHITE:
            return 7 - row, col
        else:
            return row, 7 - col

    def display_to_board(self, display_row, display_col):
        if self.starting_color == chess.WHITE:
            return 7 - display_row, display_col
        else:
            return display_row, 7 - display_col

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

    def is_check(self):
        return self.board.is_check()

    def change_resolution(self):
        new_resolution = simpledialog.askinteger("Resolution", "Enter new resolution (e.g., 500):", parent=self.root)
        if new_resolution:
            global BOARD_SIZE
            BOARD_SIZE = new_resolution
            global SQUARE_SIZE
            SQUARE_SIZE = BOARD_SIZE // 8

            # Update canvas dimensions
            self.canvas.config(width=BOARD_SIZE, height=BOARD_SIZE)

            # Load new images
            self.images = self.load_images()
            self.draw_board()

    def load_images(self):
        size = (SQUARE_SIZE, SQUARE_SIZE)
        return {
            'r': self.load_image('images/rB.png', size),
            'n': self.load_image('images/nB.png', size),
            'b': self.load_image('images/bB.png', size),
            'q': self.load_image('images/qB.png', size),
            'k': self.load_image('images/kB.png', size),
            'p': self.load_image('images/pB.png', size),
            'R': self.load_image('images/rW.png', size),
            'N': self.load_image('images/nW.png', size),
            'B': self.load_image('images/bW.png', size),
            'Q': self.load_image('images/qW.png', size),
            'K': self.load_image('images/kW.png', size),
            'P': self.load_image('images/pW.png', size),
        }

    def load_image(self, filename, size):
        return ImageTk.PhotoImage(Image.open(filename).resize(size))

    def reset_board(self):
        self.board.reset()

    def find_king(self, color):
        for square in chess.SQUARES:
            piece = self.get_piece_at(square)
            if piece is not None and piece.piece_type == chess.KING and piece.color == color:
                return square
        return None

    def push_move(self, move):
        self.board.push(move)

    def is_checkmate(self):
        return self.board.is_checkmate()

    def pop_move(self):
        self.board.pop()

    def is_pawn_promotion(self, move):
        return self.board.piece_at(move.from_square).piece_type == chess.PAWN and chess.square_rank(move.to_square) in [0, 7]

    def get_attackers(self, square, attacking_color):
        return [sq for sq in chess.SQUARES if self.board.is_attacked_by(attacking_color, square)]

    def get_last_move_origin(self, piece):
        if len(self.board.move_stack) > 0:
            last_move = self.board.peek()
            if self.board.piece_at(last_move.to_square) == piece:
                return last_move.from_square
        return None

    def __str__(self):
        return str(self.board)
