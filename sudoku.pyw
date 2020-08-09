import pygame
import numpy as np
import time
from sudoku_validator import valid_solution
import sys
from threading import Thread


sys.setrecursionlimit(9 * 9 * 9)


GRID = np.array([[0, 0, 0, 8, 0, 0, 0, 0, 4],
                 [2, 0, 0, 3, 0, 0, 0, 0, 0],
                 [0, 3, 4, 1, 7, 0, 0, 9, 5],
                 [4, 0, 0, 2, 0, 1, 6, 5, 0],
                 [0, 0, 2, 0, 9, 0, 3, 0, 0],
                 [0, 6, 9, 5, 0, 7, 0, 0, 8],
                 [7, 4, 0, 0, 8, 2, 5, 1, 0],
                 [0, 0, 0, 0, 0, 5, 0, 0, 6],
                 [5, 0, 0, 0, 0, 3, 0, 0, 0]])

now = GRID

pygame.init()

WIDTH = 800
HEIGHT = 650

# colors
BLACK = (10, 10, 10)
GREY = (224, 224, 244)
D_GREY = (100, 100, 100)
GREEN = (46, 230, 83)
BLUE = (54, 154, 247)
D_BLUE = (8, 116, 211)
WHITE = (250, 250, 250)
RED = (249, 49, 49)


STEP = 3

win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Sudoku')

clock = pygame.time.Clock()

