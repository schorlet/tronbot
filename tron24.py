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
DEBUG = True


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
            c, d = points.pop()
            for (xx, yy) in neighbors(board_fill, c, d):
                if (xx, yy) in points:
                    continue
                value = board_fill[yy][xx]
                dist = distance2(px, py, xx, yy)
                if value == 0:
                    board_fill[yy][xx] = (dist, pid)
                    points.add((xx, yy))
                elif type(value) == tuple:
                    value2, qid = value
                    if dist < value2:
                        points.add((xx, yy))
                        board_fill[yy][xx] = (dist, pid)
                    elif pid != qid and dist == value2:
                        points.add((xx, yy))
                        board_fill[yy][xx] = (dist, pid)
    # if DEBUG:
        # for row in board_fill:
            # for cell in row:
                # if type(cell) == tuple:
                    # sys.stderr.write('{0: >5}'.format(cell[0]))
                # else:
                    # sys.stderr.write('{0: >5}'.format(cell))
            # sys.stderr.write('\n')
        # print >> sys.stderr, time() - START
        # print >> sys.stderr, 'fill_board'
    return board_fill


def __flood_cross(board_cross, x, y):
    count = 1
    # board_cross[y][x] = count
    points = {(x, y)}
    while points:
        c, d = points.pop()
        for (xx, yy) in neighbors(board_cross, c, d):
            value = board_cross[yy][xx]
            if value == 0:
                count += 1
                board_cross[yy][xx] = -1
                points.add((xx, yy))
            elif 0 < value < ID_START:
                dist = distance1(x, y, xx, yy)
                if dist < value:
                    count += 1
                    board_cross[yy][xx] = -1
                    points.add((xx, yy))
    return count - 1


def flood_cross(x, y):
    board_cross = copy.deepcopy(BOARD)
    board_cross[y][x] = -2

    for pid, pos in HEADS.items():
        px, py = pos
        moves = (UP, RIGHT, DOWN, LEFT)
        for move in moves:
            c, d = next_pos(px, py, move)
            while in_board(c, d):
                value = board_cross[d][c]
                if value == 0:
                    board_cross[d][c] = distance1(px, py, c, d)
                c, d = next_pos(c, d, move)
    count = __flood_cross(board_cross, x, y)
    if DEBUG:
        for row in board_cross:
            for cell in row:
                sys.stderr.write('{0: >5}'.format(cell))
            sys.stderr.write('\n')
        print >> sys.stderr, time() - START
    return count


