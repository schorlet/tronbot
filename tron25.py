import sys, copy, heapq
from time import time
from collections import namedtuple, deque
from operator import mul, truediv, itemgetter

UP, RIGHT, DOWN, LEFT, END = (0, -1), (1, 0), (0, 1), (-1, 0), (0, 0)
DIR = {UP: 'UP', RIGHT: 'RIGHT', DOWN: 'DOWN', LEFT: 'LEFT', END: 'END'}
W, H = 30, 20
BOARD = [[0 for _ in range(W)] for _ in range(H)]
ID_START = 10001
HEADS, HEADS_F = {}, {}
LASTMOVE = None
DEBUG = False


def clear_pid(pid):
    for y in range(H):
        for x in range(W):
            if BOARD[y][x] == pid: BOARD[y][x] = 0


def read_stdin():
    heads = {}
    nbj, mid = map(int, raw_input().split(' '))
    mid = ID_START + mid
    for pid in range(ID_START, ID_START + nbj):
        x0, y0, x1, y1 = map(int, raw_input().split(' '))
        if (x1, y1) == (-1, -1) and pid != mid:
            clear_pid(pid)
        else:
            BOARD[y0][x0] = pid
            BOARD[y1][x1] = pid
            if pid == mid:
                mx, my = x1, y1
            else:
                heads[pid] = (x1, y1)
    return mx, my, heads


def in_board(x, y):
    return 0 <= x < W and 0 <= y < H


def is_clean(board, x, y):
    return in_board(x, y) and board[y][x] <= 0


def next_pos(x, y, move):
    a, b = move
    return x + a, y + b


def neighbors(board, x, y):
    ngb = []
    for (xx, yy) in (next_pos(x, y, UP),   next_pos(x, y, RIGHT),
                     next_pos(x, y, DOWN), next_pos(x, y, LEFT)):
        if in_board(xx, yy):
            ngb.append((xx, yy))
    return ngb


def neighbors_clean(board, x, y):
    ngb = []
    for (xx, yy) in (next_pos(x, y, UP),   next_pos(x, y, RIGHT),
                     next_pos(x, y, DOWN), next_pos(x, y, LEFT)):
        if is_clean(board, xx, yy):
            ngb.append((xx, yy))
    return ngb

def neighbors_clean_clean(board, x, y):
    ngb = []
    for (xx, yy) in (next_pos(x, y, UP),   next_pos(x, y, RIGHT),
                     next_pos(x, y, DOWN), next_pos(x, y, LEFT)):
        if is_clean(board, xx, yy):
            if 0 < len(neighbors_clean(board, xx, yy)):
                ngb.append((xx, yy))
    return ngb


def max_move(x, y, move):
    a, b = move
    c, d = next_pos(x, y, move)
    count = 0
    while is_clean(BOARD, c, d):
        count += 1
        c, d = next_pos(c, d, move)
    return count


def guess_moves(x, y, c, d):
    a, b = c - x, d - y
    if a == 0: return (0, b)
    elif b == 0: return (a, 0)
    return (0, b), (a, 0)


def fill_board():
    board_fill = copy.deepcopy(BOARD)

    for pid, pos in HEADS.items():
        px, py = pos
        points = {pos}

        while points:
            if time() - START > 0.065:
                break
            c, d = points.pop()
            for (xx, yy) in neighbors_clean(BOARD, c, d):
                if (xx, yy) in points:
                    continue
                value = board_fill[yy][xx]
                dist = distance1(px, py, xx, yy)
                if value == 0:
                    dest = best_dest(px, py, xx, yy, limit=500)
                    if dest:
                        board_fill[yy][xx] = dist
                        points.add((xx, yy))
                elif dist < value:
                    points.add((xx, yy))
                    board_fill[yy][xx] = dist
    return board_fill


