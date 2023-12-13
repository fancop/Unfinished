import keyboard
import os
import random

COLS = 10
ROWS = 10
EMPTY = '.'  
PLAYER = 'P'
ANT = 'a'
ANTHILL = 'A'
UP = 'up'
DOWN = 'down'
RIGHT = 'right'
LEFT = 'left'
ANTHILL_MAX = 4
ANTHILL_MINI = 1
ANTS_PER_ANTHILL_MAX = 10
ANTS_PER_ANTHILL_MIN = 10
MAX_SPAWN_COUNTER = 5


class GameObject:
    def __init__(self, y, x, image):
        self.y = y
        self.x = x
        self.image = image

    def move(self, direction, field):
        new_y, new_x = self.y, self.x

        if direction == UP and self.y > 0 and not isinstance(field.cells[self.y - 1][self.x].content, Anthill):
            new_y -= 1
        elif direction == DOWN and self.y < field.rows - 1 and not isinstance(field.cells[self.y + 1][self.x].content, Anthill):
            new_y += 1
        elif direction == LEFT and self.x > 0 and not isinstance(field.cells[self.y][self.x - 1].content, Anthill):
            new_x -= 1
        elif direction == RIGHT and self.x < field.cols - 1 and not isinstance(field.cells[self.y][self.x + 1].content, Anthill):
            new_x += 1

        field.cells[self.y][self.x].content = None
        self.y, self.x = new_y, new_x
        field.cells[self.y][self.x].content = self

    def place(self, field):
        if field.cells[self.y][self.x].content is None:
            field.cells[self.y][self.x].content = self
        else:
            empty_cells = [(i, j) for i in range(field.rows) for j in range(field.cols) if field.cells[i][j].content is None]
            if empty_cells:
                new_y, new_x = random.choice(empty_cells)
                field.cells[new_y][new_x].content = self
                self.y, self.x = new_y, new_x

    def draw(self, field):
        field.cells[self.y][self.x].content = self


class Cell:
    def __init__(self, Y=None, X=None):
        self.image = EMPTY
        self.Y = Y
        self.X = X
        self.content = None

    def draw(self):
        if self.content:
            print(self.content.image, end=' ')
        else:
            print(self.image, end=' ')


class Player(GameObject):
    def __init__(self, y=None, x=None):
        super().__init__(y, x, PLAYER)

    def move(self, direction, field):
        super().move(direction, field)


class Ant(GameObject):
    def __init__(self, y, x):
        super().__init__(y, x, ANT)


class Anthill(GameObject):
    def __init__(self, x, y, quantity):
        super().__init__(y, x, ANTHILL)
        self.quantity = quantity
        self.spawn_counter = 0
        self.ants_counter = random.randint(
            ANTS_PER_ANTHILL_MIN, ANTS_PER_ANTHILL_MAX
        )

    # Другие методы остаются без изменений

    def place(self, field):
        super().place(field)

    def draw(self, field):
        super().draw(field)


