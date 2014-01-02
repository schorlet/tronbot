import sys, copy, heapq
from time import time
from collections import deque, defaultdict, OrderedDict
from operator import itemgetter

UP, RIGHT, DOWN, LEFT, END = (0, -1), (1, 0), (0, 1), (-1, 0), (0, 0)
DIR = {UP: 'UP', RIGHT: 'RIGHT', DOWN: 'DOWN', LEFT: 'LEFT', END: 'END'}
W, H = 30, 20
BOARD = [[0 for _ in range(W)] for _ in range(H)]
ID_START = 10001
HEADS, HEADS_F = None, None
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
    neighbors = []
    for (xx, yy) in (next_pos(x, y, UP),   next_pos(x, y, RIGHT),
                     next_pos(x, y, DOWN), next_pos(x, y, LEFT)):
        if in_board(xx, yy):
            neighbors.append((xx, yy))
    return neighbors


def neighbors_clean(board, x, y):
    neighbors = []
    for (xx, yy) in (next_pos(x, y, UP),   next_pos(x, y, RIGHT),
                     next_pos(x, y, DOWN), next_pos(x, y, LEFT)):
        if is_clean(board, xx, yy):
            neighbors.append((xx, yy))
    return neighbors


def neighbors_clean_heads(board, x, y):
    neighbors = []
    for (xx, yy) in (next_pos(x, y, UP),   next_pos(x, y, RIGHT),
                     next_pos(x, y, DOWN), next_pos(x, y, LEFT)):
        if in_board(xx, yy) and (
                board[yy][xx] == 0 or (xx, yy) in HEADS.values()):
            neighbors.append((xx, yy))
    return neighbors


def moves_clean(board, x, y):
    moves = [move for move in (UP, RIGHT, DOWN, LEFT)
            if is_clean(board, *next_pos(x, y, move))]
    return moves


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


def fill_board(board, heads, me):
    sources = dict()

    pids = heads.items()
    pids.append(me)

    board_fill = copy.deepcopy(board)

    for pid, pos in pids:
        # print >> sys.stderr, 'fill_board', pid, pos
        px, py = pos
        points = [(0, pos)]
        heapq.heapify(points)
        count = 0

        while points:
            dist, point = heapq.heappop(points)
            for (xx, yy) in neighbors_clean(board, *point):
                value = board_fill[yy][xx]

                dist2 = distance1(px, py, xx, yy)
                if dist2 <= dist: dist2 = dist + 1

                if value == 0 or dist2 < value:
                    board_fill[yy][xx] = dist2
                    sources[(xx, yy)] = pid
                    heapq.heappush(points, (dist2, (xx, yy)))
                    count += 1
            if count > 300:
                break

    values = sources.values()
    counter = dict((pid, values.count(pid)) for pid, _ in pids)
    return counter


def flood_find(x, y):
    board_copy = copy.deepcopy(BOARD)
    board_copy[y][x] = -2

    points = deque([(x, y)])
    count = 0

    while points:
        point = points.popleft()
        for (xx, yy) in neighbors_clean_heads(board_copy, *point):
            value = board_copy[yy][xx]
            if value == 0:
                board_copy[yy][xx] = 1
                points.append((xx, yy))
                count += 1

            elif not value in HEADS_F:
                HEADS_F[value] = directions(xx - x, yy - y)
                if len(HEADS_F) == len(HEADS):
                    points = None
                    break
    return count


def flood_count(x, y):
    board_copy = copy.deepcopy(BOARD)
    return flood_count_2(board_copy, x, y)


def flood_count_2(board_copy, x, y):
    points = deque([(x, y)])
    count = 0

    while points:
        point = points.popleft()
        for (xx, yy) in neighbors_clean(board_copy, *point):
            if (xx, yy) == (x, y): continue

            count += 1
            board_copy[yy][xx] = count
            points.append((xx, yy))
    return count


