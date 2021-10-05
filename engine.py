import pygame

DIM = 8
GREEN = 0, 255, 0
RED = 255, 0, 0

w_pawn_moves_that_allow_ep = ["a4", "b4", "c4", "d4", "e4", "f4", "g4", "h4"]
b_pawn_moves_that_allow_ep = ["a5", "b5", "c5", "d5", "e5", "f5", "g5", "h5"]

class GameState:

    def __init__(self):
        self.board = [[" " for i in range(8)] for i in range(8)]
        self.white_to_move = True
        self.move_list = []
        self.funcs = {
            "P": self.get_pawn_moves,
            "R": self.get_rook_moves,
            "B": self.get_bishop_moves,
            "K": self.get_king_moves,
            "Q": self.get_queen_moves,
            "N": self.get_knight_moves
        }

    def reset_game(self):
        self.__init__()
        self.create_start_pos()

    def create_start_pos(self):
        self.board[0] = ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR']
        self.board[1] = ['bP' for i in range(8)]
        self.board[6] = ['wP' for i in range(8)]
        self.board[7] = ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']

    def check_player_move(self, piece:str):
        if piece[0] == 'w' and self.white_to_move == True:
            return True
        elif piece[0] == 'w' and self.white_to_move == False:
            return False
        elif piece[0] == 'b' and self.white_to_move == False:
            return True
        else:
            return False

    def check_winner(self):
        white_wins = True
        black_wins = True
        for r in range(DIM):
            for c in range(DIM):
                if self.board[r][c] == "wK":
                    black_wins = False
                elif self.board[r][c] == "bK":
                    white_wins = False
        if white_wins:
            return "White Wins! "
        elif black_wins:
            return "Black Wins! "
        else:
            return None

    def all_legal_moves(self):
        legal_moves = []
        king_moves = []
        all_moves = self.all_possible_moves()
        legal_moves = all_moves
        return legal_moves

    def all_possible_moves(self):
        moves = []
        for r in range(DIM):
            for c in range(DIM):
                square = self.board[r][c]
                team = square[0]
                if (team == 'w' and self.white_to_move) or (team == 'b' and not self.white_to_move):
                    piece = square[1]
                    
                    func = self.funcs[piece]
                    func(r, c, moves)
        return moves

    def get_pawn_moves(self, row, col, moves):
        if self.white_to_move:
            opposing_team = 'b'
            direction = -1
            if row == 6:
                right_two_squares = True
            else:
                right_two_squares = False
        else:
            opposing_team = 'w'
            direction = 1
            if row == 1:
                right_two_squares = True
            else:
                right_two_squares = False
        start_square = row, col
        end_square = row + direction, col
        diag_squares = [
            (end_square[0], end_square[1]+1),
            (end_square[0], end_square[1]-1)
        ]

        if self.board[end_square[0]][end_square[1]] == ' ':
            moves.append([start_square, end_square])

        if right_two_squares:
            two_squares_forward = (end_square[0]+direction, end_square[1])
            moves.append([start_square, two_squares_forward])

        for square in diag_squares:
            if DIM <= square[1] or 0 > square[1]:
                break
            if opposing_team in self.board[square[0]][square[1]]:
                moves.append([start_square, square])
        
        enpassant = self.check_enpassant(start_square)
        if enpassant[0]:
            ep_end_square = (end_square[0], end_square[1] + enpassant[1])
            moves.append([start_square, ep_end_square])

    def get_rook_moves(self, row, col, moves):
        directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        start_square = row, col

        if self.white_to_move:
            team = 'w'
            opposing_team = 'b'
        else:
            team = 'b'
            opposing_team = 'w'

        for direction in directions:
            r, c = direction
            for i in range(DIM):
                i += 1
                if row + (r * i) > 7 or col + (c * i) > 7:
                    break
                end_square = end_row, end_col = row + (r * i), col + (c * i)
                captured_piece = self.board[end_row][end_col]
                if captured_piece == " ":
                    moves.append([start_square, end_square])
                elif opposing_team in captured_piece:
                    moves.append([start_square, end_square])
                    break
                else:
                    break

    def get_bishop_moves(self, row, col, moves):
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        start_square = row, col

        if self.white_to_move:
            team = 'w'
            opposing_team = 'b'
        else:
            team = 'b'
            opposing_team = 'w'

        for direction in directions:
            r, c = direction
            for i in range(DIM):
                i += 1
                if row + (r * i) > 7 or col + (c * i) > 7:
                    break
                end_square = end_row, end_col = row + (r * i), col + (c * i)
                captured_piece = self.board[end_row][end_col]
                if captured_piece == " ":
                    moves.append([start_square, end_square])
                elif opposing_team in captured_piece:
                    moves.append([start_square, end_square])
                    break
                else:
                    break

    def get_queen_moves(self, row, col, moves):
        directions = [
            (1, 1), (1, -1), (-1, 1), (-1, -1),
            (1, 0), (0, 1), (-1, 0), (0, -1)
        ]
        start_square = row, col

        if self.white_to_move:
            team = 'w'
            opposing_team = 'b'
        else:
            team = 'b'
            opposing_team = 'w'

        for direction in directions:
            r, c = direction
            for i in range(DIM):
                i += 1
                if row + (r * i) > 7 or col + (c * i) > 7:
                    break
                end_square = end_row, end_col = row + (r * i), col + (c * i)
                captured_piece = self.board[end_row][end_col]
                if captured_piece == " ":
                    moves.append([start_square, end_square])
                elif opposing_team in captured_piece:
                    moves.append([start_square, end_square])
                    break
                else:
                    break

    def get_king_moves(self, row, col, moves):
        directions = [
            (1, 1), (1, -1), (-1, 1), (-1, -1),
            (1, 0), (0, 1), (-1, 0), (0, -1)
        ]
        start_square = row, col

        opposing_team = "b" if self.white_to_move else "w"

        for direction in directions:
            end_square = end_row, end_col = row + direction[0], col + direction[1]
            if end_row < 0 or end_row > 7 or end_col < 0 or end_col > 7:
                pass
            elif self.board[end_row][end_col] == " " or opposing_team in self.board[end_row][end_col]:
                moves.append([start_square, end_square])

        legal_castling = self.check_castling_rights(start_square)
        if legal_castling != []:
            for move in legal_castling:
                moves.append(move)


    def get_knight_moves(self, row, col, moves):
        directions = [
            (2, 1), (1, 2), 
            (2, -1), (1, -2),
            (-2, 1), (-1, 2),
            (-2, -1), (-1, -2)
        ]
        start_square = row, col

        if self.white_to_move:
            opposing_team = 'b'
        else:
            opposing_team = 'w'

        for direction in directions:
            end_square = end_row, end_col = row + direction[0], col + direction[1]
            if end_row < 0 or end_row > 7 or end_col < 0 or end_col > 7:
                pass
            else:
                if self.board[end_row][end_col] == " ":
                    moves.append([start_square, end_square])
                elif opposing_team in self.board[end_row][end_col]:
                    moves.append([start_square, end_square])

    def check_promotion(self, pos:tuple[int, int]):
        row, col = pos
        team = self.board[row][col][0]
        for w_square in self.board[0]: # for square in 8th rank
            for b_square in self.board[7]: # for square in 1st rank
                if "P" in w_square or "P" in b_square:
                    return True
                    self.board[row][col] = team + promote_to
    
    def check_enpassant(self, pos:tuple[int, int]):
        if len(self.move_list) == 0:
            return (False,)
        last_move = self.move_list[-1]
        full_piece = self.board[pos[0]][pos[1]]
        row, col = pos
        team = full_piece[0]
        piece = full_piece[1]
        if team == 'w':
            moves_ep = b_pawn_moves_that_allow_ep
            previously_moved_numvar = -1
            en_passant_row = 3
        else:
            moves_ep = w_pawn_moves_that_allow_ep
            previously_moved_numvar = 1
            en_passant_row = 4
        if last_move in moves_ep:
            previously_moved = last_move[0] + str(int(last_move[1])+previously_moved_numvar) # check if the pawn has moved before
            if not previously_moved in self.move_list:
                if row == en_passant_row:
                    other_pawn_col = [k for k, v in Move.col_to_file.items() if v == last_move[0]][0]
                    if other_pawn_col - col == -1: # if the pawn is to the left
                        return (True, -1)
                    elif other_pawn_col - col == 1: # to the right
                        return (True, 1)
        return (False,)

    def check_castling_rights(self, king_pos:tuple[int, int]):
        W_STARTING_KING_SQUARE = (7, 4)
        B_STARTING_KING_SQUARE = (0, 4)

        legal_castling_moves = []
        row, col = king_pos

        if self.white_to_move:
            team = 'w'
            starting_king_square = W_STARTING_KING_SQUARE
            starting_row = 7
        else:
            team = 'b'
            starting_king_square = B_STARTING_KING_SQUARE
            starting_row = 0
        rook = team + 'R'

        if king_pos != starting_king_square:
            return []

        if self.board[starting_row][0] == rook: # check if queenside castling is legal
            if self.board[starting_row][3] == " " and self.board[starting_row][2] == " ":
                legal_castling_moves.append([king_pos, (row, col-2)])
        if self.board[starting_row][7] == rook: # check if kingside castling is legal
            if self.board[starting_row][5] == " " and self.board[starting_row][6] == " ":
                legal_castling_moves.append([king_pos, (row, col+2)])

        return legal_castling_moves

