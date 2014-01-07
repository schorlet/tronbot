package main

import (
    "fmt"
    "time"
    "math"
    "os"
    "sort"
    "container/heap"
)

type Move struct {
    a, b int
}
func (move Move) String() string {
    return DIR[move]
}
func (move Move) Inverse(other Move) bool {
    return move == Move {other.a * -1, other.b * -1}
}
type ByScore struct {
    moves []Move
    scores map[Move]float64
}
func (bs ByScore) Len() int {
    return len(bs.moves)
}
func (bs ByScore) Swap(i, j int) {
    bs.moves[i], bs.moves[j] = bs.moves[j], bs.moves[i]
}
func (bs ByScore) Less(i, j int) bool {
    move0, move1 := bs.moves[i], bs.moves[j]
    return bs.scores[move0] > bs.scores[move1]
}

type Point struct {
    x, y int
}
func (point Point) String() string {
    // return fmt.Sprintf("%+v", point)
    return fmt.Sprintf("(%d, %d)", point.x, point.y)
}
type PriorityPoints struct {
    priority int
    points []Point
}
type PointsQueue []PriorityPoints
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
    ppoints := oldq[len(oldq) - 1]
    newq := oldq[0:len(oldq) - 1]
    *pqueue = newq
    return ppoints
}

type PriorityPoint struct {
    priority int
    point Point
}
type PointQueue []PriorityPoint
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
    ppoint := oldq[len(oldq) - 1]
    newq := oldq[0:len(oldq) - 1]
    *pqueue = newq
    return ppoint
}

type SortedMapByValue struct {
    dict map[int]int
    arra []int
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

const MAX_DURATION time.Duration = 86 * time.Millisecond
var (
    UP    = Move {0, -1}
    RIGHT = Move {1, 0}
    DOWN  = Move {0, 1}
    LEFT  = Move {-1, 0}
    END   = Move {0, 0}

    DIR = map[Move]string {
        UP: "UP",
        RIGHT: "RIGHT",
        DOWN: "DOWN",
        LEFT: "LEFT",
        END: "END",
    }

    BOARD [H][W]int
    HEADS map[int]Point
    HEADS_F map[int]bool
    LASTMOVE Move
    START time.Time
)

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

    for pid := ID_START; pid < ID_START + nbj; pid++ {
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
                HEADS[pid] = Point {x1, y1}
            }
        }
    }
    return Point{mx, my}
}
func in_board(point Point) bool {
    return  0 <= point.x &&
            0 <= point.y &&
            point.x < W &&
            point.y < H
}
func is_clean(board [H][W]int, point Point) bool {
    return in_board(point) && board[point.y][point.x] == 0
}
func next_pos(point Point, move Move) Point {
    return Point {point.x + move.a, point.y + move.b}
}
func neighbors(point Point) []Point {
    neighbors := []Point {}
    moves := [...]Move {UP, RIGHT, DOWN, LEFT}
    for _, move := range moves {
        next := next_pos(point, move)
        if in_board(next) {
            neighbors = append(neighbors, next)
        }
    }
    return neighbors
}
func neighbors_clean(board [H][W]int, point Point) []Point {
    neighbors := []Point {}
    moves := [...]Move {UP, RIGHT, DOWN, LEFT}
    for _, move := range moves {
        next := next_pos(point, move)
        if is_clean(board, next) {
            neighbors = append(neighbors, next)
        }
    }
    return neighbors
}
func neighbors_clean_heads(board [H][W]int, point Point) []Point {
    neighbors := []Point {}
    moves := [...]Move {UP, RIGHT, DOWN, LEFT}
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
func moves_clean(board [H][W]int, point Point) []Move {
    cleans := []Move {}
    moves := [...]Move {UP, RIGHT, DOWN, LEFT}
    for _, move := range moves {
        next := next_pos(point, move)
        if is_clean(board, next) {
            cleans = append(cleans, move)
        }
    }
    return cleans
}

func distance1(src, dest Point) int {
    return int(math.Abs(float64(src.x - dest.x)) +
               math.Abs(float64(src.y - dest.y)))
}
func distance2(src, dest Point) int {
    return int(10 * (math.Pow(math.Abs(float64(src.x - dest.x)), 2) +
                     math.Pow(math.Abs(float64(src.y - dest.y)), 2)))
}
func distance3(src, dest Point) float64 {
    return 33 * (math.Sqrt(math.Abs(float64(src.x - dest.x))) +
                 math.Sqrt(math.Abs(float64(src.y - dest.y))))
}
func distance4(src, dest Point) int {
    return int(math.Max(math.Abs(float64(src.x - dest.x)),
                        math.Abs(float64(src.y - dest.y))))
}
func distance5(src, dest Point) int {
    return int(math.Min(math.Abs(float64(src.x - dest.x)),
                        math.Abs(float64(src.y - dest.y))))
}
func directions(src, dest Point) map[Move]bool {
    dirs := map[Move]bool {}
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

func debug_board(board [H][W]int) {
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
func out_of_time() bool {
    return time.Since(START) >= MAX_DURATION
}

func flood_find(board [H][W]int, point Point) int {
    board[point.y][point.x] = -2

    points := []Point {point}
    var next Point
    var count int = 0

    for len(points) > 0 {
        next, points = points[0], points[1:]
        neighbors := neighbors_clean_heads(board, next)

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
                        points = []Point {}
                        break
                    }
                }
            }
        }
    }
    // debug("flood_find", HEADS_F, time.Since(START))
    // debug_board(board)
    return count
}
func __best_dest(board [H][W]int, src, dest Point) []Point {
    var dest_path []Point
    pqueue := &PointsQueue{}
    heap.Init(pqueue)
    heap.Push(pqueue, PriorityPoints{0, []Point {src}})

    for dest_path == nil && pqueue.Len() > 0 {
        ppoints := heap.Pop(pqueue).(PriorityPoints)
        next := ppoints.points[len(ppoints.points) - 1]
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
                // debug("  ", value2, ngb)

                n := len(ppoints.points)
                new_points := make([]Point, n, n + 1)
                copy(new_points, ppoints.points)
                new_points = append(new_points, ngb)

                // new_points := append([]Point(nil), ppoints.points...)
                // new_points = append(new_points, ngb)

                new_ppoints := PriorityPoints{value2, new_points}
                heap.Push(pqueue, new_ppoints)
            }
        }
    }
    // clean_board(&board)
    // for i, pos := range dest_path {
        // if i == 0 { continue }
        // board[pos.y][pos.x] = i
    // }
    // debug_board(board)
    return dest_path
}
func best_dest(board [H][W]int, src, dest Point) (Move, []Point) {
    dest_path := __best_dest(board, src, dest)
    if len(dest_path) > 1 {
        next := dest_path[1]
        move := Move {next.x - src.x, next.y - src.y}
        // debug("best_dest", dest, DIR[move], dest_path, time.Since(START))
        return move, dest_path[1:len(dest_path)]
    }
    return END, dest_path
}


