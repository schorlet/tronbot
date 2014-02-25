package main

import (
    "container/heap"
    "fmt"
    "math"
    "os"
    "runtime"
    "sort"
    "strings"
    "time"
)

var _ = strings.Repeat

const (
    ID_START int = 10001
    W, H int = 30, 20
    // W, H int = 10, 10
    // ID_START int = 1001
    MAX_DURATION time.Duration = 90 * time.Millisecond
    MID_DURATION time.Duration = 40 * time.Millisecond
)

var (
    UP, RIGHT, DOWN, LEFT, END = Move{0, -1}, Move{1, 0}, Move{0, 1},
        Move{-1, 0}, Move{0, 0}

    DIR = map[Move]string{UP: "UP", RIGHT: "RIGHT", DOWN: "DOWN",
        LEFT: "LEFT", END: "END"}

    BOARD   [H][W]int
    HEADS   map[int]Point
    HEADS_F map[int]bool
    HEADS_N []int
    START   time.Time
)

type (
    Move struct {
        a, b int
    }

    Point struct {
        x, y int
    }

    ByScoreF struct {
        moves  []Move
        scores map[Move]float64
    }

    ByScoreI struct {
        moves  []Move
        scores map[Move]int
    }

    ByDistance struct {
        points    []Point
        distances map[Point]int
    }

    PointQueue []PriorityPoint

    PointsQueue []PriorityPoints

    PriorityPoints struct {
        priority int
        points   []Point
    }

    PriorityPoint struct {
        priority int
        point    Point
    }

    SortedMapByValue struct {
        dict map[int]int
        arra []int
    }

    BC  struct {
        src           Point
        board         *[H][W]int
        dfn           map[Point]int
        low           map[Point]int
        num           int
        articulations map[Point]bool
    }

    CC  struct {
        board     *[H][W]int
        visited   map[Point]bool
        ccid      map[Point]int
        cid_count map[int]int
        cid       int
    }
)


func (bc *BC) bc_point(src Point) bool {
    var value, found = bc.articulations[src]
    return found && value
}
func (bc *BC) bc_dfs(check, parent Point) {
    var child_count int
    bc.num += 1
    bc.low[check] = bc.num
    bc.dfn[check] = bc.num

    neighbors := neighbors_clean(bc.board, check)
    for _, ngb := range neighbors {
        if bc.dfn[ngb] == 0 {
            child_count += 1
            bc.bc_dfs(ngb, check)

            // update low number
            if bc.low[check] > bc.low[ngb] {
                bc.low[check] = bc.low[ngb]
            }

            if parent != bc.src && bc.low[ngb] >= bc.dfn[check] {
                bc.articulations[check] = true
                // debug("Articulation point ", check, "dfn=", bc.dfn[check],
                // "low=", bc.low[ngb])
            }
        } else if ngb != parent {
            if bc.low[check] > bc.dfn[ngb] {
                bc.low[check] = bc.dfn[ngb]
            }
        }
    }
    if parent == bc.src && child_count > 1 {
        bc.articulations[check] = true
    }
}
func bc_init(board *[H][W]int, src Point) BC {
    var dfn, low = map[Point]int{}, map[Point]int{}
    var articulations = map[Point]bool{}
    var bc = BC{src: src, board: board, dfn: dfn, low: low,
            num: 0, articulations: articulations}
    bc.bc_dfs(src, src)
    return bc
}


