import chess
import random
from board import ChessBoard

class AI:
    def evaluate_move(self, move):
        points = 0

        # Reward controlling the center (squares e4, d4, e5, d5)
        center_squares = [chess.E4, chess.D4, chess.E5, chess.D5]
        if move.to_square in center_squares:
            points += 5

        # Reward capturing an opponent's piece
        if self.game.board.is_capture(move):
            points += 10

        # Penalize moving into danger (if the move leaves a piece exposed)
        if self.is_in_danger(move.to_square):
            points -= 5

        return points

    def is_in_danger(self, square):
        # Check if moving to this square leaves the piece exposed
        for attacker in self.game.board.attackers(not self.color, square):
            return True
        return False

    def make_best_move(self):
        legal_moves = self.game.get_legal_moves()
        best_move = None
        best_score = -float('inf')

        for move in legal_moves:
            score = self.evaluate_move(move)
            if score > best_score:
                best_score = score
                best_move = move

        return best_move or random.choice(legal_moves)

    print('1')
    def __init__(self, game, color):
        self.game = game
        self.color = color
        self.successful_moves = []

        self.load_successful_moves()

    def load_successful_moves(self):
        print('2')
        self.successful_moves = [
            (chess.A2, chess.A4),
            (chess.E7, chess.E5)
        ]

    def translate_move(self, move):
        print('3')
        if self.color == chess.BLACK:
            return chess.Move(chess.square_mirror(move.from_square), chess.square_mirror(move.to_square))
        return move

    def make_move(self):
        print('4')
        legal_moves = self.game.get_legal_moves()
        
        for move in self.successful_moves:
            translated_move = self.translate_move(chess.Move(move[0], move[1]))
            if translated_move in legal_moves:
                return translated_move

        return random.choice(legal_moves)