class Cell:

    side = 60
    hl_num = 0

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.num = 0
        self.note = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.rect = pygame.Rect(self.x, self.y, Cell.side, Cell.side)
        self.static = False
        self.active = False
        self.xi = (x - 20) // Cell.side
        self.yi = (y - 20) // Cell.side

        self.co_ords = []
        for i in range(self.y, self.y + Cell.side, Cell.side // 3):
            for j in range(self.x, self.x + Cell.side, Cell.side // 3):
                self.co_ords.append((j + 2, i + 2))

    def draw(self):
        if Cell.hl_num == self.num and Cell.hl_num != 0:
            self.bg_highlight()
        pygame.draw.rect(win, GREY, self.rect, 1)
        if self.active:
            self.highlight()
        self.write()
        self.write_note()

    def highlight(self):
        pygame.draw.rect(win, GREEN, (self.x, self.y,
                                      Cell.side - 2, Cell.side - 2), 4)

    def bg_highlight(self):
        pygame.draw.rect(win, (218, 233, 235), self.rect)

    def is_clicked(self, x, y):
        if self.rect.collidepoint(x, y):
            return True
        return False

    def set_active(self, state):
        if isinstance(state, bool):
            self.active = state

    def set_num(self, num):
        if not self.static:
            self.num = num
            self.note = [0, 0, 0, 0, 0, 0, 0, 0, 0]

    def set_note(self, num):
        if not self.static:
            if num not in self.note:
                self.note[num - 1] = num
            else:
                self.note[num - 1] = 0
            self.num = 0
            now[active_y][active_x] = 0

    def clear(self):
        if not self.static:
            self.note = [0, 0, 0, 0, 0, 0, 0, 0, 0]
            self.num = 0

    def write(self):
        occur_row, occur_col, occur_box = 0, 0, 0
        if self.num != 0:
            occur_row = np.count_nonzero(now[self.yi, :] == self.num, axis=0)
            occur_col = np.count_nonzero(now[:, self.xi] == self.num, axis=0)
            c, r = self.xi // 3 * 3, self.yi // 3 * 3
            occur_box = np.count_nonzero(now[r:r + 3, c:c +
                                             3].flatten() == self.num, axis=0)

        if self.static:
            color = BLACK
        elif occur_row > 1 or occur_col > 1 or occur_box > 1:
            color = RED
        else:
            color = D_BLUE
        if self.num != 0:
            font = pygame.font.SysFont('Helvetica', 52)
            text = font.render(str(self.num), 1, color)
            win.blit(text, (self.x + text.get_width() /
                            2, self.y))

    def write_note(self):
        font = pygame.font.SysFont('Helvetica', 16)
        k = 0
        for point in self.co_ords:
            if not self.note[k] == 0:
                text = font.render(str(self.note[k]), 0, D_GREY)
                win.blit(text, point)
            k += 1


class Button:

    def __init__(self, x, y, text):
        self.x = x
        self.y = y
        self.text = text
        self.rect = pygame.Rect(self.x, self.y, 100, 60)

    def draw(self, bg=GREY, fg=BLACK):
        pygame.draw.rect(win, bg, self.rect)
        font = pygame.font.SysFont('Helvetica', 33)
        text = font.render(self.text, 1, fg)
        win.blit(text, (self.x + 50 - text.get_width() / 2, self.y + 12))

    def is_clicked(self, x, y):
        if self.rect.collidepoint(x, y):
            return True
        return False


class Note(Button):

    def __init__(self, x, y, text):
        super().__init__(x, y, text)
        self.active = False

    def draw(self):
        if self.active:
            super().draw(BLUE, WHITE)
        else:
            super().draw()

    def toggle(self):
        if self.active:
            self.active = False
        else:
            self.active = True


def draw_screen():
    global win

    win.fill((255, 255, 255))

    for i in range(9):
        for j in range(9):
            board[i][j].draw()

    for i in range(STEP + 1):
        for j in range(STEP + 1):
            pygame.draw.line(win, BLACK, (i * 60 * STEP + 20, j + 20),
                             (i * 60 * STEP + 20, j * 60 * STEP + 20))
            pygame.draw.line(win, BLACK, (i + 20, j * 60 * STEP + 20),
                             (i * 60 * STEP + 20, j * 60 * STEP + 20))

    note.draw()
    clear.draw()
    reset.draw()

    pygame.display.update()


def declare_winner():
    win.fill((255, 255, 255))
    font = pygame.font.SysFont('Helvetica', 60)
    text = font.render('You won!!', 1, BLACK)
    win.blit(text, (WIDTH / 2 - text.get_width() /
                    2, HEIGHT / 2 - text.get_height() / 2))
    pygame.display.update()


def reset_board():
    for i in range(9):
        for j in range(9):
            board[i][j].set_num(0)
    now = GRID[:]
    draw_screen()


def possible(x, y, num):
    global now
    for i in range(9):
        if now[x][i] == num:
            return False
    for i in range(9):
        if now[i][y] == num:
            return False
    r = (x // 3) * 3
    c = (y // 3) * 3
    for i in range(3):
        for j in range(3):
            if now[r + i][c + j] == num:
                return False
    return True


def solve():
    global board, now
    for y in range(9):
        for x in range(9):
            if board[x][y].num == 0:
                for number in range(1, 10):
                    if possible(x, y, number):
                        board[x][y].set_num(number)
                        now[x][y] = number
                        board[x][y].set_active(True)
                        draw_screen()
                        solve()
                        board[x][y].set_num(0)
                        now[x][y] = 0
                        board[x][y].set_active(False)
                        draw_screen()
                return

    # print(now)
    input('More?')


note = Note(630, 170, 'Note')
clear = Button(630, 260, 'Clear')
reset = Button(630, 350, 'Reset')


board = []
for i in range(9):
    row = []
    for j in range(9):
        number = GRID[j][i]
        cell = Cell(i * 60 + 20, j * 60 + 20)
        cell.set_num(number)
        if number != 0:
            cell.static = True
        row.append(cell)
    board.append(row)


active_x, active_y = 4, 5
pressed = False
prev_pressed = False
space_pressed = False
run = True

times = []

while run:

    if 0 not in now.flatten():
        if valid_solution(now.tolist()):
            declare_winner()

    # clock.tick(10)
    t1 = time.time()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            for row in board:
                for cell in row:
                    if cell.is_clicked(x, y):
                        active_x, active_y = cell.xi, cell.yi
                        board[active_x][active_y].set_active(True)
                    else:
                        cell.set_active(False)

            if note.is_clicked(x, y):
                note.toggle()
            if clear.is_clicked(x, y):
                board[active_x][active_y].clear()
            if reset.is_clicked(x, y):
                print('Reset pressed')
                reset_board()

        elif event.type == pygame.KEYDOWN:
            pressed = True
        elif event.type == pygame.KEYUP:
            pressed = False


    if not space_pressed:
        keys = pygame.key.get_pressed()

        if not prev_pressed:

            if keys[pygame.K_KP1]:
                if note.active:
                    board[active_x][active_y].set_note(1)
                else:
                    now[active_y][active_x] = 1
                    board[active_x][active_y].set_num(1)

            elif keys[pygame.K_KP2]:
                if note.active:
                    board[active_x][active_y].set_note(2)
                else:
                    now[active_y][active_x] = 2
                    board[active_x][active_y].set_num(2)

            elif keys[pygame.K_KP3]:
                if note.active:
                    board[active_x][active_y].set_note(3)

                else:
                    now[active_y][active_x] = 3
                    board[active_x][active_y].set_num(3)

            elif keys[pygame.K_KP4]:
                if note.active:
                    board[active_x][active_y].set_note(4)
                else:
                    now[active_y][active_x] = 4
                    board[active_x][active_y].set_num(4)

            elif keys[pygame.K_KP5]:
                if note.active:
                    board[active_x][active_y].set_note(5)
                else:
                    now[active_y][active_x] = 5
                    board[active_x][active_y].set_num(5)

            elif keys[pygame.K_KP6]:
                if note.active:
                    board[active_x][active_y].set_note(6)
                else:
                    now[active_y][active_x] = 6
                    board[active_x][active_y].set_num(6)

            elif keys[pygame.K_KP7]:
                if note.active:
                    board[active_x][active_y].set_note(7)
                else:
                    now[active_y][active_x] = 7
                    board[active_x][active_y].set_num(7)

            elif keys[pygame.K_KP8]:
                if note.active:
                    board[active_x][active_y].set_note(8)
                else:
                    now[active_y][active_x] = 8
                    board[active_x][active_y].set_num(8)

            elif keys[pygame.K_KP9]:
                if note.active:
                    board[active_x][active_y].set_note(9)
                else:
                    now[active_y][active_x] = 9
                    board[active_x][active_y].set_num(9)

            elif any([keys[pygame.K_BACKSPACE], keys[pygame.K_DELETE]]):
                now[active_y][active_x] = 0
                board[active_x][active_y].set_num(0)

            elif keys[pygame.K_n]:
                note.toggle()

            elif keys[pygame.K_UP] and active_y > 0:
                board[active_x][active_y].set_active(False)
                active_y -= 1

            elif keys[pygame.K_DOWN] and active_y < 8:
                board[active_x][active_y].set_active(False)
                active_y += 1

            elif keys[pygame.K_LEFT] and active_x > 0:
                board[active_x][active_y].set_active(False)
                active_x -= 1

            elif keys[pygame.K_RIGHT] and active_x < 8:
                board[active_x][active_y].set_active(False)
                active_x += 1

            elif keys[pygame.K_SPACE]:
                space_pressed = True
                board[0][0].set_active(True)
                solve()

        if pressed:
            prev_pressed = True
        else:
            prev_pressed = False

        board[active_x][active_y].set_active(True)

        Cell.hl_num = board[active_x][active_y].num

        draw_screen()

    # print(f"Time elapsed: {time.time() - t1}s")
#     times.append(time.time()-t1)

# print(sum(times)/len(times))

pygame.quit()
