import random
import move as m
import engine as engine
from sys import maxsize

DEPTH = 2

materials = {"K":0, "Q": 9, "R": 5, "B": 3, "N": 3, "P":1}
CHECKMATE = maxsize
STALEMATE = 0

class Computer:

    def __init__(self, state: engine.GameState):
        self.state = state
        self.turn_multi = 1 if self.state.white_to_move else -1

    def get_material(board:list):
        material = 0
        for r in board:
            for square in r:
                if "w" in square:
                    material += materials[square[1]]
                elif "b" in square:
                    material -= materials[square[1]]
        return material

    def get_move(self) -> m.Move:
        best_choice = None
        opp_minimax_score = CHECKMATE # worst move for opp
        legal_moves = self.state.all_legal_moves()
        random.shuffle(legal_moves)
        for move in legal_moves:
            sim_board_one = self.state.create_simulated_board(move)
            opp_moves = self.state.all_legal_moves(sim_board_one, True)
            opp_max_score = -CHECKMATE # best move for opp
            for opp_move in opp_moves:
                sim_board = self.state.create_simulated_board(opp_move, sim_board_one)
                if self.state.is_checkmate(sim_board, True):
                    score = -self.turn_multi * CHECKMATE
                else:
                    score = Computer.get_material(sim_board) * -self.turn_multi
                if score > opp_max_score:
                    opp_max_score = score
            if opp_max_score < opp_minimax_score:
                opp_minimax_score = opp_max_score
                best_choice = move
        return best_choice

    def get_random_move(self) -> m.Move:
        return random.choice(self.state.all_legal_moves())

    def __str__(self) -> str:
        return self.get_move().notation

