from constants import *

class Board:
    def __init__(self):
        self.pieces = [
            [0x000000000000FF00, 0x0000000000000042, 0x0000000000000024,
             0x0000000000000081, 0x0000000000000008, 0x0000000000000010],
            [0x00FF000000000000, 0x4200000000000000, 0x2400000000000000,
             0x8100000000000000, 0x0800000000000000, 0x1000000000000000]
        ]
        self.occupancy = [0x000000000000FFFF, 0xFFFF000000000000]
        self.occupied  =  0xFFFF00000000FFFF

        self.history = [(0, 0, 0, 0)] * 1024
        self.history_idx = 0
        self.castling_rights = 15
        self.en_passant_sq = 0
        self.halfmove_clock = 0
        self.turn = WHITE
        self.zobrist = 0
        
        self.calculate_zobrist()

    def calculate_zobrist(self):
        self.zobrist = Z_CASTLING[self.castling_rights]
        for turn in (0, 1):
            for i in range(6):
                bb = self.pieces[turn][i]
                while bb:
                    mask = (bb & -bb).bit_length()-1
                    bb &= bb - 1
                    self.zobrist ^= Z_PIECES[i + 6 * self.turn][mask]

    def apply_move(self, move):
        enemy = 1 - self.turn

        src  =  move & 63
        dst  = (move >> 6) & 63
        flag =  move >> 12

        src_bb = 1 << src
        dst_bb = 1 << dst

        piece_moved = -1
        for piece_type in range(6):
            if src_bb & self.pieces[self.turn][piece_type]:
                piece_moved = piece_type
                break

        # Moving the piece
        self.pieces[self.turn][piece_moved] &= ~src_bb
        if flag in range(8, 16):
            self.pieces[self.turn][PROMOTED_TYPE[flag]] |= dst_bb
        else:
            self.pieces[self.turn][piece_moved] |= dst_bb

        # Capturing the other piece
        captured = -1
        if flag in (capture, en_passant) or 12 <= flag <= 15:
            for piece_type in range(6):
                if dst_bb & self.pieces[enemy][piece_type]:
                    self.pieces[enemy][piece_type] &= ~dst_bb
                    captured = piece_type
                    break
            if captured == -1:
                captured = 0
                self.pieces[enemy][captured] &= \
                    ~(dst_bb >> 8 if self.turn == WHITE else dst_bb << 8)

        # Saving the irreversible changes
        self.history[self.history_idx] = (
            self.castling_rights,
            self.en_passant_sq,
            self.halfmove_clock,
            captured
        )
        self.history_idx += 1

        # Setting the new en-passant square
        if flag == double_pawn:
            self.en_passant_sq = 1 << ((src + dst) >> 1)
        else:
            self.en_passant_sq = 0

        # Castling
        if flag == king_castle:
            if self.turn == WHITE:
                self.pieces[self.turn][ROOKS] &= ~H1
                self.pieces[self.turn][ROOKS] |= F1
            else:
                self.pieces[self.turn][ROOKS] &= ~H8
                self.pieces[self.turn][ROOKS] |= F8

        if flag == queen_castle:
            if self.turn == WHITE:
                self.pieces[self.turn][ROOKS] &= ~A1
                self.pieces[self.turn][ROOKS] |= D1
            else:
                self.pieces[self.turn][ROOKS] &= ~A8
                self.pieces[self.turn][ROOKS] |= D8
        
        # Castling rights update
        self.castling_rights &= CASTLING_MASK[src]
        self.castling_rights &= CASTLING_MASK[dst]

        # Halfmove clock and turn update
        if flag == capture or piece_moved == PAWNS:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1

        self.turn ^= 1

        # Update for occupancy & occupied
        self.occupancy[0] = 0
        self.occupancy[1] = 0
        for turn in (0, 1):
            for piece_type in range(6):
                self.occupancy[turn] |= self.pieces[turn][piece_type]

        self.occupied = self.occupancy[0] | self.occupancy[1]

        # Last but not least
        self.calculate_zobrist()

    def undo_move(self, move):
        self.history_idx -= 1
        state = self.history[self.history_idx]
        enemy = self.turn
        self.turn = 1-self.turn
        
        src  =  move & 63
        dst  = (move >> 6) & 63
        flag =  move >> 12

        src_bb = 1 << src
        dst_bb = 1 << dst

        # Returning the moved piece to it's original position
        if flag in range(8, 16):
            self.pieces[self.turn][PROMOTED_TYPE[flag]] &= ~dst_bb
            self.pieces[self.turn][PAWNS] |= src_bb
        else:
            piece_moved = -1
            for piece_type in range(6):
                if dst_bb & self.pieces[self.turn][piece_type]:
                    piece_moved = piece_type
                    break
            self.pieces[self.turn][piece_moved] &= ~dst_bb
            self.pieces[self.turn][piece_moved] |= src_bb

        # Restoring the captured piece
        captured = state[3]
        if flag == en_passant:
            captured_bb = dst_bb >> 8 if self.turn == WHITE else dst_bb << 8
            self.pieces[enemy][captured] |= captured_bb
        elif flag == 4 or 12 <= flag <= 15:
            self.pieces[enemy][captured] |= dst_bb

        # Undoing the castling
        if flag == king_castle:
            if self.turn == WHITE:
                self.pieces[self.turn][ROOKS] &= ~F1
                self.pieces[self.turn][ROOKS] |= H1
            else:
                self.pieces[self.turn][ROOKS] &= ~F8
                self.pieces[self.turn][ROOKS] |= H8

        if flag == queen_castle:
            if self.turn == WHITE:
                self.pieces[self.turn][ROOKS] &= ~D1
                self.pieces[self.turn][ROOKS] |= A1
            else:
                self.pieces[self.turn][ROOKS] &= ~D8
                self.pieces[self.turn][ROOKS] |= A8

        # Restoring irreversible data
        self.castling_rights = state[0]
        self.en_passant_sq   = state[1]
        self.halfmove_clock  = state[2]

        # Update for occupancy & occupied
        self.occupancy[0] = 0
        self.occupancy[1] = 0
        for turn in (0, 1):
            for piece_type in range(6):
                self.occupancy[turn] |= self.pieces[turn][piece_type]

        self.occupied = self.occupancy[0] | self.occupancy[1]

        # Zobrist recalculation
        self.calculate_zobrist()

    def set_fen(self, fen):
        parts = fen.split()
        board_str  = parts[0]
        turn_str   = parts[1]
        castle_str = parts[2]
        ep_str     = parts[3]

        # Setting the pieces
        file, rank = 0, 7
        self.pieces = [[0] * 6 for _ in (0, 1)]
        for c in board_str:
            if c == '/':
                file = 0
                rank -= 1
            elif c.isdigit():
                file += int(c)
            else:
                turn, piece = FEN_CONVERT[c]
                self.pieces[turn][piece] |= (1 << (rank * 8 + file))
                file += 1

        # Occupancy recalc
        self.occupancy[0] = 0
        self.occupancy[1] = 0
        for turn in (0, 1):
            for piece_type in range(6):
                self.occupancy[turn] |= self.pieces[turn][piece_type]

        self.occupied = self.occupancy[0] | self.occupancy[1]

        # Turn & History
        self.turn = WHITE if turn_str == 'w' else BLACK
        self.history_idx = 0
        if len(parts) > 4: self.halfmove_clock = int(parts[4])

        # Castling rights
        self.castling_rights = 0
        if 'K' in castle_str: self.castling_rights |= 1
        if 'Q' in castle_str: self.castling_rights |= 2
        if 'k' in castle_str: self.castling_rights |= 4
        if 'q' in castle_str: self.castling_rights |= 8

        # En-passant square
        if ep_str == '-':
            self.en_passant_sq = 0
        else:
            ep_file = ord(ep_str[0]) - ord('a')
            ep_rank = int(ep_str[1]) - 1
            self.en_passant_sq = 1 << (ep_rank * 8 + ep_file)

        # Zobrist
        self.calculate_zobrist()