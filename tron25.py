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
        points = [(0, (px, py))]
        heapq.heapify(points)

        while points:
            dist, point = heapq.heappop(points)
            c, d = point
            for (xx, yy) in neighbors_clean(BOARD, c, d):
                value = board_fill[yy][xx]
                dist2 = distance1(px, py, xx, yy)
                if dist2 <= dist: dist2 = dist + 1

                if value == 0:
                    board_fill[yy][xx] = dist2
                    heapq.heappush(points, (dist2, (xx, yy)))

                elif dist2 < value:
                    board_fill[yy][xx] = dist2
                    heapq.heappush(points, (dist2, (xx, yy)))
    return board_fill


def flood_find(x, y):
    board_copy = copy.deepcopy(BOARD)
    board_copy[y][x] = -2

    points = [(0, (x, y))]
    heapq.heapify(points)

    while points:
        dist, point = heapq.heappop(points)
        c, d = point

        for (xx, yy) in neighbors(board_copy, c, d):
            value = board_copy[yy][xx]
            if value == 0:
                dist2 = distance1(x, y, xx, yy)
                if dist2 <= dist: dist2 = dist + 1
                board_copy[yy][xx] = dist2
                heapq.heappush(points, (dist2, (xx, yy)))

            elif value >= ID_START and value in HEADS and HEADS[value] == (xx, yy):
                if not value in HEADS_F: HEADS_F[value] = set()
                HEADS_F[value].add(directions(xx - x, yy - y))


def flood_count(board_fill, x, y):
    board_copy = copy.deepcopy(BOARD)
    board_copy[y][x] = -2

    points = [(0, (x, y))]
    heapq.heapify(points)
    count = 0

    while points:
        dist, point = heapq.heappop(points)
        c, d = point

        for (xx, yy) in neighbors_clean(board_copy, c, d):
            if board_copy[yy][xx] == -2: continue

            dist2 = distance1(x, y, xx, yy)
            if dist2 <= dist: dist2 = dist + 1

            dist3 = board_fill[yy][xx]
            if dist3 == 0 or dist2 < dist3:
                count += 1
                board_copy[yy][xx] = dist2
                heapq.heappush(points, (dist2, (xx, yy)))
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

    elif len(flood_dirs) == 2:
        flood_dirs.sort(key=lambda x: flood_map[x], reverse=True)
        flood_dirs.sort(key=lambda x: neighbors[x], reverse=False)
        n1, n2 = neighbors[flood_dirs[0]], neighbors[flood_dirs[1]]
        if 3 == n1 == n2:
            flood_dirs.sort(key=lambda x: flood_map[x], reverse=False)
        if 2 == n1 == n2:
            flood_dirs.sort(key=lambda x: move_map[x], reverse=False)
        move = flood_dirs[0]

    else:
        flood_dirs.sort(key=lambda x: flood_map[x], reverse=True)
        flood_dirs.sort(key=lambda x: neighbors[x], reverse=False)
        n1, n2 = neighbors[flood_dirs[0]], neighbors[flood_dirs[1]]
        if 2 == n1 and 3 == n2:
            flood_dirs.sort(key=lambda x: flood_map[x], reverse=False)
        move = flood_dirs[0]

    if neighbors[move] > 1 and len(flood_dirs) > 1:
        c, d = next_pos(x, y, move)
        e, f = next_pos(c, d, move)

        if not is_clean(BOARD, e, f):
            c, d = next_pos(x, y, move)
            board_copy[d][c] = 1

            flood_dirs = [dir for dir in flood_dirs if dir != move]
            flood_map = dict()

            for dir in flood_dirs:
                c, d = next_pos(x, y, dir)
                flood_map[dir] = flood_count(board_copy, c, d)
            board_copy[d][c] = 0

            flood_dirs.sort(key=lambda x: flood_map[x], reverse=False)
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


def __distancea(x, y, c, d):
    return abs(x - c) + abs(y - d)

def __distanceb(x, y, c, d):
    return max(abs(x - c), abs(y - d))

def distance1(x, y, c, d):
    return __distancea(x, y, c, d)

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
    flood_find(x, y)
    if len(HEADS_F) == 0:
        return None

    # flood_map
    flood_map = dict()
    next_map = dict()

    for dir in move_dirs:
        c, d = next_pos(x, y, dir)
        board_fill[d][c] = ID_START + 10
        flood_map[dir] = flood_count(board_fill, c, d)
        board_fill[d][c] = 0

    flood_dirs = [dir for dir in move_dirs]
    flood_dirs.sort(key=lambda x: flood_map[x], reverse=True)

    if True:
        print >> sys.stderr, 'flood_map [',
        for k, v in flood_map.iteritems():
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

            if px < 3 or py < 3 or px > W - 4 or py > H - 4 and (
                    len(HEADS_F) == 1 and len(flood_dirs) >= 2):
                        move = floods_move

            elif len(dirs2) > 1:
                if move == ex and abs(dx) + 6 < abs(dy): move = ey
                elif move == ey and abs(dx) > abs(dy) + 4: move = ex

            # len(dirs2) == 1
            elif dist2 == 90 or dist2 == 250:
                if len(HEADS_F) == 1 and len(flood_dirs) == 3:
                    move = flood_dirs[1]

            elif dist2 == 360:
                if len(HEADS_F) == 1 and len(flood_dirs) == 3:
                    move = flood_dirs[2]

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

            if dist3 == 10 or dist3 == 50:
                move = guess_moves(ax, ay, px, py)
                if not move in flood_dirs:
                    move = floods_move
                elif flood_map[move] < 0.8 * flood_map[floods_move]:
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


        elif dist2 == 50:
            imove = inv_move(*LASTMOVE)
            if not imove in flood_dirs: pass
            elif len(flood_dirs) < 2: pass
            elif LASTMOVE in (UP, DOWN) and imove != ey: pass
            elif LASTMOVE in (LEFT, RIGHT) and imove != ex: pass
            else:
                for _ in range(4):
                    c, d = next_pos(x, y, imove)
                    if BOARD[d][c] != BOARD[y][x]: break
                    c, d = next_pos(px, py, imove)
                    if BOARD[d][c] != BOARD[py][px]: break
                else:
                    if imove == ey: move = ex
                    else: move = ey
            print >> sys.stderr, 'dist2 == 50', dir_move(move)


        # elif dist2 <= 50:
        if move is None:
            move = best_dest(x, y, px, py, limit=140)
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
                    if move == ex and abs(dx) + 6 < abs(dy): move = ey
                    elif move == ey and abs(dx) > abs(dy) + 4: move = ex
                    else: move = floods_move
                else: move = floods_move

            print >> sys.stderr, 'dist2 <= 50', dir_move(move)

        if move is None: continue
        if dist2 <= 20: break


        c, d = next_pos(x, y, move)
        dist3 = distance2(c, d, px, py)
        if dist3 <= 20:
            ngbs = neighbors_clean(BOARD, c, d)
            for e, f in ngbs:
                if distance2(px, py, e, f) == 10:
                    BOARD[f][e] = pid
                    fl = flood_count(board_fill, c, d)
                    print >> sys.stderr, 'E', (e, f),distance2(px, py, e, f), fl
                    if 2 > fl and len(flood_dirs) > 1:
                        flood_dirs = [dir for dir in flood_dirs if dir != move]
                        move = floods_move = flood_dirs[0]
                    BOARD[f][e] = 0

        if move == floods_move: pass
        elif flood_map[move] == flood_map[floods_move]: pass
        elif flood_map[move] > 0.63 * flood_map[floods_move]: pass
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

