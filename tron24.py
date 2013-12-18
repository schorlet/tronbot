import sys, copy, heapq
from time import time
from collections import deque
from operator import itemgetter

UP, RIGHT, DOWN, LEFT, END = (0, -1), (1, 0), (0, 1), (-1, 0), (0, 0)
DIR = {UP: 'UP', RIGHT: 'RIGHT', DOWN: 'DOWN', LEFT: 'LEFT', END: 'END'}
W, H = 30, 20
BOARD = [[0 for _ in range(W)] for _ in range(H)]
ID_START = 10001
HEADS, HEADS_F = None, None
BOARDS_FILL = {}
LASTMOVE = None
DEBUG = True


def clear_pid(pid):
    for y in xrange(H):
        for x in xrange(W):
            if BOARD[y][x] == pid: BOARD[y][x] = 0


def read_stdin():
    heads = {}
    nbj, mid = map(int, raw_input().split(' '))
    mid = ID_START + mid
    for pid in range(ID_START, ID_START + nbj):
        x0, y0, x1, y1 = map(int, raw_input().split(' '))
        if (x1, y1) == (-1, -1):
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
    return in_board(x, y) and board[y][x] == 0


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


def neighbors_clean_heads(board, x, y):
    ngb = []
    for (xx, yy) in (next_pos(x, y, UP),   next_pos(x, y, RIGHT),
                     next_pos(x, y, DOWN), next_pos(x, y, LEFT)):
        if in_board(xx, yy) and (
                board[yy][xx] == 0 or (xx, yy) in HEADS.values()):
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


def fill_board(board, heads):
    board_fill = copy.deepcopy(board)

    for pid, pos in heads.items():
        px, py = pos
        print >> sys.stderr, 'fill_board', pos
        points = [(0, (px, py))]
        heapq.heapify(points)

        while points:
            dist, point = heapq.heappop(points)
            c, d = point
            for (xx, yy) in neighbors_clean(board, c, d):
                value = board_fill[yy][xx]
                dist2 = distance1(px, py, xx, yy)
                if dist2 <= dist: dist2 = dist + 1

                if value == 0:
                    board_fill[yy][xx] = dist2
                    heapq.heappush(points, (dist2, (xx, yy)))

                elif dist2 < value:
                    board_fill[yy][xx] = dist2
                    heapq.heappush(points, (dist2, (xx, yy)))
    # if DEBUG:
        # for row in board_fill:
            # for cell in row:
                # if 0 < cell < ID_START:
                    # sys.stderr.write('{0: >6}'.format(cell))
                # else:
                    # sys.stderr.write('{0: >6}'.format(cell))
            # sys.stderr.write('\n')
        # print >> sys.stderr, time() - START
    return board_fill


def flood_find(x, y):
    board_copy = copy.deepcopy(BOARD)
    board_copy[y][x] = -2

    points = deque([(x, y)])

    while points:
        point = points.pop()
        c, d = point

        for (xx, yy) in neighbors_clean_heads(board_copy, c, d):
            value = board_copy[yy][xx]
            if value == 0:
                board_copy[yy][xx] = 1
                points.append((xx, yy))

            elif not value in HEADS_F:
                HEADS_F[value] = directions(xx - x, yy - y)
                if len(HEADS_F) == len(HEADS):
                    points = None
                    break
    # if DEBUG:
        # for row in board_copy:
            # for cell in row:
                # sys.stderr.write('{0: >6}'.format(cell))
            # sys.stderr.write('\n')
        # print >> sys.stderr, time() - START
    print >> sys.stderr, 'flood_find', HEADS_F


def flood_count(board_fill, x, y, moved=END):
    board_copy = copy.deepcopy(BOARD)
    return flood_count_2(board_copy, board_fill, x, y, moved)


def flood_count_2(board_copy, board_fill, x, y, moved=END):
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
    # if DEBUG:
        # for row in board_copy:
            # for cell in row:
                # sys.stderr.write('{0: >6}'.format(cell))
            # sys.stderr.write('\n')
        # print >> sys.stderr, 'flood_count', count, DIR[moved]
        # print >> sys.stderr, 'flood_count', count, time() - START
    return count


def default_move(x, y):
    move_map = {
            UP:    max_move(x, y, UP),
            RIGHT: max_move(x, y, RIGHT),
            DOWN:  max_move(x, y, DOWN),
            LEFT:  max_move(x, y, LEFT) }
    move_dirs = tuple(k for k, v in move_map.items() if v > 0)
    move_dirs  = sorted(move_dirs, key=lambda x: move_map[x])

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
        board_copy[d][c] = 1
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
        next_map = dict()
        for dir in flood_dirs:
            next_map[dir] = 0
            c, d = next_pos(x, y, dir)
            board_copy[d][c] = 1
            for ngb in neighbors_clean(board_copy, c, d):
                next_map[dir] = max(next_map[dir], flood_count(board_copy, *ngb))
            board_copy[d][c] = 0

        flood_dirs.sort(key=lambda x: move_map[x], reverse=False)
        flood_dirs.sort(key=lambda x: neighbors[x], reverse=False)
        flood_dirs.sort(key=lambda x: next_map[x], reverse=True)
        move = flood_dirs[0]

    return move


def __best_dest(x, y, hx, hy, limit):
    board_copy = copy.deepcopy(BOARD)
    paths = None

    points = [(0, [(x, y)])]
    heapq.heapify(points)

    while paths is None and points:
        value1, points2 = heapq.heappop(points)
        px, py = points2[-1]

        for (xx, yy) in neighbors_clean_heads(board_copy, px, py):
            if (xx, yy) == (hx, hy):
                paths = points2 + [(xx, yy)]
                break

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
    return move


def distance1(x, y, c, d):
    return abs(x - c) + abs(y - d)

def distance2(x, y, c, d):
    return 10 * (abs(x - c)**2 + abs(y - d)**2)

def distance3(x, y, c, d):
    return 33 * (abs(x - c)**2 + abs(y - d)**2)**0.5

def distance4(x, y, c, d):
    return max(abs(x - c), abs(y - d))

def p(l):
    import sys
    for y in range(16):
        for x in range(16):
            d = distance2(8, 8, x, y)
            if d > l: sys.stderr.write('{0: >5}'.format(0))
            else: sys.stderr.write('{0: >5.1f}'.format(d))
        sys.stderr.write('\n')


def directions(x, y):
    dx = (   0 if x == 0 else 1 if x > 0 else -1 , 0)
    dy = (0, 0 if y == 0 else 1 if y > 0 else -1)
    return dx, dy


def max_play(board, x, y, px, py, board_fill, n):
    best_score = -1000

    ngbs = neighbors_clean(board, x, y)
    if len(ngbs) == 0:
        return best_score

    for c, d in ngbs:
        board[d][c] = board[y][x]

        if not board_fill is None:
            board_copy = copy.deepcopy(board)
            score = flood_count_2(board_copy, board_fill, c, d)
        else:
            score = min_play(board, c, d, px, py, n + 1)

        board[d][c] = 0
        if score > best_score:
            best_score = score

        # if time() - START > 0.09:
            # break
    return best_score


def min_play(board, x, y, px, py, n):
    best_score = 1000

    ngbs = neighbors_clean(board, px, py)
    if len(ngbs) == 0:
        return best_score

    board_fill = None

    for c, d in ngbs:
        board[d][c] = board[py][px]

        if n == 3:
            if not (c, d) in BOARDS_FILL:
                head = {board[py][px]: (c, d)}
                BOARDS_FILL[(c, d)] = fill_board(board, head)
            board_fill = BOARDS_FILL[(c, d)]

        score = max_play(board, x, y, c, d, board_fill, n + 1)
        board[d][c] = 0
        # print >> sys.stderr, '.' * n, 'min_play', (x, y), (c, d), score

        if score < best_score:
            best_score = score

        # if time() - START > 0.09:
            # break
    return best_score


def minimax(x, y, px, py, move_map, n=1):
    # print >> sys.stderr, 'minimax', (x, y), (px, py), time() - START
    board = copy.deepcopy(BOARD)
    best_score = 0
    best_move = None

    move_dirs = [k for k, v in move_map.items() if v > 0]
    move_dirs.sort(key=lambda x: move_map[x])

    if LASTMOVE in move_dirs:
        move_dirs.remove(LASTMOVE)
        move_dirs.insert(0, LASTMOVE)

    for dir in move_dirs:
        c, d = next_pos(x, y, dir)

        board[d][c] = board[y][x]
        score = min_play(board, c, d, px, py, n)
        board[d][c] = 0
        print >> sys.stderr, 'minimax', score, DIR[dir], time() - START
        if score > best_score:
            best_score = score
            best_move = dir
        # if time() - START > 0.08:
            # break
    return best_move


