from constants import *
from board import Board
import attack_tables as at

PUSH   = [-8, 8]
D_PUSH = [-16, 16]
ATK_L  = [7, -9]
ATK_R  = [9, -7]

def _make_move(src, dst, flags, moved):
    return src | (dst << 6) | (flags << 12) | (moved << 16)

def _is_attacked(sq, attacker, board):
    occupied = board.occupied
    return (
        at.pawn_attacks_left(1 << sq, 1 - attacker) & board.pieces[attacker][PAWNS] or
        at.pawn_attacks_right(1 << sq, 1 - attacker) & board.pieces[attacker][PAWNS] or
        at.knight_attacks(sq) & board.pieces[attacker][KNIGHTS] or
        at.bishop_attacks(sq, occupied) & board.pieces[attacker][BISHOPS] or
        at.rook_attacks(sq, occupied) & board.pieces[attacker][ROOKS] or
        at.queen_attacks(sq, occupied) & board.pieces[attacker][QUEENS] or
        at.king_attacks(sq) & board.pieces[attacker][KING]
    )

def _generate_piece_moves(sq, attacks, piece_type, enemy_occ, occupied, movelist):
    for bb, flag in [
        (attacks & ~occupied, quiet_move),
        (attacks & enemy_occ, capture)
    ]:
        while bb:
            dst = (bb & -bb).bit_length()-1
            bb &= bb - 1
            move = _make_move(sq, dst, flag, piece_type)
            movelist.append(move)