func (cc *CC) cc_connected(pos0, pos1 Point) bool {
    var cid0 = cc.ccid[pos0]
    var cid1 = cc.ccid[pos1]
    var connected bool
    if cid0 != 0 && cid1 != 0 {
        connected = cid0 == cid1
    } else {
        var cids0 = cc.cc_cids(pos0)
        var cids1 = cc.cc_cids(pos1)
        for cid0 := range cids0 {
            for cid1 := range cids1 {
                if cid0 == cid1 {
                    connected = true
                    break
                }
            }
        }
    }
    return connected
}
func (cc *CC) cc_cid(pos Point) int {
    var cid = cc.ccid[pos]
    if cid > 0 {
        return cid
    }
    var cidmap = map[int]bool{}
    var neighbors = neighbors_clean(cc.board, pos)
    for _, ngb := range neighbors {
        cid = cc.ccid[ngb]
        if cid > 0 && !cidmap[cid] {
            cidmap[cid] = true
        }
    }
    var score int
    for tid := range cidmap {
        var count = cc.cc_cid_count(tid)
        if score < count {
            score = count
            cid = tid
        }
    }
    return cid
}
func (cc *CC) cc_cids(pos Point) map[int]bool {
    var cid = cc.ccid[pos]
    if cid > 0 {
        return map[int]bool{cid: true}
    }
    var cidmap = map[int]bool{}
    var neighbors = neighbors_clean(cc.board, pos)
    for _, ngb := range neighbors {
        cid = cc.ccid[ngb]
        if cid > 0 && !cidmap[cid] {
            cidmap[cid] = true
        }
    }
    return cidmap
}
func (cc *CC) cc_cid_count(cid int) int {
    return cc.cid_count[cid]
}
func (cc *CC) cc_dfs(src Point) {
    cc.visited[src] = true
    cc.ccid[src] = cc.cid + 1
    cc.cid_count[cc.cid+1] += 1

    var neighbors = neighbors_clean(cc.board, src)
    for _, ngb := range neighbors {
        if cc.visited[ngb] {
            continue
        }
        cc.cc_dfs(ngb)
    }
}
func cc_init(board *[H][W]int) CC {
    var visited = map[Point]bool{}
    var ccid = map[Point]int{}
    var cid_count = map[int]int{}
    var cc = CC{board: board, visited: visited, ccid: ccid, cid_count: cid_count}
    for y := 0; y < H; y++ {
        for x := 0; x < W; x++ {
            if board[y][x] != 0 {
                continue
            }
            p := Point{x, y}
            if cc.visited[p] {
                continue
            }
            cc.cc_dfs(p)
            cc.cid += 1
        }
    }
    return cc
}


func (move Move) String() string {
    return DIR[move]
}
func (move Move) IsInverse(other Move) bool {
    return move == Move{other.a * -1, other.b * -1}
}
func (move Move) Inverse() Move {
    return Move{move.a * -1, move.b * -1}
}
func (point Point) String() string {
    // return fmt.Sprintf("%+v", point)
    return fmt.Sprintf("(%d, %d)", point.x, point.y)
}


func (bs ByScoreF) Len() int {
    return len(bs.moves)
}
func (bs ByScoreF) Swap(i, j int) {
    bs.moves[i], bs.moves[j] = bs.moves[j], bs.moves[i]
}
func (bs ByScoreF) Less(i, j int) bool {
    var move0, move1 = bs.moves[i], bs.moves[j]
    return bs.scores[move0] > bs.scores[move1]
}


func (bs ByScoreI) Len() int {
    return len(bs.moves)
}
func (bs ByScoreI) Swap(i, j int) {
    bs.moves[i], bs.moves[j] = bs.moves[j], bs.moves[i]
}
func (bs ByScoreI) Less(i, j int) bool {
    var move0, move1 = bs.moves[i], bs.moves[j]
    return bs.scores[move0] > bs.scores[move1]
}


func (bd ByDistance) Len() int {
    return len(bd.points)
}
func (bd ByDistance) Swap(i, j int) {
    bd.points[i], bd.points[j] = bd.points[j], bd.points[i]
}
func (bd ByDistance) Less(i, j int) bool {
    var point0, point1 = bd.points[i], bd.points[j]
    return bd.distances[point0] < bd.distances[point1]
}


func (pqueue PointsQueue) Len() int {
    return len(pqueue)
}
func (pqueue PointsQueue) Less(i, j int) bool {
    return pqueue[i].priority < pqueue[j].priority
}
func (pqueue PointsQueue) Swap(i, j int) {
    pqueue[i], pqueue[j] = pqueue[j], pqueue[i]
}
func (pqueue *PointsQueue) Push(x interface{}) {
    *pqueue = append(*pqueue, x.(PriorityPoints))
}
func (pqueue *PointsQueue) Pop() interface{} {
    oldq := *pqueue
    ppoints := oldq[len(oldq)-1]
    newq := oldq[0 : len(oldq)-1]
    *pqueue = newq
    return ppoints
}