def head_min(x, y):
    # move_map
    move_map = {
            UP:    max_move(x, y, UP),
            RIGHT: max_move(x, y, RIGHT),
            DOWN:  max_move(x, y, DOWN),
            LEFT:  max_move(x, y, LEFT) }
    move_dirs  = sorted(move_map.items(), key=itemgetter(1), reverse=False)
    move_dirs = tuple(k for k, v in move_dirs if v > 0)

    # move_dirs <= 1
    if len(move_dirs) <= 1:
        return None

    move = None
    board_fill = fill_board(BOARD, HEADS)
    flood_find(x, y)
    if len(HEADS_F) == 0:
        return None

    # heads
    heads = []
    for pid in HEADS_F:
        px, py = HEADS[pid]
        dist = distance2(x, y, px, py)
        heads.append((dist, pid))
    heads.sort()


    dir_move = lambda x: DIR[x] if x in DIR else None
    inv_move = lambda x, y: (x * -1, y * -1)
    last_pos = lambda x, y: next_pos(x, y, inv_move(*LASTMOVE))

    while move is None and heads:
        dist2, pid = heads.pop(0)
        px, py = HEADS[pid]
        dx, dy = px - x, py - y

        ex, ey = HEADS_F[pid]
        dirs = tuple(e for e in (ex, ey) if e != END)
        print >> sys.stderr, 'PID', [DIR[dir] for dir in dirs], pid, ',', dist2


        if 40 < dist2:
            # flood_map
            flood_map = dict()

            for dir in move_dirs:
                c, d = next_pos(x, y, dir)
                board_fill[d][c] = board_fill[y][x]
                flood_map[dir] = flood_count(board_fill, c, d)
                board_fill[d][c] = 0

            if True:
                print >> sys.stderr, 'flood_map [',
                for k, v in flood_map.iteritems():
                    print >> sys.stderr, '(%d, %s),' % (v, DIR[k]),
                print >> sys.stderr, ']'

            flood_dirs = [dir for dir in move_dirs]
            flood_dirs.sort(key=lambda x: flood_map[x], reverse=True)
            floods_move = flood_dirs[0]


            move = best_dest(x, y, px, py)
            print >> sys.stderr, 'best_dest', (px, py), dir_move(move)
            if move is None: continue
            ratio = 0.86

            dirs2 = [dir for dir in dirs if dir in flood_dirs]

            if x < 2 or y < 2 or x > W - 3 or y > H - 3:
                ratio = 0.98

            elif x < 3 or y < 3 or x > W - 4 or y > H - 4:
                ratio = 0.96

            if (len(dirs2) == 1 and (dist2 == 90 or dist2 == 250) and
                    len(HEADS_F) == 1 and len(flood_dirs) == 3):
                print >> sys.stderr, 'LASTMOVE', (px, py), dir_move(LASTMOVE)
                if LASTMOVE in (UP, DOWN) and LASTMOVE != ey: pass
                elif LASTMOVE in (LEFT, RIGHT) and LASTMOVE != ex: pass
                else:
                    move = flood_dirs[1]
                    ratio = 0.50

            if move == floods_move: pass
            elif flood_map[move] == flood_map[floods_move]: pass
            elif flood_map[move] > ratio * flood_map[floods_move]: pass
            else: move = floods_move

            print >> sys.stderr, '40 < dist2,', ratio, dir_move(move)


        elif dist2 in (10, 40):
            flood_map = dict()

            for dir in move_dirs:
                c, d = next_pos(x, y, dir)
                board_fill[d][c] = board_fill[y][x]
                flood_map[dir] = flood_count(board_fill, c, d)
                board_fill[d][c] = 0

            flood_dirs = [dir for dir in move_dirs]
            flood_dirs.sort(key=lambda x: flood_map[x], reverse=True)
            move = flood_dirs[0]
            break


        elif dist2 <= 40:
            move = minimax(x, y, px, py, move_map)
            print >> sys.stderr, 'minimax', dir_move(move), time() - START
            break

    return move


def best_move_fast(x, y):
    move = head_min(x, y)
    BOARDS_FILL.clear()
    if move is None: move = default_move(x, y)
    if move is None: move = END
    print >> sys.stderr, DIR[move], time() - START
    return move


