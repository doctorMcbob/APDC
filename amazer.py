import pygame
from pygame.locals import *

from random import shuffle, choice, randint
import sys

pygame.init()

"""
amazer.py

playing around with different maze generators
making it up as i go

a maze will be a multi dimensional array
each cell in the array will be four bools representing the four exits of that cell
[N, E, S, W] Never Eat Soggy Waffles syntax
"""
PW = 32
W, H = 30, 30

if __name__ == "__main__":
    SCREEN = pygame.display.set_mode((PW * 20, PW * 20))
    pygame.display.set_caption("wow thats a mazing")


# ** ** ** ** THE ALGORITHMS ** ** ** **
# holy cow this is fun
def breadth_first(start=False, show=False):
    maze = blank_sheet()
    ent = start or (randint(0, W-1), randint(0, H-1))
    heads = [ent]
    routes = {ent: [ent]}
    marked = []
    while heads or len(marked) < (W*H)//2:
        if not heads:
            heads.append(choice(marked))
        x, y = heads.pop(0)
        route = routes[(x, y)]
        exits = maze[y][x]
        if show: debug(maze, (x, y), ent, route=routes[(x, y)])
        n = choice([2, 2, 3, 4])
        while sum(exits) < n:
            maze[y][x][randint(0, 3)] = 1

        for d, check in enumerate(exits):
            if check:
                x_, y_ = apply_direction(x, y, d)
                if x_ >= 0 and y_ >= 0 and x_ < W and y_ < H:
                    if (x_, y_) not in heads and (x_, y_) not in marked:
                        maze[y_][x_][(d + 2) % 4] = 1
                        heads.append((x_, y_))
                        routes[(x_, y_)] = route + [(x_, y_)]
                    elif maze[y_][x_][(d + 2) % 4] == 0:
                        maze[y][x][d] = 0
                else: maze[y][x][d] = 0
        marked.append((x, y))
    ext = ent
    for route in routes:
        if len(routes[route]) > len(routes[ext]):
            ext = route
    return maze, ent, ext, routes[ext]

def depth_first(start=False, show=False):
    maze = blank_sheet()
    ent = start or (randint(0, W-1), randint(0, H-1))
    heads = [ent]
    routes = {ent: [ent]}
    marked = []
    while heads or len(marked) < (W*H)//2:
        if not heads:
            heads.append(choice(marked))
        x, y = heads.pop()
        if show: debug(maze, (x, y), ent, route=routes[(x, y)])
        route = routes[(x, y)]
        exits = maze[y][x]

        n = choice([2, 2, 3, 4])
        while sum(exits) < n:
            maze[y][x][randint(0, 3)] = 1

        for d, check in enumerate(exits):
            if check:
                x_, y_ = apply_direction(x, y, d)
                if x_ >= 0 and y_ >= 0 and x_ < W and y_ < H:
                    if (x_, y_) not in heads and (x_, y_) not in marked:
                        maze[y_][x_][(d + 2) % 4] = 1
                        heads.append((x_, y_))
                        routes[(x_, y_)] = route + [(x_, y_)]
                    elif maze[y_][x_][(d + 2) % 4] == 0:
                        maze[y][x][d] = 0
                else: maze[y][x][d] = 0
        marked.append((x, y))
    ext = ent
    for route in routes:
        if len(routes[route]) > len(routes[ext]):
            ext = route
    return maze, ent, ext, routes[ext]

def ride_and_shuffle(start=False, show=False):
    maze = blank_sheet()
    ent = start or (randint(0, W-1), randint(0, H-1))
    heads = [ent]
    routes = {ent: [ent]}
    marked = []
    counter = (W + H) // 3
    while heads or len(marked) < (W*H)//2:
        if not heads:
            heads.append(choice(marked))
        if counter <= 0:
            counter = (W + H) // 3
            shuffle(heads)
        x, y = heads.pop()
        if show: debug(maze, (x, y), ent, route=routes[(x, y)])
        route = routes[(x, y)]
        exits = maze[y][x]

        n = choice([2, 2, 3, 4])
        while sum(exits) < n:
            maze[y][x][randint(0, 3)] = 1

        for d, check in enumerate(exits):
            if check:
                x_, y_ = apply_direction(x, y, d)
                if x_ >= 0 and y_ >= 0 and x_ < W and y_ < H:
                    if (x_, y_) not in heads and (x_, y_) not in marked:
                        maze[y_][x_][(d + 2) % 4] = 1
                        heads.append((x_, y_))
                        routes[(x_, y_)] = route + [(x_, y_)]
                    elif maze[y_][x_][(d + 2) % 4] == 0:
                        maze[y][x][d] = 0
                        counter -= 1
                else:
                    maze[y][x][d] = 0
                    counter -= 1
        marked.append((x, y))
    ext = ent
    for route in routes:
        if len(routes[route]) > len(routes[ext]):
            ext = route
    return maze, ent, ext, routes[ext]

# # # # # # # # # # # # # # # # # # # # #

def apply_direction(x, y, d):
    return x + [0, 1, 0, -1][d], y + [-1, 0, 1, 0][d]
                                    
def blank_sheet():
    maze = []
    for Y in range(H):
        maze.append([])
        for X in range(W):
            maze[-1].append([0, 0, 0, 0])
    return maze

