from move import Move

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
        self.board = [["  " for i in range(8)] for i in range(8)]
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
        self.board[1] = ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP']
        self.board[2] = ['  ', '  ', '  ', '  ', '  ', '  ', '  ', '  ']
        self.board[3] = ['  ', '  ', '  ', '  ', '  ', '  ', '  ', '  ']
        self.board[4] = ['  ', '  ', '  ', '  ', '  ', '  ', '  ', '  ']
        self.board[5] = ['  ', '  ', '  ', '  ', '  ', '  ', '  ', '  ']
        self.board[6] = ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP']
        self.board[7] = ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']

    def check_mates(self) -> str:
        check = self.is_check()
        opp_moves = self.all_legal_moves()
        if opp_moves == [] and check:
            return "checkmate"
        elif opp_moves == [] and not check:
            return "stalemate"

    def move_piece(self, move:Move, board:list=None):
        if board == None:
            board = self.board
        board[move.start_row][move.start_col] = "  "
        board[move.end_row][move.end_col] = move.piece_moved

    def all_legal_moves(self) -> list:
        # finds all legal moves by first finding
        # all possible moves ... (WIP)
        all_moves = self.all_possible_moves()
        legal_moves = []
        for move in all_moves:
            sim_board = self.create_simulated_board(move)
            king = "wK" if self.white_to_move else "bK"
            king_pos = self.find_piece_pos(king, sim_board)
            unsafe_move = self.is_piece_attacked(king_pos, sim_board)
            if not unsafe_move:
                legal_moves.append(move)
        return legal_moves

    def all_possible_moves(self, board:list = None, flip_color:bool = False) -> list:
        # finds all possible moves with each
        # get_[piece]_moves function
        moves = []
        board = self.board if board == None else board
        for r in range(DIM):
            for c in range(DIM):
                square = board[r][c]
                team = square[0]
                if square != "  ":
                    if (team == "w" and self.white_to_move and not flip_color) or (team == "b" and not self.white_to_move and not flip_color) or (self.white_to_move and team == "b" and flip_color) or (not self.white_to_move and team == "w" and flip_color):
                        piece = square[1]
                        
                        func = self.funcs[piece]
                        func(r, c, moves, flip_color, board)

        return moves

    def find_piece_pos(self, piece:str, board:list = None) -> tuple:
        if board == None:
            board = self.board
        for r in range(DIM):
            for c in range(DIM):
                if board[r][c] == piece:
                    return r, c

    def is_check(self) -> bool:
        king = self.get_team() + "K"
        king_pos = self.find_piece_pos(king)
        is_attacked = self.is_piece_attacked(king_pos)
        
        return is_attacked

    def create_simulated_board(self, move:Move) -> list:
        simulated = [i.copy() for i in self.board]
        self.move_piece(move, simulated)
        return simulated

    def is_piece_attacked(self, pos:tuple[int, int], board:list=None) -> bool:
        if board == None:
            board = self.board
        row, col = pos
        opp_moves = self.all_possible_moves(board, True)
        for opp_move in opp_moves:
            if opp_move.end_row == row and opp_move.end_col == col:
                return True
        return False

    def get_pawn_moves(self, row:int, col:int, moves:list, flip_color:bool=False, board:list=None):
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
        if board[end_square[0]][end_square[1]] == '  ':
            moves.append(Move(start_square, end_square, self.board, self.move_list))

        # checks if the pawn has the right to move forward
        # 2 squares, if so adds that to move list
        if right_two_squares:
            two_squares_forward = (end_square[0]+direction, end_square[1])
            if board[two_squares_forward[0]][two_squares_forward[1]] == "  ":
                moves.append(Move(start_square, two_squares_forward, self.board, self.move_list))

        # checks if each diagonal square of the pawn
        # is occupied by an enemy piece, if so adds
        # to move list
        for diag_square in diag_squares:
            if DIM <= diag_square[1] or 0 > diag_square[1]:
                continue
            if opposing_team in board[diag_square[0]][diag_square[1]]:
                moves.append(Move(start_square, diag_square, self.board, self.move_list))
        
        # checks if en passant is legal, if so adds to move
        # list
        ep_bool, ep_direction = self.check_enpassant(start_square)
        if ep_bool:
            ep_end_square = (end_square[0], end_square[1] + ep_direction)
            moves.append(Move(start_square, ep_end_square, self.board, self.move_list))

    def get_rook_moves(self, row:int, col:int, moves:list, flip_color:bool=False, board:list=None):
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
                if captured_piece == "  ":
                    moves.append(Move(start_square, end_square, self.board, self.move_list))
                elif opposing_team in captured_piece:
                    moves.append(Move(start_square, end_square, self.board, self.move_list))
                    break
                else:
                    break

    def get_bishop_moves(self, row:int, col:int, moves:list, flip_color:bool=False, board:list=None):
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
                elif captured_piece == "  ":
                    moves.append(Move(start_square, end_square, self.board, self.move_list))
                elif opposing_team in captured_piece:
                    moves.append(Move(start_square, end_square, self.board, self.move_list))
                    break
                else:
                    break

    def get_queen_moves(self, row:int, col:int, moves:list, flip_color:bool=False, board:list=None):
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
                elif captured_piece == "  ":
                    moves.append(Move(start_square, end_square, self.board, self.move_list))
                elif opposing_team in captured_piece:
                    moves.append(Move(start_square, end_square, self.board, self.move_list))
                    break
                else:
                    break

    def get_king_moves(self, row:int, col:int, moves:list, flip_color:bool=False, board:list=None):
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
            elif board[end_row][end_col] == "  " or opposing_team in self.board[end_row][end_col]:
                moves.append(Move(start_square, end_square, self.board, self.move_list))

        legal_castling = self.check_castling_rights(start_square)
        if legal_castling != []:
            for move in legal_castling:
                moves.append(move)

    def get_knight_moves(self, row:int, col:int, moves:list, flip_color:bool=False, board:list=None):
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
                if board[end_row][end_col] == "  ":
                    moves.append(Move(start_square, end_square, self.board, self.move_list))
                elif opposing_team in board[end_row][end_col]:
                    moves.append(Move(start_square, end_square, self.board, self.move_list))
    
    def check_enpassant(self, pos:tuple[int, int]) -> tuple:
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

    def check_castling_rights(self, king_pos:tuple[int, int]) -> list:
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
            if self.board[starting_row][3] == "  " and self.board[starting_row][2] == "  ":
                legal_castling_moves.append(Move(king_pos, (row, col-2), self.board, self.move_list))
        if self.board[starting_row][7] == rook: # check if kingside castling is legal
            if self.board[starting_row][5] == "  " and self.board[starting_row][6] == "  ":
                legal_castling_moves.append(Move(king_pos, (row, col+2), self.board, self.move_list))

        return legal_castling_moves

    def get_team(self, flip_color=False, opposing=False):
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
