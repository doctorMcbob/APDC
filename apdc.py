"""
apdc.py
a procedural dungeon crawler

built with the maze builder I made
"""
import pygame
from pygame.locals import *
from random import randint, choice
import math

import amazer

W, H = 640, 640
PW = 32

SCREEN = pygame.display.set_mode((W, H))
pygame.display.set_caption("Another Procedural Dungeon Crawler")
HEL32 = pygame.font.SysFont("Helvetica", 32)

FONTS = {
    8: pygame.font.SysFont("helvetica", 6),
    16: pygame.font.SysFont("helvetica", 12),
    32: pygame.font.SysFont("helvetica", 24),
    64: pygame.font.SysFont("helvetica", 46),
}

SCREEN.fill((255, 255, 255))
SCREEN.blit(HEL32.render("Loading", 0, (0, 0, 0)), (32, 32))
pygame.draw.rect(SCREEN, (255, 0, 0), pygame.Rect((16, 96), (1, 32)))
pygame.display.update()

#tokens
HP="HP";SPEED="SPEED";XP="XP";LVL="LVL";POS="POS";VIS="VIS";ITEM="ITEM";SCORE="SCORE";MIND="MIND"

FLOOR_DEPTH = 16

# templates
PLAYER_TEMPLATE = {
    POS: None,
    LVL: 1, XP: 0,
    HP: 20,
    SPEED: 1, VIS: 5,
    ITEM: None,
    SCORE: None,
}

ENEMY_TEMPLATE = {
    POS: None,
    HP: None,
    MIND: None,
}

def path_to(maze, p1, p2):
    x1, y1 = p1
    paths = [[p1]]
    while paths:
        path = paths.pop()
        x, y = path[-1]
        for d, check in enumerate(maze[y][x]):
            if check:
                new = amazer.apply_direction(x, y, d)
                if new == p2:
                    return path + [p2]
                if new not in path:
                    paths.append(path.copy() + [new])
    return None

def chase(maze, this, player, enemies):
    path = path_to(maze, this[POS], player[POS])
    if path is not None and len(path) > 2:
        if path[1] not in map(lambda enemy: enemy[POS], enemies):
            this[POS] = path[1]

def randy(maze, this, player, enemies):
    x, y = this[POS]
    d = choice(
        list(filter(
            lambda n: n is not None,
            [d if check else None
             for d, check in enumerate(maze[y][x])]
        )))
    newpos = amazer.apply_direction(x, y, d)
    if newpos != player[POS] and newpos not in map(lambda enemy: enemy[POS], enemies):
        this[POS] = newpos

def sleep(*args, **kwargs):
    return