def flood_count(board_fill, x, y, hf=False):
    board_copy = copy.deepcopy(BOARD)
    count = 1
    board_copy[y][x] = -2
    points = {(x, y)}
    while points:
        c, d = points.pop()
        for (xx, yy) in neighbors(board_copy, c, d):
            value = board_copy[yy][xx]
            if value == 0:
                # count += 1
                # board_copy[yy][xx] = count
                if hf: points.add((xx, yy))

                dist2 = board_fill[yy][xx]
                if dist2 == 0:
                    count += 1
                    board_copy[yy][xx] = count
                    if not hf: points.add((xx, yy))
                elif dist2 > 0:
                    dist = distance1(x, y, xx, yy)
                    if dist < dist2:
                        count += 1
                        board_copy[yy][xx] = count
                        if not hf: points.add((xx, yy))
                    else:
                        board_copy[yy][xx] = -1
            # --
            elif hf and value >= ID_START and value in HEADS and HEADS[value] == (xx, yy):
                if not value in HEADS_F: HEADS_F[value] = set()
                HEADS_F[value].add(directions(xx - x, yy - y))
    return count - 1


def flood_fill(board_fill, x, y, move, ww=None, hh=None):
    if ww is None: ww = W
    if hh is None: hh = H
    a, b = move
    c, d = next_pos(x, y, move)
    count = 0

    board_copy = copy.deepcopy(BOARD)
    if is_clean(board_copy, c, d):
        count += 1
        board_copy[d][c] = 1
        points = {(c, d)}

        while points:
            e, f = points.pop()
            for (xx, yy) in neighbors(board_copy, e, f):
                if (xx, yy) in points:
                    continue
                value = board_copy[yy][xx]
                if value == 0:
                    dist = distance1(c, d, xx, yy)
                    dist2 = board_fill[yy][xx]
                    if dist2 == 0 or dist <= dist2:
                        count += 1
                        board_copy[yy][xx] = dist
                        points.add((xx, yy))
    return count


def default_move(x, y):
    # move_map
    move_map = {
            UP:    max_move(x, y, UP),
            RIGHT: max_move(x, y, RIGHT),
            DOWN:  max_move(x, y, DOWN),
            LEFT:  max_move(x, y, LEFT) }
    move_dirs  = sorted(move_map.items(), key=itemgetter(1), reverse=True)
    move_dirs = tuple(k for k, v in move_dirs if v > 0)

    # move_dirs == 0
    if len(move_dirs) == 0:
        return None

    # move_dirs == 1
    elif len(move_dirs) == 1:
        return move_dirs[0]


    move = None
    flood_map = dict()
    neighbors = dict()
    board_copy = copy.deepcopy(BOARD)

    for move in move_dirs:
        c, d = next_pos(x, y, move)
        board_copy[d][c] = ID_START + 10
        flood_map[move] = flood_count(board_copy, c, d)
        neighbors[move] = len(neighbors_clean(board_copy, c, d))
        board_copy[d][c] = 0

    flood_dirs = sorted(flood_map.items(), key=itemgetter(1))
    max_flood = flood_dirs[-1][1]
    flood_dirs = [k for k, v in flood_dirs if v == max_flood]

    # flood_dirs == 1
    if len(flood_dirs) == 1:
        move = flood_dirs[0]

    else:
        flood_dirs.sort(key=lambda x: flood_map[x], reverse=True)
        flood_dirs.sort(key=lambda x: neighbors[x], reverse=False)
        move = flood_dirs[0]
    return move


def __best_dest(x, y, hx, hy, limit):
    board_copy = copy.deepcopy(BOARD)
    paths = None
    # set([(x, y)])
    points = [(0, [(x, y)])]
    heapq.heapify(points)
    while paths is None and points:
        value1, points2 = heapq.heappop(points)
        px, py = points2[-1]

        for (xx, yy) in neighbors(board_copy, px, py):
            if (xx, yy) == (hx, hy):
                paths = points2 + [(xx, yy)]
                break
            if (xx, yy) in points2:
                continue

            value2 = board_copy[yy][xx]
            if value2 == 0:
                value2 = distance2(xx, yy, hx, hy)
                board_copy[yy][xx] = value2
                if limit and value2 > limit: continue
                heapq.heappush(points, (value2, points2 + [(xx, yy)]))
    return paths