def flood_count(board_fill, x, y, hf=False):
    board_copy = copy.deepcopy(BOARD)
    count = 1
    board_copy[y][x] = -2
    points = {(x, y)}
    ratio = 1 if hf else 0.5
    while points:
        c, d = points.pop()
        for (xx, yy) in neighbors(board_copy, c, d):
            value = board_copy[yy][xx]
            if value == 0:
                # count += 1
                # board_copy[yy][xx] = count
                points.add((xx, yy))

                dist2 = board_fill[yy][xx]
                if type(dist2) == tuple:
                    dist = distance2(x, y, xx, yy)
                    value2, pid = dist2
                    if dist < ratio * value2:
                        count += 1
                        board_copy[yy][xx] = count
                    else:
                        board_copy[yy][xx] = -1
                elif dist2 == 0:
                    count += 1
                    board_copy[yy][xx] = count
                else:
                    board_copy[yy][xx] = -1
                # --
            elif hf and value >= ID_START and value in HEADS and HEADS[value] == (xx, yy):
                if not value in HEADS_F: HEADS_F[value] = set()
                HEADS_F[value].add(directions(xx - x, yy - y))
    if DEBUG:
        for row in board_copy:
            for cell in row:
                sys.stderr.write('{0: >5}'.format(cell))
            sys.stderr.write('\n')
        print >> sys.stderr, time() - START
        print >> sys.stderr, HEADS_F
    print >> sys.stderr, 'flood_count', count - 1
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
        board_copy[d][c] = 10
        points = {(c, d)}

        while points:
            c, d = points.pop()
            for (xx, yy) in neighbors(board_copy, c, d):
                if (xx, yy) in points:
                    continue
                # elif move == UP and yy >= y:
                    # continue
                # elif move == RIGHT and xx <= x:
                    # continue
                # elif move == DOWN and yy <= y:
                    # continue
                # elif move == LEFT and xx >= x:
                    # continue

                value = board_copy[yy][xx]
                if value == 0:
                    dist = distance2(x, y, xx, yy)
                    dist2 = board_fill[yy][xx]

                    if type(dist2) == tuple:
                        value2, pid = dist2
                        if dist < value2:
                            count += 1
                            board_copy[yy][xx] = dist
                            points.add((xx, yy))

                    elif dist2 == 0:
                        count += 1
                        board_copy[yy][xx] = dist
                        points.add((xx, yy))
    if DEBUG:
        for row in board_copy:
            for cell in row:
                if type(cell) == tuple:
                    sys.stderr.write('{0: >5}'.format(cell[0]))
                else:
                    sys.stderr.write('{0: >5}'.format(cell))
            sys.stderr.write('\n')
        print >> sys.stderr, time() - START
        print >> sys.stderr, 'flood_fill', count, DIR[move]
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

    print >> sys.stderr, 'default_move: move_dirs', move_dirs

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
    print >> sys.stderr, 'default_move: flood_map', flood_map
    print >> sys.stderr, 'default_move: neighbors', neighbors

    flood_dirs = sorted(flood_map.items(), key=itemgetter(1))
    max_flood = flood_dirs[-1][1]
    flood_dirs = [k for k, v in flood_dirs if v == max_flood]
    print >> sys.stderr, 'default_move: flood_dirs', flood_dirs

    # flood_dirs == 1
    if len(flood_dirs) == 1:
        move = flood_dirs[0]

    else:
        flood_dirs.sort(key=lambda x: flood_map[x], reverse=True)
        flood_dirs.sort(key=lambda x: neighbors[x], reverse=False)
        move = flood_dirs[0]

    print >> sys.stderr, 'default_move: move', x, y, move
    return move


def __best_dest(x, y, hx, hy, limit):
    board_copy = copy.deepcopy(BOARD)
    paths = None
    # set([(x, y)])
    points = [(0, [(x, y)])]
    heapq.heapify(points)
    while paths is None and points:
        if time() - START > 0.09:
            break
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
        if DEBUG:
            board_tmp = copy.deepcopy(BOARD)
            i = 1
            for xx, yy in paths[1:-1]:
                board_tmp[yy][xx] = i
                i += 1
            for row in board_tmp:
                for cell in row:
                    sys.stderr.write('{0: >5}'.format(cell))
                sys.stderr.write('\n')
    print >> sys.stderr, 'best_dest', move, time() - START
    return move


def distance1(x, y, c, d):
    return abs(x - c) + abs(y - d)

def distance2(x, y, c, d):
    return 10 * (abs(x - c)**2 + abs(y - d)**2)

def distance3(x, y, c, d):
    return (abs(x - c)**2 + abs(y - d)**2)**0.5