def generate_moves(board: Board) -> list:
    movelist = []

    turn        = board.turn
    enemy_occ   = board.occupancy[1 - turn]
    occupied    = board.occupied
    passant_sq  = board.en_passant_sq

    castling_rights = board.castling_rights
    castling_ks = castling_rights & (1 << (2 * turn))
    castling_qs = castling_rights & (1 << (2 * turn + 1))
    ks_squares  = [(F1 | G1) & occupied, (F8 | G8) & occupied]
    qs_squares  = [(B1 | C1 | D1) & occupied, (B8 | C8 | D8) & occupied]
    king_att = _is_attacked(4 if turn == WHITE else 60, 1-turn, board)

    pawns   = board.pieces[turn][PAWNS]
    knights = board.pieces[turn][KNIGHTS]
    bishops = board.pieces[turn][BISHOPS]
    rooks   = board.pieces[turn][ROOKS]
    queens  = board.pieces[turn][QUEENS]
    king    = board.pieces[turn][KING]

    # Pawn attacks generation
    pushes        = at.pawn_push(pawns, turn) & ~occupied
    attacks_lraw  = at.pawn_attacks_left(pawns, turn)
    attacks_rraw  = at.pawn_attacks_right(pawns, turn)
    attacks_left  = attacks_lraw & enemy_occ
    attacks_right = attacks_rraw & enemy_occ

    d_pushes      = at.pawn_d_push(pawns, turn, occupied)

    attacks_left_np  = attacks_left & ~RANK_8 if turn == WHITE else attacks_left & ~RANK_1
    attacks_left_p   = attacks_left &  RANK_8 if turn == WHITE else attacks_left &  RANK_1
    attacks_right_np = attacks_right & ~RANK_8 if turn == WHITE else attacks_right & ~RANK_1
    attacks_right_p  = attacks_right &  RANK_8 if turn == WHITE else attacks_right &  RANK_1

    pushes_np = pushes & ~RANK_8 if turn == WHITE else pushes & ~RANK_1
    pushes_p  = pushes &  RANK_8 if turn == WHITE else pushes &  RANK_1

    passant_left  = attacks_lraw & passant_sq
    passant_right = attacks_rraw & passant_sq

    while d_pushes:
        sq = (d_pushes & -d_pushes).bit_length()-1
        d_pushes &= d_pushes - 1
        move = _make_move(sq + D_PUSH[turn], sq, double_pawn, PAWNS)
        movelist.append(move)

    while attacks_left_np:
        sq = (attacks_left_np & -attacks_left_np).bit_length()-1
        attacks_left_np &= attacks_left_np - 1
        move = _make_move(sq + ATK_R[1-turn], sq, capture, PAWNS)
        movelist.append(move)

    while attacks_left_p:
        sq = (attacks_left_p & -attacks_left_p).bit_length()-1
        attacks_left_p &= attacks_left_p - 1
        for flag in range(12, 16):
            move = _make_move(sq + ATK_R[1-turn], sq, flag, PAWNS)
            movelist.append(move)

    while attacks_right_np:
        sq = (attacks_right_np & -attacks_right_np).bit_length()-1
        attacks_right_np &= attacks_right_np - 1
        move = _make_move(sq + ATK_L[1-turn], sq, capture, PAWNS)
        movelist.append(move)

    while attacks_right_p:
        sq = (attacks_right_p & -attacks_right_p).bit_length()-1
        attacks_right_p &= attacks_right_p - 1
        for flag in range(12, 16):
            move = _make_move(sq + ATK_L[1-turn], sq, flag, PAWNS)
            movelist.append(move)

    while pushes_np:
        sq = (pushes_np & -pushes_np).bit_length()-1
        pushes_np &= pushes_np - 1
        move = _make_move(sq + PUSH[turn], sq, quiet_move, PAWNS)
        movelist.append(move)

    while pushes_p:
        sq = (pushes_p & -pushes_p).bit_length()-1
        pushes_p &= pushes_p - 1
        for flag in range(8, 12):
            move = _make_move(sq + PUSH[turn], sq, flag, PAWNS)
            movelist.append(move)

    if passant_left:
        sq = (passant_left & -passant_left).bit_length()-1
        move = _make_move(sq + ATK_R[1-turn], sq, en_passant, PAWNS)
        movelist.append(move)

    if passant_right:
        sq = (passant_right & -passant_right).bit_length()-1
        move = _make_move(sq + ATK_L[1-turn], sq, en_passant, PAWNS)
        movelist.append(move)

    # Knight generation
    while knights:
        sq = (knights & -knights).bit_length()-1
        knights &= knights - 1
        attacks = at.knight_attacks(sq)
        _generate_piece_moves(sq, attacks, KNIGHTS, enemy_occ, occupied, movelist)

    # Bishop generation
    while bishops:
        sq = (bishops & -bishops).bit_length()-1
        bishops &= bishops - 1
        attacks = at.bishop_attacks(sq, occupied)
        _generate_piece_moves(sq, attacks, BISHOPS, enemy_occ, occupied, movelist)

    # Rook generation
    while rooks:
        sq = (rooks & -rooks).bit_length()-1
        rooks &= rooks - 1
        attacks = at.rook_attacks(sq, occupied)
        _generate_piece_moves(sq, attacks, ROOKS, enemy_occ, occupied, movelist)

    # Queen generation
    while queens:
        sq = (queens & -queens).bit_length()-1
        queens &= queens - 1
        attacks = at.queen_attacks(sq, occupied)
        _generate_piece_moves(sq, attacks, QUEENS, enemy_occ, occupied, movelist)

    # King generation
    sq = (king & -king).bit_length()-1
    attacks = at.king_attacks(sq)
    _generate_piece_moves(sq, attacks, KING, enemy_occ, occupied, movelist)

    # Castling generation
    if turn == WHITE:
        attacked_ks = (_is_attacked(5, 1 - turn, board) or
                       _is_attacked(6, 1 - turn, board))
        attacked_qs = (_is_attacked(2, 1 - turn, board) or
                       _is_attacked(3, 1 - turn, board))
        if not attacked_ks and castling_ks and not ks_squares[turn] and not king_att:
            move = _make_move(4, 6, king_castle, KING)
            movelist.append(move)
        if not attacked_qs and castling_qs and not qs_squares[turn] and not king_att:
            move = _make_move(4, 2, queen_castle, KING)
            movelist.append(move)
    else:
        attacked_ks = (_is_attacked(61, 1 - turn, board) or
                       _is_attacked(62, 1 - turn, board))
        attacked_qs = (_is_attacked(58, 1 - turn, board) or
                       _is_attacked(59, 1 - turn, board))
        if not attacked_ks and castling_ks and not ks_squares[turn] and not king_att:
            move = _make_move(60, 62, king_castle, KING)
            movelist.append(move)
        if not attacked_qs and castling_qs and not qs_squares[turn] and not king_att:
            move = _make_move(60, 58, queen_castle, KING)
            movelist.append(move)

    return movelist