# Sudoku Solver

A flexible 9×9 Sudoku solver combining the power of Prolog's constraint logic programming with a user-friendly Python interface. Originally developed for the Logic Applied to Computing course at UFPB (Federal University of Paraíba, Brazil), this project demonstrates practical applications of declarative programming and automated reasoning.

## Features

- **Multiple Input Formats**: Accepts various input styles and preserves the original format in output
  - Compact: `123456789`
  - Spaced: `1 2 3 4 5 6 7 8 9`
  - Comma-separated: `1,2,3,4,5,6,7,8,9`
  - Dots for empty cells: `..3.2.6..`
  - Zeros for empty cells: `003020600`
  - Mixed formats: `1 2,3 4 5,6 7 8 9`

- **Flexible Usage**:
  - Interactive command-line mode
  - File-based input/output
  - Direct Prolog interface with example puzzles

- **Efficient Solving**: Uses SWI-Prolog's CLP(FD) library for constraint-based solving with backtracking

## Requirements

- **SWI-Prolog**: Version 7.0 or higher
  ```bash
  # Ubuntu/Debian
  sudo apt-get install swi-prolog

  # macOS
  brew install swi-prolog

  # Fedora
  sudo dnf install pl
  ```

- **Python 3.6+**: For the wrapper interface (sudoku_solver.py)

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/AlbertNewton/sudoku-solver.git
   cd sudoku-solver
   ```

2. Verify SWI-Prolog installation:
   ```bash
   swipl --version
   ```

## Usage

### Python Wrapper (Recommended)

**Interactive Mode**:
```bash
python3 sudoku_solver.py
```
You'll be prompted to enter the puzzle line by line.

**From File**:
```bash
python3 sudoku_solver.py --input puzzle.txt
```

**Save to File**:
```bash
python3 sudoku_solver.py --input puzzle.txt --output solution.txt
```

**Command-line Options**:
- `--input, -i`: Input file containing the puzzle
- `--output, -o`: Output file for the solution

### Direct Prolog Interface

Run the interactive Prolog menu:
```bash
swipl atva02.pl
```

The menu offers:
1. Solve example puzzles (easy, medium, hard)
2. Enter a puzzle manually
3. About information
0. Exit

### Programmatic Prolog Usage

```prolog
swipl -g "puzzle(easy, B), sudoku(B), display_board(B), halt" atva02.pl
```

## Input Format Examples

The solver accepts various formats per line. Comments (lines starting with `#`, `%`, or `//`) are ignored.

**Example 1: Compact with zeros**
```
003020600
900305001
001806400
008102900
700000008
006708200
002609500
800203009
005010300
```

**Example 2: Dots for empty cells**
```
..3.2.6..
9..3.5..1
..1.8.6.4..
..8.1.2.9..
7........8
..6.7.8.2..
..2.6.9.5..
8..2.3..9
..5..1..3..
```

**Example 3: Spaced format**
```
0 0 3 0 2 0 6 0 0
9 0 0 3 0 5 0 0 1
0 0 1 8 0 6 4 0 0
0 0 8 1 0 2 9 0 0
7 0 0 0 0 0 0 0 8
0 0 6 7 0 8 2 0 0
0 0 2 6 0 9 5 0 0
8 0 0 2 0 3 0 0 9
0 0 5 0 1 0 3 0 0
```

The output format will match the input format automatically!

## How It Works

### Prolog Core (atva02.pl)

The solver uses Constraint Logic Programming over Finite Domains (CLP(FD)):

1. **Domain Definition**: Each cell must contain a digit from 1 to 9
2. **Row Constraints**: All cells in a row must be distinct
3. **Column Constraints**: All cells in a column must be distinct
4. **Region Constraints**: All cells in each 3×3 block must be distinct
5. **Labeling**: Find values that satisfy all constraints using backtracking

Key predicates:
- `sudoku/1`: Main solver predicate
- `valid_rows/1`, `valid_columns/1`, `valid_regions/1`: Constraint validators
- `display_board/1`: Pretty-prints the board

### Python Wrapper (sudoku_solver.py)

The Python script provides:
- **Format Detection**: Identifies and records the input format of each line
- **Parser**: Normalizes various input formats into a standard board representation
- **Prolog Interface**: Generates Prolog goals and executes SWI-Prolog as a subprocess
- **Format Preservation**: Reconstructs output in the original input format

## Project Structure

```
sudoku-solver/
├── atva02.pl           # Prolog solver with CLP(FD)
├── sudoku_solver.py    # Python wrapper and CLI interface
├── LICENSE             # MIT License
└── README.md           # This file
```

## Technical Details

**Algorithm**: Constraint propagation with backtracking search
- Uses SWI-Prolog's `clpfd` library
- First-fail strategy for efficient variable assignment
- Guarantees finding a solution if one exists

**Complexity**:
- Worst case: $O(9^n)$ where $n$ is the number of empty cells
- Typical performance: < 1 second for most puzzles due to constraint propagation

## Example Session

```bash
$ python3 sudoku_solver.py
Enter the Sudoku puzzle (9 lines).
Supported formats per line:
  • 123456789
  • 1 2 3 4 5 6 7 8 9
  • 1,2,3,4,5,6,7,8,9
  • ..3.2.6..
  • 003020600
Lines starting with # are ignored.

Line 1: ..3.2.6..
Line 2: 9..3.5..1
Line 3: ..1.8.6.4..
Line 4: ..8.1.2.9..
Line 5: 7........8
Line 6: ..6.7.8.2..
Line 7: ..2.6.9.5..
Line 8: 8..2.3..9
Line 9: ..5..1..3..
Solving...
483921657
967345821
251876493
548132976
729564138
136798245
372689514
814253769
695417382
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

*Originally developed as a final project for Logic Applied to Computing course at UFPB, 2026.*