func (pqueue PointQueue) Len() int {
    return len(pqueue)
}
func (pqueue PointQueue) Less(i, j int) bool {
    return pqueue[i].priority < pqueue[j].priority
}
func (pqueue PointQueue) Swap(i, j int) {
    pqueue[i], pqueue[j] = pqueue[j], pqueue[i]
}
func (pqueue *PointQueue) Push(x interface{}) {
    *pqueue = append(*pqueue, x.(PriorityPoint))
}
func (pqueue *PointQueue) Pop() interface{} {
    oldq := *pqueue
    ppoint := oldq[len(oldq)-1]
    newq := oldq[0 : len(oldq)-1]
    *pqueue = newq
    return ppoint
}


func (sm *SortedMapByValue) Len() int {
    return len(sm.dict)
}
func (sm *SortedMapByValue) Less(i, j int) bool {
    return sm.dict[sm.arra[i]] < sm.dict[sm.arra[j]]
}
func (sm *SortedMapByValue) Swap(i, j int) {
    sm.arra[i], sm.arra[j] = sm.arra[j], sm.arra[i]
}
func sortByValue(dict map[int]int) []int {
    sm := new(SortedMapByValue)
    sm.dict = dict
    sm.arra = make([]int, len(dict))
    i := 0
    for key := range dict {
        sm.arra[i] = key
        i++
    }
    sort.Sort(sm)
    return sm.arra
}


func clear_pid(pid int) {
    for y := 0; y < H; y++ {
        for x := 0; x < W; x++ {
            if BOARD[y][x] == pid {
                BOARD[y][x] = 0
            }
        }
    }
}
func read_stdin() Point {
    var mx, my int
    HEADS = make(map[int]Point)
    HEADS_F = make(map[int]bool)

    var nbj, mid int
    fmt.Scanf("%d %d", &nbj, &mid)
    mid = ID_START + mid

    for pid := ID_START; pid < ID_START+nbj; pid++ {
        var x0, y0, x1, y1 int
        fmt.Scanf("%d %d %d %d", &x0, &y0, &x1, &y1)

        if x1 == -1 && y1 == -1 {
            clear_pid(pid)

        } else {
            BOARD[y0][x0] = pid
            BOARD[y1][x1] = pid

            if pid == mid {
                mx, my = x1, y1
            } else {
                HEADS[pid] = Point{x1, y1}
            }
        }
    }
    HEADS_N = []int{}
    for pid := mid+1; pid < ID_START+4; pid++ {
        if _, ok := HEADS[pid]; ok {
            HEADS_N = append(HEADS_N, pid)
        }
    }
    for pid := ID_START; pid < mid; pid++ {
        if _, ok := HEADS[pid]; ok {
            HEADS_N = append(HEADS_N, pid)
        }
    }
    HEADS_N = append(HEADS_N, mid)
    return Point{mx, my}
}
func in_board(point Point) bool {
    return 0 <= point.x &&
        0 <= point.y &&
        point.x < W &&
        point.y < H
}
func is_clean(board *[H][W]int, point Point) bool {
    return in_board(point) && board[point.y][point.x] == 0
}
func next_pos(point Point, move Move) Point {
    return Point{point.x + move.a, point.y + move.b}
}
func neighbors(point Point) []Point {
    var neighbors = []Point{}
    var moves = [4]Move{UP, RIGHT, DOWN, LEFT}
    for _, move := range moves {
        var next = next_pos(point, move)
        if in_board(next) {
            neighbors = append(neighbors, next)
        }
    }
    return neighbors
}
func neighbors_clean(board *[H][W]int, point Point) []Point {
    var neighbors = []Point{}
    var moves = [4]Move{UP, RIGHT, DOWN, LEFT}
    for _, move := range moves {
        var next = next_pos(point, move)
        if is_clean(board, next) {
            neighbors = append(neighbors, next)
        }
    }
    return neighbors
}
func neighbors_count(board *[H][W]int, point Point) int {
    var count int
    var moves = [4]Move{UP, RIGHT, DOWN, LEFT}
    for _, move := range moves {
        var next = next_pos(point, move)
        if is_clean(board, next) {
            count += 1
        }
    }
    return count
}
func neighbors_clean_heads(board *[H][W]int, point Point) []Point {
    var neighbors = []Point{}
    var moves = [4]Move{UP, RIGHT, DOWN, LEFT}
    for _, move := range moves {
        var next = next_pos(point, move)
        if is_clean(board, next) {
            neighbors = append(neighbors, next)
        } else {
            for _, pos := range HEADS {
                if next == pos {
                    neighbors = append(neighbors, next)
                    break
                }
            }
        }
    }
    return neighbors
}
func moves_clean(board *[H][W]int, point Point) []Move {
    var cleans = []Move{}
    var moves = [4]Move{UP, RIGHT, DOWN, LEFT}
    for _, move := range moves {
        var next = next_pos(point, move)
        if is_clean(board, next) {
            cleans = append(cleans, move)
        }
    }
    return cleans
}


