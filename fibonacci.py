import numpy as np
import itertools


# a single cell in a fibonacci grid
# hold the data such as the current fibonacci value and how to calculate the successor
class Fibonacci_Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.reset()

    def update(self):
        self.value = self.value + 1
        if self.value >= self.cur:
            self.next()

    # update cell to the next fibonacci value
    def next(self):
        tmp = self.cur
        self.cur = self.successor()
        self.prev = tmp

    def reset(self):
        self.prev = 0  # the current fibonacci lower bound
        self.cur = 1  # the current fibonacci upper bound
        self.value = 0  # the numerical value within the cell

    def successor(self):
        if self.value == self.prev and self.value != 1:
            return self.cur
        return self.cur + self.prev

    def predecessor(self):
        if self.value == self.prev:
            return self.cur - self.prev
        return self.prev

    def __str__(self):
        return str(self.fib)


def dummy_cell():
    return Fibonacci_Cell(-1, -1)


# is current value a fibonacci successor of the next?
# Note, edge cases added for two 1's following each other in succession
# e.g. 1-1 is a fibonacci series, but 1-1-1 is not
def is_successor(cur, next, prev=-1):
    if cur.value <= 0 or next.value <= 0:
        return False
    a = cur.value == next.successor() and cur.predecessor() == next.value
    b = cur.value == 1 and next.value == 1 and prev.value != 1
    return a or b


# for every element in the values list, how long is the successive series it is a part of
def succession_length(cells, fib_len):
    i = 0
    lengths = [0] * len(cells)
    while i < len(cells) - (fib_len - 1):
        succession_len = 1
        for j in range(i, len(cells)):
            cur_value = cells[j]
            prev_value = np.concatenate(([dummy_cell()], cells))[j]
            next_value = np.concatenate((cells, [dummy_cell()]))[j + 1]
            if is_successor(cur_value, next_value, prev_value):
                succession_len = succession_len + 1
            else:
                break
        for k in range(i, j + 1):
            lengths[k] = succession_len
        i = j + 1
    return lengths


# for every fibonacci cell, determine whether the value needs to be reset
def toggle_n_succession(cells, fib_len):
    lengths = zip(cells,
                  [length >= fib_len for length in succession_length(cells, fib_len)],
                  list(reversed([length >= fib_len for length in succession_length(list(reversed(cells)), fib_len)])))
    return [v[0] for v in lengths if v[1] or v[2]]


# a fibonacci grid holds width x height fibonacci cells
class Fibonacci_Grid:
    def __init__(self, width=50, height=50, fib_len=5):
        self.reset(width, height, fib_len)

    def __getitem__(self, keys):
        return self.grid[keys[1]][keys[0]]

    def reset(self, width=50, height=50, fib_len=5):
        self.width = width
        self.height = height
        self.fib_len = fib_len
        self.grid = np.array([[Fibonacci_Cell(x, y) for y in range(self.height)] for x in range(self.width)])

    def get_col(self, col):
        return self.grid[col, :]

    def get_row(self, row):
        return self.grid[:, row]

    # add 1 to every cell in a (row, column).
    # if this leads to a series of n {= self.fib_len} successive fibonacci digits
    # then reset all those digits
    def toggle(self, row_index, col_index):
        # update all cell values
        row = self.get_row(row_index)
        col = self.get_col(col_index)
        toggle_cells = np.concatenate((row, np.delete(col, row_index)))
        [cell.update() for cell in toggle_cells]

        # find all orthogonal series to check for a reset
        row_orthogonal = [self.grid[cell.x, max(0, (cell.y - self.fib_len)):min(self.width, cell.y + self.fib_len + 1)]
                          for cell in row]
        col_orthogonal = [self.grid[max(0, (cell.x - self.fib_len)):min(self.height, cell.x + self.fib_len + 1), cell.y]
                          for cell in col]

        # find all cells to check for a reset within the orthogonal series
        reset_cells = [toggle_n_succession(series, self.fib_len) for series in row_orthogonal] + \
                      [toggle_n_succession(series, self.fib_len) for series in col_orthogonal] + \
                      [toggle_n_succession(list(row), self.fib_len)] + \
                      [toggle_n_succession(list(col), self.fib_len)]

        # reset the flagged cells
        reset_cells = list(itertools.chain.from_iterable(reset_cells))
        [cell.reset() for cell in reset_cells]

        # return the cells that were toggled, and the cells that were reset
        return list(toggle_cells), list(reset_cells)

    def __str__(self):
        return '\n'.join([' '.join([str(cell) for cell in self.get_col(row_index)]) for row_index in range(self.width)])
