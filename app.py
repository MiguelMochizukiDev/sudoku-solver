import streamlit as st
import subprocess
import copy
import os

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Sudoku Solver", page_icon="🧩", layout="centered")

st.title("🧩 Sudoku Solver")
st.caption("Powered by SWI-Prolog CLP(FD)")

# ── Session state ─────────────────────────────────────────────────────────────
if "board" not in st.session_state:
    st.session_state.board = [[0] * 9 for _ in range(9)]
if "solution" not in st.session_state:
    st.session_state.solution = None
if "error" not in st.session_state:
    st.session_state.error = None
if "cell_errors" not in st.session_state:
    st.session_state.cell_errors = []

# ── Helpers ───────────────────────────────────────────────────────────────────

def board_from_session() -> tuple[list[list[int]], list[str]]:
    """
    Read current 9x9 board from session state widget keys.

    Returns:
        (board, invalid_cells) — board is a 9x9 list of ints (0 = empty),
        invalid_cells is a list of cell labels with bad input.
    """
    board = []
    invalid_cells = []
    for r in range(9):
        row = []
        for c in range(9):
            val = st.session_state.get(f"cell_{r}_{c}", "")
            if isinstance(val, str) and val.strip() == "":
                row.append(0)
            elif isinstance(val, str) and val.isdigit() and 1 <= int(val) <= 9:
                row.append(int(val))
            else:
                row.append(0)
                invalid_cells.append(f"R{r+1}C{c+1}")
        board.append(row)
    return board, invalid_cells


def validate_cell_input(key: str) -> None:
    """
    on_change callback: rejects non-digit or out-of-range values by clearing
    the cell and recording the error in session state (rendered in main flow).
    """
    val = st.session_state.get(key, "")
    if val and (not val.isdigit() or not 1 <= int(val) <= 9):
        st.session_state[key] = ""
        st.session_state.cell_errors.append(key)


def _load_puzzle(difficulty: str) -> None:
    """Fetch a puzzle by difficulty and populate session state."""
    puzzle, err = get_puzzle_from_prolog(difficulty)
    if puzzle:
        st.session_state.board = copy.deepcopy(puzzle)
        st.session_state.solution = None
        st.session_state.error = None
        for r in range(9):
            for c in range(9):
                val = puzzle[r][c]
                st.session_state[f"cell_{r}_{c}"] = str(val) if val != 0 else ""
    else:
        st.session_state.error = f"Failed to load {difficulty} puzzle. {err or ''}"


def _clear_board() -> None:
    """Reset the entire board to blank state."""
    st.session_state.board = [[0] * 9 for _ in range(9)]
    st.session_state.solution = None
    st.session_state.error = None
    st.session_state.cell_errors = []
    for r in range(9):
        for c in range(9):
            st.session_state[f"cell_{r}_{c}"] = ""


# ── Prolog interface ──────────────────────────────────────────────────────────

_SOLVER_DIR = os.path.dirname(os.path.abspath(__file__))


def _run_prolog(goal: str, timeout: int = 10) -> tuple[str | None, str | None]:
    """
    Run a SWI-Prolog goal against solver.pl.

    Returns:
        (stdout, error_message) — stdout is None on failure.
    """
    try:
        result = subprocess.run(
            ["swipl", "-q", "-g", goal, "-t", "halt", "solver.pl"],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=_SOLVER_DIR,
        )
        if result.returncode != 0:
            msg = (result.stdout + result.stderr).strip()
            return None, msg or "Prolog process exited with an error."
        return result.stdout, None
    except subprocess.TimeoutExpired:
        return None, "Prolog solver timed out."
    except FileNotFoundError:
        return None, "SWI-Prolog not found. Make sure 'swipl' is installed."
    except Exception as exc:
        return None, str(exc)


def _parse_board_lines(output: str) -> list[list[int]] | None:
    """Parse 9 lines of '[n,n,n,...]' Prolog output into a 9x9 list."""
    board = []
    for line in output.strip().splitlines():
        line = line.strip().strip("[]")
        if not line:
            continue
        try:
            cells = [int(x.strip()) for x in line.split(",")]
        except ValueError:
            return None
        if len(cells) == 9:
            board.append(cells)
    return board if len(board) == 9 else None


def get_puzzle_from_prolog(difficulty: str) -> tuple[list[list[int]] | None, str | None]:
    """
    Fetch a pre-built puzzle from Prolog.

    Returns:
        (board, error) — board is 9x9 with 0 for empty cells.
    """
    stdout, err = _run_prolog(f"print_puzzle_as_list({difficulty})", timeout=5)
    if stdout is None:
        return None, err
    board = _parse_board_lines(stdout)
    if board is None:
        return None, "Could not parse puzzle output from Prolog."
    return board, None


