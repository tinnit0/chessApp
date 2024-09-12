import tkinter as tk
from PIL import Image, ImageTk
from game import ChessGame
from board import ChessBoard
# from ai import AI

BOARD_SIZE = 500
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
# TODO Must
#  ai die per turn check wat ie in een vorige  game succesfol heeft gedaan example ai had gewonen met start move a4 dan gaat ie dat weer proberen (er moet dan wel translation komen voor andere zijde example white a2->a4 black a7->a5)
#  Should:
#  light modus die maakt het zodat het ai vs random moves is met gebruik van print chess board ipv fotos die he tmooi maken
#  Points for ai example voor het midden controllen winnen pieces pakken of zo min mogelijk pieces in gevaar brengen  
#  deze ai wordt erg light weight en slecht vergeleken example stockfish en gaat niet in depth kunnen zien