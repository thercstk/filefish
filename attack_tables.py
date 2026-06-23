from constants import *

# ============================== #
#             TABLES             #
# ============================== #

KNIGHT_ATTACKS   = [0] * 64
KING_ATTACKS     = [0] * 64
ROOK_ATTACKS     = [[0] * 8192 for _ in range(64)]
BISHOP_ATTACKS   = [[0] * 2048 for _ in range(64)]

ROOK_RELEVANCE   = [0] * 64
BISHOP_RELEVANCE = [0] * 64

ROOK_MAGICS = [
    0x0080022080124000, 0x0040200110004000, 0x0080085000200080, 0x0080080080041000,
    0x1080040008008082, 0x01002804000A0100, 0x0100040081000200, 0x0080108000402100,
    0x1000800080400420, 0x4A00401000412000, 0x00010040A0001100, 0x0840800802100080,
    0x0100800400280080, 0x0002001004020008, 0x8004009004030218, 0x0A00800100004080,
    0x0080004020004000, 0x8090104000200040, 0x0010002008002400, 0x0800808010000800,
    0x0A08010031000408, 0x0000808004000200, 0x0000040011080210, 0x2001220000840041,
    0x0000400080008020, 0x0000400100210082, 0x00C0200180100081, 0x04C0100080080080,
    0x8000040080800800, 0x0002000280040080, 0x0020010080800200, 0x0000010200008044,
    0x0008400481800028, 0x00C0804000802000, 0x0010002009801082, 0x0000080280801000,
    0x0000820400800800, 0x0000040080800200, 0x0000020804000170, 0x0101000085000042,
    0x401C204000808001, 0x0020500820004000, 0x0020020400101000, 0x0000100100090020,
    0x1014000800808004, 0x0004000402008080, 0x2000020110040018, 0x0002008241020004,
    0x2000204000800080, 0x0001400280A00080, 0x8100184101200100, 0x0000100080080180,
    0x0001001004080100, 0x0200240002008080, 0x0000A81002010400, 0x0400008044010200,
    0x0014800014410021, 0x0000802201083042, 0x0084200100400813, 0x0001042010010109,
    0x000100148800101F, 0x0402001408091002, 0x0000421000880104, 0x0200040908402082
]

BISHOP_MAGICS = [
    0x0220600102008010, 0x001001020410C001, 0x0004840082000000, 0x0004040080001084,
    0x400A021022C00000, 0x0401100210080000, 0x0014008444200000, 0x0002010101012000,
    0x00084005012C0100, 0x800C2001020200C4, 0x081008880102A004, 0x0010140400800000,
    0x0000020210000000, 0x0300008220210010, 0x00004044100410A0, 0x0400004206100202,
    0x88620010041000A0, 0x0002002004010200, 0x0010008204001060, 0x0002400401020040,
    0x0802000402110200, 0x00124008080A1000, 0x1804000084040200, 0x08020080C2008400,
    0x0020040230040800, 0x0002208010040888, 0x2002020001040400, 0x8000802006020200,
    0x0202002022008040, 0x0002008008080100, 0x8008020020420202, 0x0082020000410082,
    0x0222084040051000, 0x0288224228100440, 0x0804002400020400, 0x4200110801140040,
    0x0002008400020020, 0x0005190408020200, 0x2408880500884100, 0x0002008100002400,
    0x0405103004001001, 0x20220084040D2180, 0x0000108410000100, 0x0040004200800800,
    0x0000080104004140, 0x02024E1141004200, 0x0010022204100840, 0x4088080108400220,
    0x0002080105100000, 0x00010100B0040000, 0x2100010088140202, 0x0400000084141080,
    0x0080004008220000, 0x0800401022008000, 0x8008108408024000, 0x0090040084004800,
    0x0000808808021200, 0x008400A108080420, 0x0400000042080400, 0x0004000000420200,
    0x0148100208502401, 0x8024414014080220, 0x0000400404008200, 0x2402101121040080,
]

# ============================== #
#           GENERATORS           #
# ============================== #

def generate_rook_attacks(i, bb):
    attacks = 0

    # Rook North
    mask = 1 << i
    for j in range(i+8, 65, 8):
        mask <<= 8
        attacks |= mask
        if mask & bb:
            break
    # Rook South
    mask = 1 << i
    for j in range(i-8, -1, -8):
        mask >>= 8
        attacks |= mask
        if mask & bb:
            break
    # Rook East
    mask = 1 << i
    while mask & FILE_H == 0:
        mask <<= 1
        attacks |= mask
        if mask & bb:
            break
    # Rook West
    mask = 1 << i
    while mask & FILE_A == 0:
        mask >>= 1
        attacks |= mask
        if mask & bb:
            break

    return attacks

