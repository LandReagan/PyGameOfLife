from random import randint

from kivy.app import App
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
        print(str(self.index) + ': ' + str(self.cell_state))

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

    def __init__(self, cells, line_length, **kwargs):
        FloatLayout.__init__(self, **kwargs)
        for cell in cells:
            self.grid.add_widget(cell)
        self.line_length = line_length

    def on_size(self, *args):
        max_size = min(self.width, self.height)
        self.grid.size_hint_max = (max_size, max_size)
        if max_size > self.height:
            self.y += (max_size - self.height)


class Engine:

    cells = []
    line_length = 0

    def __init__(self, lines, cols):
        for n in range(lines * cols):
            self.cells.append(Cell(n))
        self.line_length = cols

    def step(self):
        print('Step!')
        for cell in self.cells:
            # get cells state around and add it to get number of alive cells
            line_number = cell.index / self.line_length
            col_number = cell.index - line_number * self.line_length
            # Do the birth / survival calculation
            # update cell's state

    def randomize_cells_state(self):
        for cell in self.cells:
            cell.cell_state = bool(randint(0, 1))


class ControlZone(BoxLayout):
    area_cols = NumericProperty(0)
    area_lines = NumericProperty(0)

    def __init__(self, engine, **kwargs):
        BoxLayout.__init__(self, **kwargs)
        self.engine = engine

    def reset_engine(self):
        print('Reset Engine to ' + str(self.area_cols) + ' columns and ' + str(self.area_lines) + ' lines')

    def engine_step(self):
        self.engine.step()

    def engine_randomize_cells(self):
        self.engine.randomize_cells_state()


class FullWindow(BoxLayout):

    def __init__(self, **kwargs):
        BoxLayout.__init__(self, **kwargs)
        self.orientation = 'horizontal'
        self.engine = Engine(20, 20)
        self.add_widget(CellsGrid(self.engine.cells, self.engine.line_length))
        self.add_widget(ControlZone(self.engine))


class GameOfLifeApp(App):
    def build(self):
        return FullWindow()


if __name__ == '__main__':
    GameOfLifeApp().run()