func distance1(src, dest Point) int {
    return int(math.Abs(float64(src.x-dest.x)) +
        math.Abs(float64(src.y-dest.y)))
}
func distance2(src, dest Point) int {
    return int(10 * (math.Pow(math.Abs(float64(src.x-dest.x)), 2) +
        math.Pow(math.Abs(float64(src.y-dest.y)), 2)))
}
func distance3(src, dest Point) float64 {
    return 33 * (math.Sqrt(math.Abs(float64(src.x-dest.x))) +
        math.Sqrt(math.Abs(float64(src.y-dest.y))))
}
func distance4(src, dest Point) int {
    return int(math.Max(math.Abs(float64(src.x-dest.x)),
        math.Abs(float64(src.y-dest.y))))
}
func distance5(src, dest Point) int {
    return int(math.Min(math.Abs(float64(src.x-dest.x)),
        math.Abs(float64(src.y-dest.y))))
}
func directions(src, dest Point) map[Move]bool {
    dirs := map[Move]bool{}
    xx := dest.x - src.x
    yy := dest.y - src.y
    if xx > 0 {
        dirs[RIGHT] = true
    } else if xx < 0 {
        dirs[LEFT] = true
    }
    if yy > 0 {
        dirs[DOWN] = true
    } else if yy < 0 {
        dirs[UP] = true
    }
    return dirs
}


func debug_board(board *[H][W]int) {
    fmt.Fprintf(os.Stderr, "%3d |", -1)
    for x := range board[0] {
        fmt.Fprintf(os.Stderr, "%5d", x)
    }
    fmt.Fprintln(os.Stderr)
    fmt.Fprint(os.Stderr, "----+")
    for _ = range board[0] {
        fmt.Fprint(os.Stderr, "-----")
    }
    fmt.Fprintln(os.Stderr)
    for y := range board {
        fmt.Fprintf(os.Stderr, "%3d |", y)
        for x := range board[y] {
            fmt.Fprintf(os.Stderr, "%5d", board[y][x])
        }
        fmt.Fprintln(os.Stderr)
    }
    fmt.Fprintln(os.Stderr, "----------------------")
}
func clean_board(board *[H][W]int) {
    for y := range board {
        for x := range board[y] {
            value := board[y][x]
            if value > 0 && value < ID_START {
                board[y][x] = 0
            }
        }
    }
}
func debug(args ...interface{}) {
    fmt.Fprintln(os.Stderr, args)
}