def default_move(x, y):
    moves = moves_clean(BOARD, x, y)

    if len(moves) == 0:
        return None
    elif len(moves) == 1:
        return moves[0]

    best_scores = dict((move, 0) for move in moves)
    board_copy = copy.deepcopy(BOARD)

    def dm_move(px, py, limit):
        if limit == 0:
            board_count = copy.deepcopy(board_copy)
            return flood_count_2(board_count, px, py)

        neighbors = neighbors_clean(board_copy, px, py)
        count = 0

        for c, d in neighbors:
            board_copy[d][c] = board_copy[py][px]
            count = max(count, dm_move(c, d, limit - 1))
            board_copy[d][c] = 0
        return count

    for i in range(3):
        for move in moves:
            c, d = next_pos(x, y, move)
            board_copy[d][c] = board_copy[y][x]
            best_scores[move] += dm_move(c, d, i)
            board_copy[d][c] = 0

    best_dirs = best_scores.keys()
    best_dirs.sort(key=lambda x: best_scores[x], reverse=True)

    scores = set(best_scores.values())

    if len(scores) == len(moves):
        best_move = best_dirs[0]

    else:
        max_score = max(scores)
        best_dirs = [move for move in best_dirs
                    if max_score == best_scores[move]]
        neighbors = dict()

        for move in best_dirs:
            c, d = next_pos(x, y, move)
            board_copy[d][c] = board_copy[y][x]
            neighbors[move] = len(neighbors_clean(board_copy, c, d))
            board_copy[d][c] = 0

        best_dirs.sort(key=lambda x: neighbors[x])
        neighbors_scores = set(neighbors.values())

        if len(neighbors_scores) == len(best_dirs):
            best_move = best_dirs[0]

        elif len(moves) == 2:
            for move in best_dirs:
                c, d = next_pos(x, y, move)
                best_scores[move] = distance2(x, y, c, d)
            best_dirs.sort(key=lambda x: best_scores[x])
            best_move = best_dirs[0]

        else:
            min_score = min(scores)
            for move, score in best_scores.items():
                if score == min_score: min_move = move
            a, b = next_pos(x, y, min_move)
            c, d = next_pos(x, y, min_move)

            if in_board(c, d):
                for move in best_dirs:
                    c, d = next_pos(x, y, move)
                    best_scores[move] = distance2(x, y, c, d)

            else:
                board_copy[b][a] = board_copy[y][x]
                for move in best_dirs:
                    c, d = next_pos(x, y, move)
                    board_copy[d][c] = board_copy[y][x]
                    best_scores[move] = dm_move(c, d, 0)
                    board_copy[d][c] = 0
                board_copy[b][a] = 0

            print >> sys.stderr, 'default_move', best_scores
            best_dirs.sort(key=lambda x: best_scores[x])
            best_move = best_dirs[0]

    return best_move


def __best_dest(x, y, hx, hy):
    board_copy = copy.deepcopy(BOARD)
    path = None

    points = [(0, [(x, y)])]
    heapq.heapify(points)

    while path is None and points:
        value1, points2 = heapq.heappop(points)
        px, py = points2[-1]

        for (xx, yy) in neighbors_clean_heads(board_copy, px, py):
            if (xx, yy) == (hx, hy):
                path = points2 + [(xx, yy)]
                break

            value2 = board_copy[yy][xx]
            if value2 == 0:
                value2 = distance2(xx, yy, hx, hy)
                board_copy[yy][xx] = value2
                heapq.heappush(points, (value2, points2 + [(xx, yy)]))
    return path


def best_dest(x, y, hx, hy):
    path = __best_dest(x, y, hx, hy)
    if path:
        a, b = path[1]
        move = (a - x, b - y)
        print >> sys.stderr, 'best_dest', DIR[move], time() - START
        return move, path[1:-1]
    return None, None


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