func fill_board(board [H][W]int, heads map[int]Point) map[int]int {
    sources := map[Point]int {}
    board_fill := board

    // TODO: iterate by less interesting points
    for pid, pos := range heads {
        pqueue := &PointQueue{}
        heap.Init(pqueue)
        heap.Push(pqueue, PriorityPoint{0, pos})
        count := 0

        for count < 300 && pqueue.Len() > 0 {
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
                    count += 1
                }
            }
        }
    }

    counter := map[int]int {}
    for _, pid := range sources {
        counter[pid] += 1
    }

    // pids := sort.IntSlice {}
    // for pid, _ := range counter {
        // pids = append(pids, pid)
    // }
    // sort.Sort(pids)
    // for _, pid := range pids {
        // debug("fill_board", pid, counter[pid])
    // }

    return counter
}
func max_play(board [H][W]int, next Point, dest Point,
        alpha float64, beta float64, n int) float64 {
    if out_of_time() {
        return 0.0
    }
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
            score = max_play(board, ngb, dest, alpha, beta, n - 1)
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
func min_play(board [H][W]int, next Point, dest Point,
        alpha float64, beta float64, n int) float64 {
    if out_of_time() {
        return 0.0
    }
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
            score = max_play(board, next, ngb, alpha, beta, n - 1)
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
func evaluate(board [H][W]int, next, dest Point) float64 {
    heads := map[int]Point {}
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


func head_min(board [H][W]int, point Point) Move {
    flood_find(board, point)
    if len(HEADS_F) == 0 {
        return END
    }

    move_dirs := moves_clean(board, point)
    if len(move_dirs) <= 1 {
        return END
    }

    // heads
    head_paths := map[int]int {}
    head_moves := map[int]Move {}

    for pid, _ := range HEADS_F {
        move, path := best_dest(board, point, HEADS[pid])
        head_paths[pid] = len(path)
        head_moves[pid] = move
    }
    heads := sortByValue(head_paths)
    head0 := heads[0]

    dest := HEADS[head0]
    dirs := directions(point, dest)
    debug("PID", head0, dest, dirs)

    best_scores := map[Move]float64 {}
    var alpha, beta float64
    best_move := END
    m := int(math.Min(2.0, math.Max(6.0, float64(head_paths[head0]))))

    for n:= 0; n < m; n++ {
        if out_of_time() { break }

        for _, move := range move_dirs {
            next := next_pos(point, move)
            board[next.y][next.x] = board[point.y][point.x]

            if n == 0 {
                best_scores[move] = evaluate(board, next, dest)
            } else {
                score := min_play(board, next, dest, alpha, beta, n)
                if out_of_time() { break }
                best_scores[move] = score
            }

            board[next.y][next.x] = 0
            // debug("minimax", n, move, best_scores[move], time.Since(START))
        }
        if out_of_time() { break }

        sort.Sort(ByScore{move_dirs, best_scores})

        scores := sort.Float64Slice {}
        for _, score := range best_scores {
            scores = append(scores, score)
        }
        sort.Sort(scores)
        alpha, beta = scores[0], scores[scores.Len() - 1]
        // debug("alpha:", alpha, "beta:", beta)
    }

    sort.Sort(ByScore{move_dirs, best_scores})
    best_move = move_dirs[0]

    if len(move_dirs) == 2 {
        dist2 := distance2(point, dest)
        if dist2 == 20 {
            score0 := best_scores[best_move]
            score1 := best_scores[move_dirs[1]]
            if score0 > score1 * 0.9 && score1 > score0 * 0.9 {
                for _, move := range move_dirs {
                    if dirs[move] {
                        best_move = move
                        break
                    }
                }
            }
        } else if dist2 == 10 {
            score0 := best_scores[best_move]
            score1 := best_scores[move_dirs[1]]
            if score0 > score1 * 0.9 && score1 > score0 * 0.9 {
                for move, _ := range dirs {
                    if best_move.Inverse(move) {
                        best_move = move_dirs[1]
                        break
                    }
                }
            }
        }
    }

    return best_move
}


func max_move(board [H][W]int, point Point, move Move) int {
    next := next_pos(point, move)
    var count int
    for is_clean(board, next) {
        count += 1
        next = next_pos(next, move)
    }
    return count
}
func flood_count(board [H][W]int, point Point) int {
    pqueue := &PointQueue{}
    heap.Init(pqueue)
    heap.Push(pqueue, PriorityPoint{0, point})

    board_copy := board
    board_copy[point.y][point.x] = 1
    var count int

    for pqueue.Len() > 0 {
        ppoint := heap.Pop(pqueue).(PriorityPoint)
        next := ppoint.point
        neighbors := neighbors_clean(board_copy, next)

        for _, ngb := range neighbors {
            count += 1
            board_copy[ngb.y][ngb.x] = count
            heap.Push(pqueue, PriorityPoint{count, ngb})
        }
    }
    return count
}
func dm_move(board [H][W]int, point Point, limit int, rec int) int {
    if limit == 0 {
        return rec + flood_count(board, point)
    }

    neighbors := neighbors_clean(board, point)
    if len(neighbors) == 0 {
        return rec
    }

    var count int
    for _, ngb := range neighbors {
        board[ngb.y][ngb.x] = board[point.y][point.x]
        dm_count := dm_move(board, ngb, limit - 1, rec + 1)
        count = int(math.Max(float64(count), float64(dm_count)))
        board[ngb.y][ngb.x] = 0
    }
    return count
}
func default_move(board [H][W]int, point Point) Move {
    moves := [...]Move {UP, RIGHT, DOWN, LEFT}
    move_dirs := []Move {}

    neighbors := map[Move]float64 {}
    best_scores := map[Move]float64 {}

    for _, move := range moves {
        count := max_move(board, point, move)
        if count > 0 {
            move_dirs = append(move_dirs, move)

            next := next_pos(point, move)
            neighbors[move] = float64(len(neighbors_clean(board, next)))

            best_scores[move] = float64(W * H)
        }
    }

    if len(move_dirs) == 0 {
        return END
    } else if len(move_dirs) == 1 {
        return move_dirs[0]
    }

    for i := 0; i < 20; i++ {
        begin := time.Now()
        for _, move := range move_dirs {
            if out_of_time() { break }
            next := next_pos(point, move)
            board[next.y][next.x] = board[point.y][point.x]
            dm_count := dm_move(board, next, i, 1)
            best_scores[move] = math.Min(best_scores[move], float64(dm_count))
            board[next.y][next.x] = 0
        }
        if out_of_time() { break }
        duration := time.Since(begin)
        limit := time.Since(START) + (3 * duration)
        if limit > MAX_DURATION {
            break
        }
    }
    // debug("best_scores", best_scores)

    sort.Sort(ByScore{move_dirs, best_scores})
    best_move := move_dirs[0]
    alt_move := move_dirs[1]

    if best_scores[best_move] == best_scores[alt_move] {
        // debug("neighbors", neighbors)
        move_dirs = []Move {best_move, alt_move}
        sort.Sort(ByScore{move_dirs, neighbors})
        best_move = move_dirs[1]
    }

    // debug(best_move, time.Since(START))
    return best_move
}


func best_move_fast(board [H][W]int, point Point) Move {
    move := head_min(board, point)
    if move == END {
        move = default_move(board, point)
    }
    debug(move, time.Since(START))
    return move
}

const W, H int = 30, 20
const ID_START int = 10001
func main() {
    for {
        point := read_stdin()
        START = time.Now()
        LASTMOVE = best_move_fast(BOARD, point)
        fmt.Println(LASTMOVE)
    }
}


// func simulation(board [H][W]int, point Point) {
    // START = time.Now()
    // LASTMOVE = default_move(board, point)
    // if time.Since(START) > 95 * time.Millisecond {
        // panic("timeout")
    // }
    // var count int
    // for LASTMOVE != END {
        // point = next_pos(point, LASTMOVE)
        // count += 1
        // board[point.y][point.x] = count
        // debug_board(board)
        // START = time.Now()
        // LASTMOVE = default_move(board, point)
        // if time.Since(START) > 95 * time.Millisecond {
            // panic("timeout")
        // }
    // }
// }
// const ID_START int = 1001
// func main() {
    // test1()
// }
// const W, H int = 10, 10
// func test1() {
    // zer := [10]int{   0,    0,    0,    0,    0,    0,    0,    0,    0,    0}
    // one := [10]int{1003, 1003,    0,    0,    0,    0,    0,    0,    0,    0}
    // two := [10]int{   0,    0,    0,    0,    0,    0,    0,    0,    0,    0}
    // thr := [10]int{   0,    0,    0,    0,    0,    0,    0,    0,    0,    0}
    // fou := [10]int{1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002,    0,    0}
    // fiv := [10]int{   0,    0,    0,    0,    0,    0,    0,    0,    0,    0}
    // six := [10]int{   0,    0,    0,    0,    0,    0,    0,    0,    0,    0}
    // sev := [10]int{   0, 1001, 1001,    0,    0,    0,    0,    0,    0,    0}
    // eig := [10]int{   0,    0,    0,    0,    0,    0,    0,    0,    0,    0}
    // nin := [10]int{   0,    0,    0,    0,    0,    0,    0,    0,    0,    0}
    // BOARD := [H][W]int{zer, one, two, thr, fou, fiv, six, sev, eig, nin}
    // START = time.Now()
    // me := Point {2, 7}
    // HEADS_F = map[int]bool {}
    // HEADS = map[int]Point {1002: Point {7, 4}, 1003: Point {1, 1}}
    // LASTMOVE = best_move_fast(BOARD, me)
// }
// const W, H int = 4, 7
// func test2() {
    // zer := [4]int{   0, 1003,    0,    0}
    // one := [4]int{   0, 1003,    0,    0}
    // two := [4]int{   0,    0,    0,    0}
    // thr := [4]int{1002, 1002, 1002,    0}
    // fou := [4]int{   0,    0,    0,    0}
    // fiv := [4]int{   0,    0,    0,    0}
    // six := [4]int{   0, 1001, 1001,    0}
    // BOARD := [H][W]int{zer, one, two, thr, fou, fiv, six}
    // START = time.Now()
    // me := Point {2, 6}
    // HEADS_F = map[int]bool {}
    // HEADS = map[int]Point {}
    // simulation(BOARD, me)
// }
// const W, H int = 10, 10
// func test3() {
    // zer := [10]int{   0,    0,    0,    0,    0,    0,    0,    0,    0,    0}
    // one := [10]int{1003, 1003,    0,    0,    0,    0,    0,    0,    0,    0}
    // two := [10]int{   0,    0,    0,    0,    0,    0,    0,    0,    0,    0}
    // thr := [10]int{   0,    0,    0,    0,    0,    0,    0,    0,    0,    0}
    // fou := [10]int{1002, 1002, 1002, 1002, 1002, 1002, 1002, 1002,    0,    0}
    // fiv := [10]int{   0,    0,    0,    0,    0,    0,    0,    0,    0,    0}
    // six := [10]int{   0,    0,    0,    0,    0,    0,    0,    0,    0,    0}
    // sev := [10]int{   0, 1001, 1001,    0,    0,    0,    0,    0,    0,    0}
    // eig := [10]int{   0,    0,    0,    0,    0,    0,    0,    0,    0,    0}
    // nin := [10]int{   0,    0,    0,    0,    0,    0,    0,    0,    0,    0}
    // BOARD := [H][W]int{zer, one, two, thr, fou, fiv, six, sev, eig, nin}
    // START = time.Now()
    // me := Point {2, 7}
    // HEADS_F = map[int]bool {}
    // HEADS = map[int]Point {}
    // simulation(BOARD, me)
// }