class Move:

    # Dictionaries that translate the grid notation
    # (starting in the top right corner with 0, 0 and going
    # right and down in +1 increments) to rank-file notation

    # ranks are rows which are from whites perspective starting
    # from bottom to top numbered 1, 2, 3... up to 8

    # files are the columns also from whites perspective starting
    # from left to right labeled a, b, c, d... up till h

    # Squares in rank-file notation are labeled by the file
    # letter then the rank number (ex: e4, d8, a3, h2)
    row_to_rank = {7: "1", 6: "2", 5: "3", 4: "4", 3: "5", 2: "6", 1: "7", 0: "8"}
    col_to_file = {0: "a", 1: "b", 2: "c", 3: "d", 4: "e", 5: "f", 6: "g", 7: "h"}

    def __init__(self, start_square:tuple[int, int], end_square:tuple[int,int], board):
        self.board = board
        self.start_square = start_square
        self.start_row = start_square[0]
        self.start_col = start_square[1]
        self.end_square = end_square
        self.end_row = end_square[0]
        self.end_col = end_square[1]

        self.piece_moved = self.board[self.start_row][self.start_col]
        self.piece_captured = self.board[self.end_row][self.end_col]

        self.castling = self.is_move_castling()
        self.notation = self.get_algebraic_notation()


    def get_algebraic_notation(self):
        # gets the algebraic notation of the move
        # ex: pawn to e4 is e4, kingside castles is O-O,
        # knight to c4 is Nc4, queen to h7 is Qh7, etc.
        originating_file = Move.col_to_file[self.start_col]
        file = Move.col_to_file[self.end_col]
        rank = Move.row_to_rank[self.end_row]

        if self.piece_moved[1] == 'K' and self.castling:
            if self.end_col == 6:
                return "O-O"
            else:
                return "O-O-O"

        if self.piece_moved[1] == 'P' and originating_file != file: 
            notated_piece_moved = originating_file
            capture_str = 'x'
        elif self.piece_moved[1] == 'P': 
            notated_piece_moved = ''
            capture_str = ''
        elif self.piece_captured != ' ':
            notated_piece_moved = self.piece_moved[1]
            capture_str = 'x'
        else:
            notated_piece_moved = self.piece_moved[1]
            capture_str = ''

        return f"{notated_piece_moved}{capture_str}{file}{rank}"

    def check_enpassant(self, state):
        if len(state.move_list) < 2:
            return None
        # If it is whites turn, then the move that allow
        # en passant would come from black, and that would include
        # any pawn move that goes two spaces forward

        # direction is the the direction that the pawn moves
        # in rows.

        # opposite pawn is the pawn of the opposite color 
        if state.white_to_move:
            direction = 1
            moves_ep = b_pawn_moves_that_allow_ep
            opposite_pawn = "bP"
        else:
            direction = -1
            moves_ep = w_pawn_moves_that_allow_ep
            opposite_pawn = "wP"
        if state.move_list[-2] in moves_ep:
            if self.piece_captured == " ":
                enpassanted_piece = self.board[self.end_row+direction][self.end_col]
                if enpassanted_piece == opposite_pawn:
                    if self.piece_moved[1] == "P":
                        self.board[self.end_row+direction][self.end_col] = " "
        return False

    def is_move_castling(self):
        # Checks if the current move is castling, by
        # checking if the piece moved is a King and
        # if the King moved 2 columns over in this move
        if "K" in self.piece_moved:
            if abs(self.start_col - self.end_col) == 2:
                return True
        return False

    def move_piece(self):
        # moves the piece by making the starting square
        # empty and the end square the piece that moved
        self.board[self.start_row][self.start_col] = " "
        self.board[self.end_row][self.end_col] = self.piece_moved

    def is_move_legal(self, moves):
        # checks if the current move is legal by checking
        # if the current move (type = list) is in the list
        # of moves given
        if ([(self.start_square), (self.end_square)]) in moves:
            return True
        return False