if __name__ == '__main__':
    ID_START = 1001

    # W, H = 15, 15
    # BOARD = [[0 for _ in range(W)] for _ in range(H)]
    # BOARD[0] =  [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[1] =  [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[2] =  [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[3] =  [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[4] =  [   0,    0,    0, 1001, 1001, 1001, 1001, 1001, 1001, 1001, 1001, 1001, 1001, 1001, 1001]
    # BOARD[5] =  [   0,    0, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002]
    # BOARD[6] =  [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[7] =  [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[8] =  [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[9] =  [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[10] = [   0,    0,    0,    0, 1002, 1002,    0, 1001,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[11] = [   0,    0,    0, 1002, 1002,    0,    0, 1001,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[12] = [   0,    0,    0,    0,    0, 1001, 1001, 1001,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[13] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[14] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # DEBUG = True
    # START = time()
    # mx, my = 5, 12
    # LASTMOVE = LEFT
    # HEADS = {1002: (3, 11)}
    # HEADS_F = {}
    # assert DOWN == best_move_fast(mx, my)
    # assert time() - START < 0.095

    W, H = 15, 15
    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[0] =  [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[1] =  [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[2] =  [   0,    0,    0,    0,    0,    0, 1002, 1001,    0,    0,    0,    0,    0,    0,    0]
    BOARD[3] =  [   0,    0,    0,    0,    0,    0, 1002, 1001,    0,    0,    0,    0,    0,    0,    0]
    BOARD[4] =  [   0,    0,    0,    0,    0,    0, 1002, 1001,    0,    0,    0,    0,    0,    0,    0]
    BOARD[5] =  [   0,    0,    0,    0,    0,    0, 1002, 1001,    0,    0,    0,    0,    0,    0,    0]
    BOARD[6] =  [   0,    0,    0,    0,    0,    0, 1002, 1001,    0,    0,    0,    0,    0,    0,    0]
    BOARD[7] =  [   0,    0,    0,    0,    0,    0, 1002, 1001,    0,    0,    0,    0,    0,    0,    0]
    BOARD[8] =  [   0,    0,    0,    0,    0,    0, 1002, 1001,    0,    0,    0,    0,    0,    0,    0]
    BOARD[9] =  [   0,    0,    0,    0,    0,    0, 1002, 1001,    0,    0,    0,    0,    0,    0,    0]
    BOARD[10] = [   0,    0,    0,    0, 1002, 1002,    0, 1001,    0,    0,    0,    0,    0,    0,    0]
    BOARD[11] = [   0,    0,    0, 1002, 1002,    0,    0, 1001,    0,    0,    0,    0,    0,    0,    0]
    BOARD[12] = [   0,    0,    0,    0,    0, 1001, 1001, 1001,    0,    0,    0,    0,    0,    0,    0]
    BOARD[13] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[14] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    DEBUG = True
    START = time()
    mx, my = 5, 12
    LASTMOVE = LEFT
    HEADS = {1002: (3, 11)}
    HEADS_F = {}
    assert DOWN == best_move_fast(mx, my)
    assert time() - START < 0.095

    # sys.exit()

    W, H = 10, 10
    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[2] = [   0,    0,    0,    0, 1003, 1003, 1003, 1003,    0,    0]
    BOARD[3] = [   0,    0,    0,    0,    0,    0,    0,    0, 1002,    0]
    BOARD[4] = [   0,    0,    0,    0, 1001,    0,    0,    0, 1002,    0]
    BOARD[5] = [   0,    0,    0,    0, 1001,    0,    0,    0, 1002,    0]
    BOARD[6] = [   0,    0,    0,    0, 1001,    0,    0,    0, 1002,    0]
    BOARD[7] = [   0,    0,    0,    0, 1001, 1001,    0,    0,    0,    0]
    BOARD[8] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[9] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    DEBUG = True
    START = time()
    mx, my = 4, 4
    LASTMOVE = UP
    HEADS = {1002: (8, 6), 1003: (4, 2)}
    HEADS_F = {}
    assert UP == best_move_fast(mx, my)
    assert time() - START < 0.095


    W, H = 10, 10
    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[2] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[3] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[4] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[5] = [   0,    0, 1001, 1001, 1001,    0,    0,    0,    0,    0]
    BOARD[6] = [   0, 1002,    0, 1002, 1002,    0,    0,    0,    0,    0]
    BOARD[7] = [   0, 1002, 1002, 1002, 1002,    0,    0,    0,    0,    0]
    BOARD[8] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[9] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    DEBUG = True
    START = time()
    mx, my = 2, 5
    LASTMOVE = LEFT
    HEADS = {1002: (1, 6)}
    HEADS_F = {}
    assert UP == best_move_fast(mx, my)
    # assert DOWN != best_move_fast(mx, my)
    assert time() - START < 0.095


    W, H = 10, 10
    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[2] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[3] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[4] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[5] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[6] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[7] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[8] = [   0,    0,    0, 1002, 1002, 1002, 1002,    0,    0,    0]
    BOARD[9] = [   0,    0,    0, 1002, 1002, 1002, 1002,    0,    0,    0]
    DEBUG = True
    START = time()
    mx, my = 3, 8
    assert LEFT == default_move(mx, my)
    assert time() - START < 0.095

    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[2] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[3] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[4] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[5] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[6] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[7] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[8] = [   0,    0, 1002, 1002, 1002, 1002, 1002,    0,    0,    0]
    BOARD[9] = [   0,    0,    0, 1002, 1002, 1002, 1002,    0,    0,    0]
    DEBUG = True
    START = time()
    mx, my = 2, 8
    assert DOWN == default_move(mx, my)
    assert time() - START < 0.095

    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[0] = [   0,    0,    0,    0, 1002,    0,    0,    0,    0,    0]
    BOARD[1] = [   0,    0,    0,    0, 1002,    0,    0,    0,    0,    0]
    BOARD[2] = [   0,    0,    0,    0, 1002,    0,    0,    0,    0,    0]
    BOARD[3] = [   0,    0,    0,    0, 1002,    0,    0,    0,    0,    0]
    BOARD[4] = [   0,    0,    0,    0, 1002,    0,    0,    0,    0,    0]
    BOARD[5] = [   0,    0,    0,    0, 1002,    0,    0,    0,    0,    0]
    BOARD[6] = [   0,    0,    0,    0, 1002,    0,    0,    0,    0,    0]
    BOARD[7] = [   0,    0,    0,    0, 1002,    0,    0,    0,    0,    0]
    BOARD[8] = [   0,    0,    0,    0, 1002,    0,    0,    0,    0,    0]
    BOARD[9] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    DEBUG = True
    START = time()
    mx, my = 4, 8
    assert LEFT == default_move(mx, my)
    assert time() - START < 0.095

    print >> sys.stderr, '\n\n'
    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[0] = [   0,    0,    0,    0, 1002,    0,    0,    0,    0,    0]
    BOARD[1] = [   0,    0,    0,    0, 1002,    0,    0,    0,    0,    0]
    BOARD[2] = [   0,    0,    0,    0, 1002,    0,    0,    0,    0,    0]
    BOARD[3] = [   0,    0,    0,    0, 1002,    0,    0,    0,    0,    0]
    BOARD[4] = [   0,    0,    0,    0, 1002,    0,    0,    0,    0,    0]
    BOARD[5] = [   0,    0,    0,    0, 1002,    0,    0,    0,    0,    0]
    BOARD[6] = [   0,    0,    0,    0, 1002,    0,    0,    0,    0,    0]
    BOARD[7] = [   0,    0,    0,    0, 1002,    0,    0,    0,    0,    0]
    BOARD[8] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[9] = [   0,    0, 1001, 1001,    0,    0,    0,    0,    0,    0]
    DEBUG = True
    START = time()
    mx, my = 3, 9
    assert RIGHT == default_move(mx, my)
    assert time() - START < 0.095

    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[0] = [   0,    0,    0,    0, 1002,    0,    0,    0,    0,    0]
    BOARD[1] = [   0,    0,    0,    0, 1002,    0,    0,    0,    0,    0]
    BOARD[2] = [   0,    0,    0,    0, 1002,    0,    0,    0,    0,    0]
    BOARD[3] = [   0,    0,    0,    0, 1002,    0,    0,    0,    0,    0]
    BOARD[4] = [   0,    0,    0,    0, 1002,    0,    0,    0,    0,    0]
    BOARD[5] = [   0,    0,    0,    0, 1002,    0,    0,    0,    0,    0]
    BOARD[6] = [   0,    0,    0,    0, 1002,    0,    0,    0,    0,    0]
    BOARD[7] = [   0,    0,    0,    0, 1002,    0,    0,    0,    0,    0]
    BOARD[8] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[9] = [   0,    0, 1001, 1001, 1001,    0,    0,    0,    0,    0]
    DEBUG = True
    START = time()
    mx, my = 4, 9
    assert RIGHT == default_move(mx, my)
    assert time() - START < 0.095

    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[2] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[3] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[4] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[5] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[6] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[7] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[8] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[9] = [   0, 1002, 1002, 1002, 1002,    0,    0,    0,    0,    0]
    DEBUG = True
    START = time()
    mx, my = 1, 9
    assert LEFT == default_move(mx, my)
    assert time() - START < 0.095

    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[2] = [   0,    0,    0,    0,    0,    0,    0,    0, 1001,    0]
    BOARD[3] = [   0,    0,    0,    0,    0,    0,    0,    0, 1001,    0]
    BOARD[4] = [   0,    0,    0,    0,    0,    0,    0,    0, 1001,    0]
    BOARD[5] = [   0,    0,    0, 1002, 1002, 1002, 1002, 1002, 1001,    0]
    BOARD[6] = [   0,    0,    0, 1002,    0,    0,    0,    0, 1001,    0]
    BOARD[7] = [   0,    0,    0, 1002,    0,    0,    0,    0,    0,    0]
    BOARD[8] = [   0,    0,    0, 1002,    0,    0,    0,    0,    0,    0]
    BOARD[9] = [   0,    0, 1002, 1002,    0,    0,    0,    0,    0,    0]
    DEBUG = True
    START = time()
    mx, my = 8, 6
    assert LEFT == default_move(mx, my)
    assert time() - START < 0.095

    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[2] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[3] = [   0,    0,    0,    0,    0, 1002, 1002, 1002, 1002,    0]
    BOARD[4] = [   0,    0,    0,    0,    0, 1002,    0,    0, 1002,    0]
    BOARD[5] = [   0,    0,    0,    0,    0, 1002,    0,    0, 1002,    0]
    BOARD[6] = [   0,    0,    0,    0,    0, 1002,    0, 1002, 1002,    0]
    BOARD[7] = [   0,    0,    0,    0,    0, 1002,    0, 1002, 1002,    0]
    BOARD[8] = [   0,    0,    0,    0,    0, 1002,    0,    0, 1002,    0]
    BOARD[9] = [   0,    0,    0,    0,    0, 1002,    0,    0,    0,    0]
    DEBUG = True
    START = time()
    mx, my = 8, 8
    assert LEFT == default_move(mx, my)
    assert time() - START < 0.095

    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[0] = [   0,    0,    0,    0,    0,    0, 1002,    0,    0,    0]
    BOARD[1] = [   0,    0,    0,    0,    0,    0, 1002,    0,    0,    0]
    BOARD[2] = [   0,    0,    0,    0,    0,    0, 1002,    0,    0,    0]
    BOARD[3] = [   0,    0,    0,    0,    0,    0, 1002, 1002,    0,    0]
    BOARD[4] = [   0,    0,    0,    0,    0,    0,    0,    0,    0, 1001]
    BOARD[5] = [   0,    0,    0,    0,    0,    0,    0,    0,    0, 1001]
    BOARD[6] = [   0,    0,    0,    0,    0,    0,    0,    0,    0, 1001]
    BOARD[7] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[8] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[9] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    DEBUG = True
    START = time()
    mx, my = 9, 4
    assert UP == default_move(mx, my)
    assert time() - START < 0.095

    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[0] = [   0,    0,    0,    0,    0,    0, 1002,    0,    0,    0]
    BOARD[1] = [   0,    0,    0,    0,    0,    0, 1002,    0,    0,    0]
    BOARD[2] = [   0,    0,    0,    0,    0,    0, 1002,    0,    0,    0]
    BOARD[3] = [   0,    0,    0,    0,    0,    0, 1002, 1002, 1002,    0]
    BOARD[4] = [   0,    0,    0,    0,    0,    0,    0,    0,    0, 1001]
    BOARD[5] = [   0,    0,    0,    0,    0,    0,    0,    0,    0, 1001]
    BOARD[6] = [   0,    0,    0,    0,    0,    0,    0,    0,    0, 1001]
    BOARD[7] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[8] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[9] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    DEBUG = True
    START = time()
    mx, my = 9, 4
    assert LEFT == default_move(mx, my)
    assert time() - START < 0.095

    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0, 1001]
    BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0, 1001]
    BOARD[2] = [   0,    0,    0,    0,    0,    0,    0,    0,    0, 1001]
    BOARD[3] = [   0,    0,    0,    0,    0,    0,    0,    0,    0, 1001]
    BOARD[4] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[5] = [1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002,    0]
    BOARD[6] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[7] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[8] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[9] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    DEBUG = True
    START = time()
    mx, my = 9, 3
    assert LEFT == default_move(mx, my)
    assert time() - START < 0.095

    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0, 1001]
    BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0, 1001]
    BOARD[2] = [   0,    0,    0,    0,    0,    0,    0,    0,    0, 1001]
    BOARD[3] = [   0,    0,    0,    0,    0,    0,    0,    0, 1001, 1001]
    BOARD[4] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[5] = [1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002,    0]
    BOARD[6] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[7] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[8] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[9] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    DEBUG = True
    START = time()
    mx, my = 8, 3
    assert UP == default_move(mx, my)
    assert time() - START < 0.095


    # ##  ##  ##  ##  ##  ##  ##  ##
    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[2] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[3] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[4] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[5] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[6] = [   0,    0,    0, 1002, 1002,    0,    0, 1001, 1001, 1001]
    BOARD[7] = [   0,    0,    0, 1002,    0,    0,    0,    0,    0,    0]
    BOARD[8] = [   0,    0,    0, 1002,    0,    0,    0,    0,    0,    0]
    BOARD[9] = [   0,    0,    0, 1002,    0,    0,    0,    0,    0,    0]
    DEBUG = True
    START = time()
    mx, my = 7, 6
    LASTMOVE = LEFT
    HEADS = {1002: (4, 6)}
    HEADS_F = {}
    assert LEFT == best_move_fast(mx, my)
    assert time() - START < 0.095

    W, H = 5, 5
    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[0] = [   0,    0,    0,    0,    0]
    BOARD[1] = [   0,    0,    0,    0,    0]
    BOARD[2] = [   0, 1002,    0,    0,    0]
    BOARD[3] = [1002, 1002,    0, 1001, 1001]
    BOARD[4] = [1002,    0,    0,    0,    0]
    DEBUG = True
    START = time()
    mx, my = 3, 3
    LASTMOVE = LEFT
    HEADS = {1002: (1, 2)}
    HEADS_F = {}
    assert UP == best_move_fast(mx, my)
    assert time() - START < 0.095


    W, H = 15, 10
    # BOARD = [[0 for _ in range(W)] for _ in range(H)]
    # BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[2] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[3] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[4] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[5] = [1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002,    0,    0]
    # BOARD[6] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[7] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[8] = [   0,    0, 1001,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # BOARD[9] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    # DEBUG = True
    # START = time()
    # mx, my = 2, 8
    # LASTMOVE = LEFT
    # HEADS = {1002: (12, 5)}
    # HEADS_F = {}
    # flood_find(mx, my)
    # board_fill = fill_board()
