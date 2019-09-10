from random import randint

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.properties import BooleanProperty
from kivy.properties import NumericProperty
from kivy.properties import ObjectProperty
from kivy.graphics import Color, Rectangle
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.behaviors.button import ButtonBehavior


class Cell(ButtonBehavior, Label):
    """ This class represents a cell, that can be alive (state = True) or dead (state = False)"""

    cell_state = BooleanProperty(False)

    def __init__(self, index, state=False, **kwargs):
        ButtonBehavior.__init__(self, **kwargs)
        self.background_normal = ''
        self.text = ''
        self.index = index
        self.cell_state = state

    def toggle_state(self):
        self.cell_state = not self.cell_state

    def on_press(self):
        self.toggle_state()

    def on_cell_state(self, *args):
        self.draw()

    def on_size(self, *args):
        self.draw()

    def draw(self):
        self.canvas.clear()
        if self.cell_state is True:
            self.canvas.add(Color(0, 0, 1))
        else:
            self.canvas.add(Color(1, 1, 1))
        self.canvas.add(Rectangle(pos=self.pos, size=self.size))


class CellsGrid(FloatLayout):

    grid = ObjectProperty(None)
    line_length = NumericProperty(None)

    def __init__(self, engine, **kwargs):
        FloatLayout.__init__(self, **kwargs)
        self.engine = engine
        for cell in engine.cells:
            self.grid.add_widget(cell)
        self.line_length = engine.line_length
        self.engine.grid_ref = self

    def rebuild(self):
        self.grid.clear_widgets()
        for cell in self.engine.cells:
            self.grid.add_widget(cell)
        self.line_length = self.engine.line_length

    def on_size(self, *args):
        max_size = min(self.width, self.height)
        self.grid.size_hint_max = (max_size, max_size)
        if max_size > self.height:
            self.y += (max_size - self.height)


class Engine:

    cells = []
    line_length = 0
    grid_ref = None
    step_event = None
    toroidal_boundary = True

    def __init__(self, lines, cols):
        self.reset(lines, cols)

    @property
    def lines(self):
        return len(self.cells) // self.line_length

    @property
    def cols(self):
        return self.line_length

    def reset(self, lines, cols):
        self.cells.clear()
        for n in range(lines * cols):
            self.cells.append(Cell(n))
        self.line_length = cols
        if self.grid_ref is not None:
            self.grid_ref.rebuild()

    def step(self, dt):

        cells = self.cells
        cells_number = len(cells)
        line_length = self.line_length
        col_length = int(len(cells) / line_length)

        for cell in self.cells:
            # get cells state around and add it to get number of alive cells
            alive_surrounding = 0
            index = cell.index
            line_number = index // line_length
            col_number = index - line_number * line_length

            # Get cells indexes around
            upper_left_cell_index = index - line_length - 1
            upper_cell_index = index - line_length
            upper_right_cell_index = index - line_length + 1
            right_cell_index = index + 1
            lower_right_cell_index = index + line_length + 1
            lower_cell_index = index + line_length
            lower_left_cell_index = index + line_length - 1
            left_cell_index = index - 1

            # If toroidal coords is True, convert indexes, if not and out of area, set to None
            if self.toroidal_boundary and line_number == 0:
                upper_left_cell_index += cells_number
                upper_cell_index += cells_number
                upper_right_cell_index += cells_number
            elif line_number == 0:
                upper_left_cell_index = None
                upper_cell_index = None
                upper_right_cell_index = None

            if self.toroidal_boundary and line_number == col_length - 1:
                lower_left_cell_index -= cells_number
                lower_cell_index -= cells_number
                lower_right_cell_index -= cells_number
            elif line_number == col_length - 1:
                lower_left_cell_index = None
                lower_cell_index = None
                lower_right_cell_index = None

            if self.toroidal_boundary and col_number == 0:
                upper_left_cell_index += line_length
                left_cell_index += line_length
                lower_left_cell_index += line_length
            elif col_number == 0:
                upper_left_cell_index = None
                left_cell_index = None
                lower_left_cell_index = None

            if self.toroidal_boundary and col_number == line_length - 1:
                upper_right_cell_index -= line_length
                right_cell_index -= line_length
                lower_right_cell_index -= line_length
            elif col_number == line_length - 1:
                upper_right_cell_index = None
                right_cell_index = None
                lower_right_cell_index = None

            if upper_right_cell_index is not None and cells[upper_right_cell_index].cell_state is True:
                alive_surrounding += 1
            if right_cell_index is not None and cells[right_cell_index].cell_state is True:
                alive_surrounding += 1
            if lower_right_cell_index is not None and cells[lower_right_cell_index].cell_state is True:
                alive_surrounding += 1
            if lower_cell_index is not None and cells[lower_cell_index].cell_state is True:
                alive_surrounding += 1
            if lower_left_cell_index is not None and cells[lower_left_cell_index].cell_state is True:
                alive_surrounding += 1
            if left_cell_index is not None and cells[left_cell_index].cell_state is True:
                alive_surrounding += 1
            if upper_left_cell_index is not None and cells[upper_left_cell_index].cell_state is True:
                alive_surrounding += 1
            if upper_cell_index is not None and cells[upper_cell_index].cell_state is True:
                alive_surrounding += 1

            # Do the birth / survival calculation. Standard rule:
            # Surrounded by 2 or 3, survival OK, surrounded by 3, birth!
            if cell.cell_state is True:
                if alive_surrounding == 2 or alive_surrounding == 3:
                    cell.next_state = True
                else:
                    cell.next_state = False
            else:
                if alive_surrounding == 3:
                    cell.next_state = True
                else:
                    cell.next_state = False

        for cell in cells:
            cell.cell_state = cell.next_state

    def play(self):
        self.step_event = Clock.schedule_interval(self.step, .01)

    def stop(self):
        self.step_event.cancel()

    def randomize_cells_state(self):
        for cell in self.cells:
            cell.cell_state = bool(randint(0, 1))


class ControlZone(BoxLayout):
    area_cols = NumericProperty(0)
    area_lines = NumericProperty(0)
    toroidal = BooleanProperty(False)

    text_input_cols = ObjectProperty(None)
    text_input_lines = ObjectProperty(None)
    option_toroidal_checkbox = ObjectProperty(None)

    def __init__(self, engine, **kwargs):
        BoxLayout.__init__(self, **kwargs)
        self.engine = engine
        self.area_cols = engine.cols
        self.area_lines = engine.lines
        self.option_toroidal_checkbox.bind(active=self.on_option_toroidal)

    def reset_engine(self):
        self.area_cols = int(self.text_input_cols.text)
        self.area_lines = int(self.text_input_lines.text)
        self.engine.reset(self.area_lines, self.area_cols)

    def engine_step(self):
        self.engine.toroidal_boundary = self.toroidal
        self.engine.step(None)

    def play(self):
        self.engine.toroidal_boundary = self.toroidal
        self.engine.play()

    def engine_randomize_cells(self):
        self.engine.randomize_cells_state()

    def on_option_toroidal(self, widget, value):
        self.toroidal = value


class FullWindow(BoxLayout):

    def __init__(self, **kwargs):
        BoxLayout.__init__(self, **kwargs)
        self.orientation = 'horizontal'
        self.engine = Engine(10, 10)
        self.add_widget(CellsGrid(self.engine))
        self.add_widget(ControlZone(self.engine))


class GameOfLifeApp(App):
    def build(self):
        return FullWindow()


if __name__ == '__main__':
    GameOfLifeApp().run()
