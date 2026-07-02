from constants import *

def print_bb(bb: int):
    board = ['0'] * 64
    for i in range(64):
        if 1 << i & bb != 0:
            board[i] = '1'
    for i in range(7, -1, -1):
        print('['+' '.join(board[i*8:(i+1)*8])+']')