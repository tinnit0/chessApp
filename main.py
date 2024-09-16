import tkinter as tk
from PIL import Image, ImageTk
import chess
from game import ChessGame

BOARD_SIZE = 500
SQUARE_SIZE = BOARD_SIZE // 8

def load_image(filename):
    return ImageTk.PhotoImage(Image.open(filename))

class ChessApp:
    def __init__(self, root=None, light_mode=False):
        self.light_mode = light_mode

        if not self.light_mode:
            self.root = root
            self.root.title("Chess Game")

            self.images = self.load_images()
            self.canvas = tk.Canvas(root, width=BOARD_SIZE, height=BOARD_SIZE)
            self.canvas.pack()

            self.game = ChessGame(self.canvas, self.images, self.root)
            self.canvas.bind("<Button-1>", self.game.handle_click)
        else:
            self.game = ChessGame(None, {}, None)
            self.run_light_mode()

    def run_light_mode(self):
        while not self.game.board.is_game_over():
            self.game.print_board()
            self.game.make_random_opponent_move()
            self.game.print_board()

    def load_images(self):
        return {
            'r': load_image('images/rB.png'),
            'n': load_image('images/nB.png'),
            'b': load_image('images/bB.png'),
            'q': load_image('images/qB.png'),
            'k': load_image('images/kB.png'),
            'p': load_image('images/pB.png'),
            'R': load_image('images/rW.png'),
            'N': load_image('images/nW.png'),
            'B': load_image('images/bW.png'),
            'Q': load_image('images/qW.png'),
            'K': load_image('images/kW.png'),
            'P': load_image('images/pW.png'),
        }

    def prompt_for_move(self, player):
        print(f"{player}'s turn:")
        move = input("Enter your move (e.g., e2e4): ")
        try:
            return chess.Move.from_uci(move)
        except ValueError:
            print("Invalid move, please try again.")
            return None

    def print_board(self):
        print(self.game.board.board)
        print("\n")

if __name__ == "__main__":
    mode = input("'1' for light mode: ")
    if mode.lower() == '1':
        app = ChessApp(light_mode=True)
    else:
        root = tk.Tk()
        app = ChessApp(root)
        root.mainloop()