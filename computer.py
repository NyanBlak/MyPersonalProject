import random
import move as m

class Computer:

    def __init__(self, legal_moves:list):
        self.legal_moves = legal_moves

    def get_move(self) -> m.Move:
        return random.choice(self.legal_moves)

    def __str__(self) -> str:
        return self.get_move().notation

