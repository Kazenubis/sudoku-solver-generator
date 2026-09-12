# Sudoku Solver + Generator

A from-scratch 9x9 Sudoku engine: a backtracking solver with a
minimum-remaining-values heuristic, and a puzzle generator that digs holes
out of a random full solution while checking uniqueness after every
removal, at three difficulty levels.

Real output — a generated "hard" puzzle, then the same board solved:

```
Puzzle (hard, 26 clues):
. . . | . . . | . 9 .
3 7 6 | . . 9 | . 2 5
. . . | 5 4 . | . . .
------+-------+------
4 . 2 | . 3 . | . 8 1
6 . . | . . . | . . .
. . . | . . 4 | 7 . 9
------+-------+------
. . . | 9 . . | . . .
9 4 . | . . . | . 3 .
8 . . | . . . | 9 1 6

Solved:
2 5 4 | 3 6 7 | 1 9 8
3 7 6 | 1 8 9 | 4 2 5
1 8 9 | 5 4 2 | 6 7 3
------+-------+------
4 9 2 | 7 3 6 | 5 8 1
6 1 7 | 8 9 5 | 3 4 2
5 3 8 | 2 1 4 | 7 6 9
------+-------+------
7 6 3 | 9 2 1 | 8 5 4
9 4 1 | 6 5 8 | 2 3 7
8 2 5 | 4 7 3 | 9 1 6
```

## Features

- Backtracking solver with a **minimum-remaining-values (MRV)** heuristic —
  always branches on the empty cell with the fewest legal candidates first,
  which finds dead ends immediately instead of after a long, pointless dive
- Generator digs holes out of a randomly built full solution, checking
  `count_solutions(puzzle, limit=2) == 1` after every removal and reverting
  any removal that would break uniqueness — every generated puzzle has
  exactly one solution, not just "a" solution
- Three difficulty levels (`easy` / `medium` / `hard`) targeting 40 / 32 /
  26 clues respectively — uniqueness can force stopping slightly above a
  target, but never below it
- `count_solutions` stops counting as soon as it hits the limit, so proving
  "unique" never means fully enumerating every possible completion of a
  near-empty grid

## Tech Stack

Python 3, standard library only

## Getting Started

```bash
git clone https://github.com/Kazenubis/sudoku-solver-generator.git
cd sudoku-solver-generator
python3 sudoku.py --difficulty hard --seed 7
```

Run the tests:

```bash
python3 -m unittest test_sudoku.py -v
```

## What I Learned

The solver on its own is a straightforward classic backtracker, but the
generator taught me the actually interesting part: "always solvable" is a
much weaker guarantee than it sounds, because a randomly-dug-out puzzle can
easily have *multiple* valid solutions — which still counts as "solvable"
but isn't a real Sudoku puzzle in the sense anyone means it. Enforcing
uniqueness meant `count_solutions` needs to be able to stop the instant it
finds a *second* solution rather than exhaustively searching — otherwise
checking uniqueness after every single hole dug would be far too slow to
generate a puzzle in reasonable time, especially early on when the grid is
still nearly full and has very few empty cells to branch on.

The MRV heuristic turned out to matter more than I expected for something
this small: without it (branching on the first empty cell found, top-left
to bottom-right) both solving and the uniqueness checks during generation
were noticeably slower, since a bad early branch could wander deep into
constraint space before hitting the contradiction that MRV would have
caught in the very next call by picking the most-constrained cell first.
