from constants import *

def _decode_move(move) -> tuple:
    return (move & 63,
           (move >> 6) & 63, 
           (move >> 12) & 15,
            move >> 16)

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

        self.history = [(0, 0, 0, 0, 0)] * 1024
        self.history_idx = 0
        self.castling_rights = 15
        self.en_passant_sq = 0
        self.halfmove_clock = 0
        self.turn = WHITE
        self.zobrist = 0

        self.init_zobrist()

    def init_zobrist(self):
        self.zobrist = Z_CASTLING[self.castling_rights]
        for turn in (0, 1):
            for i in range(6):
                bb = self.pieces[turn][i]
                while bb:
                    mask = (bb & -bb).bit_length()-1
                    bb &= bb - 1
                    self.zobrist ^= Z_PIECES[i + 6 * self.turn][mask]
        if self.en_passant_sq:
            ep_sq = (self.en_passant_sq & -self.en_passant_sq).bit_length()-1
            self.zobrist ^= Z_EN_PASSANT[ep_sq & 7]
        if self.turn == BLACK:
            self.zobrist ^= Z_SIDE

    def apply_move(self, move):
        enemy = 1 - self.turn

        src, dst, flag, piece_moved = _decode_move(move)

        src_bb = 1 << src
        dst_bb = 1 << dst

        z = self.zobrist

        # Moving the piece
        self.pieces[self.turn][piece_moved] &= ~src_bb
        if flag in range(8, 16):
            self.pieces[self.turn][PROMOTED_TYPE[flag]] |= dst_bb
            z ^= Z_PIECES[6 * self.turn + piece_moved][src]
            z ^= Z_PIECES[6 * self.turn + PROMOTED_TYPE[flag]][dst]
        else:
            self.pieces[self.turn][piece_moved] |= dst_bb
            z ^= Z_PIECES[6 * self.turn + piece_moved][src]
            z ^= Z_PIECES[6 * self.turn + piece_moved][dst]

        # Occupancy
        self.occupancy[self.turn] ^= src_bb ^ dst_bb

        # Capturing the other piece
        captured = -1
        if flag in (capture, en_passant) or 12 <= flag <= 15:
            if flag == en_passant:
                captured = PAWNS
                cap_bb = dst_bb >> 8 if self.turn == WHITE else dst_bb << 8
                cap_sq = dst - 8 if self.turn == WHITE else dst + 8
                self.pieces[enemy][captured] &= ~cap_bb
                self.occupancy[enemy] ^= cap_bb
                z ^= Z_PIECES[enemy * 6 + captured][cap_sq]
            else:
                for piece_type in range(6):
                    if dst_bb & self.pieces[enemy][piece_type]:
                        self.pieces[enemy][piece_type] &= ~dst_bb
                        captured = piece_type
                        break
                self.occupancy[enemy] ^= dst_bb
                z ^= Z_PIECES[enemy * 6 + captured][dst]

        # Saving the irreversible changes
        self.history[self.history_idx] = (
            self.castling_rights,
            self.en_passant_sq,
            self.halfmove_clock,
            captured,
            self.zobrist
        )
        self.history_idx += 1

        # Clearing old en_passant zobrist
        if self.en_passant_sq:
            z ^= Z_EN_PASSANT[((en_passant & -en_passant).bit_length()-1) & 7]

        # Setting the new en-passant square
        if flag == double_pawn:
            self.en_passant_sq = 1 << ((src + dst) >> 1)
            z ^= Z_EN_PASSANT[((src + dst) >> 1) & 7]
        else:
            self.en_passant_sq = 0

        # Castling
        if flag == king_castle:
            if self.turn == WHITE:
                self.pieces[self.turn][ROOKS] &= ~H1
                self.pieces[self.turn][ROOKS] |= F1
                self.occupancy[self.turn] ^=  H1 ^ F1
                z ^= Z_PIECES[self.turn * 6 + ROOKS][7]
                z ^= Z_PIECES[self.turn * 6 + ROOKS][5]
            else:
                self.pieces[self.turn][ROOKS] &= ~H8
                self.pieces[self.turn][ROOKS] |= F8
                self.occupancy[self.turn] ^= H8 ^ F8
                z ^= Z_PIECES[self.turn * 6 + ROOKS][63]
                z ^= Z_PIECES[self.turn * 6 + ROOKS][61]

        if flag == queen_castle:
            if self.turn == WHITE:
                self.pieces[self.turn][ROOKS] &= ~A1
                self.pieces[self.turn][ROOKS] |= D1
                self.occupancy[self.turn] ^= A1 ^ D1
                z ^= Z_PIECES[self.turn * 6 + ROOKS][0]
                z ^= Z_PIECES[self.turn * 6 + ROOKS][3]
            else:
                self.pieces[self.turn][ROOKS] &= ~A8
                self.pieces[self.turn][ROOKS] |= D8
                self.occupancy[self.turn] ^= A8 ^ D8
                z ^= Z_PIECES[self.turn * 6 + ROOKS][56]
                z ^= Z_PIECES[self.turn * 6 + ROOKS][59]

        # Castling rights update
        old_rights = self.castling_rights
        self.castling_rights &= CASTLING_MASK[src]
        self.castling_rights &= CASTLING_MASK[dst]
        if old_rights != self.castling_rights:
            z ^= Z_CASTLING[old_rights]
            z ^= Z_CASTLING[self.castling_rights]

        # Halfmove clock and turn update
        if flag == capture or piece_moved == PAWNS:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1

        self.turn ^= 1
        z ^= Z_SIDE

        # Update for occupied
        self.occupied = self.occupancy[0] | self.occupancy[1]

        # Last but not least
        self.zobrist = z

    def undo_move(self, move):
        self.history_idx -= 1
        state = self.history[self.history_idx]
        enemy = self.turn
        self.turn = 1-self.turn

        src, dst, flag, piece_moved = _decode_move(move)

        src_bb = 1 << src
        dst_bb = 1 << dst

        # Returning the moved piece to it's original position
        if flag & 0b1000:
            self.pieces[self.turn][PROMOTED_TYPE[flag]] &= ~dst_bb
            self.pieces[self.turn][PAWNS] |= src_bb
        else:
            self.pieces[self.turn][piece_moved] &= ~dst_bb
            self.pieces[self.turn][piece_moved] |= src_bb

        self.occupancy[self.turn] ^= src_bb ^ dst_bb

        # Restoring the captured piece
        captured = state[3]
        if flag == en_passant:
            captured_bb = dst_bb >> 8 if self.turn == WHITE else dst_bb << 8
            self.pieces[enemy][captured] |= captured_bb
            self.occupancy[enemy] ^= captured_bb
        elif flag == 4 or 12 <= flag <= 15:
            self.pieces[enemy][captured] |= dst_bb
            self.occupancy[enemy] ^= dst_bb

        # Undoing the castling
        if flag == king_castle:
            if self.turn == WHITE:
                self.pieces[self.turn][ROOKS] &= ~F1
                self.pieces[self.turn][ROOKS] |= H1
                self.occupancy[self.turn] ^=  H1 ^ F1
            else:
                self.pieces[self.turn][ROOKS] &= ~F8
                self.pieces[self.turn][ROOKS] |= H8
                self.occupancy[self.turn] ^= H8 ^ F8

        if flag == queen_castle:
            if self.turn == WHITE:
                self.pieces[self.turn][ROOKS] &= ~D1
                self.pieces[self.turn][ROOKS] |= A1
                self.occupancy[self.turn] ^= A1 ^ D1
            else:
                self.pieces[self.turn][ROOKS] &= ~D8
                self.pieces[self.turn][ROOKS] |= A8
                self.occupancy[self.turn] ^= A8 ^ D8

        # Restoring irreversible data
        self.castling_rights = state[0]
        self.en_passant_sq   = state[1]
        self.halfmove_clock  = state[2]

        # Update for occupied
        self.occupied = self.occupancy[0] | self.occupancy[1]

        # Zobrist
        self.zobrist = state[4]

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
        self.init_zobrist()