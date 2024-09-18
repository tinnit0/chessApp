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
    def __init__(self, root=None, light_mode=False):
        self.root = root
        self.light_mode = light_mode
        self.board_size = BOARD_SIZE
        self.square_size = SQUARE_SIZE

        if root:
            self.canvas = tk.Canvas(
                root, width=self.board_size, height=self.board_size)
            self.canvas.pack()

        self.images = self.load_images()
        self.game = ChessGame(self.canvas if not light_mode else None, self.images if not light_mode else {
        }, self.root if not light_mode else None)

        if not light_mode:
            self.setup_ui()
        else:
            self.run_light_mode()

    def setup_ui(self):
        self.root.title("Chess Game")
        settings_button = tk.Button(
            self.root, text="Settings", command=self.open_settings)
        settings_button.pack()
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

    def open_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        tk.Label(settings_window, text="Resolution:").pack()
        resolution_var = tk.StringVar(value=str(self.board_size))
        resolutions = [540, 1080]
        for res in resolutions:
            tk.Radiobutton(
                settings_window,
                text=f"{res}x{res}",
                variable=resolution_var,
                value=str(res),
                command=lambda: self.change_resolution(
                    int(resolution_var.get()))
            ).pack()

    def change_resolution(self, new_size):
        self.board_size = new_size
        self.square_size = new_size // 8
        self.canvas.config(width=self.board_size, height=self.board_size)
        self.images = self.load_images()
        self.game.update_images(self.images)
        self.game.redraw_board()

    def run_light_mode(self):
        ai_color = chess.WHITE
        ai = AI(ai_color, self.game.board)
        self.play_game(ai_color, ai)

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
    mode = input("'1' for light mode: ")
    if mode.lower() == '1':
        ChessApp(light_mode=True)
    else:
        root = tk.Tk()
        ChessApp(root)
        root.mainloop()
