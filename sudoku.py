"""
Sudoku Solver + Generator — a from-scratch 9x9 Sudoku engine. Solves any
valid puzzle via backtracking with a minimum-remaining-values (MRV)
heuristic, and generates puzzles at three difficulty levels by digging
holes out of a randomly generated full solution while checking that the
puzzle still has exactly one solution after each removal.

Board representation: a flat list of 81 ints, row-major (index = row*9 +
col), 0 meaning "empty".
"""

import argparse
import random


def _peers_for(index):
    row, col = divmod(index, 9)
    box_row, box_col = (row // 3) * 3, (col // 3) * 3
    peers = set()
    for c in range(9):
        peers.add(row * 9 + c)
    for r in range(9):
        peers.add(r * 9 + col)
    for r in range(box_row, box_row + 3):
        for c in range(box_col, box_col + 3):
            peers.add(r * 9 + c)
    peers.discard(index)
    return peers


PEERS = [_peers_for(i) for i in range(81)]

DIFFICULTY_CLUES = {"easy": 40, "medium": 32, "hard": 26}


def empty_board():
    return [0] * 81


def is_valid_board(board):
    """No duplicate value among any cell's peers — doesn't check
    completeness, just that no rule is currently broken."""
    for i in range(81):
        v = board[i]
        if v == 0:
            continue
        for p in PEERS[i]:
            if board[p] == v:
                return False
    return True


def is_complete_and_valid(board):
    return 0 not in board and is_valid_board(board)


def _candidates(board, index):
    used = {board[p] for p in PEERS[index] if board[p] != 0}
    return [v for v in range(1, 10) if v not in used]


def _find_empty_mrv(board):
    """Picks the empty cell with the fewest remaining candidates (minimum
    remaining values) — this is what keeps backtracking fast: a cell with 0
    candidates is found and fails immediately instead of after a long dive,
    and cells with 1 candidate get resolved first, propagating constraints."""
    best_index, best_candidates = None, None
    for i in range(81):
        if board[i] == 0:
            candidates = _candidates(board, i)
            if best_candidates is None or len(candidates) < len(best_candidates):
                best_index, best_candidates = i, candidates
                if len(candidates) == 0:
                    return best_index, best_candidates
    return best_index, best_candidates


def _backtrack(board, rng=None):
    index, candidates = _find_empty_mrv(board)
    if index is None:
        return True  # no empty cells left — solved
    if not candidates:
        return False  # dead end
    values = list(candidates)
    if rng is not None:
        rng.shuffle(values)
    for v in values:
        board[index] = v
        if _backtrack(board, rng):
            return True
        board[index] = 0
    return False


def solve(board):
    """Returns a solved copy of `board`, or None if it has no solution.
    Does not mutate the input."""
    working = list(board)
    if _backtrack(working):
        return working
    return None


def count_solutions(board, limit=2):
    """Counts solutions up to `limit` (stops early once the limit is hit —
    generation only ever needs to know "is it exactly 1", so it never needs
    to enumerate every solution of an under-constrained board)."""
    working = list(board)
    count = 0

    def helper():
        nonlocal count
        if count >= limit:
            return
        index, candidates = _find_empty_mrv(working)
        if index is None:
            count += 1
            return
        if not candidates:
            return
        for v in candidates:
            working[index] = v
            helper()
            working[index] = 0
            if count >= limit:
                return

    helper()
    return count


def generate_full_solution(rng=None):
    """Generates a random, fully solved, valid 9x9 grid by backtracking
    from empty with candidate order shuffled at each cell."""
    rng = rng or random.Random()
    board = empty_board()
    ok = _backtrack(board, rng=rng)
    if not ok:
        raise RuntimeError("Failed to generate a full solution (should not happen)")
    return board


def generate_puzzle(difficulty="medium", rng=None):
    """Generates a puzzle with a unique solution at the given difficulty by
    digging holes out of a random full solution: cells are zeroed in random
    order, but a removal is reverted whenever it would leave more than one
    solution. Returns (puzzle, solution)."""
    rng = rng or random.Random()
    if difficulty not in DIFFICULTY_CLUES:
        raise ValueError(f"Unknown difficulty {difficulty!r} — choose from {list(DIFFICULTY_CLUES)}")

    solution = generate_full_solution(rng)
    puzzle = list(solution)
    target_clues = DIFFICULTY_CLUES[difficulty]

    cell_order = list(range(81))
    rng.shuffle(cell_order)

    clues_remaining = 81
    for index in cell_order:
        if clues_remaining <= target_clues:
            break
        backup = puzzle[index]
        puzzle[index] = 0
        if count_solutions(puzzle, limit=2) != 1:
            puzzle[index] = backup  # removal broke uniqueness — keep the clue
        else:
            clues_remaining -= 1

    return puzzle, solution


def render_board(board):
    lines = []
    for r in range(9):
        if r % 3 == 0 and r != 0:
            lines.append("------+-------+------")
        cells = []
        for c in range(9):
            v = board[r * 9 + c]
            cells.append(str(v) if v != 0 else ".")
            if c % 3 == 2 and c != 8:
                cells.append("|")
        lines.append(" ".join(cells))
    return "\n".join(lines)


def clue_count(board):
    return sum(1 for v in board if v != 0)


def main():
    parser = argparse.ArgumentParser(description="Sudoku Solver + Generator")
    parser.add_argument("--difficulty", choices=list(DIFFICULTY_CLUES), default="medium")
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()

    rng = random.Random(args.seed)
    puzzle, solution = generate_puzzle(args.difficulty, rng=rng)

    print(f"Puzzle ({args.difficulty}, {clue_count(puzzle)} clues):")
    print(render_board(puzzle))
    print()
    solved = solve(puzzle)
    print("Solved:" if solved else "No solution found (unexpected!):")
    print(render_board(solved if solved else puzzle))


if __name__ == "__main__":
    main()
