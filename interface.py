import PySimpleGUI as sg
import fibonacci
from threading import Timer


# build the window
def build_window(grid):
    return sg.Window('Fibonacci Grid').Layout(
        [[sg.Column(build_window_layout(grid), size=(1024, 768), scrollable=True)]]
    )


# build a window layout based on the fibonacci grid size
def build_window_layout(grid):
    layout = [
        [sg.Text('width'), sg.Input(grid.width, size=(10, 1)), sg.Text('height'), sg.Input(grid.height, size=(10, 1)),
         sg.Text('fibonacci length'), sg.Input(grid.fib_len, size=(10, 1)), sg.Button('Reset')],
    ]
    return layout + [[build_window_cell(x, y) for x in range(grid.width)] for y in range(grid.height)]


# build a single cell within the window layout
def build_window_cell(x, y):
    return sg.Button('', pad=(0, 0), size=(5, 1), key=f'{x}-{y}')


# get a window cell based on the location of a fibonacci grid cell
def get_window_cell(grid_cell):
    return window[f'{grid_cell.y}-{grid_cell.x}']


def set_color(cell, color):
    cell.update(button_color=('black', color))
    reset_color(cell)


def reset_color(cell, delay=1):
    if cell.Key in color_timers:
        color_timers[cell.Key].cancel()
        color_timers.pop(cell.Key)

    def reset(cell):
        cell.update(button_color=('black', '#405559'))
        if cell.Key in color_timers:
            color_timers.pop(cell.Key)

    color_timers[cell.Key] = Timer(delay, reset, [cell])
    color_timers[cell.Key].start()


# setup the window
sg.theme('DarkGrey6')
disable_timer = 0.3
grid = fibonacci.Fibonacci_Grid(10, 10)
window = build_window(grid)
color_timers = {}

# an event loop that runs the window until exited
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        # if window is closed, end program
        break
    elif event == 'Reset':
        # if reset button is pressed, build a new window
        try:
            new_width = max(1, int(values[0]))
            new_height = max(1, int(values[1]))
            new_fib_len = max(3, int(values[2]))
            assert new_height > 0
            assert new_fib_len > 0
            grid.reset(new_width, new_height, new_fib_len)
            window = build_window(grid)
        except ValueError:
            sg.popup('could not parse input')
    else:
        # if a button is pressed, handle the event
        xy = event.split('-')
        toggle_cells, reset_cells = grid.toggle(int(xy[0]), int(xy[1]))
        for cell in toggle_cells:
            cell_value = str(cell.value)
            window_cell = get_window_cell(cell)
            window_cell.update(text=cell_value)
            set_color(window_cell, 'yellow')
        for cell in reset_cells:
            window_cell = get_window_cell(cell)
            set_color(window_cell, 'green')
            window_cell.update('')

window.close()