def p(l):
    import sys
    for y in range(20):
        for x in range(20):
            d = distance2(10, 10, x, y)
            if d > l: d = 0
            sys.stderr.write('{0: >5}'.format(d))
        sys.stderr.write('\n')


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

    if DEBUG:
        print >> sys.stderr, 'move_map [',
        for k, v in move_map.iteritems():
            print >> sys.stderr, '(%d, %s), ' % (v, DIR[k]),
        print >> sys.stderr, ']'

    # move_dirs <= 1
    if len(move_dirs) <= 1:
        return None

    move = None
    board_fill = fill_board()
    count_flood = flood_count(board_fill, x, y, hf=True)
    if len(HEADS_F) == 0:
        return None

    # flood_map
    flood_map = {
            UP:    flood_fill(board_fill, x, y, UP),
            RIGHT: flood_fill(board_fill, x, y, RIGHT),
            DOWN:  flood_fill(board_fill, x, y, DOWN),
            LEFT:  flood_fill(board_fill, x, y, LEFT) }

    flood_dirs  = sorted(flood_map.items(), key=itemgetter(1), reverse=True)
    flood_dirs  = tuple(k for k, v in flood_dirs if v > 0)

    if DEBUG:
        print >> sys.stderr, 'flood_map [',
        for k, v in flood_map.iteritems():
            print >> sys.stderr, '(%d, %s), ' % (v, DIR[k]),
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
        dirs = tuple(e for e in (ex, ey) if e != (0, 0))
        print >> sys.stderr, 'PID', [DIR[dir] for dir in dirs], pid, ',', dist2

        if 80 < dist2 < 5000:
            move = best_dest(x, y, px, py)
            print >> sys.stderr, '130 < dist2 < 5000', dir_move(move)

        elif dist2 == 10:
            ax, ay = last_pos(x, y)
            dist3 = distance2(ax, ay, px, py)
            if dist3 == 20 or dist3 == 50:
                move = LASTMOVE
            else:
                move = floods_move
            print >> sys.stderr, 'dist2 == 10', dist3, dir_move(move)

        elif dist2 == 20:
            ax, ay = last_pos(x, y)
            dist3 = distance2(ax, ay, px, py)
            if dist3 == 10:
                move = floods_move
            if dist3 == 50:
                move = floods_move

        elif dist2 <= 80:
            if LEFT in flood_dirs and RIGHT in dirs:
                if flood_map[RIGHT] > flood_map[LEFT]: move = RIGHT
            elif RIGHT in flood_dirs and LEFT in dirs:
                if flood_map[RIGHT] < flood_map[LEFT]: move = LEFT
            elif UP in flood_dirs and DOWN in dirs:
                if flood_map[DOWN] > flood_map[UP]: move = DOWN
            elif DOWN in flood_dirs and UP in dirs:
                if flood_map[DOWN] < flood_map[UP]: move = UP

            if not move is None:
                pass
            elif LEFT in flood_dirs and LEFT in dirs:
                if dx < 0: move = LEFT
            elif RIGHT in flood_dirs and RIGHT in dirs:
                if dx > 0: move = RIGHT
            elif DOWN in flood_dirs and DOWN in dirs:
                if dy > 0: move = DOWN
            elif UP in flood_dirs and UP in dirs:
                if dy < 0: move = UP

            if move is None:
                move = floods_move

            print >> sys.stderr, 'dist2 <= 80', dir_move(move)

        if move is None: continue
        if move == floods_move: break
        if flood_map[move] == flood_map[floods_move]: break

        c, d = next_pos(x, y, move)
        ngb = neighbors_clean_clean(BOARD, c, d)

        if len(ngb) == 0:
            move = floods_move
            print >> sys.stderr, 'len(ngb) == 0', dir_move(move)

        if len(ngb) == 1:
            dist3 = distance2(c, d, px, py)
            if dist3 == 20:
                move = floods_move
                print >> sys.stderr, 'D', dir_move(move)
            else:
                next_flood = flood_fill(board_fill, c, d, move)
                print >> sys.stderr, 'B', next_flood, '<', flood_map[move]
                if next_flood < flood_map[move] or flood_map[move] < 10:
                    move = floods_move
            print >> sys.stderr, 'len(ngb) == 1', dir_move(move)

        else:
            next_flood = flood_fill(board_fill, c, d, move)
            print >> sys.stderr, 'E', next_flood, '<', flood_map[move]
            if next_flood < flood_map[move] or flood_map[move] < 10:
                move = floods_move
            print >> sys.stderr, 'len(ngb) == 2', dir_move(move)

        # print >> sys.stderr, '-------------'
        # for dir in move_dirs:
            # pos = next_pos(x, y, dir)
            # count = flood_cross(*pos)
            # print >> sys.stderr, 'move_dirs', dir_move(dir), count
    return move