def generate_bishop_attacks(i, bb):
    attacks = 0

    # Bishop NW
    mask = 1 << i
    while mask & (FILE_A | RANK_8)  == 0:
        mask <<= 7
        attacks |= mask
        if mask & bb:
            break
    # Bishop NE
    mask = 1 << i
    while mask & (FILE_H | RANK_8) == 0:
        mask <<= 9
        attacks |= mask
        if mask & bb:
            break
    # Bishop SE
    mask = 1 << i
    while mask & (FILE_H | RANK_1) == 0:
        mask >>= 7
        attacks |= mask
        if mask & bb:
            break
    # Bishop SW
    mask = 1 << i
    while mask & (FILE_A | RANK_1) == 0:
        mask >>= 9
        attacks |= mask
        if mask & bb:
            break

    return attacks

def generate_subsets(bb) -> list:
    subsets = []
    subset = 0
    while True:
        subsets.append(subset)
        subset = (subset - bb) & bb
        if subset == 0:
            break
    return subsets

def init_tables():
    # KING AND KNIGHT ATTACK PRECALC
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

    # BISHOP AND ROOK RELEVANCE PRECALC
    for i in range(64):
        rook_i = bishop_i = 0

        # Rook North
        mask = 1 << i
        for j in range(i+8, 56, 8):
            mask <<= 8
            rook_i |= mask
        # Rook South
        mask = 1 << i
        for j in range(i-8, 7, -8):
            mask >>= 8
            rook_i |= mask
        # Rook East
        mask = 1 << i
        while (mask | mask << 1) & FILE_H == 0:
            mask <<= 1
            rook_i |= mask
        # Rook West
        mask = 1 << i
        while (mask | mask >> 1) & FILE_A == 0:
            mask >>= 1
            rook_i |= mask

        # Bishop NW
        mask = 1 << i
        while mask & (FILE_A | RANK_8)  == 0:
            mask <<= 7
            bishop_i |= mask
        # Bishop NE
        mask = 1 << i
        while mask & (FILE_H | RANK_8) == 0:
            mask <<= 9
            bishop_i |= mask
        # Bishop SE
        mask = 1 << i
        while mask & (FILE_H | RANK_1) == 0:
            mask >>= 7
            bishop_i |= mask
        # Bishop SW
        mask = 1 << i
        while mask & (FILE_A | RANK_1) == 0:
            mask >>= 9
            bishop_i |= mask

        ROOK_RELEVANCE[i]   = rook_i
        BISHOP_RELEVANCE[i] = bishop_i & ~BOARD_EDGE

    # ROOK ATTACK PRECALC
    for i in range(64):
        subsets = generate_subsets(ROOK_RELEVANCE[i])
        n_bits = ROOK_RELEVANCE[i].bit_count()
        magic = ROOK_MAGICS[i]
        attacks_i = [0] * 8192
        for sub in subsets:
            key = ((sub * magic) & FULL_BOARD) >> (64 - n_bits)
            val = generate_rook_attacks(i, sub)
            attacks_i[key] = val

        ROOK_ATTACKS[i] = attacks_i

    # BISHOP ATTACK PRECALC
    for i in range(64):
        subsets = generate_subsets(BISHOP_RELEVANCE[i])
        n_bits = BISHOP_RELEVANCE[i].bit_count()
        magic = BISHOP_MAGICS[i]
        attacks_i = [0] * 8192
        for sub in subsets:
            key = ((sub * magic) & FULL_BOARD) >> (64 - n_bits)
            val = generate_bishop_attacks(i, sub)
            attacks_i[key] = val

        BISHOP_ATTACKS[i] = attacks_i
        for sub in subsets:
            key = ((sub * magic) & FULL_BOARD) >> (64 - n_bits)
            val = generate_bishop_attacks(i, sub)
            assert BISHOP_ATTACKS[i][key] == val

# ============================== #
#             LOOKUP             #
# ============================== #

def pawn_attacks(bb, color):
    if color == WHITE:
        return ((bb << 7) & ~FILE_H) | ((bb << 9) & ~FILE_A)
    else:
        return ((bb >> 7) & ~FILE_A) | ((bb >> 9) & ~FILE_H)

def knight_attacks(sq):
    return KNIGHT_ATTACKS[sq]

def king_attacks(sq):
    return KING_ATTACKS[sq]

def rook_attacks(sq, occupied):
    attacks = ROOK_RELEVANCE[sq] & occupied
    n_bits = ROOK_RELEVANCE[sq].bit_count()
    index = ((attacks * ROOK_MAGICS[sq]) & FULL_BOARD) >> (64 - n_bits)
    return ROOK_ATTACKS[sq][index]

def bishop_attacks(sq, occupied):
    attacks = BISHOP_RELEVANCE[sq] & occupied
    n_bits = BISHOP_RELEVANCE[sq].bit_count()
    index = ((attacks * BISHOP_MAGICS[sq]) & FULL_BOARD) >> (64 - n_bits)
    return BISHOP_ATTACKS[sq][index]

def queen_attacks(sq, occupied):
    return (rook_attacks(sq, occupied) |
            bishop_attacks(sq, occupied))

# You might know what this does
init_tables()