def debug(maze, pos1, pos2, lines={}, pause=False, route=False):
    for spos in lines:
        pygame.draw.line(SCREEN, (255, 0, 0), (pos1[0]*PW, pos1[1]*PW), (pos2[0]*PW, pos2[1]*PW))
    SCREEN.blit(drawn_maze(maze, pos1, pos2, route=route, lit=True), (0, 0))
    pygame.display.update()
    for e in pygame.event.get():
        if e.type == QUIT: quit()
    while pause:
        for e in pygame.event.get():
            if e.type == QUIT: quit()
            if e.type == KEYDOWN:
                if e.key == K_SPACE: pause = False    
    

def drawn_maze(maze, ent, ext, route=None, lit=False):
    surf = pygame.Surface((len(maze[0])*PW, len(maze)*PW))
    for Y, line in enumerate(maze):
        for X, cell in enumerate(line):
            col = (255, 255, 255) if lit and (X, Y) in lit else (0, 0, 0)
            if (X, Y) == ent: col = (0, 0, 255)
            elif (X, Y) == ext: col = (0, 255, 0)
            elif route and (X, Y) in route: col = (255, 0, 0)
            if sum(cell): pygame.draw.rect(surf, col, pygame.rect.Rect((X*PW + PW/8, Y*PW + PW/8), (PW - (PW/8)*2, PW - (PW/8)*2)))
            if cell[0]: pygame.draw.rect(surf, col, pygame.rect.Rect((X*PW + PW/8, Y*PW), (PW - (PW/8)*2, PW/8)))
            if cell[1]: pygame.draw.rect(surf, col, pygame.rect.Rect((X*PW + (PW - (PW/8)), Y*PW + PW/8), (PW/8, PW - (PW/8)*2)))
            if cell[2]: pygame.draw.rect(surf, col, pygame.rect.Rect((X*PW + PW/8, Y*PW + (PW - (PW/8))), (PW - (PW/8)*2, PW/8)))
            if cell[3]: pygame.draw.rect(surf, col, pygame.rect.Rect((X*PW, Y*PW + (PW/8)), (PW/8, PW - (PW/8)*2)))
    return surf

def demo():
    global PW
    x, y = 0, 0
    mazes = [breadth_first(show=True), depth_first(show=True), ride_and_shuffle(show=True)]
    maze, ent, ext, route = mazes.pop(0)
    show = False
    zoom = [8, 16, 32, 64]
    zidx = 1
    img = drawn_maze(maze, ent, ext)
    rimg = drawn_maze(maze, ent, ext, route=route )
    while True:
        if PW != zoom[zidx]:
            PW = zoom[zidx]
            img = drawn_maze(maze, ent, ext)
            rimg = drawn_maze(maze, ent, ext, route=route )
        SCREEN.fill((0, 0, 0))
        if show:
            SCREEN.blit(rimg, (x*PW, y*PW))
        else:
            SCREEN.blit(img, (x*PW, y*PW))
        pygame.display.update()
        for e in pygame.event.get():
            if e.type == QUIT: quit()
            if e.type == KEYDOWN:
                if e.key == K_RIGHT:
                    x -= 1
                if e.key == K_LEFT:
                    x += 1
                if e.key == K_UP:
                    y += 1
                if e.key == K_DOWN:
                    y -= 1

                if e.key == K_z:
                    zidx = (zidx + 1) % 4
                if e.key == K_x:
                    zidx = (zidx - 1) % 4
                    
                if e.key == K_n:
                    if not mazes: quit()
                    maze, ent, ext, route = mazes.pop(0)
                    img = drawn_maze(maze, ent, ext)
                    rimg = drawn_maze(maze, ent, ext, route=route )
                if e.key == K_SPACE:
                    show = (show + 1) % 2

def solve(mazes):
    global PW
    mazes = mazes or [breadth_first(), depth_first(), ride_and_shuffle()]    
    for maze, ent, ext, route in mazes:
        img = drawn_maze(maze, ent, ext)
        X, Y = ent
        zoom = [8, 16, 32, 64]
        zidx = 1
        while (X, Y) != ext:
            if PW != zoom[zidx]:
                PW = zoom[zidx]
                img = drawn_maze(maze, ent, ext)
            mov = [0, 0]
            for e in pygame.event.get():
                if e.type == QUIT: quit()
                if e.type == KEYDOWN:
                    if e.key == K_UP: mov[1] -= 1
                    if e.key == K_DOWN: mov[1] += 1
                    if e.key == K_LEFT: mov[0] += 1
                    if e.key == K_RIGHT: mov[0] -= 1

                    if e.key == K_z:
                        zidx = (zidx + 1) % 4
                    if e.key == K_x:
                        zidx = (zidx - 1) % 4
            if sum(mov):
                slot = maze[Y][X]
                if mov[1] < 0 and slot[0]: Y -= 1
                if mov[1] > 0 and slot[2]: Y += 1
                if mov[0] > 0 and slot[3]: X -= 1
                if mov[0] < 0 and slot[1]: X += 1
            SCREEN.fill((0, 0, 0))
            SCREEN.blit(img, ((((SCREEN.get_width() / PW) // 2) - X) * PW, (((SCREEN.get_height() / PW) // 2) - Y) * PW))
            rect =  pygame.rect.Rect((((SCREEN.get_width() // PW) // 2) * PW + PW/8, ((SCREEN.get_height() / PW) // 2) * PW + PW/8), (PW-(PW/8)*2, PW-(PW/8)*2))
            pygame.draw.rect(SCREEN, (255, 0, 255), rect)
            pygame.display.update()
            
if __name__ == "__main__":
    if "-d" in sys.argv:
        flag = True
        while flag:
            for e in pygame.event.get():
                if e.type == KEYDOWN: flag=False
        demo()
    else:
        solve()
