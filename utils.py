from constants import *
import random

def scan(bb: int) -> int:
    mask = bb & -bb
    return DEBRUJIN_ID[((mask * DEBRUJIN64) & FULL_BOARD) >> 58]