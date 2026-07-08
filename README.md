# FileFish

UCI-compliant chess engine written in pure Python

## Current Status

- [x] Bitboard representation
- [x] Pseudo-legal move generation (magic bitboards)
- [x] Incremental apply_move/undo_move
- [x] Perft validated against canonical values
- [ ] Evaluation
- [ ] Search (negamax + alpha-beta)
- [ ] UCI protocol

## Requirements

This project has no external dependencies beyond the standard library. However, the  use of PyPy3 is strongly recommended, as it provides a significant performance boost over CPython.

## Usage

```bash
git clone https://github.com/thercstk/filefish.git
cd filefish
pypy3 tests/perft.py
```

Keep in mind that the project is still in development, these are only raw move generation benchmarks.

## Architecture

| File | Role |
| ------------------ | ---------------------------- |
| `constants.py`     | General-purpose constants    |
| `board.py`         | Board state, apply/undo      |
| `attack_tables.py` | Precomputed attack tables    |
| `movegen.py`       | Pseudo-legal move generation |

## Inspiration

This engine was inspired by:

- **[The Chess Programming Wiki](https://chessprogramming.org)** — where all the techniques used in this project can be found
- **[Stockfish](https://github.com/official-stockfish/stockfish)** — as a design guide, even though this project follows a different implementation path
- **[Sunfish](https://github.com/thomasahle/sunfish) and [D-house](https://github.com/alvinypeng/d-house)** — mostly used as a reference point for performance comparisons