func __best_dest(board *[H][W]int, src, dest Point) []Point {
    var dest_path []Point
    pqueue := &PointsQueue{}
    heap.Init(pqueue)
    heap.Push(pqueue, PriorityPoints{0, []Point{src}})

    for dest_path == nil && pqueue.Len() > 0 {
        ppoints := heap.Pop(pqueue).(PriorityPoints)
        next := ppoints.points[len(ppoints.points)-1]
        neighbors := neighbors_clean_heads(board, next)
        // debug(ppoints.priority, next)

        for _, ngb := range neighbors {
            if ngb == dest {
                // dest_path = make([]Point, len(ppoints.points))
                // copy(dest_path, ppoints.points)

                // dest_path = ppoints.points

                dest_path = append([]Point(nil), ppoints.points...)
                break
            }

            value := board[ngb.y][ngb.x]
            if value == 0 {
                // value2 := distance2(ngb, dest)
                value2 := int(distance3(ngb, dest))
                board[ngb.y][ngb.x] = value2

                // n := len(ppoints.points)
                // new_points := make([]Point, n, n+1)
                // copy(new_points, ppoints.points)
                // new_points = append(new_points, ngb)

                new_points := append([]Point(nil), ppoints.points...)
                new_points = append(new_points, ngb)

                new_ppoints := PriorityPoints{value2, new_points}
                heap.Push(pqueue, new_ppoints)
            }
        }
    }

    // clean_board(board)
    // for i, pos := range dest_path {
    // if i == 0 { continue }
    // board[pos.y][pos.x] = i
    // }
    // debug_board(board)
    return dest_path
}
func best_dest(board [H][W]int, src, dest Point) (Move, []Point) {
    dest_path := __best_dest(&board, src, dest)
    if len(dest_path) > 1 {
        next := dest_path[1]
        move := Move{next.x - src.x, next.y - src.y}
        // debug("best_dest", dest, DIR[move], dest_path, time.Since(START))
        return move, dest_path[1:len(dest_path)]
    }
    return END, dest_path
}

func evaluate(board *[H][W]int, src, dest Point) int {
    var sources = map[Point]int{}
    var connection bool

    var cc = cc_init(board)
    var board_fill = *board

    var mid = board[src.y][src.x]
    var hid = board[dest.y][dest.x]

    for _, pid := range HEADS_N {
        var pos Point
        if pid == mid {
            pos = src
        } else if pid == hid && cc.cc_connected(src, dest) {
            pos = dest
            connection = true
        } else if cc.cc_connected(src, HEADS[pid]) {
            pos = HEADS[pid]
            connection = true
        } else {
            continue
        }

        var pqueue = &PointQueue{}
        heap.Init(pqueue)
        heap.Push(pqueue, PriorityPoint{0, pos})

        for pqueue.Len() > 0 {
            var ppoint = heap.Pop(pqueue).(PriorityPoint)
            var dist = ppoint.priority
            var next = ppoint.point
            var neighbors = neighbors_clean(board, next)

            for _, ngb := range neighbors {
                var value = board_fill[ngb.y][ngb.x]

                var dist2 = distance1(pos, ngb)
                if dist2 <= dist {
                    dist2 = dist + 1
                }

                if value == 0 || dist2 < value {
                    board_fill[ngb.y][ngb.x] = dist2
                    sources[ngb] = pid
                    heap.Push(pqueue, PriorityPoint{dist2, ngb})

                // } else if pid == mid && dist2 == value {
                    // sources[ngb] = pid
                }
            }
        }
    }
    var counter = map[int]int{}
    // var bc = bc_init(board, src)
    for point, pid := range sources {
        if pid == mid {
            var nc = neighbors_count(board, point)
            switch nc {
                case 2: nc = 6
                case 3: nc = 18
                case 4: nc = 20
            }
            // if bc.bc_point(point) {
                // nc -= 2
            // }
            counter[cc.ccid[point]] += nc
        }
    }
    var score int
    for _, value := range counter {
        if value > score {
            score = value
        }
    }
    if !connection {
        score = 2 * score / 3
    }
    // debug("        evaluate", src, score)
    return score
}