def solve_prolog(board: list[list[int]]) -> tuple[list[list[int]] | None, str | None]:
    """
    Solve a Sudoku board via solver.pl.

    Returns:
        (solution, error) — solution is 9x9 or None on failure.
    """
    rows = []
    for row in board:
        cells = ",".join(str(v) if v != 0 else "_" for v in row)
        rows.append(f"[{cells}]")
    board_str = "[" + ",".join(rows) + "]"

    stdout, err = _run_prolog(f"solve_and_print({board_str})", timeout=10)
    if stdout is None:
        return None, err

    solution = _parse_board_lines(stdout)
    if solution is None:
        return None, "Could not parse solution output from Prolog."
    return solution, None


# ── UI ────────────────────────────────────────────────────────────────────────

# Top control bar
col_clear, col_easy, col_medium, col_hard, col_solve = st.columns(5)

with col_clear:
    if st.button("🗑️ Clear", use_container_width=True):
        _clear_board()
        st.rerun()

# Difficulty buttons — single loop, no duplication
for col, (label, difficulty) in zip(
    [col_easy, col_medium, col_hard],
    [("Easy", "easy"), ("Medium", "medium"), ("Hard", "hard")],
):
    with col:
        if st.button(label, use_container_width=True):
            _load_puzzle(difficulty)
            st.rerun()

with col_solve:
    solve_clicked = st.button("▶ Solve", use_container_width=True, type="primary")

st.divider()

# ── Grid ──────────────────────────────────────────────────────────────────────
st.markdown("**Enter your puzzle** — click on any cell to edit (1–9, or leave empty):")

st.markdown("""
<style>
div[data-testid="column"] { padding: 0 !important; }
.stTextInput > div > div > input {
    text-align: center;
    font-size: 20px;
    font-weight: 600;
    padding: 12px 0;
    height: 52px;
}
</style>
""", unsafe_allow_html=True)

# Flush cell-level validation errors from previous run
if st.session_state.cell_errors:
    bad = ", ".join(st.session_state.cell_errors)
    st.warning(f"Only digits 1–9 are allowed. Cleared: {bad}")
    st.session_state.cell_errors = []

for r in range(9):
    cols = st.columns([1] * 9, gap="small")
    for c in range(9):
        cell_key = f"cell_{r}_{c}"
        with cols[c]:
            # Initialise cell on first render
            if cell_key not in st.session_state:
                v = st.session_state.board[r][c]
                st.session_state[cell_key] = str(v) if v != 0 else ""

            if st.session_state.solution:
                val = st.session_state.solution[r][c]
                is_clue = st.session_state.board[r][c] != 0
                color = "#1e3a5f" if is_clue else "#16a34a"
                st.markdown(
                    f"<div style='text-align:center;font-size:24px;"
                    f"font-weight:700;color:{color};padding:14px 0'>{val}</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.text_input(
                    label=f"r{r}c{c}",
                    key=cell_key,
                    label_visibility="collapsed",
                    max_chars=1,
                    placeholder="·",
                    on_change=validate_cell_input,
                    args=(cell_key,),
                )

    # Visual row separators
    if r in {2, 5}:
        st.markdown("<hr style='margin:8px 0;border:1px solid #333'>", unsafe_allow_html=True)
    elif r < 8:
        st.markdown("<div style='margin:4px 0'></div>", unsafe_allow_html=True)

st.divider()

# "Try Again" button — only shown when a solution is on screen
if st.session_state.solution:
    if st.button("🔄 Try Again"):
        st.session_state.solution = None
        st.session_state.error = None
        st.rerun()

# ── Solve logic ───────────────────────────────────────────────────────────────
if solve_clicked:
    current_board, invalid_cells = board_from_session()

    if invalid_cells:
        st.warning(f"Invalid input in cells: {', '.join(invalid_cells)}. Only digits 1–9 are allowed.")
        st.stop()

    if all(v == 0 for row in current_board for v in row):
        st.warning("Please enter at least one clue.")
        st.stop()

    st.session_state.board = current_board
    st.session_state.solution = None
    st.session_state.error = None

    solution, err = solve_prolog(current_board)
    if solution:
        st.session_state.solution = solution
    else:
        st.session_state.error = f"Could not solve puzzle. {err or 'No solution exists.'}"

    st.rerun()

# ── Status messages ───────────────────────────────────────────────────────────
if st.session_state.solution:
    st.success("✅ Solved! Click 'Try Again' to edit the puzzle.")

if st.session_state.error:
    st.error(st.session_state.error)