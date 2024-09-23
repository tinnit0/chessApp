import tkinter as tk
from PIL import Image, ImageTk
import chess
from game import ChessGame, AI
import time

BOARD_SIZE = 540
SQUARE_SIZE = BOARD_SIZE // 8


def load_image(filename, size):
    return ImageTk.PhotoImage(Image.open(filename).resize(size))


class ChessApp:
    def __init__(self, root=None):
        self.root = root
        self.board_size = BOARD_SIZE
        self.square_size = SQUARE_SIZE

        if root:
            self.canvas = tk.Canvas(
                root, width=self.board_size, height=self.board_size)
            self.canvas.pack()

        self.images = self.load_images()
        self.game = ChessGame(self.canvas, self.images, self.root)
        self.setup_ui()


    def setup_ui(self):
        self.root.title("Chess Game")
        self.canvas.bind("<Button-1>", self.game.handle_click)

    def load_images(self):
        size = (self.square_size, self.square_size)
        return {
            'r': load_image('images/rB.png', size),
            'n': load_image('images/nB.png', size),
            'b': load_image('images/bB.png', size),
            'q': load_image('images/qB.png', size),
            'k': load_image('images/kB.png', size),
            'p': load_image('images/pB.png', size),
            'R': load_image('images/rW.png', size),
            'N': load_image('images/nW.png', size),
            'B': load_image('images/bW.png', size),
            'Q': load_image('images/qW.png', size),
            'K': load_image('images/kW.png', size),
            'P': load_image('images/pW.png', size),
        }

    def change_resolution(self, new_size):
        self.board_size = new_size
        self.square_size = new_size // 8
        self.canvas.config(width=self.board_size, height=self.board_size)
        self.images = self.load_images()
        self.game.update_images(self.images)
        self.game.redraw_board()

    def restart_game(self):
        self.game = ChessGame(None, {}, None)
        ai_color = chess.WHITE
        ai = AI(ai_color, self.game.board)
        self.play_game(ai_color, ai)

    def play_game(self, ai_color, ai):
        while not self.game.board.is_game_over():
            self.print_board()
            if self.game.board.get_turn() == ai_color:
                best_move = ai.make_move()
                if best_move:
                    print(f"AI move: {best_move}")
                    self.game.board.push_move(best_move)
                    self.game.log_move(best_move, "AI")
            else:
                self.game.make_random_opponent_move()
            self.print_board()

        print("Game over!")
        time.sleep(1)
        self.restart_game()

    def print_board(self):
        print(self.game.board.board)
        print("\n")


if __name__ == "__main__":
        root = tk.Tk()
        ChessApp(root)
        root.mainloop()