func max_play(board *[H][W]int, next Point, dest Point,
    alpha int, beta int, n int) int {
    // debug(strings.Repeat("  ", 2-n), "max_play", n, next, dest)

    var best_score = math.MinInt32
    var neighbors = neighbors_clean(board, next)
    if len(neighbors) == 0 {
        return best_score
    }

    var distances = map[Point]int{}
    for _, ngb := range neighbors {
        distances[ngb] = distance1(dest, ngb)
    }
    sort.Sort(ByDistance{neighbors, distances})

    var score int
    for _, ngb := range neighbors {
        board[ngb.y][ngb.x] = board[next.y][next.x]
        if n == 0 {
            score = evaluate(board, ngb, dest)
        } else {
            score = min_play(board, ngb, dest, alpha, beta, n-1)
        }
        board[ngb.y][ngb.x] = 0

        if score > best_score {
            best_score = score
        }

        if time.Since(START) > MAX_DURATION {
            break
        }
        alpha = int(math.Max(float64(alpha), float64(score)))
        if beta <= alpha {
            break
        }
    }

    return best_score
}
func min_play(board *[H][W]int, next Point, dest Point,
    alpha int, beta int, n int) int {
    // debug(strings.Repeat("  ", 2-n), "min_play", n, next, dest)

    var best_score = math.MaxInt32
    var neighbors = neighbors_clean(board, dest)
    if len(neighbors) == 0 {
        return best_score
    }

    var distances = map[Point]int{}
    for _, ngb := range neighbors {
        distances[ngb] = distance1(next, ngb)
    }
    sort.Sort(ByDistance{neighbors, distances})

    var score int
    for _, ngb := range neighbors {
        board[ngb.y][ngb.x] = board[dest.y][dest.x]
        if n == 0 {
            score = evaluate(board, next, ngb)
        } else {
            score = max_play(board, next, ngb, alpha, beta, n-1)
        }
        board[ngb.y][ngb.x] = 0

        if score < best_score {
            best_score = score
        }

        if time.Since(START) > MAX_DURATION {
            break
        }
        beta = int(math.Min(float64(beta), float64(score)))
        if beta <= alpha {
            break
        }
    }

    return best_score
}

func select_head(board *[H][W]int, src Point) []int {
    var head_dists = map[int]int{}

    for pid := range HEADS_F {
        _, path := best_dest(*board, src, HEADS[pid])
        head_dists[pid] = len(path)
    }

    var heads_d = sortByValue(head_dists)
    return heads_d
}
func head_min(board *[H][W]int, src Point) Move {
    var move_dirs = moves_clean(board, src)
    if len(move_dirs) <= 1 {
        return END
    }

    var cc = cc_init(board)
    for pid, point := range HEADS {
        if cc.cc_connected(src, point) {
            HEADS_F[pid] = true
        }
    }

    if len(HEADS_F) == 0 {
        return END
    }

    var heads_d = select_head(board, src)
    var head0 = heads_d[0]

    var best_scores = map[Move]int{}
    var alpha, beta = math.MinInt32, math.MaxInt32
    var score int
    var best_move Move

    var m = 2
    if len(move_dirs) == 4 {
        m = 1
    }
    for n := 0; n < m; n++ {
        for _, move := range move_dirs {
            board_copy := *board

            func(board_calcul *[H][W]int, move Move) {
                var next = next_pos(src, move)
                var dest = HEADS[head0]

                if !cc.cc_connected(next, dest) {
                    for i, pid := range heads_d {
                        if i == 0 {
                            continue
                        }
                        if HEADS_F[pid] && cc.cc_connected(next, HEADS[pid]) {
                            dest = HEADS[pid]
                        }
                    }
                }

                board_calcul[next.y][next.x] = board_calcul[src.y][src.x]
                if n == 0 {
                    score = evaluate(board_calcul, next, dest)
                } else {
                    score = min_play(board_calcul, next, dest, alpha, beta, n)
                }

                board_calcul[next.y][next.x] = 0
                best_scores[move] = score

            }(&board_copy, move)
        }

        debug("minimax", best_scores)
        sort.Sort(ByScoreI{move_dirs, best_scores})
        best_move = move_dirs[0]

        if time.Since(START) > MID_DURATION {
            break
        }
        if n == 0 {
            var scores = sort.IntSlice{}
            for _, score := range best_scores {
                scores = append(scores, score)
            }
            sort.Sort(scores)
            alpha, beta = scores[0], scores[scores.Len()-1]
            // debug(n, "alpha:", alpha, "beta:", beta)
        }
    }
    return best_move
}


