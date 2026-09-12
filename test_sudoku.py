"""
Tests for sudoku.py. The strongest checks here are round-trip and
self-verifying rather than hand-typed puzzle/solution pairs: generate a
puzzle, solve it, and confirm the result is a complete, rule-valid grid that
matches the known original solution — the actual DoD is "solver solves any
valid puzzle; generator output is always solvable", checked directly.
"""

import random
import unittest

import sudoku as sd


class TestPeers(unittest.TestCase):
    def test_every_cell_has_twenty_peers(self):
        # 8 (row) + 8 (col) + 4 (remaining box cells) = 20, with overlaps
        # already deduplicated by the set.
        for i in range(81):
            self.assertEqual(len(sd.PEERS[i]), 20)

    def test_peers_are_symmetric(self):
        for i in range(81):
            for p in sd.PEERS[i]:
                self.assertIn(i, sd.PEERS[p])


class TestIsValidBoard(unittest.TestCase):
    def test_empty_board_is_valid(self):
        self.assertTrue(sd.is_valid_board(sd.empty_board()))

    def test_duplicate_in_row_is_invalid(self):
        board = sd.empty_board()
        board[0] = 5
        board[1] = 5
        self.assertFalse(sd.is_valid_board(board))

    def test_duplicate_in_box_is_invalid(self):
        board = sd.empty_board()
        board[0] = 7  # (0,0)
        board[10] = 7  # (1,1) — same box, different row/col
        self.assertFalse(sd.is_valid_board(board))

    def test_same_value_in_non_conflicting_cells_is_valid(self):
        board = sd.empty_board()
        board[0] = 3  # (0,0)
        board[40] = 3  # (4,4) — different row, column, and box
        self.assertTrue(sd.is_valid_board(board))


class TestSolveRoundTrip(unittest.TestCase):
    """Generate a puzzle, solve it, verify the result is complete/valid and
    matches the known solution — this is the actual DoD, checked for real
    across all three difficulties rather than assumed."""

    def test_solver_recovers_the_known_solution_for_each_difficulty(self):
        rng = random.Random(2026)
        for difficulty in ["easy", "medium", "hard"]:
            puzzle, known_solution = sd.generate_puzzle(difficulty, rng=rng)
            solved = sd.solve(puzzle)
            self.assertIsNotNone(solved, f"{difficulty} puzzle was reported unsolvable")
            self.assertTrue(sd.is_complete_and_valid(solved))
            self.assertEqual(solved, known_solution)

    def test_solving_an_already_solved_board_returns_it_unchanged(self):
        rng = random.Random(3)
        solution = sd.generate_full_solution(rng)
        self.assertEqual(sd.solve(solution), solution)

    def test_solve_does_not_mutate_the_input(self):
        rng = random.Random(4)
        puzzle, _ = sd.generate_puzzle("easy", rng=rng)
        original = list(puzzle)
        sd.solve(puzzle)
        self.assertEqual(puzzle, original)


class TestUnsolvableBoardIsDetected(unittest.TestCase):
    def test_a_board_with_a_forced_contradiction_returns_none(self):
        # Box 0 (cells (0,0)-(2,2)) filled with 1-8, leaving (2,2) empty —
        # by box constraint (2,2) can only be 9. Row 2 also contains a 9
        # elsewhere (at (2,5)), so by row constraint (2,2) can't be 9
        # either. Zero remaining candidates: no valid board (0-9 duplicate)
        # exists yet, just a genuinely unsolvable configuration.
        board = sd.empty_board()
        box_values = [1, 2, 3, 4, 5, 6, 7, 8]
        box_cells = [0, 1, 2, 9, 10, 11, 18, 19]  # (0,0)..(1,2) row-major, excluding (2,2)=20
        for cell, value in zip(box_cells, box_values):
            board[cell] = value
        board[23] = 9  # (2,5) — same row as (2,2)=index 20
        self.assertIsNone(sd.solve(board))


class TestGeneratePuzzle(unittest.TestCase):
    def test_puzzle_has_a_unique_solution(self):
        rng = random.Random(11)
        puzzle, _ = sd.generate_puzzle("medium", rng=rng)
        self.assertEqual(sd.count_solutions(puzzle, limit=2), 1)

    def test_puzzle_clue_count_matches_difficulty_target_or_higher(self):
        rng = random.Random(12)
        for difficulty, target in sd.DIFFICULTY_CLUES.items():
            puzzle, _ = sd.generate_puzzle(difficulty, rng=rng)
            # Uniqueness can force stopping before reaching the target
            # exactly, but it should never remove MORE than the target.
            self.assertGreaterEqual(sd.clue_count(puzzle), target)

    def test_harder_difficulty_has_fewer_or_equal_clues_than_easier(self):
        rng = random.Random(13)
        easy, _ = sd.generate_puzzle("easy", rng=rng)
        hard, _ = sd.generate_puzzle("hard", rng=rng)
        self.assertGreaterEqual(sd.clue_count(easy), sd.clue_count(hard))

    def test_puzzle_is_a_subset_of_its_solution(self):
        rng = random.Random(14)
        puzzle, solution = sd.generate_puzzle("easy", rng=rng)
        for given, solved in zip(puzzle, solution):
            if given != 0:
                self.assertEqual(given, solved)

    def test_unknown_difficulty_raises(self):
        with self.assertRaises(ValueError):
            sd.generate_puzzle("impossible")


class TestManyGeneratedPuzzlesAreAlwaysSolvable(unittest.TestCase):
    """The literal DoD statement: generator output is ALWAYS solvable —
    checked across many independently seeded generations, not just one."""

    def test_ten_generated_puzzles_are_all_solvable_and_unique(self):
        for seed in range(10):
            rng = random.Random(seed)
            puzzle, solution = sd.generate_puzzle("hard", rng=rng)
            solved = sd.solve(puzzle)
            self.assertIsNotNone(solved)
            self.assertEqual(solved, solution)
            self.assertEqual(sd.count_solutions(puzzle, limit=2), 1)


class TestRenderBoard(unittest.TestCase):
    def test_render_includes_box_separators_and_dots_for_empty_cells(self):
        board = sd.empty_board()
        board[0] = 5
        text = sd.render_board(board)
        self.assertIn("5", text)
        self.assertIn(".", text)
        self.assertIn("------+-------+------", text)
        self.assertEqual(text.count("\n"), 10)  # 9 rows + 2 separators = 11 lines


if __name__ == "__main__":
    unittest.main()