class Field:
    def __init__(self, cell=Cell, player=Player, anthill=Anthill):
        self.rows = ROWS
        self.cols = COLS
        self.anthills = []
        self.ants = []
        self.cells = [[cell(Y=y, X=x) for x in range(COLS)] for y in range(ROWS)]
        self.player = player(y=random.randint(0, ROWS - 1), x=random.randint(0, COLS - 1))
        self.player.place(self)
        self.player.draw(self)

    def drawrows(self):
        for row in self.cells:
            for cell in row:
                cell.draw()
            print()

    def add_anthill(self, anthill):
        self.anthills.append(anthill)
        anthill.place(self)

    def add_anthills_randomly(self):
        available_cells = [(x, y) for x in range(self.cols) for y in range(self.rows) if (x, y) != (self.player.x, self.player.y)]
        quantity = random.randint(ANTHILL_MINI, ANTHILL_MAX)

        for i in range(quantity):
            if not available_cells:
                break
            anthill_x, anthill_y = random.sample(available_cells, 1)[0]
            available_cells.remove((anthill_x, anthill_y))

            anthill = Anthill(x=anthill_x, y=anthill_y, quantity=random.randint(ANTHILL_MINI, ANTHILL_MAX))
            self.add_anthill(anthill)

    def get_neighbours(self, y, x):
        neighbours_coords = []
        for row in (-1, 0, -1):
            for col in (-1, 0, 1):
                if row == 0 and col == 0:
                    continue
                neighbours_coords.append(
                    (y + row, x + col)
                )
        return neighbours_coords

    def spawn_ants(self):
        for anthill in self.anthills:
            if anthill.ants_counter > 0 and anthill.spawn_counter == 0:
                anthill_x, anthill_y = anthill.x, anthill.y
                neighbors = [
                    (anthill_y - 1, anthill_x - 1), (anthill_y - 1, anthill_x), (anthill_y - 1, anthill_x + 1),
                    (anthill_y, anthill_x - 1),                                 (anthill_y, anthill_x + 1),
                    (anthill_y + 1, anthill_x - 1), (anthill_y + 1, anthill_x), (anthill_y + 1, anthill_x + 1)
                ]
                empty_neighbors = filter(lambda pos: 0 <= pos[0] < self.rows and 0 <= pos[1] < self.cols and not self.cells[pos[0]][pos[1]].content, neighbors)

                empty_neighbors = list(empty_neighbors)

                if empty_neighbors:
                    ant_y, ant_x = random.choice(empty_neighbors)
                    ant = Ant(y=ant_y, x=ant_x)
                    self.cells[ant_y][ant_x].content = ant
                    anthill.ants_counter -= 1
                    anthill.spawn_counter = 1
                    self.ants.append(ant)


            if anthill.spawn_counter > 0:
                anthill.spawn_counter += 1
                if anthill.spawn_counter > MAX_SPAWN_COUNTER:
                    anthill.spawn_counter = 0

    def move_ants(self):
        # движение муравья
        for ant in self.ants:
            neighbourds_coords = self.get_neighbours(ant.y, ant.x)

            random.shuffle(neighbourds_coords)
            for y, x in neighbourds_coords:          
                if y < 0 or y > self.rows - 1 or x < 0 or x > self.cols - 1:
                    # + 1 в счетчик сбежавших
                    if ant in self.ants:
                        self.ants.remove(ant)
                        self.cells[ant.y][ant.x].content = None
                    break

                new_cell = self.cells[y][x]
                if new_cell.content:
                    continue
                self.cells[ant.y][ant.x].content = None
                new_cell.content = ant
                ant.y = y
                ant.x = x
                break           

def clear_screen():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')


class Game:
    def __init__(self):
        self.field = Field()
        self.field.add_anthills_randomly()
        self.game_over = False  # Добавляем флаг для проверки окончания игры

    def handle_keyboard_event(self, event):
        if event.event_type == keyboard.KEY_DOWN:
            if event.name == UP:
                self.field.player.move(UP, self.field)
            elif event.name == DOWN:
                self.field.player.move(DOWN, self.field)
            elif event.name == LEFT:
                self.field.player.move(LEFT, self.field)
            elif event.name == RIGHT:
                self.field.player.move(RIGHT, self.field)
            elif event.name == 'esc':
                print("Выход из игры.")
                return True
        return False

    def update_game_state(self):
        clear_screen()
        self.field.drawrows()
        self.field.spawn_ants()
        self.field.move_ants()

        # Проверка на наличие муравьев во всех муравейниках
        total_ants = 0

        for anthill in self.field.anthills:
            total_ants += anthill.ants_counter
        
        # Проверка на наличие муравьев на поле
        ants_on_field = False

        for row in self.field.cells:
            for cell in row:
                if cell.content and isinstance(cell.content, Ant):
                    ants_on_field = True
                    break
            if ants_on_field:
                break

        if total_ants == 0 and not ants_on_field:
            self.game_over = True
            print("Все муравьи съедены или убежали. Игра окончена!")

    def run(self):
        self.field.drawrows()

        while not self.game_over:
            event = keyboard.read_event(suppress=True)
            if self.handle_keyboard_event(event):
                break

            self.update_game_state()


game_instance = Game()
game_instance.run()