def distance(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def make_enemies(maze, ent, ext, level=1):
    enemies = []
    spawn_rate = 8 + level // 5
    for y, row in enumerate(maze):
        for x, slot in enumerate(row):
            if (x, y) in [ent, ext]:
                continue
            if sum(slot):
                roll = randint(0, 100)
                if roll < spawn_rate:
                    enemy = ENEMY_TEMPLATE.copy()
                    enemy[POS] = (x, y)
                    if roll % 2:
                        if randint(0, 3) <= 2:
                            enemy[MIND] = randy
                        else:
                            enemy[MIND] = chase
                    else: enemy[MIND] = sleep
                    enemy[HP] = max(1, choice(
                        [level // 3 - randint(2, 5)] +
                        [level // 3 - randint(1, 3)] * 3 +
                        [level // 3] * 5 +
                        [level // 3 + randint(1, 3)] +
                        [level // 3 + randint(2, 5)]))
                    enemies.append(enemy)
    return enemies

def combat(enemies, enemy, player):
    player[HP] -= 1
    enemy[HP] -= 1
    if enemy[HP] <= 0:
        enemies.remove(enemy)
    if player[HP] <= 0:
        print("You have died")
        quit()

def players_turn(maze, enemies, player):
    global PW, flr
    stairs = False
    mov = [0, 0]
    for e in pygame.event.get():
        if e.type == QUIT or e.type == KEYDOWN and e.key == K_ESCAPE: quit()
        if e.type == KEYDOWN:
            if e.key == K_UP: mov[1] -= 1
            if e.key == K_DOWN: mov[1] += 1
            if e.key == K_LEFT: mov[0] += 1
            if e.key == K_RIGHT: mov[0] -= 1
            
            if e.key == K_SPACE:
                stairs = True
            if e.key == K_z:
                PW = min(PW * 2, 64)
            if e.key == K_x:
                PW = max(PW / 2, 8)
    if sum(mov):
        slot = maze[Y][X]
        _x, _y = player[POS]
        if mov[1] < 0 and slot[0]: _y -= 1
        if mov[1] > 0 and slot[2]: _y += 1
        if mov[0] > 0 and slot[3]: _x -= 1
        if mov[0] < 0 and slot[1]: _x += 1
        enemy = None
        for nme in enemies:
            if nme[POS] == (_x, _y):
                enemy = nme
                break
        if enemy is None:
            player[POS] = (_x, _y)
        else:
            combat(enemies, enemy, player)
        return True 
    if stairs:
        if (X, Y) == ent: flr = max(0, flr - 1)
        if (X, Y) == ext: flr += 1
        return True
    return False

def update_enemies(maze, enemies, player, lit):
    for enemy in enemies:
        if enemy[POS] in lit:
            enemy[MIND](maze, enemy, player, enemies)

def drawn_maze(maze, ent, ext, enemies=None, route=None, lit=False):
    font = FONTS[PW]
    surf = pygame.Surface((len(maze[0])*PW, len(maze)*PW))
    for Y, line in enumerate(maze):
        for X, cell in enumerate(line):
            if lit:
                if (X, Y) in lit:
                    col = (255, 255, 255)
                else:
                    col = (0, 0, 0)
                    for d, check in enumerate(cell):
                        if check and amazer.apply_direction(X, Y, d) in lit:
                            col = (50, 50, 50)
            else:
                col = (255, 255, 255)
            if not lit or (X, Y) in lit or col == (50, 50 , 50):
                if (X, Y) == ent and ent in lit: col = (0, 0, 255)
                elif (X, Y) == ext and ext in lit: col = (0, 255, 0)
                elif route and (X, Y) in route: col = (255, 0, 0)
                if enemies and (X, Y) in map(lambda enemy: enemy[POS], enemies): col = (200, 130, 0)
                if sum(cell): pygame.draw.rect(surf, col, pygame.rect.Rect((X*PW + PW/8, Y*PW + PW/8), (PW - (PW/8)*2, PW - (PW/8)*2)))
                if cell[0]: pygame.draw.rect(surf, col, pygame.rect.Rect((X*PW + PW/8, Y*PW), (PW - (PW/8)*2, PW/8)))
                if cell[1]: pygame.draw.rect(surf, col, pygame.rect.Rect((X*PW + (PW - (PW/8)), Y*PW + PW/8), (PW/8, PW - (PW/8)*2)))
                if cell[2]: pygame.draw.rect(surf, col, pygame.rect.Rect((X*PW + PW/8, Y*PW + (PW - (PW/8))), (PW - (PW/8)*2, PW/8)))
                if cell[3]: pygame.draw.rect(surf, col, pygame.rect.Rect((X*PW, Y*PW + (PW/8)), (PW/8, PW - (PW/8)*2)))
                if enemies and (X, Y) in map(lambda enemy: enemy[POS], enemies):
                    for enemy in enemies:
                        if enemy[POS] == (X, Y):
                            surf.blit(font.render(str(enemy[HP]), 0, (0, 0, 0)), (X*PW, Y*PW))
                            break
    return surf

def update_screen(img, PLAYER):
    SCREEN.fill((0, 0, 0))
    SCREEN.blit(img, ((((SCREEN.get_width() / PW) // 2) - X) * PW, (((SCREEN.get_height() / PW) // 2) - Y) * PW))
    rect =  pygame.rect.Rect((((SCREEN.get_width() // PW) // 2) * PW + PW/8, ((SCREEN.get_height() / PW) // 2) * PW + PW/8), (PW-(PW/8)*2, PW-(PW/8)*2))
    pygame.draw.rect(SCREEN, (255, 0, 255), rect)
    SCREEN.blit(FONTS[PW].render(str(PLAYER[HP]), 0, (0, 0, 0)), (((SCREEN.get_width() // PW) // 2) * PW + PW/8, ((SCREEN.get_height() / PW) // 2) * PW + PW/8))
    pygame.draw.rect(SCREEN, (100, 100, 100), pygame.Rect((0, 0), (256, 32)))
    SCREEN.blit(HEL32.render(str(flr), 0, (0, 0, 0)), (0, 0))
    pygame.display.update()

PLAYER = PLAYER_TEMPLATE.copy()

# build the dungeon --
DUNGEON = []
LIT = []
ENEMIES = []
while len(DUNGEON) < FLOOR_DEPTH:
    pygame.draw.rect(SCREEN, (255, 0, 0), pygame.Rect((16, 96), ((608 / FLOOR_DEPTH)*len(DUNGEON), 32)))
    pygame.display.update()
    lvl = len(DUNGEON)
    amazer.W, amazer.H = (16 + int(lvl * 1.75), 16 + int(lvl * 1.75))
    ent = (randint(0, amazer.W), randint(0, amazer.H)) if len(DUNGEON) == 0 else DUNGEON[-1][2] 
    LIT.append(set())
    DUNGEON.append(choice([
        amazer.breadth_first,
        amazer.breadth_first,
        amazer.breadth_first,
        amazer.depth_first,
        amazer.ride_and_shuffle,
        amazer.ride_and_shuffle,
    ])(ent))
    ENEMIES.append(
        make_enemies(DUNGEON[-1][0], DUNGEON[-1][1],
                     DUNGEON[-1][2], level=len(DUNGEON))
    )

# play --
PLAYER[POS] = list(DUNGEON[0][1])
flr = 0
turns = 0
while flr < FLOOR_DEPTH:
    maze, ent, ext, route = DUNGEON[flr]
    FLR = flr
    while flr == FLR:
        X, Y = PLAYER[POS]
        for x_ in range(X-PLAYER[VIS], X+PLAYER[VIS]):
            for y_ in range(Y-PLAYER[VIS], Y+PLAYER[VIS]):
                if distance(PLAYER[POS], (x_, y_)) < PLAYER[VIS]:
                    LIT[flr].add((x_, y_))

        update_screen(drawn_maze(maze, ent, ext, enemies=ENEMIES[flr], lit=LIT[flr]), PLAYER)

        if players_turn(maze, ENEMIES[flr], PLAYER):
            turns += 1
        if turns >= PLAYER[SPEED]:
            update_enemies(maze, ENEMIES[flr], PLAYER, LIT[flr])
            turns = 0

print("wow you did it!")
