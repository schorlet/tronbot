package main

import (
    "container/heap"
    "fmt"
    "math"
    "os"
    "runtime"
    "sort"
    "strings"
    "sync"
    "time"
)
var _ = strings.Repeat

const (
    // ID_START int = 10001
    // W, H int = 30, 20
    W, H int = 10, 10
    ID_START int = 1001
    MAX_DURATION time.Duration = 90 * time.Millisecond
)

var (
    UP, RIGHT, DOWN, LEFT, END = Move{0, -1}, Move{1, 0}, Move{0, 1},
        Move{-1, 0}, Move{0, 0}

    DIR = map[Move]string{UP: "UP", RIGHT: "RIGHT", DOWN: "DOWN",
        LEFT: "LEFT", END: "END"}

    BOARD    [H][W]int
    HEADS    map[int]Point
    HEADS_F  map[int]bool
    HEADS_N  []int
    START    time.Time
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

    BC struct {
        src Point
        board *[H][W]int
        dfn map[Point]int
        low map[Point]int
        num int
        articulations []Point
    }

    CC struct {
        board *[H][W]int
        visited map[Point]bool
        ccid map[Point]int
        cid_count map[int]int
        cid int
    }
)


func (bc *BC) bc_point(src Point) bool {
    var found bool
    for _, point := range bc.articulations {
        if point == src {
            found = true
            break
        }
    }
    return found
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
            if bc.low[check] >= bc.low[ngb] {
                bc.low[check] = bc.low[ngb]
            }

            if parent != bc.src && bc.low[ngb] >= bc.dfn[check] {
                bc.articulations = append(bc.articulations, check)
                // debug("Articulation point ", check, "dfn=", bc.dfn[check],
                    // "low=", bc.low[ngb])
            }
        } else if ngb != parent {
            if bc.low[check] >= bc.dfn[ngb] {
                bc.low[check] = bc.dfn[ngb]
            }
        }
    }
    if parent == bc.src && child_count > 1 {
        bc.articulations = append(bc.articulations, check)
    }
}
func bc_init(board *[H][W]int, src Point) BC {
    bc := BC{src: src, board: board,
            dfn: map[Point]int{}, low: map[Point]int{},
            num: 0, articulations: []Point{}}
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
        for cid0, _ := range cids0 {
            for cid1, _ := range cids1 {
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
    return cc.ccid[pos]
}
func (cc *CC) cc_cids(pos Point) map[int]bool {
    var cid = cc.ccid[pos]
    if cid > 0 {
        return map[int]bool{cid:true}
    }
    cidmap := map[int]bool{}
    neighbors := neighbors_clean(cc.board, pos)
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
    cc.cid_count[cc.cid + 1] += 1

    neighbors := neighbors_clean(cc.board, src)
    for _, ngb := range neighbors {
        if cc.visited[ngb] {
            continue
        }
        cc.cc_dfs(ngb)
    }
}
func cc_init(board *[H][W]int) CC {
    cc := CC{board: board, visited: map[Point]bool{},
        ccid: map[Point]int{}, cid_count: map[int]int{}}
    for y := 0; y < H; y++ {
        for x := 0; x < W; x++ {
            if board[y][x] != 0 {
                continue
            }
            p := Point{x,y}
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
    move0, move1 := bs.moves[i], bs.moves[j]
    return bs.scores[move0] > bs.scores[move1]
}


func (bs ByScoreI) Len() int {
    return len(bs.moves)
}
func (bs ByScoreI) Swap(i, j int) {
    bs.moves[i], bs.moves[j] = bs.moves[j], bs.moves[i]
}
func (bs ByScoreI) Less(i, j int) bool {
    move0, move1 := bs.moves[i], bs.moves[j]
    return bs.scores[move0] > bs.scores[move1]
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
    for key, _ := range dict {
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
    neighbors := []Point{}
    moves := [4]Move{UP, RIGHT, DOWN, LEFT}
    for _, move := range moves {
        next := next_pos(point, move)
        if in_board(next) {
            neighbors = append(neighbors, next)
        }
    }
    return neighbors
}
func neighbors_clean(board *[H][W]int, point Point) []Point {
    neighbors := []Point{}
    moves := [4]Move{UP, RIGHT, DOWN, LEFT}
    for _, move := range moves {
        next := next_pos(point, move)
        if is_clean(board, next) {
            neighbors = append(neighbors, next)
        }
    }
    return neighbors
}
func neighbors_count(board *[H][W]int, point Point) int {
    var count int
    moves := [4]Move{UP, RIGHT, DOWN, LEFT}
    for _, move := range moves {
        next := next_pos(point, move)
        if is_clean(board, next) {
            count += 1
        }
    }
    return count
}
func neighbors_clean_heads(board *[H][W]int, point Point) []Point {
    neighbors := []Point{}
    moves := [4]Move{UP, RIGHT, DOWN, LEFT}
    for _, move := range moves {
        next := next_pos(point, move)
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
    cleans := []Move{}
    moves := [4]Move{UP, RIGHT, DOWN, LEFT}
    for _, move := range moves {
        next := next_pos(point, move)
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

func evaluate(board *[H][W]int, next, dest Point) int {
    var sources = map[Point]int{}

    var cc = cc_init(board)
    var board_fill = *board

    var mid = board[next.y][next.x]
    var hid = board[dest.y][dest.x]

    for _, pid := range HEADS_N {
        var pos Point
        if pid == mid {
            pos = next
        } else if pid == hid {
            pos = dest
        } else if cc.cc_connected(next, HEADS[pid]) {
            pos = HEADS[pid]
        } else if cc.cc_connected(dest, HEADS[pid]) {
            pos = HEADS[pid]
        } else {
            continue
        }

        pqueue := &PointQueue{}
        heap.Init(pqueue)
        heap.Push(pqueue, PriorityPoint{0, pos})

        for pqueue.Len() > 0 {
            ppoint := heap.Pop(pqueue).(PriorityPoint)
            dist := ppoint.priority
            next := ppoint.point
            neighbors := neighbors_clean(board, next)

            for _, ngb := range neighbors {
                value := board_fill[ngb.y][ngb.x]

                dist2 := distance1(pos, ngb)
                if dist2 <= dist {
                    dist2 = dist + 1
                }

                if value == 0 || dist2 < value {
                    board_fill[ngb.y][ngb.x] = dist2
                    sources[ngb] = pid
                    heap.Push(pqueue, PriorityPoint{dist2, ngb})
                }
            }
        }
    }


    var connected = cc.cc_connected(next, dest)
    var counter = map[int]int{}
    var others = map[int]int{}

    for point, pid := range sources {
        var nc = neighbors_count(board, point)
        if nc > 2 {
            nc += nc
        }
        if pid == mid {
            counter[cc.cc_cid(point)] += nc

        } else if pid == hid && connected {
            others[cc.cc_cid(point)] += nc

        } else if pid != hid && cc.cc_connected(next, point) {
            others[cc.cc_cid(point)] += nc
        }
    }

    // debug("counter", counter, others, connected)
    for cid, count := range counter {
        var other, ok = others[cid]
        if ok && other > 0 {
            counter[cid] = int(float64(count * count) / float64(other))
        } else {
            counter[cid] = int(float64(count) * 0.43)
        }
    }

    // debug("counter2", counter)
    var score = math.MinInt32
    for _, count := range counter {
        if count > score {
            score = count
        }
    }
    return score
}

func max_play(board *[H][W]int, next Point, dest Point,
    alpha int, beta int, n int) int {
    // debug(strings.Repeat("  ", 2-n), "max_play", n, next, dest)

    best_score := math.MinInt32
    neighbors := neighbors_clean(board, next)
    if len(neighbors) == 0 {
        return best_score
    }

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

    best_score := math.MaxInt32
    neighbors := neighbors_clean(board, dest)
    if len(neighbors) == 0 {
        return best_score
    }

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

        beta = int(math.Min(float64(beta), float64(score)))
        if beta <= alpha {
            break
        }
    }

    return best_score
}

func select_head(board *[H][W]int, src Point) []int {
    var head_dists = map[int]int{}

    for pid, _ := range HEADS_F {
        _, path := best_dest(*board, src, HEADS[pid])
        head_dists[pid] = len(path)
    }

    var heads_d = sortByValue(head_dists)
    // heads_d = append(heads_d, board[src.y][src.x])
    return heads_d
}
func head_min(board *[H][W]int, src Point, out chan Move) {
    defer func() {
        // A closed channel never blocks
        // A nil channel always blocks
        out = nil
    }()

    var move_dirs = moves_clean(board, src)
    if len(move_dirs) <= 1 {
        out <-END
        return
    }

    var cc = cc_init(board)
    for pid, point := range HEADS {
        if cc.cc_connected(src, point) {
            HEADS_F[pid] = true
        }
    }

    if len(HEADS_F) == 0 {
        out <-END
        return
    }

    var heads_d = select_head(board, src)
    var head0 = heads_d[0]

    var best_scores = map[Move]int{}
    var score, alpha, beta int

    for n := 0; n < 2; n++ {
        var wg sync.WaitGroup

        for _, move := range move_dirs {
            wg.Add(1)
            board_copy := *board

            go func(board_calcul *[H][W]int, move Move) {
                defer wg.Done()

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

                // debug(n, "minimax", move, best_scores[move], time.Since(START))
            }(&board_copy, move)
        }

        wg.Wait()
        debug("minimax", best_scores)
        sort.Sort(ByScoreI{move_dirs, best_scores})
        out <-move_dirs[0]

        var scores = sort.IntSlice{}
        for _, score := range best_scores {
            scores = append(scores, score)
        }
        sort.Sort(scores)
        alpha, beta = scores[0], scores[scores.Len()-1]
        // debug(n, "alpha:", alpha, "beta:", beta)

        if float64(alpha) < float64(beta) * 0.11 {
            if len(move_dirs) == 2 {
                break
            } else {
                var bad_move = move_dirs[len(move_dirs)-1]
                delete(best_scores, bad_move)
                move_dirs = move_dirs[0:len(move_dirs)-1]
                alpha = scores[1] - alpha
            }
        }
    }
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
        if isbc  {
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
    // for _, point := range bc.articulations {
        // if point != src {
            // board_bc[point.y][point.x] = -1
        // }
    // }
    // debug_board(&board_bc)
    var visited = map[Point]bool{}
    var count = dm_dfs(board, src, visited, true)
    return count
}

func dm_bfs(board *[H][W]int, src Point, cc CC) int {
    pqueue := &PointQueue{}
    heap.Init(pqueue)
    heap.Push(pqueue, PriorityPoint{0, src})

    var count int
    var best_score int
    var cid_count = map[int]int{}

    for pqueue.Len() > 0 {
        var ppoint = heap.Pop(pqueue).(PriorityPoint)
        var next = ppoint.point

        var neighbors = neighbors(next)
        var ngb_value, ngb_count int

        for _, ngb := range neighbors {
            var value = board[ngb.y][ngb.x]
            if value == -1 || value == -2 {
                ngb_value += value * value
            }
            if value == -1 {
                ngb_count += 1
            }
        }

        var ngb_distinct bool
        if ngb_value == 2 || ngb_value == 6 {
            var ngb_one = []Point{}
            for _, ngb := range neighbors {
                var value = board[ngb.y][ngb.x]
                if value == -1 {
                    ngb_one = append(ngb_one, ngb)
                }
            }
            var ngb0, ngb1 = ngb_one[0], ngb_one[1]
            if ngb0.x == ngb1.x || ngb0.y == ngb1.y {
                ngb_distinct = true
            }
        }

        for _, ngb := range neighbors {
            var value = board[ngb.y][ngb.x]
            if value == 0 {
                count += 1
                board[ngb.y][ngb.x] = count
                heap.Push(pqueue, PriorityPoint{count, ngb})

                if ngb_distinct {
                    cid_count[cc.cc_cid(ngb)] += 1
                } else {
                    cid_count[1] += 1
                }

            } else if value == -1 {
                board[ngb.y][ngb.x] = -2
                var score = 1 + dm_bfs(board, ngb, cc)

                if !ngb_distinct {
                    if score > best_score {
                        best_score = score
                    }
                } else if ngb_value != 1 && ngb_value != 3 && ngb_value != 7 {
                    best_score += score
                } else if score > best_score {
                    best_score = score
                }
            }
        }
    }
    // debug(src, cid_count, best_score)
    if len(cid_count) > 1 {
        count = best_score
        for _, score := range cid_count {
            if score > count {
                count = score
            }
        }
    } else {
        count += best_score
    }
    return count
}
func dm_bfs_start(board *[H][W]int, src Point) int {
    var bc = bc_init(board, src)
    var board_bc = *board
    for _, point := range bc.articulations {
        if point != src {
            board_bc[point.y][point.x] = -1
        } else {
            return 1 + dm_max(board, src, 0)
        }
    }
    // debug_board(&board_bc)

    var cc = cc_init(&board_bc)
    // board_cc := board_bc
    // for point, cid := range cc.ccid {
        // board_cc[point.y][point.x] = cid
    // }
    // debug_board(&board_cc)

    var count = dm_bfs(&board_bc, src, cc)
    // debug_board(&board_bc)
    // debug(src, count, time.Since(START))
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
    var nc_count = len(neighbors)
    var alt_count = 10 - nc_count * nc_count
    return best_score + alt_count
}
func default_move(board *[H][W]int, src Point) Move {
    move_dirs := moves_clean(board, src)
    move_len := len(move_dirs)

    if move_len == 0 {
        return END
    } else if move_len == 1 {
        return move_dirs[0]
    }

    var best_scores = map[Move]int{}
    var score int

    for _, move := range move_dirs {
        next := next_pos(src, move)
        board[next.y][next.x] = board[src.y][src.x]
        score = dm_max(board, next, 2)
        board[next.y][next.x] = 0
        best_scores[move] = score
    }
    // debug("best_scores", best_scores)

    sort.Sort(ByScoreI{move_dirs, best_scores})
    best_move := move_dirs[0]

    return best_move
}


func best_move_fast(board [H][W]int, src Point) Move {
    var max_delay = time.After(MAX_DURATION)
    var best_move Move

    var channel = make(chan Move, 1)
    go head_min(&board, src, channel)

    for channel != nil {
        select {
            case best_move = <-channel:
                if best_move == END {
                    channel = nil
                    best_move = default_move(&board, src)
                }
            case <-max_delay:
                channel = nil
        }
    }
    // debug(time.Since(START))
    return best_move
}

func main() {
    runtime.GOMAXPROCS(runtime.NumCPU())
    for {
        src := read_stdin()
        START = time.Now()
        move := best_move_fast(BOARD, src)
        fmt.Println(move)
    }
}