func dm_dfs(board *[H][W]int, src Point, visited map[Point]bool, isbc bool) int {
    var neighbors = neighbors_clean(board, src)
    var count = 1
    for _, ngb := range neighbors {
        var score int
        if !visited[ngb] {
            visited[ngb] = true
            if isbc {
                score = 1 + dm_dfs(board, ngb, visited, false)
            } else {
                score += dm_dfs(board, ngb, visited, false)
            }
        }
        if isbc {
            count = int(math.Max(float64(count), float64(score)))
        } else {
            count += score
        }
    }
    return count
}
func dm_dfs_start(board *[H][W]int, src Point) int {
    // var bc = bc_init(board, src)
    // var board_bc = *board
    // for point := range bc.articulations {
    // if point != src {
    // board_bc[point.y][point.x] = -1
    // }
    // }
    // debug_board(&board_bc)
    var visited = map[Point]bool{}
    var count = dm_dfs(board, src, visited, true)
    return count
}

func dm_max(board *[H][W]int, src Point, n int) int {
    var neighbors = neighbors_clean(board, src)
    var best_score = 1

    var score int
    for _, ngb := range neighbors {
        board[ngb.y][ngb.x] = board[src.y][src.x]
        if n == 0 {
            score = dm_dfs_start(board, ngb)
        } else {
            score = 1 + dm_max(board, ngb, n-1)
        }
        board[ngb.y][ngb.x] = 0

        if score > best_score {
            best_score = score
        }
    }
    return best_score
}
func dm_neighbors(board *[H][W]int, src Point, n int) int {
    var neighbors = neighbors_clean(board, src)

    var best_score = len(neighbors)
    best_score = 10 - best_score*best_score

    if n > 0 {
        var alt_score int
        for _, ngb := range neighbors {
            board[ngb.y][ngb.x] = board[src.y][src.x]
            var score = dm_neighbors(board, ngb, n-1)
            board[ngb.y][ngb.x] = 0

            if score > alt_score {
                alt_score = score
            }
        }
        best_score += alt_score
    }
    return best_score
}
func default_move(board *[H][W]int, src Point) Move {
    var move_dirs = moves_clean(board, src)
    var move_len = len(move_dirs)

    if move_len == 0 {
        return END
    } else if move_len == 1 {
        return move_dirs[0]
    }

    var best_scores = map[Move]int{}
    var neighbors = map[Move]int{}

    for _, move := range move_dirs {
        next := next_pos(src, move)
        board[next.y][next.x] = board[src.y][src.x]
        best_scores[move] = dm_max(board, next, 3)
        neighbors[move] = dm_neighbors(board, next, 6)
        board[next.y][next.x] = 0
    }
    // debug("best_scores", best_scores, neighbors)

    sort.Sort(ByScoreI{move_dirs, best_scores})
    var best_move = move_dirs[0]

    var best_score = best_scores[best_move]
    var best_moves = []Move{}

    for _, move := range move_dirs {
        if best_scores[move] == best_score {
            best_moves = append(best_moves, move)
        }
    }

    if len(best_moves) > 1 {
        sort.Sort(ByScoreI{best_moves, neighbors})
        best_move = best_moves[0]
    }

    return best_move
}

func best_move_fast(board [H][W]int, src Point) Move {
    var best_move = head_min(&board, src)
    if best_move == END {
        best_move = default_move(&board, src)
    }
    // debug(time.Since(START))
    return best_move
}

func main() {
    for {
        var src = read_stdin()
        START = time.Now()
        var move = best_move_fast(BOARD, src)
        fmt.Println(move)
    }
}
func init() {
    runtime.LockOSThread()
}