def best_move_fast(x, y):
    move = head_min(x, y)
    if move is None: move = default_move(x, y)
    if move is None: move = END
    print >> sys.stderr, DIR[move], time() - START
    return move


if __name__ == '__main__':
    ID_START = 1001
    W, H = 15, 10
    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    # BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0, 1002,    0,    0,    0,    0,    0]
    # BOARD[2] = [1001, 1001, 1001, 1001,    0,    0,    0,    0,    0, 1002,    0,    0,    0,    0,    0]
    # BOARD[3] = [   0,    0,    0,    0,    0,    0,    0,    0,    0, 1002,    0,    0,    0,    0,    0]
    # BOARD[4] = [   0,    0,    0,    0,    0,    0,    0,    0,    0, 1002,    0,    0,    0,    0,    0]
    # START = time()
    # mx, my = 3, 2
    # HEADS[1002] = (9, 4)
    # HEADS_F = {}
    # best_move_fast(mx, my)

    # BOARD[0] = [   0,    0,    0,    0,    0, 1001,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[1] = [   0,    0,    0,    0,    0, 1001,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[2] = [   0,    0,    0,    0,    0, 1001,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[3] = [   0,    0,    0,    0,    0, 1001,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[4] = [   0,    0,    0,    0, 1002, 1001,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[5] = [   0,    0,    0,    0, 1002, 1001, 1001, 1001, 1001,    0,    0,    0,    0,    0,    0]
    # BOARD[6] = [   0,    0,    0,    0, 1002,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[7] = [   0,    0,    0,    0, 1002,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[8] = [   0,    0,    0,    0, 1002,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[9] = [   0,    0,    0,    0, 1002, 1002,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # START = time()
    # mx, my = 5, 0
    # HEADS[1002] = (5, 9)
    # HEADS_F = {}
    # best_move_fast(mx, my)

    # BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001, 1001, 1001, 1001]
    # BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001, 1001, 1001, 1001]
    # BOARD[2] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001,    0, 1002, 1002]
    # BOARD[3] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001, 1002, 1002, 1002]
    # BOARD[4] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001, 1002, 1002, 1002]
    # BOARD[5] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001, 1002, 1002, 1002]
    # BOARD[6] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002,    0,    0,    0, 1002]
    # BOARD[7] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002,    0,    0,    0, 1002]
    # BOARD[8] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002,    0,    0,    0, 1002]
    # BOARD[9] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002, 1002, 1002, 1002, 1002]
    # START = time()
    # mx, my = 11, 5
    # HEADS[1002] = (12, 3)
    # HEADS_F = {}
    # best_move_fast(mx, my)

    # BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[2] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[3] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[4] = [1001, 1001, 1001, 1001, 1001,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[5] = [   0, 1002, 1002, 1002, 1002,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[6] = [   0, 1002,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[7] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[8] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[9] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # START = time()
    # mx, my = 0, 4
    # HEADS[1002] = (1, 6)
    # HEADS_F = {}
    # best_move_fast(mx, my)


    # BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[2] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[3] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[4] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[5] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[6] = [   0,    0,    0,    0, 1002, 1001,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[7] = [   0, 1002, 1002, 1002, 1002, 1001, 1001, 1001, 1001,    0,    0,    0,    0,    0,    0]
    # BOARD[8] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[9] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # START = time()
    # mx, my = 5, 6
    # HEADS[1002] = (4, 6)
    # HEADS_F = {}
    # best_move_fast(mx, my)


    # BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[2] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[3] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[4] = [   0,    0,    0, 1001, 1001, 1001, 1001, 1001, 1001, 1001, 1001, 1001, 1001, 1001, 1001]
    # BOARD[5] = [   0,    0, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002]
    # BOARD[6] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[7] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[8] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[9] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # START = time()
    # mx, my = 3, 4
    # HEADS[1002] = (2, 5)
    # HEADS_F = {}
    # best_move_fast(mx, my)

    # BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[2] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[3] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[4] = [   0, 1001, 1001, 1001, 1001, 1001, 1001, 1001, 1001, 1001, 1001, 1001, 1001, 1001, 1001]
    # BOARD[5] = [1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002]
    # BOARD[6] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[7] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[8] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[9] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # START = time()
    # mx, my = 1, 4
    # HEADS[1002] = (0, 5)
    # HEADS_F = {}
    # best_move_fast(mx, my)


    # BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[2] = [1002, 1002, 1002, 1002,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[3] = [1001, 1001, 1001, 1001, 1002, 1002, 1002,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[4] = [   0,    0,    0, 1001, 1001, 1001, 1001, 1002, 1002, 1002, 1002,    0,    0,    0, 1002]
    # BOARD[5] = [   0,    0,    0,    0,    0,    0,    0, 1001, 1001, 1001, 1001, 1002, 1002, 1002, 1002]
    # BOARD[6] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001, 1001, 1001, 1001]
    # BOARD[7] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001, 1001, 1001, 1001, 1001]
    # BOARD[8] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[9] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # START = time()
    # mx, my = 10, 7
    # HEADS[1002] = (14, 4)
    # HEADS_F = {}
    # best_move_fast(mx, my)

    # BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[2] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[3] = [   0,    0,    0,    0, 1001, 1001, 1002,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[4] = [   0,    0,    0, 1001, 1001,    0, 1002,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[5] = [   0,    0, 1001, 1001, 1002, 1002, 1002,    0,    0, 1003, 1003, 1003, 1003, 1003,    0]
    # BOARD[6] = [   0, 1001, 1001,    0, 1002, 1002, 1002, 1002, 1002, 1003,    0,    0,    0,    0,    0]
    # BOARD[7] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[8] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[9] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # START = time()
    # mx, my = 5, 3
    # HEADS[1002] = (8, 6)
    # HEADS[1003] = (9, 6)
    # LASTMOVE = RIGHT
    # HEADS_F = {}
    # best_move_fast(mx, my)

    # BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[2] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0,    0]
    # BOARD[3] = [1001,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0,    0]
    # BOARD[4] = [1001, 1001, 1001, 1001, 1001, 1001, 1001, 1001, 1001, 1001, 1001, 1001,    0,    0,    0]
    # BOARD[5] = [1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002,    0,    0,    0]
    # BOARD[6] = [1002,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002,    0,    0,    0]
    # BOARD[7] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002,    0,    0,    0]
    # BOARD[8] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[9] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # START = time()
    # mx, my = 0, 3
    # HEADS[1002] = (0, 6)
    # HEADS_F = {}
    # best_move_fast(mx, my)

    # BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[2] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0,    0]
    # BOARD[3] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0,    0]
    # BOARD[4] = [   0, 1001, 1001, 1001, 1001, 1001, 1001, 1001, 1001, 1001, 1001, 1001,    0,    0,    0]
    # BOARD[5] = [1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002,    0,    0,    0]
    # BOARD[6] = [1002,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002,    0,    0,    0]
    # BOARD[7] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002,    0,    0,    0]
    # BOARD[8] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[9] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # START = time()
    # mx, my = 1, 4
    # HEADS[1002] = (0, 6)
    # HEADS_F = {}
    # best_move_fast(mx, my)


    # BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[2] = [   0,    0,    0,    0,    0,    0,    0, 1002,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[3] = [   0,    0,    0,    0,    0,    0,    0, 1002,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[4] = [1001,    0,    0,    0,    0,    0,    0, 1002,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[5] = [   0,    0,    0,    0,    0,    0,    0, 1002,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[6] = [   0,    0,    0,    0,    0,    0,    0, 1002,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[7] = [   0,    0,    0,    0,    0,    0,    0, 1002,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[8] = [   0,    0,    0,    0,    0,    0,    0, 1002,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[9] = [   0,    0,    0,    0,    0,    0,    0, 1002,    0,    0,    0,    0,    0,    0,    0]
    # START = time()
    # mx, my = 0, 4
    # HEADS[1002] = (7, 2)
    # HEADS_F = {}
    # best_move_fast(mx, my)



    # BOARD[0] = [   0,    0, 1002, 1001,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[1] = [   0,    0, 1002, 1001,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[2] = [   0,    0, 1002, 1001,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[3] = [   0,    0, 1002, 1001,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[4] = [   0,    0, 1002, 1001,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[5] = [   0,    0, 1002, 1001,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[6] = [   0,    0, 1002, 1001,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[7] = [   0,    0, 1002, 1001,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[8] = [   0, 1002, 1002, 1001,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[9] = [   0,    0,    0, 1001,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # START = time()
    # mx, my = 3, 9
    # HEADS[1002] = (1, 8)
    # HEADS_F = {}
    # best_move_fast(mx, my)


    # BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002, 1001,    0,    0]
    # BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002, 1001,    0,    0]
    # BOARD[2] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002, 1001,    0,    0]
    # BOARD[3] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002, 1001,    0,    0]
    # BOARD[4] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002, 1001,    0,    0]
    # BOARD[5] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002, 1001,    0,    0]
    # BOARD[6] = [   0,    0,    0,    0,    0,    0,    0,    0, 1002, 1002, 1002, 1002, 1001,    0,    0]
    # BOARD[7] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002, 1002, 1001,    0,    0]
    # BOARD[8] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002, 1002, 1001,    0,    0]
    # BOARD[9] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0]
    # START = time()
    # mx, my = 12, 9
    # HEADS[1002] = (8, 6)
    # HEADS_F = {}
    # best_move_fast(mx, my)

    # BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[2] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[3] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[4] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[5] = [   0,    0,    0,    0, 1002, 1002,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[6] = [   0, 1001, 1001,    0, 1002, 1002,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[7] = [   0, 1001, 1001, 1001, 1002, 1002, 1002, 1002, 1002,    0,    0,    0,    0,    0,    0]
    # BOARD[8] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[9] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # START = time()
    # mx, my = 2, 6
    # HEADS[1002] = (4, 5)
    # HEADS_F = {}
    # best_move_fast(mx, my)
