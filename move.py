class Move:

    w_pawn_moves_that_allow_ep = ["a4", "b4", "c4", "d4", "e4", "f4", "g4", "h4"]
    b_pawn_moves_that_allow_ep = ["a5", "b5", "c5", "d5", "e5", "f5", "g5", "h5"]


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

    def __init__(self, start_square:tuple[int, int], end_square:tuple[int,int], board:list, move_list:list):
        # initalizes the move with its required attributes
        # (board, start_square(row, col), end_square(row, col),
        # the piece that moved, the piece/space that is being
        # "captured", the pieces notation, etc.)
        self.move_list = move_list
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
        elif self.piece_captured != '  ':
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
        if self.end_row == 0 and self.piece_moved == "wP":
            return True
        elif self.end_row == 7 and self.piece_moved == "bP":
            return True
        return False

    def is_move_enpassant(self):
        if len(self.move_list) < 2:
            return (False, False)
        # If it is whites turn, then the move that allow
        # en passant would come from black, and that would include
        # any pawn move that goes two spaces forward

        # direction is the the direction that the pawn moves
        # in rows.

        # opposite pawn is the pawn of the opposite color 
        if self.piece_moved[0] == 'w':
            direction = 1
            moves_ep = Move.b_pawn_moves_that_allow_ep
            opposite_pawn = "bP"
        else:
            direction = -1
            moves_ep = Move.w_pawn_moves_that_allow_ep
            opposite_pawn = "wP"
        if self.move_list[-1] in moves_ep:
            if self.piece_captured == "  " and self.piece_moved[1] == "P":
                enpassanted_piece = self.board[self.end_row+direction][self.end_col]
                if enpassanted_piece == opposite_pawn:
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