def max_play(board, x, y, px, py, alpha, beta, n):
    best_score = ~sys.maxint

    neighbors = neighbors_clean(board, x, y)
    if len(neighbors) == 0:
        return best_score

    for c, d in neighbors:
        board[d][c] = board[y][x]
        if n == 0:
            score = evaluate(board, c, d, px, py)
        else:
            score = min_play(board, c, d, px, py, alpha, beta, n - 1)
        board[d][c] = 0

        if score > best_score:
            best_score = score

        if time() - START > 0.09:
            break

    return best_score


def min_play(board, x, y, px, py, alpha, beta, n):
    best_score = sys.maxint

    neighbors = neighbors_clean(board, px, py)
    if len(neighbors) == 0:
        return best_score

    for c, d in neighbors:
        board[d][c] = board[py][px]
        if n == 0:
            score = evaluate(board, x, y, c, d)
        else:
            score = max_play(board, x, y, c, d, alpha, beta, n - 1)
        board[d][c] = 0

        if score < best_score:
            best_score = score

        if time() - START > 0.09:
            break

    return best_score


def evaluate(board, x, y, px, py):
    heads = dict((pid, HEADS[pid]) for pid in HEADS_F)
    mid = board[y][x]
    pid = board[py][px]
    heads[pid] = (px, py)
    counter = fill_board(board, heads, (mid, (x, y)))
    if counter[pid] == 0: counter[pid] = 1
    score = 1.0 * counter[mid]**2 / counter[pid]
    return score


def head_min(x, y):
    flood_find(x, y)
    if len(HEADS_F) == 0:
        return None

    move_dirs = moves_clean(BOARD, x, y)

    # move_dirs <= 1
    if len(move_dirs) <= 1:
        return None

    # heads
    heads = sorted(HEADS_F.keys(), key=lambda pid: distance2(x, y, *HEADS[pid]))
    head0 = heads[0]

    px, py = HEADS[head0]
    dirs = tuple(e for e in HEADS_F[head0] if e != END)
    print >> sys.stderr, 'PID', head0, [DIR[dir] for dir in dirs], (px, py)

    best_scores = dict((move, ~sys.maxint) for move in move_dirs)
    board = copy.deepcopy(BOARD)
    best_move = None

    for n in range(2):
        for move in move_dirs:
            c, d = next_pos(x, y, move)
            board[d][c] = board[y][x]

            if n == 0:
                best_scores[move] = evaluate(board, c, d, px, py)
            else:
                best_scores[move] = min_play(board, c, d, px, py, alpha, beta, n)
            board[d][c] = 0
            # print >> sys.stderr, 'minimax', n, DIR[move], best_scores[move], time() - START

            if time() - START > 0.08:
                break

        move_dirs.sort(key=lambda x: best_scores[x], reverse=True)
        scores = set(best_scores.values())
        alpha, beta = min(scores), max(scores)

        if n == 0 and len(move_dirs) > 2 and alpha < 0.66 * beta:
            del move_dirs[-1]

        if n == 1 and len(move_dirs) > 2:
            del move_dirs[-1]

        if time() - START > 0.08:
            break

    move_dirs.sort(key=lambda x: best_scores[x], reverse=True)
    best_move = move_dirs[0]

    if time() - START < 0.08:
        dist2 = distance2(x, y, px, py)
        if dist2 > 380:
            move, path = best_dest(x, y, px, py)
            if move != best_move and move in best_scores:
                if best_scores[move] > 0.8 * best_scores[best_move]:
                    best_move = move

        scores = set(best_scores.values())
        if len(scores) == 1:
            distances = dict()
            for move in move_dirs:
                c, d = next_pos(x, y, move)
                distances[move] = distance2(c, d, px, py)
            move_dirs.sort(key=lambda x: distances[x])
            best_move = move_dirs[0]

    return best_move


def best_move_fast(x, y):
    move = head_min(x, y)
    if move is None: move = default_move(x, y)
    if move is None: move = END
    print >> sys.stderr, DIR[move], time() - START
    return move


if __name__ == '__main__':
    while True:
        mx, my, HEADS = read_stdin()
        HEADS_F = {}
        START = time()
        LASTMOVE = best_move_fast(mx, my)
        print DIR[LASTMOVE]

