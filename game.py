import chess.pgn
import chess
from board import ChessBoard
import random
import tkinter.simpledialog as simpledialog
import tkinter as tk
import tkinter.messagebox as messagebox

BOARD_SIZE = 500
SQUARE_SIZE = BOARD_SIZE // 8


class ChessGame:
    def __init__(self, canvas, images, root):
        self.player_color = random.choice([chess.WHITE, chess.BLACK])
        self.board = ChessBoard(canvas, images, self.player_color)
        self.root = root
        self.pgn_game = chess.pgn.Game()
        self.current_node = self.pgn_game.add_variation(chess.Move.null())
        self.pgn_moves = []
        self.ai_vs_ai = False
        self.images = images

        self.ai_color = chess.BLACK if self.player_color == chess.WHITE else chess.WHITE
        self.ai = AI(self.ai_color, self.board)

        self.decide_first_turn()

        if canvas:
            self.status_label = tk.Label(
                root, text="1 = Player vs AI, 2 = AI vs AI", font=("Arial", 12), anchor="w")
            self.status_label.pack(side="bottom", fill="x")

            self.board.draw_board()
            self.bind_keys()
            canvas.bind("<Button-1>", self.handle_click)

    def print_board(self):
        print(self.board.board)

    def update_images(self, new_images):
        """Update images and redraw the board."""
        self.images = new_images
        self.board.images = new_images  # Directly update ChessBoard's images
        self.board.draw_board()
        self.root.update()

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

    def decide_first_turn(self):
        if self.player_color == chess.BLACK:
            move = self.ai.make_move()
            if move:
                self.board.push_move(move)
                self.log_move(move, "AI")
            self.board.draw_board()
            self.root.update()

    def make_random_opponent_move(self):
        if self.check_game_over():
            return None

        legal_moves = self.board.get_legal_moves()
        if legal_moves:
            random_move = random.choice(legal_moves)
            if self.board.is_pawn_promotion(random_move):
                random_move = chess.Move(
                    random_move.from_square, random_move.to_square, promotion=chess.QUEEN)
            self.board.push_move(random_move)
            self.log_move(random_move, "Opponent")
            return random_move
        return None

    def log_move(self, move, player):
        move_str = move.uci()
        self.current_node = self.current_node.add_variation(move)
        self.pgn_moves.append(move_str)

    def check_game_over(self):
        if self.board.is_game_over():
            print('Game ended')
            self.save_game()

            if self.ai_vs_ai:
                print("AI vs AI game over. Restarting in 4 seconds...")
                self.root.after(4000, self.reset_game)
            else:
                self.show_player_vs_ai_end_dialog()

            self.board.reset_board()
            self.ai_vs_ai = False
            return True
        return False

    def show_player_vs_ai_end_dialog(self):
        if self.board.is_checkmate():
            if self.board.get_turn() == self.player_color:
                message = "Game Over: You lost. Do you want to retry?"
            else:
                message = "You won! Do you want to retry?"
        elif self.board.is_stalemate():
            message = "The game is a draw. Do you want to retry?"
        else:
            return

        result = messagebox.askquestion("Game Over", message, icon='warning')

        if result == 'yes':
            self.reset_game()
        else:
            self.root.quit()

    def reset_game(self):
        self.board.reset_board()
        self.pgn_game = chess.pgn.Game()
        self.current_node = self.pgn_game.add_variation(chess.Move.null())
        self.decide_first_turn()
        self.board.draw_board()
        self.root.update()

    def run_ai_vs_ai(self):
        if self.check_game_over():
            print("Game over detected")
            return

        current_turn = self.board.get_turn()
        print(f"Current turn: {
              'White' if current_turn == chess.WHITE else 'Black'}")

        if current_turn == self.ai_color:
            move = self.ai.make_move()
            if move and move in self.board.get_legal_moves():
                self.board.push_move(move)
                self.log_move(move, "AI")
                print(f"AI move: {move}")
            else:
                print(f"Invalid move by AI: {move}")
        else:
            move = self.make_random_opponent_move()
            print(f"Opponent random AI move: {move}")

        self.board.draw_board()
        self.root.update()

        self.root.after(400, self.run_ai_vs_ai)

    def handle_click(self, event):
        if self.ai_vs_ai:
            return

        if self.check_game_over():
            print("Game over detected, no further moves allowed.")
            return

        current_turn = self.board.get_turn()
        if current_turn != self.player_color:
            print("Not player's turn")
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
            if piece and piece.color == self.board.get_turn():
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

                    if not self.check_game_over() and self.board.get_turn() == self.ai_color:
                        self.root.after(200, self.ai_turn)

                self.board.selected_piece = None
                self.board.possible_moves = set()
            else:
                self.board.selected_piece = None
                self.board.possible_moves = set()

        self.board.draw_board()

    def ai_turn(self):
        if self.check_game_over():
            return

        if self.board.get_turn() != self.ai_color:
            return

        ai_move = self.ai.make_move()
        if ai_move:
            self.board.push_move(ai_move)
            self.log_move(ai_move, "AI")
            self.check_game_over()
        
        self.board.draw_board()
        self.root.update()

