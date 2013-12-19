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
BOARDS_FILL = None
LASTMOVE = None
DEBUG = False


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


def flood_count(board_fill, x, y):
    board_copy = copy.deepcopy(BOARD)
    return flood_count_2(board_copy, board_fill, x, y)


def flood_count_2(board_copy, board_fill, x, y):
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


def __default_move2(board, x, y, n=1):
    ngbs = neighbors_clean(board, x, y)
    if len(ngbs) == 0:
        return n

    best_score = 0
    board_move = copy.deepcopy(board)

    for c, d in ngbs:
        board_move[d][c] = board[y][x]
        if n == 2:
            board_copy = copy.deepcopy(board_move)
            score = n + flood_count_2(board_copy, board_move, c, d)
        else:
            score = __default_move2(board_move, c, d, n + 1)
        board_move[d][c] = 0

        if score > best_score:
            best_score = score

        if time() - START > 0.09:
            break
    return best_score


def default_move2(x, y):
    move_map = {
            UP:    max_move(x, y, UP),
            RIGHT: max_move(x, y, RIGHT),
            DOWN:  max_move(x, y, DOWN),
            LEFT:  max_move(x, y, LEFT) }
    move_dirs = tuple(k for k, v in move_map.items() if v > 0)
    move_dirs  = sorted(move_dirs)

    # move_dirs == 0
    if len(move_dirs) == 0:
        return None

    # move_dirs == 1
    elif len(move_dirs) == 1:
        return move_dirs[0]


    best_scores = dict()
    board = copy.deepcopy(BOARD)

    for dir in move_dirs:
        c, d = next_pos(x, y, dir)
        board[d][c] = board[y][x]
        best_scores[dir] = __default_move2(board, c, d)
        board[d][c] = 0
        print >> sys.stderr, 'default_move2', best_scores[dir], DIR[dir], time() - START
        if time() - START > 0.08:
            break

    best_dirs = sorted(best_scores.items(), key=itemgetter(1))
    max_flood = best_dirs[-1][1]
    best_dirs = [k for k, v in best_dirs if v == max_flood]

    if len(best_dirs) > 1:
        best_dirs.sort(key=lambda x: move_map[x], reverse=False)

    best_move = best_dirs[0]
    return best_move


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
    return move


def distance1(x, y, c, d):
    return abs(x - c) + abs(y - d)

def distance2(x, y, c, d):
    return 10 * (abs(x - c)**2 + abs(y - d)**2)

def distance3(x, y, c, d):
    return 33 * (abs(x - c)**2 + abs(y - d)**2)**0.5

def distance4(x, y, c, d):
    return max(abs(x - c), abs(y - d))


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

        if time() - START > 0.09:
            break
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
                heads = dict((k, HEADS[k]) for k,v in HEADS_F.items())
                heads[board[py][px]] = (c, d)
                BOARDS_FILL[(c, d)] = fill_board(board, heads)
            board_fill = BOARDS_FILL[(c, d)]

        score = max_play(board, x, y, c, d, board_fill, n + 1)
        board[d][c] = 0
        if score < best_score:
            best_score = score

        if time() - START > 0.09:
            break
    return best_score


def minimax(x, y, px, py, move_map, n=1):
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
        if time() - START > 0.08:
            break
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

    if LASTMOVE is None:
        return move_dirs[-1]


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
    if move is None: move = default_move2(x, y)
    if move is None: move = END
    return move


if __name__ == '__main__':
    while True:
        mx, my, HEADS = read_stdin()
        HEADS_F = {}
        BOARDS_FILL = {}
        START = time()
        LASTMOVE = best_move_fast(mx, my)
        print DIR[LASTMOVE]

