class GameState:

    def __init__(self):
        self.board = [[" " for i in range(8)] for i in range(8)]
        self.white_to_move = True
        self.move_list = []

    def create_start_pos(self):
        self.board[0] = ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR']
        self.board[1] = ['bP' for i in range(8)]
        self.board[6] = ['wP' for i in range(8)]
        self.board[7] = ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']

    def move_piece(self, move:list[tuple[int, int], tuple[int, int]]):
        prev_square = move[0]
        new_square = move[1]
        piece = self.board[prev_square[0]][prev_square[1]]

        self.board[prev_square[0]][prev_square[1]] = " "
        self.board[new_square[0]][new_square[1]] = piece
        self.white_to_move = not self.white_to_move
    


    def check_player_move(self, piece:str):
        if piece[0] == 'w' and self.white_to_move == True:
            return True
        elif piece[0] == 'w' and self.white_to_move == False:
            return False
        elif piece[0] == 'b' and self.white_to_move == False:
            return True
        else:
            return False