class AI:
    def __init__(self, color, board, max_depth=2):
        self.board = board
        self.color = color
        self.max_depth = max_depth
        self.successful_moves = []
        self.past_moves = []
        self.load_successful_moves()

    def evaluate_board(self):
        piece_values = {
            chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9,
            chess.KING: 0  # King is invaluable, so no direct score
        }

        center_squares = [chess.E4, chess.D4, chess.E5, chess.D5]
        score = 0

        # Check for checkmate or stalemate
        if self.board.is_checkmate():
            if self.board.get_turn() == self.color:
                print("Checkmate: AI lost")
                return -float('inf')  # AI is losing
            else:
                print("Checkmate: AI is winning")
                return float('inf')   # AI is winning

        if self.board.is_stalemate():
            print("Stalemate: Negative points for stalemate")
            return -50  # Penalize a stalemate with -50 points

        # Evaluate piece values and control of center
        for square in chess.SQUARES:
            piece = self.board.get_piece_at(square)
            if piece:
                value = piece_values[piece.piece_type]
                if piece.color == self.color:
                    score += value
                    print(f"AI piece {piece} at {square} adds {
                        value}. Current score: {score}")
                else:
                    score -= value
                    print(f"Opponent piece {piece} at {square} subtracts {
                        value}. Current score: {score}")

                # Bonus for controlling the center
                if square in center_squares:
                    if piece.color == self.color:
                        score += 0.5  # Small bonus for controlling center
                        print(f"AI piece {piece} controls center at {
                            square}. Bonus: 0.5. Current score: {score}")
                    else:
                        score -= 0.5
                        print(f"Opponent piece {piece} controls center at {
                            square}. Penalty: -0.5. Current score: {score}")

        # Evaluate sacrifices
        # Check if sacrificing a piece results in a better score
        if self.board.is_check():
            king_square = self.board.find_king(not self.color)
            attacking_pieces = self.board.get_attackers(king_square, self.color)
            score += len(attacking_pieces) * 0.5
            print(f"Attacking king with {len(attacking_pieces)} pieces. Bonus: {
                len(attacking_pieces) * 0.5}. Current score: {score}")

        return score

    def minimax(self, depth, alpha, beta, maximizing_player):
        if depth == 0 or self.board.is_game_over():
            print(f"Evaluating position at depth {depth} with score: {self.evaluate_board()}")
            return self.evaluate_board(), None

        legal_moves = list(self.board.get_legal_moves())
        best_move = None

        if maximizing_player:
            print("Maximizing player")
            max_eval = -float('inf')
            for move in legal_moves:
                self.board.push_move(move)

                # Toggle to minimizing_player
                evaluation, _ = self.minimax(depth - 1, alpha, beta, False)
                self.board.pop_move()

                if evaluation > max_eval:
                    max_eval = evaluation
                    best_move = move
                    # print(f"Maximizing: New best move found: {
                    #     move} with evaluation {max_eval}")

                alpha = max(alpha, evaluation)
                if beta <= alpha:
                    break

            return max_eval, best_move
        else:
            # print("Minimizing player")
            min_eval = float('inf')
            for move in legal_moves:
                self.board.push_move(move)
                evaluation, _ = self.minimax(depth - 1, alpha, beta, True)
                self.board.pop_move()

                if evaluation < min_eval:
                    min_eval = evaluation
                    best_move = move
                    # print(f"Minimizing: New best move found: {
                    #     move} with evaluation {min_eval}")

                beta = min(beta, evaluation)
                if beta <= alpha:
                    break

            return min_eval, best_move
        
    def make_best_move(self):
        _, best_move = self.minimax(
            self.max_depth, -float('inf'), float('inf'), True)
        if best_move:
            self.past_moves.append(best_move)
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
                # print(f"Making successful move: {translated_move}")
                return translated_move

        # print("No successful move found, evaluating best move.")
        return self.make_best_move()
