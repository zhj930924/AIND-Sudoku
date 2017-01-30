from itertools import combinations

# Define constants
ROWS = 'ABCDEFGHI'
COLS = '123456789'

assignments = []


def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values


def cross(a, b):
    """Cross product of elements in a and elements in b."""
    return [s + t for s in a for t in b]


def combine(a, b):
    """Elementwisely combine a and b"""
    return [x + y for x, y in list(zip(a, b))]


# Define global variables
BOXES = cross(ROWS, COLS)
ROW_UNITS = [cross(r, COLS) for r in ROWS]
COLUMN_UNITS = [cross(ROWS, c) for c in COLS]
SQUARE_UNITS = [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')]
DIAGONAL_UNITS = [combine(ROWS, COLS), combine(ROWS, COLS[::-1])]

UNITLIST = ROW_UNITS + COLUMN_UNITS + SQUARE_UNITS + DIAGONAL_UNITS
UNITS = dict((s, [u for u in UNITLIST if s in u]) for s in BOXES)
PEERS = dict((s, set(sum(UNITS[s], [])) - {s}) for s in BOXES)


def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The BOXES, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value
            will be '123456789'.
    """
    chars = []
    digits = '123456789'
    for c in grid:
        if c in digits:
            chars.append(c)
        if c == '.':
            chars.append(digits)
    assert len(chars) == 81
    return dict(zip(BOXES, chars))


def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    if values:
        width = 1 + max(len(values[s]) for s in BOXES)
        line = '+'.join(['-' * (width * 3)] * 3)
        for r in ROWS:
            print(''.join(values[r + c].center(width) + ('|' if c in '36' else '')
                          for c in COLS))
            if r in 'CF': print(line)
        print()
    else:
        print("""
      _____
     / ____|
    | (___   ___  _ __ _ __ _   _
     \___ \ / _ \| '__| '__| | | |
     ____) | (_) | |  | |  | |_| |
    |_____/ \___/|_|  |_|   \__, |
                             __/ |
                            |___/
        """)
        print("The agent can't solve this problem.")
        return False


def get_values_set(values, boxes):
    """Helper: Get a set of unique values from specified boxes"""
    return set(''.join([values[box] for box in boxes]))


def set_to_value(s):
    """Helper: Get sudoku value from a set"""
    return ''.join(sorted(s))


def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from PEERS.
    """
    # Find all instances of naked twins
    for unit in UNITLIST:
        unsolved = [box for box in unit if len(values[box]) > 1]
        pairs = list(combinations(unsolved, 2))
        for pair in pairs:
            pair_digits = get_values_set(values, pair)
            if len(pair_digits) == 2:
                strippers = set(unsolved) - set(pair)
                for stripper in strippers:
                    clothes1, clothes2 = pair_digits
                    naked = values[stripper].replace(clothes1, '').replace(clothes2, '')
                    values = assign_value(values, stripper, naked)
    return values


def hidden_twins(values):
    """Eliminate values using the hidden twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the hidden twins eliminated from PEERS.
    """
    # Find all instances of hidden twins

    for unit in UNITLIST:
        unsolved = [box for box in unit if len(values[box]) > 1]
        pairs = list(combinations(unsolved, 2))
        for pair in pairs:
            twin1, twin2 = pair
            pair_digits = set(values[twin1]) & set(values[twin2])
            others = set(unsolved) - set(pair)
            others_digits = get_values_set(values, others)

            # Identify the hidden twin
            if len(pair_digits) > 2 and len(pair_digits - others_digits) == 2:
                twin_value = set_to_value(pair_digits - others_digits)
                values = assign_value(values, twin1, twin_value)
                values = assign_value(values, twin2, twin_value)
    return values


def eliminate(values):
    """
    Go through all the boxes, and whenever there is a box with a value, eliminate this value from
    the values of all its peers.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in PEERS[box]:
            eliminated = values[peer].replace(digit, '')
            values = assign_value(values, peer, eliminated)
    return values


def only_choice(values):
    """
    Go through all the UNITS, and whenever there is a unit with a value that only fits in one
    box, assign the value to this box.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    for unit in UNITLIST:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                values = assign_value(values, dplaces[0], digit)
    return values


def reduce_puzzle(values):
    """
    Iterate eliminate() and only_choice(). If at some point, there is a box with no available
    values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same, return the sudoku.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    stalled = False
    while not stalled:
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

        values = eliminate(values)

        values = only_choice(values)

        values = eliminate(values)

        values = naked_twins(values)

        values = eliminate(values)

        values = hidden_twins(values)

        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        stalled = solved_values_before == solved_values_after
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values


def search(values):
    """Using depth-first search and propagation, create a search tree and solve the sudoku."""

    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values is False:
        return False
    if all(len(values[s]) == 1 for s in BOXES):
        return values

    # Choose one of the unfilled squares with the fewest possibilities
    n, s = min((len(values[s]), s) for s in BOXES if len(values[s]) > 1)
    # Now use recursion to solve each one of the resulting sudokus, and if one returns a value (
    # not False), return that answer!
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt


def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52
            .............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    values = grid_values(grid)
    return search(values)


if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52' \
                       '.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments

        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print(
            'We could not visualize your board due to a pygame issue. Not a problem! It is not a '
            'requirement.')