#
    # BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0,    0]
    # BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0,    0]
    # BOARD[2] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0,    0]
    # BOARD[3] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0,    0]
    # BOARD[4] = [   0,    0,    0,    0,    0,    0, 1002, 1001, 1001, 1001, 1001, 1001,    0,    0,    0]
    # BOARD[5] = [   0,    0,    0,    0,    0,    0, 1002,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[6] = [   0,    0,    0,    0,    0,    0, 1002,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[7] = [   0,    0,    0,    0,    0,    0, 1002,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[8] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[9] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # START = time()
    # mx, my = 7, 4
    # LASTMOVE = (-1, 0)
    # HEADS[1002] = (6, 4)
    # HEADS_F = {}
    # best_move_fast(mx, my)

    # BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0,    0]
    # BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0,    0]
    # BOARD[2] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0,    0]
    # BOARD[3] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0,    0]
    # BOARD[4] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0,    0]
    # BOARD[5] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0,    0]
    # BOARD[6] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0,    0]
    # BOARD[7] = [   0,    0,    0,    0,    0,    0, 1002, 1001, 1001, 1001, 1001, 1001,    0,    0,    0]
    # BOARD[8] = [   0,    0,    0,    0,    0,    0, 1002,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[9] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # START = time()
    # mx, my = 7, 7
    # LASTMOVE = (-1, 0)
    # HEADS[1002] = (6, 7)
    # HEADS_F = {}
    # best_move_fast(mx, my)

    # W, H = 30, 20
    # BOARD = [[0 for _ in range(W)] for _ in range(H)]
    # BOARD[14][3] = 1002
    # BOARD[14][4] = 1002
    # BOARD[15][4] = 1001
    # BOARD[15][3] = 1001
    # BOARD[15][2] = 1001
    # BOARD[18][0] = 1003
    # BOARD[18][1] = 1003
    # START = time()
    # mx, my = 4, 14
    # LASTMOVE = (1, 0)
    # HEADS[1001] = (2, 15)
    # HEADS[1003] = (1, 18)
    # HEADS_F = {}
    # best_move_fast(mx, my)

    # BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0,    0,    0,    0,    0]
    # BOARD[1] = [1001, 1001, 1001,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[2] = [   0,    0,    0,    0,    0,    0, 1001, 1001, 1001, 1001, 1001, 1001,    0,    0,    0]
    # BOARD[3] = [   0,    0,    0,    0,    0,    0, 1001,    0,    0,    0,    0,    0, 1001,    0,    0]
    # BOARD[4] = [   0,    0,    0,    0,    0,    0, 1001,    0,    0,    0,    0,    0, 1001,    0,    0]
    # BOARD[5] = [   0,    0,    0,    0,    0,    0, 1001,    0,    0,    0,    0,    0, 1001,    0,    0]
    # BOARD[6] = [   0,    0,    0,    0,    0,    0, 1001,    0,    0,    0,    0,    0, 1001,    0,    0]
    # BOARD[7] = [   0,    0,    0,    0,    0,    0, 1001,    0,    0,    0,    0,    0, 1001,    0,    0]
    # BOARD[8] = [   0,    0,    0,    0,    0,    0, 1001, 1001, 1001, 1001, 1001, 1001, 1001,    0,    0]
    # BOARD[9] = [   0,    0,    0,    0,    0,    0,    0, 1001,    0,    0,    0,    0,    0,    0,    0]
    # START = time()
    # mx, my = 12, 3
    # HEADS_F = {}
    # DM = list()
    # best_move_fast(mx, my)

    BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[1] = [1001, 1001, 1001,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[2] = [   0,    0,    0,    0,    0,    0, 1001, 1001, 1001, 1001, 1001, 1001,    0,    0,    0]
    BOARD[3] = [   0,    0,    0,    0,    0,    0, 1001,    0,    0,    0,    0,    0, 1001,    0,    0]
    BOARD[4] = [   0,    0,    0,    0,    0,    0, 1001,    0,    0,    0,    0,    0, 1001,    0,    0]
    BOARD[5] = [   0,    0,    0,    0,    0,    0, 1001,    0,    0,    0,    0,    0, 1001,    0,    0]
    BOARD[6] = [   0,    0,    0,    0,    0,    0, 1001,    0,    0,    0,    0,    0, 1001,    0,    0]
    BOARD[7] = [   0,    0,    0,    0,    0,    0, 1001, 1001, 1001, 1001, 1001, 1001, 1001,    0,    0]
    BOARD[8] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[9] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    START = time()
    mx, my = 12, 3
    HEADS_F = {}
    DM = list()
    best_move_fast(mx, my)

    # - Is there a snake or wall directly in front of me? If so, turn into the area [left or right]
    # with the most open space.
    #
    # - Are other snakes heading in my direction? Who is closer to our intersection?
    # If it is me, keep going, if it is a tie or the other snake, change direction
    #
    # - Is another snake near me moving in paralell to me? Who is ahead? If I am ahead,
    # turn in the direction of that snake. If I am behind, turn away.
    #
    # - Am I stuck in an enclosed space? If so, stick to the walls to better use the area I am left with.