def best_dest(x, y, hx, hy, limit=0):
    paths = __best_dest(x, y, hx, hy, limit)
    move = None
    if paths:
        a, b = paths[1]
        move = (a - x, b - y)
    return move


def __distance1(x, y, c, d):
    return 10 * (abs(x - c) + abs(y - d))

def distance1(x, y, c, d):
    d = __distance1(x, y, c, d)
    return 5 if d == 10 else d

def distance2(x, y, c, d):
    return 10 * (abs(x - c)**2 + abs(y - d)**2)

def distance3(x, y, c, d):
    return 33 * (abs(x - c)**2 + abs(y - d)**2)**0.5


def directions(x, y):
    dx = (   0 if x == 0 else 1 if x > 0 else -1 , 0)
    dy = (0, 0 if y == 0 else 1 if y > 0 else -1)
    return dx, dy


def head_min(x, y):
    # move_map
    move_map = {
            UP:    max_move(x, y, UP),
            RIGHT: max_move(x, y, RIGHT),
            DOWN:  max_move(x, y, DOWN),
            LEFT:  max_move(x, y, LEFT) }
    move_dirs  = sorted(move_map.items(), key=itemgetter(1), reverse=True)
    move_dirs = tuple(k for k, v in move_dirs if v > 0)

    if True:
        print >> sys.stderr, 'move_map [',
        for k, v in move_map.iteritems():
            print >> sys.stderr, '(%d, %s),' % (v, DIR[k]),
        print >> sys.stderr, ']'

    # move_dirs <= 1
    if len(move_dirs) <= 1:
        return None

    if LASTMOVE is None:
        return move_dirs[0]


    move = None
    board_fill = fill_board()
    count_flood = flood_count(board_fill, x, y, hf=True)
    if len(HEADS_F) == 0:
        return None

    # flood_map
    flood_map = dict()
    next_map = dict()

    for dir in move_dirs:
        flood_map[dir] = flood_fill(board_fill, x, y, dir)
        c, d = next_pos(x, y, dir)
        board_fill[d][c] = ID_START + 10
        next_map[dir] = flood_count(board_fill, c, d)
        board_fill[d][c] = 0

    flood_dirs = [dir for dir in move_dirs]
    flood_dirs.sort(key=lambda x: flood_map[x], reverse=True)
    flood_dirs.sort(key=lambda x: next_map[x], reverse=True)

    if True:
        print >> sys.stderr, 'flood_map [',
        for k, v in flood_map.iteritems():
            print >> sys.stderr, '(%d, %s),' % (v, DIR[k]),
        print >> sys.stderr, ']'
        print >> sys.stderr, 'next_map [',
        for k, v in next_map.iteritems():
            print >> sys.stderr, '(%d, %s),' % (v, DIR[k]),
        print >> sys.stderr, ']'


    # flood_dirs == 0
    if len(flood_dirs) == 0:
        return None
    floods_move = flood_dirs[0]


    # heads
    heads = []
    for pid in HEADS_F:
        px, py = HEADS[pid]
        dist = distance2(x, y, px, py)
        heads.append((dist, pid))
    heads.sort()

    if True:
        print >> sys.stderr, 'HEADS', heads

    dir_move = lambda x: DIR[x] if x in DIR else None
    inv_move = lambda x, y: (x * -1, y * -1)
    last_pos = lambda x, y: next_pos(x, y, inv_move(*LASTMOVE))

    while move is None and heads:
        dist2, pid = heads.pop(0)
        px, py = HEADS[pid]
        dx, dy = px - x, py - y

        ex, ey = HEADS_F[pid].pop()
        dirs = tuple(e for e in (ex, ey) if e != END)
        print >> sys.stderr, 'PID', [DIR[dir] for dir in dirs], pid, ',', dist2


        if 50 < dist2:
            move = best_dest(x, y, px, py)
            print >> sys.stderr, 'best_dest', (px, py), dir_move(move)
            dirs2 = [dir for dir in dirs if dir in flood_dirs]
            if len(dirs2) > 1:
                if move == ex and abs(dx) < abs(dy): move = ey
                elif move == ey and abs(dx) >= abs(dy): move = ex
            print >> sys.stderr, '130 < dist2 < 5000', dir_move(move)


        elif dist2 == 10:
            move = floods_move

            ax, ay = last_pos(x, y)
            dist3 = distance2(ax, ay, px, py)

            if dist3 == 20 or dist3 == 50:
                if LASTMOVE in flood_dirs:
                    move = LASTMOVE
            print >> sys.stderr, 'dist2 == 10', dist3, dir_move(move)


        elif dist2 == 20:
            move = floods_move

            ax, ay = last_pos(x, y)
            dist3 = distance2(ax, ay, px, py)

            if dist3 == 10:
                move = guess_moves(ax, ay, px, py)
                if not move in flood_dirs:
                    move = floods_move
                elif not move in next_map:
                    move = floods_move
                elif next_map[move] < 0.8 * next_map[floods_move]:
                    move = floods_move

            if dist3 == 50:
                gmove = guess_moves(ax, ay, x, y)
                qx, qy = next_pos(px, py, gmove)

                if is_clean(BOARD, qx, qy):
                    move = floods_move
                else:
                    move = floods_move

            print >> sys.stderr, 'dist2 == 20', dist3, dir_move(move)


        elif dist2 == 40:
            if len(dirs) == 1:
                dir0 = dirs[0]
                if dir0 in flood_dirs:
                    move = dir0

            if move is None:
                move = floods_move

            print >> sys.stderr, 'dist2 == 40', dir_move(move)


        # elif dist2 <= 50:
        if move is None:
            move = best_dest(x, y, px, py, limit=80)
            print >> sys.stderr, 'best_dest', (px, py), dir_move(move)

            if move is None:
                dist_map = {}
                for dir in flood_dirs:
                    c, d = next_pos(x, y, dir)
                    dist_map[dir] = distance3(px, py, c, d)

                dist_dirs = sorted(dist_map.items(), key=itemgetter(1))
                move = dist_dirs[-1][0]

            else:
                dirs2 = [dir for dir in dirs if dir in flood_dirs]
                if len(dirs2) > 1:
                    if move == ex and abs(dx) < abs(dy): move = ey
                    elif move == ey and abs(dx) >= abs(dy): move = ex

            print >> sys.stderr, 'dist2 <= 50', dir_move(move)

        if move is None: continue
        if dist2 <= 20: break

        c, d = next_pos(x, y, move)
        ngb = neighbors_clean_clean(BOARD, c, d)

        if len(ngb) == 0:
            move = floods_move
            print >> sys.stderr, 'len(ngb) == 0', dir_move(move)

        if len(ngb) == 1:
            dist3 = distance2(c, d, px, py)
            if dist3 <= 20:
                move = floods_move
                print >> sys.stderr, 'C', dir_move(move)

        if next_map[move] == 0:
            flood_dirs = [dir for dir in flood_dirs if dir != move]
            move = floods_move = flood_dirs[0]
            print >> sys.stderr, 'D', dir_move(move)

        if move == floods_move: pass
        elif flood_map[move] == flood_map[floods_move]: pass
        elif next_map[move] > 0.66 * next_map[floods_move]: pass
        else: move = floods_move

    return move


def best_move_fast(x, y):
    move = head_min(x, y)
    if move is None: move = default_move(x, y)
    if move is None: move = END
    print >> sys.stderr, DIR[move], time() - START
    return move


while True:
    mx, my, HEADS = read_stdin()
    HEADS_F = {}
    START = time()
    LASTMOVE = best_move_fast(mx, my)
    print DIR[LASTMOVE]

