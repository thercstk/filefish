from src.constants import *
import src.board as board
import src.movegen as movegen

import time

TEST_POSITIONS = {
    "Initial": {
        "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        "expected": {1: 20, 2: 400, 3: 8902, 4: 197281, 5: 4865609, 6: 119060324}
    },
    "Kiwipete": {
        "fen": "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1",
        "expected": {1: 48, 2: 2039, 3: 97862, 4: 4085603, 5: 193690690, 6: 8031647685}
    },
    "Position 3": {
        "fen": "8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1",
        "expected": {1: 14, 2: 191, 3: 2812, 4: 43238, 5: 674624, 6: 11030083}
    },
    "Position 4": {
        "fen": "r3k2r/Pppp1ppp/1b3nbN/nP6/BBP1P3/q4N2/Pp1P2PP/R2Q1RK1 w kq - 0 1",
        "expected": {1: 6, 2: 264, 3: 9467, 4: 422333, 5: 15833292, 6: 706045033}
    },
    "Position 5": {
        "fen": "rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8",
        "expected": {1: 44, 2: 1486, 3: 62379, 4: 2103487, 5: 89941194, 6: -1}
    }
}

class Perft:
    def __init__(self):
        self.board = board.Board()

    def perft(self, depth):
        if depth == 0:
            return 1
        nodes = 0
        moves = movegen.generate_moves(self.board)
        for move in moves:
            self.board.apply_move(move)
            king = self.board.pieces[1-self.board.turn][KING]
            if not movegen._is_attacked(
                (king & -king).bit_length()-1,
                self.board.turn,
                self.board
            ):
                nodes += self.perft(depth-1)
            self.board.undo_move(move)
        return nodes

    def test(self):
        for pos in TEST_POSITIONS:
            print('\n' + '=' * 69)
            print(f"Position: {pos}", "\n")
            print("Depth |    Time    |    Nodes     |   Expected   |    NPS    | Status")
            print("------|------------|--------------|--------------|-----------|-------")

            total_nodes = 0
            self.board.set_fen(TEST_POSITIONS[pos]["fen"])
            for depth in range(1, 6):
                expected = TEST_POSITIONS[pos]["expected"][depth]

                start = time.time()
                nodes = self.perft(depth)
                elapsed = time.time() - start
                total_nodes += nodes

                print(f"{depth:>5} | {elapsed:>9.4f}s | "
                    f"{expected:>12,} | {nodes:>12,} | "
                    f"{total_nodes/elapsed:>9,.0f}", end=' | ')
                print("  PASS" if nodes == expected else "  FAIL")

p = Perft().test()