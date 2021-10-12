import pygame

DIM = 8
GREEN = 0, 255, 0
RED = 255, 0, 0

w_pawn_moves_that_allow_ep = ["a4", "b4", "c4", "d4", "e4", "f4", "g4", "h4"]
b_pawn_moves_that_allow_ep = ["a5", "b5", "c5", "d5", "e5", "f5", "g5", "h5"]

class GameState:

    def __init__(self):
        # initializes the game state with its
        # basic attributes (board, white_to_move,
        # move_list, etc.)
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
        # resets the game state by reinitializing it
        # and re-creating the start position
        self.__init__()
        self.create_start_pos()

    def create_start_pos(self):
        # creates the basic start position of any chess game
        self.board[0] = ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR']
        self.board[1] = ['bP', 'bP', 'bP', ' ', 'bP', 'bP', 'bP', 'bP']
        self.board[6] = ['wP', 'wP', 'wP', 'wP', ' ', 'wP', 'wP', 'wP']
        self.board[7] = ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']

    def check_player_move(self, piece:str):
        # checks if the piece that is given
        # is allowed to be moved this turn
        if piece[0] == 'w' and self.white_to_move == True:
            return True
        elif piece[0] == 'w' and self.white_to_move == False:
            return False
        elif piece[0] == 'b' and self.white_to_move == False:
            return True
        else:
            return False

    def check_winner(self):
        # Checks if both kings are on the board
        # if one of them is not there, the player
        # who doesn't have a king loses
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

    def move_piece(self, move, board=None):
        if board == None:
            board = self.board
        board[move.start_row][move.start_col] = " "
        board[move.end_row][move.end_col] = move.piece_moved

    def all_legal_moves(self):
        # finds all legal moves by first finding
        # all possible moves ... (WIP)
        all_moves = self.all_possible_moves()
        check = self.check_check()
        legal_moves = []
        for move in all_moves:
            sim_board = self.create_simulated_board(move)
            king = "wK" if self.white_to_move else "bK"
            king_pos = self.find_piece_pos(king, sim_board)
            unsafe_move = self.is_piece_attacked(king_pos[0], king_pos[1], sim_board)
            if not unsafe_move:
                legal_moves.append(move)
        return legal_moves

    def all_possible_moves(self, board=None, flip_color=False):
        # finds all possible moves with each
        # get_[piece]_moves function
        moves = []
        board = self.board if board == None else board
        for r in range(DIM):
            for c in range(DIM):
                square = board[r][c]
                team = square[0]
                if square != " ":
                    if (team == "w" and self.white_to_move and not flip_color) or (team == "b" and not self.white_to_move and not flip_color) or (self.white_to_move and team == "b" and flip_color) or (not self.white_to_move and team == "w" and flip_color):
                        piece = square[1]
                        
                        func = self.funcs[piece]
                        func(r, c, moves, flip_color, board)

        return moves

    def find_piece_pos(self, piece, board=None):
        if board == None:
            board = self.board
        for r in range(DIM):
            for c in range(DIM):
                if board[r][c] == piece:
                    return r, c

    def check_check(self):
        king = "wK" if self.white_to_move else "bK"
        king_pos = self.find_piece_pos(king)

        return self.is_piece_attacked(king_pos[0], king_pos[1])

    def create_simulated_board(self, move):
        simulated = [i.copy() for i in self.board]
        self.move_piece(move, simulated)
        return simulated

    def is_piece_attacked(self, row, col, board=None):
        if board == None:
            board = self.board
        opp_moves = self.all_possible_moves(board, True)
        for opp_move in opp_moves:
            if opp_move.end_row == row and opp_move.end_col == col:
                return True
        return False

    def get_pawn_moves(self, row, col, moves, flip_color=False, board=None):
        # gets all pawn moves by first getting
        # the direction that pawns go by
        # seeing who's turn it is, if it's
        # white to move, then pawns move -1
        # rows (up), otherwise they move
        # +1 row (down). Next, checks if the
        # space in front of the pawn is occupied
        # and checks if the spaces diagonal to
        # the pawn are occupied by an
        # opposing piece. Also, checks if en
        # passant is legal with
        # check_enpassant()
        board = self.board if board == None else board

        team = self.get_team(flip_color)
        opposing_team = self.get_team(flip_color, True)
        direction = -1 if team == 'w' else 1

        start_square = row, col
        end_square = row + direction, col
        diag_squares = [
            (end_square[0], end_square[1]+1),
            (end_square[0], end_square[1]-1)
        ]

        # If the pawn is on the white team and it is
        # on the starting row (6) then it can move two
        # squares, same for the black time, but row 1
        if team == 'w':
            right_two_squares = True if row == 6 else False
        else:
            right_two_squares = True if row == 1 else False

        # check if space in front is empty, adds it to the move
        # list if so
        if board[end_square[0]][end_square[1]] == ' ':
            moves.append(Move(start_square, end_square, self))

        # checks if the pawn has the right to move forward
        # 2 squares, if so adds that to move list
        if right_two_squares:
            two_squares_forward = (end_square[0]+direction, end_square[1])
            if board[two_squares_forward[0]][two_squares_forward[1]] == " ":
                moves.append(Move(start_square, two_squares_forward, self))

        # checks if each diagonal square of the pawn
        # is occupied by an enemy piece, if so adds
        # to move list
        for diag_square in diag_squares:
            if DIM <= diag_square[1] or 0 > diag_square[1]:
                break
            if opposing_team in board[diag_square[0]][diag_square[1]]:
                moves.append(Move(start_square, diag_square, self))
        
        # checks if en passant is legal, if so adds to move
        # list
        ep_bool, ep_direction = self.check_enpassant(start_square)
        if ep_bool:
            ep_end_square = (end_square[0], end_square[1] + ep_direction)
            moves.append(Move(start_square, ep_end_square, self))

    def get_rook_moves(self, row, col, moves, flip_color=False, board=None):
        # Gets rook moves by iteration over
        # directions list (horizontal direciton) 
        # and continuing
        # adding to each direction until
        # the loop encounters a any other piece
        # and checks if the piece is capturable
        # (if its from the opposing team)
        board = self.board if board == None else board
        directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        start_square = row, col

        team = self.get_team(flip_color)
        opposing_team = self.get_team(flip_color, True)

        for direction in directions:
            r, c = direction
            for i in range(DIM):
                i += 1
                if row + (r * i) > 7 or col + (c * i) > 7:
                    break
                end_square = end_row, end_col = row + (r * i), col + (c * i)
                captured_piece = board[end_row][end_col]
                if end_row < 0 or end_col < 0:
                    break
                if captured_piece == " ":
                    moves.append(Move(start_square, end_square, self))
                elif opposing_team in captured_piece:
                    moves.append(Move(start_square, end_square, self))
                    break
                else:
                    break

    def get_bishop_moves(self, row, col, moves, flip_color=False, board=None):
        # Gets bishop moves by iteration over
        # directions list (diagonal directions)
        # and continuing
        # adding to each direction until
        # the loop encounters a any other piece
        # and checks if the piece is capturable
        # (if its from the opposing team)
        board = self.board if board == None else board
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        start_square = row, col

        team = self.get_team(flip_color)
        opposing_team = self.get_team(flip_color, True)
        
        for direction in directions:
            r, c = direction
            for i in range(DIM):
                i += 1
                if row + (r * i) > 7 or col + (c * i) > 7:
                    break
                end_square = end_row, end_col = row + (r * i), col + (c * i)
                captured_piece = board[end_row][end_col]
                if end_row < 0 or end_col < 0:
                    break
                elif captured_piece == " ":
                    moves.append(Move(start_square, end_square, self))
                elif opposing_team in captured_piece:
                    moves.append(Move(start_square, end_square, self))
                    break
                else:
                    break

    def get_queen_moves(self, row, col, moves, flip_color=False, board=None):
        # Gets queen moves by combining logic from
        # bishop and queen in to one function
        board = self.board if board == None else board
        directions = [
            (1, 1), (1, -1), (-1, 1), (-1, -1),
            (1, 0), (0, 1), (-1, 0), (0, -1)
        ]
        start_square = row, col

        team = self.get_team(flip_color)
        opposing_team = self.get_team(flip_color, True)

        for direction in directions:
            r, c = direction
            for i in range(DIM):
                i += 1
                if row + (r * i) > 7 or col + (c * i) > 7:
                    break
                end_square = end_row, end_col = row + (r * i), col + (c * i)
                captured_piece = board[end_row][end_col]
                if end_row < 0 or end_col < 0:
                    break
                elif captured_piece == " ":
                    moves.append(Move(start_square, end_square, self))
                elif opposing_team in captured_piece:
                    moves.append(Move(start_square, end_square, self))
                    break
                else:
                    break

    def get_king_moves(self, row, col, moves, flip_color=False, board=None):
        # Gets all king moves by checking if the
        # from the start square are either occupied
        # by nothing or by an opposing piece.
        # Also checks if castling is legal with
        # self.check_castling_rights() function
        board = self.board if board == None else board
        directions = [
            (1, 1), (1, -1), (-1, 1), (-1, -1),
            (1, 0), (0, 1), (-1, 0), (0, -1)
        ]
        start_square = row, col

        opposing_team = self.get_team(flip_color, True)

        for direction in directions:
            end_square = end_row, end_col = row + direction[0], col + direction[1]
            if end_row < 0 or end_row > 7 or end_col < 0 or end_col > 7:
                pass
            elif board[end_row][end_col] == " " or opposing_team in self.board[end_row][end_col]:
                moves.append(Move(start_square, end_square, self))

        legal_castling = self.check_castling_rights(start_square)
        if legal_castling != []:
            for move in legal_castling:
                moves.append(move)


    def get_knight_moves(self, row, col, moves, flip_color=False, board=None):
        # Gets all knight moves by checking if the directions 
        # from the start square are either occupied by nothing
        # or by an opposing piece
        board = self.board if board == None else board
        directions = [
            (2, 1), (1, 2), 
            (2, -1), (1, -2),
            (-2, 1), (-1, 2),
            (-2, -1), (-1, -2)
        ]
        start_square = row, col

        opposing_team = self.get_team(flip_color, True)

        for direction in directions:
            end_square = end_row, end_col = row + direction[0], col + direction[1]
            if end_row < 0 or end_row > 7 or end_col < 0 or end_col > 7:
                pass
            else:
                if board[end_row][end_col] == " ":
                    moves.append(Move(start_square, end_square, self))
                elif opposing_team in board[end_row][end_col]:
                    moves.append(Move(start_square, end_square, self))
    
    def check_enpassant(self, pos:tuple[int, int]):
        # checks if en passant is legal by checking if
        # the last move played was a pawn up two squares
        # and if there is a pawn on the correct row
        # to actually play en passant
        if len(self.move_list) == 0:
            return (False, False)
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
        return (False, False)

    def check_castling_rights(self, king_pos:tuple[int, int]):
        # checks if castling is legal on either side
        # by checking if the king has moved from its
        # starting square and if the rooks have
        # moved from their starting squares
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
                legal_castling_moves.append(Move(king_pos, (row, col-2), self))
        if self.board[starting_row][7] == rook: # check if kingside castling is legal
            if self.board[starting_row][5] == " " and self.board[starting_row][6] == " ":
                legal_castling_moves.append(Move(king_pos, (row, col+2), self))

        return legal_castling_moves

    def get_team(self, flip_color, opposing=False):
        if opposing:
            black = "w"
            white = "b"
        else:
            black = "b"
            white = "w"
        if self.white_to_move and flip_color:
            return black
        elif self.white_to_move and not flip_color:
            return white
        elif not self.white_to_move and flip_color:
            return white
        else:
            return black

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

    def __init__(self, start_square:tuple[int, int], end_square:tuple[int,int], state):
        # initalizes the move with its required attributes
        # (board, start_square(row, col), end_square(row, col),
        # the piece that moved, the piece/space that is being
        # "captured", the pieces notation, etc.)
        self.state = state
        self.board = self.state.board
        self.start_square = start_square
        self.start_row = start_square[0]
        self.start_col = start_square[1]
        self.end_square = end_square
        self.end_row = end_square[0]
        self.end_col = end_square[1]

        self.piece_moved = self.board[self.start_row][self.start_col]
        self.piece_captured = self.board[self.end_row][self.end_col]

        self.castling = self.is_move_castling()
        self.enpassant, self.ep_direction = self.is_move_enpassant()
        self.promotion = self.is_move_promotion()
        self.notation = self.get_algebraic_notation()

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __str__(self):
        return self.notation

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
    
    def is_move_promotion(self):
        # checks if a pawn has reached the 8th or 1st rank
        # will promote it to a queen at the moment, this must
        # be changed to allow for under promotion to at least
        # a knight, however bishops and rooks should also
        # be included
        for w_square in self.board[0]: # for square in 8th rank
            for b_square in self.board[7]: # for square in 1st rank
                if "P" in w_square or "P" in b_square:
                    return True

    def is_move_enpassant(self):
        if len(self.state.move_list) < 2:
            return (False, False)
        # If it is whites turn, then the move that allow
        # en passant would come from black, and that would include
        # any pawn move that goes two spaces forward

        # direction is the the direction that the pawn moves
        # in rows.

        # opposite pawn is the pawn of the opposite color 
        if self.piece_moved[0] == 'w':
            direction = 1
            moves_ep = b_pawn_moves_that_allow_ep
            opposite_pawn = "bP"
        else:
            direction = -1
            moves_ep = w_pawn_moves_that_allow_ep
            opposite_pawn = "wP"
        if self.state.move_list[-1] in moves_ep:
            if self.piece_captured == " ":
                enpassanted_piece = self.board[self.end_row+direction][self.end_col]
                if enpassanted_piece == opposite_pawn:
                    if self.piece_moved[1] == "P":
                        return (True, direction)
                        
        return (False, False)

    def is_move_castling(self):
        # Checks if the current move is castling, by
        # checking if the piece moved is a King and
        # if the King moved 2 columns over in this move
        if "K" in self.piece_moved:
            if abs(self.start_col - self.end_col) == 2:
                return True
        return False