#
    # flood_map = dict()
    # for dir in DIR:
        # c, d = next_pos(mx, my, dir)
        # board_fill[d][c] = ID_START + 10
        # flood_map[dir] = flood_count(board_fill, c, d, dir)
        # board_fill[d][c] = 0
#
    # flood_dirs = [dir for dir in DIR]
    # flood_dirs.sort(key=lambda x: flood_map[x], reverse=True)
#
    # print >> sys.stderr, 'flood_map [',
    # for k, v in flood_map.iteritems():
        # print >> sys.stderr, '(%d, %s),' % (v, DIR[k]),
    # print >> sys.stderr, ']'
    # print >> sys.stderr, flood_dirs
#
    # sys.exit()

    W, H = 15, 15
    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[2] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[3] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[4] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[5] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[6] = [   0, 1001, 1001, 1001, 1001, 1001, 1001,    0,    0, 1002, 1002, 1002,    0,    0,    0]
    BOARD[7] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[8] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[9] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[10] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[11] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[12] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[13] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[14] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    DEBUG = True
    START = time()
    mx, my = 6, 6
    LASTMOVE = RIGHT
    HEADS = {1002: (9, 6)}
    HEADS_F = {}
    assert DOWN == best_move_fast(mx, my)
    assert time() - START < 0.095
    # sys.exit()


    W, H = 15, 10
    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[0] = [   0,    0,    0,    0,    0, 1001,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[1] = [   0,    0,    0,    0,    0, 1001,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[2] = [   0,    0,    0,    0,    0, 1001,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[3] = [   0,    0,    0,    0,    0, 1001,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[4] = [   0,    0,    0,    0, 1002, 1001,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[5] = [   0,    0,    0,    0, 1002, 1001, 1001, 1001, 1001,    0,    0,    0,    0,    0,    0]
    BOARD[6] = [   0,    0,    0,    0, 1002,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[7] = [   0,    0,    0,    0, 1002,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[8] = [   0,    0,    0,    0, 1002,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[9] = [   0,    0,    0,    0, 1002, 1002,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    DEBUG = True
    START = time()
    mx, my = 5, 0
    LASTMOVE = UP
    HEADS = {1002: (5, 9)}
    HEADS_F = {}
    assert RIGHT == best_move_fast(mx, my)
    assert time() - START < 0.095

    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001, 1001, 1001, 1001]
    BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001, 1001, 1001, 1001]
    BOARD[2] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001,    0, 1002, 1002]
    BOARD[3] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001, 1002, 1002, 1002]
    BOARD[4] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001, 1002, 1002, 1002]
    BOARD[5] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001, 1002, 1002, 1002]
    BOARD[6] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002,    0,    0,    0, 1002]
    BOARD[7] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002,    0,    0,    0, 1002]
    BOARD[8] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002,    0,    0,    0, 1002]
    BOARD[9] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002, 1002, 1002, 1002, 1002]
    DEBUG = True
    START = time()
    mx, my = 11, 5
    LASTMOVE = DOWN
    HEADS = {1002: (12, 3)}
    HEADS_F = {}
    assert LEFT == best_move_fast(mx, my)
    assert time() - START < 0.095

    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[2] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[3] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[4] = [1001, 1001, 1001, 1001, 1001,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[5] = [   0, 1002, 1002, 1002, 1002,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[6] = [   0, 1002,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[7] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[8] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[9] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    DEBUG = True
    START = time()
    mx, my = 0, 4
    LASTMOVE = LEFT
    HEADS = {1002: (1, 6)}
    HEADS_F = {}
    assert UP == best_move_fast(mx, my)
    assert time() - START < 0.095


    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[2] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[3] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[4] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[5] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[6] = [   0,    0,    0,    0, 1002, 1001,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[7] = [   0, 1002, 1002, 1002, 1002, 1001, 1001, 1001, 1001,    0,    0,    0,    0,    0,    0]
    BOARD[8] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[9] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    DEBUG = True
    START = time()
    mx, my = 5, 6
    LASTMOVE = UP
    HEADS = {1002: (4, 6)}
    HEADS_F = {}
    assert UP == best_move_fast(mx, my)
    assert time() - START < 0.095

    BOARD = [[0 for _ in range(W)] for _ in range(H)]

    BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[2] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[3] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[4] = [   0,    0,    0, 1001, 1001, 1001, 1001, 1001, 1001, 1001, 1001, 1001, 1001, 1001, 1001]
    BOARD[5] = [   0,    0, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002]
    BOARD[6] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[7] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[8] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[9] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    DEBUG = True
    START = time()
    mx, my = 3, 4
    LASTMOVE = LEFT
    HEADS = {1002: (2, 5)}
    HEADS_F = {}
    assert LEFT == best_move_fast(mx, my)
    assert time() - START < 0.095

    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[2] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[3] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[4] = [   0, 1001, 1001, 1001, 1001, 1001, 1001, 1001, 1001, 1001, 1001, 1001, 1001, 1001, 1001]
    BOARD[5] = [1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002]
    BOARD[6] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[7] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[8] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[9] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    DEBUG = True
    START = time()
    mx, my = 1, 4
    LASTMOVE = LEFT
    HEADS = {1002: (0, 5)}
    HEADS_F = {}
    assert LEFT == best_move_fast(mx, my)
    assert time() - START < 0.095


    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[2] = [1002, 1002, 1002, 1002,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[3] = [1001, 1001, 1001, 1001, 1002, 1002, 1002,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[4] = [   0,    0,    0, 1001, 1001, 1001, 1001, 1002, 1002, 1002, 1002,    0,    0,    0, 1002]
    BOARD[5] = [   0,    0,    0,    0,    0,    0,    0, 1001, 1001, 1001, 1001, 1002, 1002, 1002, 1002]
    BOARD[6] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001, 1001, 1001, 1001]
    BOARD[7] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001, 1001, 1001, 1001, 1001]
    BOARD[8] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[9] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    DEBUG = True
    START = time()
    mx, my = 10, 7
    HEADS = {1002: (14, 4)}
    HEADS_F = {}
    best_move_fast(mx, my)

    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[2] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[3] = [   0,    0,    0,    0, 1001, 1001, 1002,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[4] = [   0,    0,    0, 1001, 1001,    0, 1002,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[5] = [   0,    0, 1001, 1001, 1002, 1002, 1002,    0,    0, 1003, 1003, 1003, 1003, 1003,    0]
    BOARD[6] = [   0, 1001, 1001,    0, 1002, 1002, 1002, 1002, 1002, 1003,    0,    0,    0,    0,    0]
    BOARD[7] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[8] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[9] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    DEBUG = True
    START = time()
    mx, my = 5, 3
    HEADS = {1002: (8, 6), 1003: (9, 6)}
    LASTMOVE = RIGHT
    HEADS_F = {}
    assert UP == best_move_fast(mx, my)
    assert time() - START < 0.095

    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[2] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0,    0]
    BOARD[3] = [1001,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0,    0]
    BOARD[4] = [1001, 1001, 1001, 1001, 1001, 1001, 1001, 1001, 1001, 1001, 1001, 1001,    0,    0,    0]
    BOARD[5] = [1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002,    0,    0,    0]
    BOARD[6] = [1002,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002,    0,    0,    0]
    BOARD[7] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002,    0,    0,    0]
    BOARD[8] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[9] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    DEBUG = True
    START = time()
    mx, my = 0, 3
    LASTMOVE = UP
    HEADS = {1002: (0, 6)}
    HEADS_F = {}
    assert RIGHT == best_move_fast(mx, my)
    assert time() - START < 0.095

    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[2] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0,    0]
    BOARD[3] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0,    0]
    BOARD[4] = [   0, 1001, 1001, 1001, 1001, 1001, 1001, 1001, 1001, 1001, 1001, 1001,    0,    0,    0]
    BOARD[5] = [1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002,    0,    0,    0]
    BOARD[6] = [1002,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002,    0,    0,    0]
    BOARD[7] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002,    0,    0,    0]
    BOARD[8] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[9] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    DEBUG = True
    START = time()
    mx, my = 1, 4
    LASTMOVE = LEFT
    HEADS = {1002: (0, 6)}
    HEADS_F = {}
    assert UP == best_move_fast(mx, my)
    assert time() - START < 0.095


    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[2] = [   0,    0,    0,    0,    0,    0,    0, 1002,    0,    0,    0,    0,    0,    0,    0]
    BOARD[3] = [   0,    0,    0,    0,    0,    0,    0, 1002,    0,    0,    0,    0,    0,    0,    0]
    BOARD[4] = [1001,    0,    0,    0,    0,    0,    0, 1002,    0,    0,    0,    0,    0,    0,    0]
    BOARD[5] = [   0,    0,    0,    0,    0,    0,    0, 1002,    0,    0,    0,    0,    0,    0,    0]
    BOARD[6] = [   0,    0,    0,    0,    0,    0,    0, 1002,    0,    0,    0,    0,    0,    0,    0]
    BOARD[7] = [   0,    0,    0,    0,    0,    0,    0, 1002,    0,    0,    0,    0,    0,    0,    0]
    BOARD[8] = [   0,    0,    0,    0,    0,    0,    0, 1002,    0,    0,    0,    0,    0,    0,    0]
    BOARD[9] = [   0,    0,    0,    0,    0,    0,    0, 1002,    0,    0,    0,    0,    0,    0,    0]
    DEBUG = True
    START = time()
    mx, my = 0, 4
    HEADS = {1002: (7, 2)}
    HEADS_F = {}
    assert RIGHT == best_move_fast(mx, my)
    assert time() - START < 0.095


    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[0] = [   0,    0, 1002, 1001,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[1] = [   0,    0, 1002, 1001,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[2] = [   0,    0, 1002, 1001,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[3] = [   0,    0, 1002, 1001,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[4] = [   0,    0, 1002, 1001,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[5] = [   0,    0, 1002, 1001,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[6] = [   0,    0, 1002, 1001,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[7] = [   0,    0, 1002, 1001,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[8] = [   0, 1002, 1002, 1001,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[9] = [   0,    0,    0, 1001,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    DEBUG = True
    START = time()
    mx, my = 3, 9
    LASTMOVE = DOWN
    HEADS = {1002: (1, 8)}
    HEADS_F = {}
    assert RIGHT == best_move_fast(mx, my)
    assert time() - START < 0.095

    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0,    0,    0,    0,    0]
    BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0,    0,    0,    0,    0]
    BOARD[2] = [   0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0,    0,    0,    0,    0]
    BOARD[3] = [   0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0,    0,    0,    0,    0]
    BOARD[4] = [   0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0,    0,    0,    0,    0]
    BOARD[5] = [   0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0,    0,    0,    0,    0]
    BOARD[6] = [   0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0,    0,    0,    0,    0]
    BOARD[7] = [   0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0,    0,    0,    0,    0]
    BOARD[8] = [   0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0,    0,    0,    0,    0]
    BOARD[9] = [   0,    0,    0,    0,    0,    0,    0,    0, 1002, 1002, 1002, 1002, 1002, 1002,    0]
    DEBUG = True
    START = time()
    mx, my = 8, 8
    LASTMOVE = DOWN
    HEADS = {1002: (8, 9)}
    HEADS_F = {}
    assert LEFT == best_move_fast(mx, my)
    assert time() - START < 0.095

    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0,    0,    0,    0,    0]
    BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0,    0,    0,    0,    0]
    BOARD[2] = [   0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0,    0,    0,    0,    0]
    BOARD[3] = [   0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0,    0,    0,    0,    0]
    BOARD[4] = [   0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0,    0,    0,    0,    0]
    BOARD[5] = [   0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0,    0,    0,    0,    0]
    BOARD[6] = [   0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0,    0,    0,    0,    0]
    BOARD[7] = [   0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0,    0,    0,    0,    0]
    BOARD[8] = [   0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0,    0,    0,    0,    0]
    BOARD[9] = [   0,    0,    0,    0,    0,    0,    0, 1002, 1002, 1002, 1002, 1002, 1002, 1002,    0]
    DEBUG = True
    START = time()
    mx, my = 8, 8
    LASTMOVE = DOWN
    HEADS = {1002: (7, 9)}
    HEADS_F = {}
    assert LEFT == best_move_fast(mx, my)
    assert time() - START < 0.095

    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002, 1001,    0,    0]
    BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002, 1001,    0,    0]
    BOARD[2] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002, 1001,    0,    0]
    BOARD[3] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002, 1001,    0,    0]
    BOARD[4] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002, 1001,    0,    0]
    BOARD[5] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002, 1001,    0,    0]
    BOARD[6] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002, 1001,    0,    0]
    BOARD[7] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002, 1001,    0,    0]
    BOARD[8] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002, 1001,    0,    0]
    BOARD[9] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0]
    DEBUG = True
    START = time()
    mx, my = 12, 9
    LASTMOVE = DOWN
    HEADS = {1002: (11, 8)}
    HEADS_F = {}
    assert RIGHT == best_move_fast(mx, my)
    assert time() - START < 0.095

    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002, 1001,    0,    0]
    BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002, 1001,    0,    0]
    BOARD[2] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002, 1001,    0,    0]
    BOARD[3] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002, 1001,    0,    0]
    BOARD[4] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002, 1001,    0,    0]
    BOARD[5] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002, 1001,    0,    0]
    BOARD[6] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002, 1001,    0,    0]
    BOARD[7] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002, 1001,    0,    0]
    BOARD[8] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002, 1002, 1001,    0,    0]
    BOARD[9] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0]
    DEBUG = True
    START = time()
    mx, my = 12, 9
    LASTMOVE = DOWN
    HEADS = {1002: (10, 8)}
    HEADS_F = {}
    assert RIGHT == best_move_fast(mx, my)
    assert time() - START < 0.095

    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002, 1001,    0,    0]
    BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002, 1001,    0,    0]
    BOARD[2] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002, 1001,    0,    0]
    BOARD[3] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002, 1001,    0,    0]
    BOARD[4] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002, 1001,    0,    0]
    BOARD[5] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002, 1001,    0,    0]
    BOARD[6] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002, 1001,    0,    0]
    BOARD[7] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002, 1001,    0,    0]
    BOARD[8] = [   0,    0,    0,    0,    0,    0,    0,    0,    0, 1002, 1002, 1002, 1001,    0,    0]
    BOARD[9] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0]
    DEBUG = True
    START = time()
    mx, my = 12, 9
    LASTMOVE = DOWN
    HEADS = {1002: (9, 8)}
    HEADS_F = {}
    assert RIGHT == best_move_fast(mx, my)
    assert time() - START < 0.095

    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002, 1001,    0,    0]
    BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002, 1001,    0,    0]
    BOARD[2] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002, 1001,    0,    0]
    BOARD[3] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002, 1001,    0,    0]
    BOARD[4] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002, 1001,    0,    0]
    BOARD[5] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002, 1001,    0,    0]
    BOARD[6] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002, 1001,    0,    0]
    BOARD[7] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002, 1001,    0,    0]
    BOARD[8] = [   0,    0,    0,    0,    0,    0,    0,    0, 1002, 1002, 1002, 1002, 1001,    0,    0]
    BOARD[9] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0]
    DEBUG = True
    START = time()
    mx, my = 12, 9
    LASTMOVE = DOWN
    HEADS = {1002: (8, 8)}
    HEADS_F = {}
    assert RIGHT == best_move_fast(mx, my)
    assert time() - START < 0.095

    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002, 1001,    0,    0]
    BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002, 1001,    0,    0]
    BOARD[2] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002, 1001,    0,    0]
    BOARD[3] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002, 1001,    0,    0]
    BOARD[4] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002, 1001,    0,    0]
    BOARD[5] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002, 1001,    0,    0]
    BOARD[6] = [   0,    0,    0,    0,    0,    0,    0,    0, 1002, 1002, 1002, 1002, 1001,    0,    0]
    BOARD[7] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002, 1002, 1001,    0,    0]
    BOARD[8] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002, 1002, 1001,    0,    0]
    BOARD[9] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0]
    DEBUG = True
    START = time()
    mx, my = 12, 9
    LASTMOVE = DOWN
    HEADS = {1002: (8, 6)}
    HEADS_F = {}
    assert RIGHT == best_move_fast(mx, my)
    assert time() - START < 0.095

    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[2] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[3] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[4] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[5] = [   0,    0,    0,    0, 1002, 1002,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[6] = [   0, 1001, 1001,    0, 1002, 1002,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[7] = [   0, 1001, 1001, 1001, 1002, 1002, 1002, 1002, 1002,    0,    0,    0,    0,    0,    0]
    BOARD[8] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[9] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    DEBUG = True
    START = time()
    mx, my = 2, 6
    LASTMOVE = RIGHT
    HEADS = {1002: (4, 5)}
    HEADS_F = {}
    assert UP == best_move_fast(mx, my)
    assert time() - START < 0.095


    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[2] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[3] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[4] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[5] = [   0,    0,    0,    0, 1002, 1002,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[6] = [   0, 1001, 1001,    0, 1002, 1002,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[7] = [   0, 1001, 1001,    0, 1002, 1002, 1002, 1002, 1002,    0,    0,    0,    0,    0,    0]
    BOARD[8] = [   0,    0, 1001, 1001,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[9] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    DEBUG = True
    START = time()
    mx, my = 2, 6
    LASTMOVE = RIGHT
    HEADS = {1002: (4, 5)}
    HEADS_F = {}
    assert UP == best_move_fast(mx, my)
    assert time() - START < 0.095

    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0,    0]
    BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0,    0]
    BOARD[2] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0,    0]
    BOARD[3] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0,    0]
    BOARD[4] = [   0,    0,    0,    0,    0,    0, 1002, 1001, 1001, 1001, 1001, 1001,    0,    0,    0]
    BOARD[5] = [   0,    0,    0,    0,    0,    0, 1002,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[6] = [   0,    0,    0,    0,    0,    0, 1002,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[7] = [   0,    0,    0,    0,    0,    0, 1002,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[8] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[9] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    DEBUG = True
    START = time()
    mx, my = 7, 4
    LASTMOVE = LEFT
    HEADS = {1002: (6, 4)}
    HEADS_F = {}
    assert DOWN == best_move_fast(mx, my)
    assert time() - START < 0.095

    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0,    0]
    BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0,    0]
    BOARD[2] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0,    0]
    BOARD[3] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0,    0]
    BOARD[4] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0,    0]
    BOARD[5] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0,    0]
    BOARD[6] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0,    0]
    BOARD[7] = [   0,    0,    0,    0,    0,    0, 1002, 1001, 1001, 1001, 1001, 1001,    0,    0,    0]
    BOARD[8] = [   0,    0,    0,    0,    0,    0, 1002,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[9] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    DEBUG = True
    START = time()
    mx, my = 7, 7
    LASTMOVE = LEFT
    HEADS = {1002: (6, 7)}
    HEADS_F = {}
    assert DOWN == best_move_fast(mx, my)
    assert time() - START < 0.095

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
    # HEADS = {1001: (2, 15), 1003: (1, 18)}
    # HEADS_F = {}
    # assert UP == best_move_fast(mx, my)

    W, H = 15, 10
    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0,    0,    0,    0,    0]
    BOARD[1] = [1001, 1001, 1001,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[2] = [   0,    0,    0,    0,    0,    0, 1001, 1001, 1001, 1001, 1001, 1001,    0,    0,    0]
    BOARD[3] = [   0,    0,    0,    0,    0,    0, 1001,    0,    0,    0,    0,    0, 1001,    0,    0]
    BOARD[4] = [   0,    0,    0,    0,    0,    0, 1001,    0,    0,    0,    0,    0, 1001,    0,    0]
    BOARD[5] = [   0,    0,    0,    0,    0,    0, 1001,    0,    0,    0,    0,    0, 1001,    0,    0]
    BOARD[6] = [   0,    0,    0,    0,    0,    0, 1001,    0,    0,    0,    0,    0, 1001,    0,    0]
    BOARD[7] = [   0,    0,    0,    0,    0,    0, 1001,    0,    0,    0,    0,    0, 1001,    0,    0]
    BOARD[8] = [   0,    0,    0,    0,    0,    0, 1001, 1001, 1001, 1001, 1001, 1001, 1001,    0,    0]
    BOARD[9] = [   0,    0,    0,    0,    0,    0,    0, 1001,    0,    0,    0,    0,    0,    0,    0]
    DEBUG = True
    START = time()
    mx, my = 12, 3
    HEADS = {}
    HEADS_F = {}
    assert UP == best_move_fast(mx, my)
    assert time() - START < 0.095

    BOARD = [[0 for _ in range(W)] for _ in range(H)]
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
    DEBUG = True
    START = time()
    mx, my = 12, 3
    HEADS = {}
    HEADS_F = {}
    assert UP == best_move_fast(mx, my)
    assert time() - START < 0.095

    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[2] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[3] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[4] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[5] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[6] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[7] = [1001, 1001, 1001, 1001,    0, 1002, 1002, 1002, 1002, 1002,    0,    0,    0,    0,    0]
    BOARD[8] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[9] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    DEBUG = True
    START = time()
    mx, my = 3, 7
    LASTMOVE = RIGHT
    HEADS = {1002: (5, 7)}
    HEADS_F = {}
    assert UP == best_move_fast(mx, my)
    # assert RIGHT == best_move_fast(mx, my)
    assert time() - START < 0.095

    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[0] = [   0, 1001,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[1] = [   0, 1001, 1002, 1002, 1002,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[2] = [   0, 1001, 1002, 1002, 1002,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[3] = [   0, 1001, 1001, 1001, 1002,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[4] = [   0,    0,    0, 1001, 1002,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[5] = [   0,    0,    0, 1001, 1002,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[6] = [   0,    0,    0, 1001,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[7] = [   0,    0,    0, 1001,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[8] = [   0,    0, 1001, 1001,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[9] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    DEBUG = True
    START = time()
    mx, my = 1, 0
    LASTMOVE = UP
    HEADS = {1002: (4, 1)}
    HEADS_F = {}
    assert LEFT == best_move_fast(mx, my)
    assert time() - START < 0.095


    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002, 1002, 1002, 1002, 1002]
    BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002,    0,    0,    0, 1002]
    BOARD[2] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002,    0,    0,    0, 1002]
    BOARD[3] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002,    0,    0,    0, 1002]
    BOARD[4] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002,    0,    0,    0, 1002]
    BOARD[5] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002,    0,    0,    0, 1002]
    BOARD[6] = [   0,    0,    0,    0,    0, 1001, 1001, 1001, 1001, 1001, 1001, 1001, 1001, 1001,    0]
    BOARD[7] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[8] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[9] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    DEBUG = True
    START = time()
    mx, my = 13, 6
    LASTMOVE = RIGHT
    HEADS = {1002: (14, 5)}
    HEADS_F = {}
    # assert DOWN == best_move_fast(mx, my)
    assert RIGHT == best_move_fast(mx, my)
    assert time() - START < 0.095

    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002, 1002, 1002, 1002, 1002]
    BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002,    0,    0,    0, 1002]
    BOARD[2] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002,    0,    0,    0, 1002]
    BOARD[3] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002,    0,    0,    0, 1002]
    BOARD[4] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002,    0,    0,    0, 1002]
    BOARD[5] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002,    0,    0,    0, 1002]
    BOARD[6] = [   0,    0,    0,    0,    0, 1001, 1001, 1001, 1001, 1001, 1001, 1001, 1001, 1001, 1002]
    BOARD[7] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002]
    BOARD[8] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[9] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    DEBUG = True
    START = time()
    mx, my = 13, 6
    LASTMOVE = RIGHT
    HEADS = {1002: (14, 7)}
    HEADS_F = {}
    assert DOWN == best_move_fast(mx, my)
    assert time() - START < 0.095

    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[2] = [   0,    0,    0,    0,    0,    0, 1001,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[3] = [   0,    0,    0,    0,    0,    0, 1001,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[4] = [   0,    0,    0,    0,    0,    0, 1001, 1001,    0,    0,    0,    0,    0,    0,    0]
    BOARD[5] = [   0,    0,    0,    0,    0,    0,    0, 1001,    0,    0,    0,    0,    0,    0,    0]
    BOARD[6] = [   0,    0,    0,    0,    0, 1002, 1002, 1002, 1002, 1002,    0,    0,    0,    0,    0]
    BOARD[7] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[8] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[9] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    DEBUG = True
    START = time()
    mx, my = 7, 5
    LASTMOVE = DOWN
    HEADS = {1002: (5, 6)}
    HEADS_F = {}
    assert RIGHT == best_move_fast(mx, my)
    # assert LEFT != best_move_fast(mx, my)
    assert time() - START < 0.095


    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[2] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[3] = [1002, 1002, 1002, 1002, 1002,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[4] = [   0,    0, 1002, 1002, 1002,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[5] = [   0, 1001,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[6] = [   0, 1001,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[7] = [1001, 1001,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[8] = [1001,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[9] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    DEBUG = True
    START = time()
    mx, my = 1, 5
    LASTMOVE = UP
    HEADS = {1002: (2, 4)}
    HEADS_F = {}
    assert RIGHT == best_move_fast(mx, my)
    assert time() - START < 0.095


    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[0] = [1002, 1002, 1002, 1002,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[1] = [1002,    0, 1001,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[2] = [1002, 1001, 1001,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[3] = [1002, 1001,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[4] = [1002, 1001,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[5] = [1002, 1001,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[6] = [1002, 1001,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[7] = [1002, 1001,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[8] = [1002, 1001,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[9] = [   0, 1001,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    DEBUG = True
    START = time()
    mx, my = 2, 1
    LASTMOVE = UP
    HEADS = {1002: (3, 0)}
    HEADS_F = {}
    assert RIGHT == best_move_fast(mx, my)
    assert time() - START < 0.095


    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[2] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[3] = [1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002,    0]
    BOARD[4] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002,    0]
    BOARD[5] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002,    0]
    BOARD[6] = [   0,    0, 1001, 1001, 1001, 1001, 1001, 1001, 1001, 1001, 1001, 1001, 1001, 1002,    0]
    BOARD[7] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001, 1002,    0]
    BOARD[8] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0]
    BOARD[9] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    DEBUG = True
    START = time()
    LASTMOVE = DOWN
    mx, my = 12, 8
    HEADS = {1002: (13, 7)}
    HEADS_F = {}
    assert RIGHT == best_move_fast(mx, my)
    assert time() - START < 0.095

    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[2] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[3] = [1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002,    0]
    BOARD[4] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002,    0]
    BOARD[5] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002,    0]
    BOARD[6] = [   0,    0, 1001, 1001, 1001, 1001, 1001, 1001, 1001, 1001, 1001, 1001, 1001, 1002,    0]
    BOARD[7] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001, 1002, 1002]
    BOARD[8] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001, 1001,    0]
    BOARD[9] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    DEBUG = True
    START = time()
    LASTMOVE = RIGHT
    mx, my = 13, 8
    HEADS = {1002: (14, 7)}
    HEADS_F = {}
    assert RIGHT == best_move_fast(mx, my)
    assert time() - START < 0.095

    W, H = 30, 20
    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[7][0:27] = [1002] * 27
    BOARD[8][26] = 1002
    BOARD[9][26] = 1002
    BOARD[10][26] = 1002
    BOARD[11][26] = 1002
    BOARD[12][26] = 1002
    BOARD[13][26] = 1002
    BOARD[13][27] = 1002
    BOARD[13][28] = 1002
    BOARD[14][28] = 1002
    BOARD[15][28] = 1002
    BOARD[16][28] = 1002
    BOARD[17][28] = 1002

    BOARD[8][9:25] = [1003] * 16

    BOARD[13][1] = 1001
    BOARD[14][1:28] = [1001] * 27
    BOARD[15][27] = 1001
    BOARD[16][27] = 1001
    BOARD[17][27] = 1001
    BOARD[18][27] = 1001

    DEBUG = True
    START = time()
    mx, my = 27, 18
    LASTMOVE = DOWN
    HEADS = {1002: (28, 17), 1003: (9, 8)}
    HEADS_F = {}
    assert RIGHT == best_move_fast(mx, my)
    # assert time() - START < 0.095

    # sys.exit()

    W, H = 15, 10
    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[2] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0,    0,    0]
    BOARD[3] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0,    0,    0]
    BOARD[4] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0,    0,    0]
    BOARD[5] = [   0,    0,    0,    0,    0,    0,    0,    0,    0, 1002, 1001,    0,    0,    0,    0]
    BOARD[6] = [   0,    0,    0,    0,    0, 1002, 1002, 1002, 1002, 1002, 1001,    0,    0,    0,    0]
    BOARD[7] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[8] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[9] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    DEBUG = True
    START = time()
    mx, my = 10, 6
    LASTMOVE = DOWN
    HEADS = {1002: (9, 5)}
    HEADS_F = {}
    assert DOWN == best_move_fast(mx, my)
    assert time() - START < 0.095

    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[2] = [   0,    0,    0,    0,    0,    0, 1002,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[3] = [   0,    0,    0,    0,    0, 1002, 1002, 1001, 1001, 1001, 1001,    0,    0,    0,    0]
    BOARD[4] = [   0,    0,    0,    0,    0, 1002,    0, 1001,    0,    0,    0,    0,    0,    0,    0]
    BOARD[5] = [   0,    0,    0,    0,    0, 1002,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[6] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[7] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[8] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[9] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    DEBUG = True
    START = time()
    mx, my = 7, 4
    LASTMOVE = DOWN
    HEADS = {1002: (5, 5)}
    HEADS_F = {}
    assert DOWN == best_move_fast(mx, my)
    # assert RIGHT != best_move_fast(mx, my)
    assert time() - START < 0.095



    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[2] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[3] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[4] = [1001, 1001, 1001, 1001, 1001,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[5] = [   0,    0,    0,    0, 1001,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[6] = [   0,    0,    0,    0,    0,    0, 1002, 1002,    0,    0,    0,    0,    0,    0,    0]
    BOARD[7] = [   0,    0,    0,    0,    0,    0,    0, 1002,    0,    0,    0,    0,    0,    0,    0]
    BOARD[8] = [   0,    0,    0,    0,    0,    0,    0, 1002, 1002, 1002, 1002, 1002, 1002, 1002,    0]
    BOARD[9] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    DEBUG = True
    START = time()
    LASTMOVE = DOWN
    mx, my = 4, 5
    HEADS = {1002: (6, 6)}
    HEADS_F = {}
    assert RIGHT == best_move_fast(mx, my)
    assert time() - START < 0.095

    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[2] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[3] = [1001, 1001, 1001, 1001, 1001,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[4] = [   0,    0,    0,    0, 1001,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[5] = [   0,    0,    0,    0,    0,    0, 1002, 1002,    0,    0,    0,    0,    0,    0,    0]
    BOARD[6] = [   0,    0,    0,    0,    0,    0,    0, 1002,    0,    0,    0,    0,    0,    0,    0]
    BOARD[7] = [   0,    0,    0,    0,    0,    0,    0, 1002, 1002, 1002, 1002, 1002, 1002, 1002,    0]
    BOARD[8] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[9] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    DEBUG = True
    START = time()
    LASTMOVE = DOWN
    mx, my = 4, 4
    HEADS = {1002: (6, 5)}
    HEADS_F = {}
    # assert RIGHT == best_move_fast(mx, my)
    assert DOWN == best_move_fast(mx, my)
    assert time() - START < 0.095


    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[2] = [   0,    0,    0,    0,    0, 1002, 1002, 1002, 1002, 1002, 1002,    0,    0,    0,    0]
    BOARD[3] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[4] = [   0, 1001, 1001, 1001, 1001,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[5] = [   0,    0,    0,    0,    0, 1003, 1003, 1003, 1003, 1003, 1003,    0,    0,    0,    0]
    BOARD[6] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[7] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[8] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[9] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    DEBUG = True
    START = time()
    mx, my = 4, 4
    LASTMOVE = RIGHT
    HEADS = {1002: (10, 2), 1003: (10, 5)}
    HEADS_F = {}
    # assert DOWN == best_move_fast(mx, my)
    assert RIGHT == best_move_fast(mx, my)
    assert time() - START < 0.095

    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[2] = [   0,    0,    0,    0,    0, 1002, 1002, 1002, 1002,    0, 1003, 1003, 1003,    0,    0]
    BOARD[3] = [   0,    0,    0,    0,    0,    0,    0,    0, 1002, 1003, 1003,    0,    0,    0,    0]
    BOARD[4] = [   0,    0,    0,    0,    0,    0,    0,    0, 1002, 1003,    0,    0, 1001, 1001,    0]
    BOARD[5] = [   0,    0,    0,    0,    0,    0,    0,    0,    0, 1003,    0,    0,    0,    0,    0]
    BOARD[6] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[7] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[8] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[9] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    DEBUG = True
    START = time()
    mx, my = 12, 4
    LASTMOVE = LEFT
    HEADS = {1002: (8, 4), 1003: (12, 2)}
    HEADS_F = {}
    assert DOWN == best_move_fast(mx, my)
    # assert time() - START < 0.095

    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[2] = [   0,    0, 1002,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[3] = [   0,    0, 1002,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[4] = [   0, 1001, 1002,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[5] = [   0, 1001, 1002,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[6] = [   0, 1001, 1002,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[7] = [   0, 1001, 1002,    0,    0, 1002, 1002, 1002,    0,    0,    0,    0,    0,    0,    0]
    BOARD[8] = [   0, 1001, 1002, 1002, 1002, 1002,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[9] = [   0, 1001,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    DEBUG = True
    START = time()
    mx, my = 1, 9
    LASTMOVE = DOWN
    HEADS = {1002: (7, 7)}
    HEADS_F = {}
    assert LEFT == best_move_fast(mx, my)
    assert time() - START < 0.095

    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[2] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[3] = [   0,    0,    0,    0,    0,    0,    0,    0,    0, 1002,    0,    0,    0,    0,    0]
    BOARD[4] = [   0,    0,    0,    0,    0,    0,    0,    0,    0, 1002,    0,    0,    0,    0, 1003]
    BOARD[5] = [   0,    0,    0,    0,    0,    0,    0,    0,    0, 1002, 1002,    0,    0, 1003, 1003]
    BOARD[6] = [   0,    0,    0,    0,    0,    0,    0,    0,    0, 1002, 1002,    0,    0,    0,    0]
    BOARD[7] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0,    0,    0]
    BOARD[8] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0,    0,    0]
    BOARD[9] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0,    0,    0]
    DEBUG = True
    START = time()
    mx, my = 10, 7
    LASTMOVE = UP
    HEADS = {1002: (10, 5), 1003: (13, 5)}
    HEADS_F = {}
    assert LEFT == best_move_fast(mx, my)
    assert time() - START < 0.095

    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0, 1001,    0,    0,    0,    0,    0]
    BOARD[1] = [   0,    0,    0,    0, 1001, 1001, 1001, 1001, 1001, 1001, 1002, 1002, 1002, 1002, 1002]
    BOARD[2] = [   0,    0,    0,    0,    0, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002]
    BOARD[3] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[4] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[5] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[6] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[7] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[8] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[9] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    DEBUG = True
    START = time()
    mx, my = 9, 0
    LASTMOVE = UP
    HEADS = {1002: (10, 1)}
    HEADS_F = {}
    # assert LEFT == best_move_fast(mx, my)
    assert RIGHT == best_move_fast(mx, my)
    assert time() - START < 0.095


    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[2] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[3] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[4] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[5] = [   0,    0,    0,    0,    0,    0,    0, 1002, 1002, 1002,    0,    0,    0,    0,    0]
    BOARD[6] = [   0,    0,    0,    0,    0,    0,    0,    0,    0, 1002, 1002,    0,    0,    0,    0]
    BOARD[7] = [   0,    0,    0,    0,    0,    0,    0,    0, 1001, 1001, 1001, 1001,    0,    0,    0]
    BOARD[8] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[9] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    DEBUG = True
    START = time()
    mx, my = 8, 7
    LASTMOVE = LEFT
    HEADS = {1002: (7, 5)}
    HEADS_F = {}
    assert LEFT == best_move_fast(mx, my)
    # assert UP != best_move_fast(mx, my)
    assert time() - START < 0.095

    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[2] = [1002, 1002, 1002,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[3] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[4] = [1001, 1001,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[5] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[6] = [   0,    0,    0,    0,    0, 1003,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[7] = [   0,    0,    0,    0,    0, 1003,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[8] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[9] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    DEBUG = True
    START = time()
    mx, my = 1, 4
    LASTMOVE = RIGHT
    HEADS = {1002: (2, 2), 1003: (5, 6)}
    HEADS_F = {}
    assert RIGHT == best_move_fast(mx, my)
    assert time() - START < 0.095

    BOARD = [[0 for _ in range(W)] for _ in range(H)]
    BOARD[0] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[1] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[2] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1002, 1002, 1002]
    BOARD[3] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[4] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, 1001, 1001]
    BOARD[5] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[6] = [   0,    0,    0,    0,    0,    0,    0,    0,    0, 1003,    0,    0,    0,    0,    0]
    BOARD[7] = [   0,    0,    0,    0,    0,    0,    0,    0,    0, 1003,    0,    0,    0,    0,    0]
    BOARD[8] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    BOARD[9] = [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0]
    DEBUG = True
    START = time()
    mx, my = 13, 4
    LASTMOVE = LEFT
    HEADS = {1002: (12, 2), 1003: (9, 6)}
    HEADS_F = {}
    assert LEFT == best_move_fast(mx, my)
    assert time() - START < 0.095


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


