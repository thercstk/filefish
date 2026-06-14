from constants import *

# Non-Sliding Pieces
KNIGHT_ATTACKS = [0] * 64
KING_ATTACKS   = [0] * 64

# Sliding Pieces
BISHOP_OCCUPANCY = [0] * 64
ROOK_OCCUPANCY   = [0] * 64

def get_knight_attacks(square):
    return KNIGHT_ATTACKS[square]
def get_king_attacks(square):
    return KING_ATTACKS[square]
def get_pawn_attacks(bb, color):
    if color == WHITE:
        return ((bb << 7) & ~FILE_H) | ((bb << 9) & ~FILE_A)
    else:
        return ((bb >> 7) & ~FILE_A) | ((bb >> 9) & ~FILE_H)    

for i in range(64):
    mask = 1 << i
    knight_i = king_i = 0

    knight_i |= (mask << 17) & ~ FILE_A
    knight_i |= (mask << 10) & ~(FILE_A | FILE_B)
    knight_i |= (mask >>  6) & ~(FILE_A | FILE_B)
    knight_i |= (mask >> 15) & ~ FILE_A
    knight_i |= (mask >> 17) & ~ FILE_H
    knight_i |= (mask >> 10) & ~(FILE_H | FILE_G) 
    knight_i |= (mask <<  6) & ~(FILE_H | FILE_G)
    knight_i |= (mask << 15) & ~ FILE_H

    king_i |= (mask << 8)
    king_i |= (mask << 9) & ~FILE_A
    king_i |= (mask << 1) & ~FILE_A
    king_i |= (mask >> 7) & ~FILE_A
    king_i |= (mask >> 8)
    king_i |= (mask >> 9) & ~FILE_H
    king_i |= (mask >> 1) & ~FILE_H
    king_i |= (mask << 7) & ~FILE_H

    KNIGHT_ATTACKS[i] = knight_i
    KING_ATTACKS[i]   = king_i