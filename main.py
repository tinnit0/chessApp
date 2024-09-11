import tkinter as tk
from PIL import Image, ImageTk
from game import ChessGame
from board import ChessBoard

BOARD_SIZE = 1000
SQUARE_SIZE = BOARD_SIZE // 8


def load_image(filename):
    return ImageTk.PhotoImage(Image.open(filename))


class ChessApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess Game")

        self.images = self.load_images()
        self.canvas = tk.Canvas(root, width=BOARD_SIZE, height=BOARD_SIZE)
        self.canvas.pack()

        self.game = ChessGame(self.canvas, self.images, self.root)

        self.canvas.bind("<Button-1>", self.game.handle_click)

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


if __name__ == "__main__":
    root = tk.Tk()
    app = ChessApp(root)
    root.mainloop()
