package main

import (
    "container/heap"
    "fmt"
    "math"
    "os"
    "runtime"
    "sort"
    "time"
)

const (
    // ID_START int = 10001
    // W, H int = 30, 20
    W, H int = 10, 10
    ID_START int = 1001
    MAX_DURATION time.Duration = 95 * time.Millisecond
)

var (
    UP, RIGHT, DOWN, LEFT, END = Move{0, -1}, Move{1, 0}, Move{0, 1},
        Move{-1, 0}, Move{0, 0}

    DIR = map[Move]string{UP: "UP", RIGHT: "RIGHT", DOWN: "DOWN",
        LEFT: "LEFT", END: "END"}

    BOARD    [H][W]int
    HEADS    map[int]Point
    HEADS_F  map[int]bool
    HEADS_D  []int
    LASTMOVE Move
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
)


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
    for y := range board {
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


func flood_find(board [H][W]int, src Point) int {
    board[src.y][src.x] = -2

    points := []Point{src}
    var next Point
    var count int = 0

    for len(points) > 0 {
        next, points = points[0], points[1:]
        neighbors := neighbors_clean_heads(&board, next)

        for _, ngb := range neighbors {
            value := board[ngb.y][ngb.x]
            if value == 0 {
                count += 1
                board[ngb.y][ngb.x] = count
                points = append(points, ngb)
            } else {
                _, exists := HEADS_F[value]
                if !exists {
                    HEADS_F[value] = true
                    if len(HEADS_F) == len(HEADS) {
                        points = []Point{}
                        break
                    }
                }
            }
        }
    }
    // debug("flood_find", HEADS_F, time.Since(START))
    // debug_board(&board)
    return count
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


func fill_board(board *[H][W]int, heads map[int]Point) map[int]int {
    sources := map[Point]int{}
    board_fill := *board

    for _, pid := range HEADS_D {
        pos := heads[pid]
        // debug("fill_board", pid, pos)
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

    counter := map[int]int{}
    mid := HEADS_D[len(HEADS_D)-1]
    count_mid := 0
    for point, pid := range sources {
        counter[pid] += 1
        if pid == mid {
            count_mid += len(neighbors_clean(board, point))
        }
    }
    counter[mid] += count_mid

    // -----------
    // pids := sort.IntSlice {}
    // for pid, _ := range counter {
        // pids = append(pids, pid)
    // }
    // sort.Sort(pids)
    // for _, pid := range pids {
        // if pid == mid {
            // debug("fill_board", pid, counter[pid] - count_mid, count_mid)
        // } else {
            // debug("fill_board", pid, counter[pid])
        // }
    // }
    // for point, pid := range sources {
        // if pid == 1002 {
            // board_fill[point.y][point.x] = ^board_fill[point.y][point.x]
        // }
    // }
    // debug_board(&board_fill)

    return counter
}
func max_play(board *[H][W]int, next Point, dest Point,
    alpha float64, beta float64, n int) float64 {
    // debug("max_play", n, next, dest)

    best_score := float64(math.MinInt32)
    neighbors := neighbors_clean(board, next)
    if len(neighbors) == 0 {
        return best_score
    }

    var score float64
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

        alpha = math.Max(alpha, score)
        if beta <= alpha {
            break
        }
    }

    return best_score
}
func min_play(board *[H][W]int, next Point, dest Point,
    alpha float64, beta float64, n int) float64 {
    // debug("min_play", n, next, dest)

    best_score := float64(math.MaxInt32)
    neighbors := neighbors_clean(board, dest)
    if len(neighbors) == 0 {
        return best_score
    }

    var score float64
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

        beta = math.Min(beta, score)
        if beta <= alpha {
            break
        }
    }

    return best_score
}
func evaluate(board *[H][W]int, next, dest Point) float64 {
    heads := map[int]Point{}
    for pid, _ := range HEADS_F {
        heads[pid] = HEADS[pid]
    }

    mid := board[next.y][next.x]
    heads[mid] = next

    pid := board[dest.y][dest.x]
    heads[pid] = dest

    counter := fill_board(board, heads)
    if counter[pid] == 0 {
        counter[pid] = 1
    }

    score := math.Pow(float64(counter[mid]), 2) / float64(counter[pid])
    return score
}


func couloir(board [H][W]int, path []Point) bool {
    var alt_move bool
    path_len := len(path)
    for count := 0; count < path_len-1; count++ {
        point := path[count]
        board[point.y][point.x] = count + 1
        if len(neighbors_clean(&board, point)) == 1 {
            if float64(count) > 0.4 * float64(path_len) {
                alt_move = true
            }
            break
        }
    }
    return alt_move
}
func head_min(board *[H][W]int, src Point, out chan Move) {
    defer func() {
        // A closed channel never blocks
        // A nil channel always blocks
        out = nil
    }()

    flood_find(*board, src)
    if len(HEADS_F) == 0 {
        out <-END
        return
    }

    move_dirs := moves_clean(board, src)
    if len(move_dirs) <= 1 {
        out <-END
        return
    }

    // heads
    head_paths := map[int][]Point{}
    head_dists := map[int]int{}
    head_moves := map[int]Move{}

    for pid, _ := range HEADS_F {
        move, path := best_dest(*board, src, HEADS[pid])
        head_paths[pid] = path
        head_dists[pid] = len(path)
        head_moves[pid] = move
    }

    HEADS_D = sortByValue(head_dists)
    HEADS_D = append(HEADS_D, board[src.y][src.x])
    var head0 int = HEADS_D[0]

    // if couloir(*board, head_paths[head0]) {
        // out <-END
        // return
    // }

    var dest Point = HEADS[head0]
    best_scores := map[Move]float64{}
    var alpha, beta float64

    for n := 0; n < 6; n++ {
        for _, move := range move_dirs {
            next := next_pos(src, move)
            board[next.y][next.x] = board[src.y][src.x]

            if n == 0 {
                best_scores[move] = evaluate(board, next, dest)
            } else {
                score := min_play(board, next, dest, alpha, beta, n)
                best_scores[move] = score
            }

            board[next.y][next.x] = 0
            debug("minimax", n, move, best_scores[move], time.Since(START))
        }

        sort.Sort(ByScoreF{move_dirs, best_scores})
        out <-move_dirs[0]

        scores := sort.Float64Slice{}
        for _, score := range best_scores {
            scores = append(scores, score)
        }
        sort.Sort(scores)
        alpha, beta = scores[0], scores[scores.Len()-1]
        // debug(n, "alpha:", alpha, "beta:", beta)

        if alpha == 0 {
            if len(move_dirs) == 2 {
                break
            } else {
                move_dirs = move_dirs[0:len(move_dirs)-1]
            }
        }
    }
}


func max_move(board *[H][W]int, point Point, move Move) int {
    next := next_pos(point, move)
    var count int
    for is_clean(board, next) {
        count += 1
        next = next_pos(next, move)
    }
    return count
}
func flood_count(board [H][W]int, src Point) int {
    pqueue := &PointQueue{}
    heap.Init(pqueue)
    heap.Push(pqueue, PriorityPoint{0, src})

    board[src.y][src.x] = 1
    var count int

    for pqueue.Len() > 0 {
        ppoint := heap.Pop(pqueue).(PriorityPoint)
        next := ppoint.point
        neighbors := neighbors_clean(&board, next)

        for _, ngb := range neighbors {
            count += 1
            board[ngb.y][ngb.x] = count
            heap.Push(pqueue, PriorityPoint{count, ngb})
        }
    }
    return count
}
func dfs(board *[H][W]int, src Point, visited map[Point]bool) int {
    neighbors := neighbors_clean(board, src)
    count := 0
    for _, ngb := range neighbors {
        score := 0
        if !visited[ngb] {
            visited[ngb] = true
            score += 1
            score += dfs(board, ngb, visited)
        }
        count = int(math.Max(float64(count), float64(score)))
    }
    return count
}
func dfs_start(board *[H][W]int, src Point) int {
    visited := map[Point]bool{}
    return dfs(board, src, visited)
}
func default_move(board *[H][W]int, src Point) Move {
    move_dirs := moves_clean(board, src)
    move_len := len(move_dirs)

    if move_len == 0 {
        return END
    } else if move_len == 1 {
        return move_dirs[0]
    }

    best_scores := map[Move]int{}
    neighbors := map[Move]int{}

    for _, move := range move_dirs {
        next := next_pos(src, move)
        neighbors[move] = len(neighbors_clean(board, next))

        board[next.y][next.x] = board[src.y][src.x]
        best_scores[move] = dfs_start(board, next)
        board[next.y][next.x] = 0
    }

    // debug("best_scores", best_scores)
    sort.Sort(ByScoreI{move_dirs, best_scores})
    best_move := move_dirs[0]
    alt_move := move_dirs[1]

    score0 := best_scores[best_move]
    score1 := best_scores[alt_move]

    if score0 == score1 {
        // debug("neighbors", neighbors)
        move_dirs = []Move{best_move, alt_move}
        sort.Sort(ByScoreI{move_dirs, neighbors})

        move1 := move_dirs[1]
        move0 := move_dirs[0]

        score1 := neighbors[move1]
        score0 := neighbors[move0]

        if score0 > score1 {
            best_move = move1
        }
    }

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

    return best_move
}

func main() {
    runtime.GOMAXPROCS(runtime.NumCPU())
    for {
        src := read_stdin()
        START = time.Now()
        LASTMOVE = best_move_fast(BOARD, src)
        fmt.Println(LASTMOVE)
    }
}
