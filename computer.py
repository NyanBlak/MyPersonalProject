import random
import move as m
import engine as engine
from sys import maxsize

DEPTH = 2
class Computer:

    def __init__(self, state: engine.GameState, player_num):
        self.state = state
        self.player_num = player_num

    def get_move(self) -> m.Move:
        best_value = maxsize * -self.player_num
        best_choice = None
        for move in self.state.all_legal_moves():
            node = Node(DEPTH, self.player_num, self.state.board, move)
            for child in node.children:
                val = minimax(child, DEPTH, -self.player_num)
                if (abs(self.player_num * maxsize - val)) <= (abs(self.player_num * maxsize - best_value)):
                    best_value = val
                    best_choice = node.move
        return best_choice

    def __str__(self) -> str:
        return self.get_move().notation

class Node:

    def __init__(self, depth, player_num, board, move, value=0):
        self.depth = depth
        self.player_num = player_num
        self.board = board
        self.move = move
        self.value = value
        self.state = engine.GameState()
        self.children = []
        self.create_children()

    def create_children(self):
        if self.depth >= 0:
            if DEPTH % 2 == 0:
                flip_color = False if self.depth % 2 == 0 else True
            else:
                flip_color = False if self.depth % 2 == 1 else True
            legal_moves = self.state.all_legal_moves(flip_color=flip_color)
            for move in legal_moves:
                sim_board = self.state.create_simulated_board(move)
                material = self.state.get_material(sim_board)
                self.children.append(Node(self.depth - 1, -self.player_num, sim_board, move, self.real_val(sim_board)))

    def real_val(self, board):
        material = self.state.get_material(board)

        val = material

        return val

def minimax(node, depth, player_num):
    if (depth == 0) or (abs(node.value == maxsize)):
        return node.value
    
    best_value = maxsize * -player_num

    for child in node.children:
        val = minimax(child, depth-1, -player_num)
        if abs(maxsize * player_num - val) < abs(maxsize * player_num - best_value):
            best_value = val
    if best_value != 7:
        print(best_value)
    return best_value

