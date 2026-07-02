import tkinter as tk
from tkinter import messagebox
<<<<<<< HEAD
from collections import deque
import copy
import random
import time
=======
import random
from collections import deque
import heapq
>>>>>>> Huy

# ===== THEME =====
BG = "#1a1a2e"
PANEL = "#16213e"
CARD = "#0f3460"
TEXT = "#e6e6e6"
SUB = "#8d99ae"
ACCENT = "#00d4ff"
BTN = "#3a86ff"
BTN_H = "#2a75e6"
BTN_SEL = "#e63946"
CELL = "#3d5a80"
CELL_E = "#0e0e1a"
GREEN = "#06d6a0"
RED = "#ef476f"
YELLOW = "#ffd166"

GOAL = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 0]]
DEFAULT = [[1, 2, 3, 4], [5, 6, 0, 8], [9, 10, 7, 11], [13, 14, 15, 12]]

<<<<<<< HEAD
def count_inversions(board):
    flat = [board[i][j] for i in range(4) for j in range(4)]
    nums = [x for x in flat if x != 0]
    inv = 0
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] > nums[j]:
                inv += 1
    return inv

def is_solvable(board):
    """Kiểm tra bảng 4x4 có thể giải được không (nghịch thế + vị trí ô trống)."""
    inv = count_inversions(board)
    blank_row_from_bottom = 0
    for i in range(4):
        for j in range(4):
            if board[i][j] == 0:
                blank_row_from_bottom = 4 - i
    return (inv + blank_row_from_bottom) % 2 == 1

class SearchNode:
    def __init__(self, board, action=None, tile_val=None, depth=0, parent=None, cost=0):
        self.board = [r[:] for r in board]
        self.action = action
        self.tile_val = tile_val
        self.depth = depth
        self.parent = parent
        self.cost = cost
        
=======
# ===== STATE CLASS =====
class State:
    def __init__(self, board):
        self.board = [r[:] for r in board]

>>>>>>> Huy
    def blank(self):
        for i in range(4):
            for j in range(4):
                if self.board[i][j] == 0:
                    return i, j
<<<<<<< HEAD
                    
    def nbrs(self):
=======

    def get_neighbors(self):
>>>>>>> Huy
        res = []
        bi, bj = self.blank()
        for di, dj, nm in [(-1, 0, "↑"), (1, 0, "↓"), (0, -1, "←"), (0, 1, "→")]:
            ni, nj = bi + di, bj + dj
            if 0 <= ni < 4 and 0 <= nj < 4:
                b = [r[:] for r in self.board]
<<<<<<< HEAD
                b[bi][bj], b[ni][nj] = b[ni][nj], b[bi][bj]
                res.append(SearchNode(b, action=nm, tile_val=b[bi][bj], depth=self.depth + 1, parent=self, cost=self.cost + 1))
        return res
        
    def state_tuple(self):
        return tuple(tuple(row) for row in self.board)
        
    def __eq__(self, o):
        return isinstance(o, SearchNode) and self.board == o.board

def solve_bfs(start_board, max_steps=2000):
    root = SearchNode(start_board)
    frontier = deque([root])
    reached = set()
    steps = []
    
    steps.append({
        'cur': None,
        'frontier': list(frontier),
        'reached': list(reached),
        'text': "Khởi tạo: Hàng đợi Frontier chứa trạng thái ban đầu B0"
    })
    
    nodes_expanded = 0
    while frontier and len(steps) < max_steps:
        curr = frontier.popleft()
        
        t = curr.state_tuple()
        if t in reached:
            continue
        reached.add(t)
        nodes_expanded += 1
        
        steps.append({
            'cur': curr,
            'frontier': list(frontier),
            'reached': list(reached),
            'text': f"Bước {nodes_expanded} (POP): Lấy node đầu hàng đợi ra xét.\nĐộ sâu g = {curr.cost}.\nHành động: Trượt ô {curr.tile_val or ''} {curr.action or ''}."
        })
        
        if curr.board == GOAL:
            path = []
            node = curr
            while node:
                path.append(node)
                node = node.parent
            path.reverse()
            path_desc = " → ".join([f"{n.tile_val or 'Start'}{n.action or ''}" for n in path])
            steps.append({
                'cur': curr,
                'frontier': list(frontier),
                'reached': list(reached),
                'text': f"🎉 ĐÃ TÌM THẤY ĐÍCH!\nTổng node duyệt: {nodes_expanded}\nĐộ dài lời giải: {len(path)-1} bước\nĐường đi: {path_desc}"
            })
            return steps
            
        children = curr.nbrs()
        new_children = []
        for child in children:
            if child.state_tuple() not in reached:
                frontier.append(child)
                new_children.append(child)
                
        nl = ", ".join([f"({c.tile_val}{c.action})" for c in new_children]) or "không có"
        steps.append({
            'cur': curr,
            'frontier': list(frontier),
            'reached': list(reached),
            'text': f"Sinh các node con: {nl}.\nThêm những node chưa duyệt (không nằm trong Reached) vào cuối hàng đợi Frontier."
        })
        
    steps.append({
        'cur': None,
        'frontier': list(frontier),
        'reached': list(reached),
        'text': f"⚠ Đã duyệt {nodes_expanded} node, chưa tìm thấy đích.\n" +
                ("Frontier rỗng — không còn node để mở rộng." if not frontier else f"Đạt giới hạn {max_steps} bước.")
    })
    return steps

def solve_dfs(start_board, max_steps=2000):
    root = SearchNode(start_board)
    frontier = [root]
    reached = set()
    steps = []
    
    steps.append({
        'cur': None,
        'frontier': list(frontier),
        'reached': list(reached),
        'text': "Khởi tạo: Ngăn xếp Stack Frontier chứa trạng thái ban đầu B0"
    })
    
    nodes_expanded = 0
    while frontier and len(steps) < max_steps:
        curr = frontier.pop()
        
        t = curr.state_tuple()
        if t in reached:
            continue
        reached.add(t)
        nodes_expanded += 1
        
        steps.append({
            'cur': curr,
            'frontier': list(frontier),
            'reached': list(reached),
            'text': f"Bước {nodes_expanded} (POP): Lấy node trên đỉnh ngăn xếp ra xét.\nĐộ sâu g = {curr.cost}.\nHành động: Trượt ô {curr.tile_val or ''} {curr.action or ''}."
        })
        
        if curr.board == GOAL:
            path = []
            node = curr
            while node:
                path.append(node)
                node = node.parent
            path.reverse()
            path_desc = " → ".join([f"{n.tile_val or 'Start'}{n.action or ''}" for n in path])
            steps.append({
                'cur': curr,
                'frontier': list(frontier),
                'reached': list(reached),
                'text': f"🎉 ĐÃ TÌM THẤY ĐÍCH!\nTổng node duyệt: {nodes_expanded}\nĐộ dài lời giải: {len(path)-1} bước\nĐường đi: {path_desc}"
            })
            return steps
            
        children = curr.nbrs()
        new_children = []
        for child in children:
            if child.state_tuple() not in reached:
                frontier.append(child)
                new_children.append(child)
                
        nl = ", ".join([f"({c.tile_val}{c.action})" for c in new_children]) or "không có"
        steps.append({
            'cur': curr,
            'frontier': list(frontier),
            'reached': list(reached),
            'text': f"Sinh các node con: {nl}.\nThêm những node chưa duyệt vào đỉnh stack Frontier."
        })
        
    steps.append({
        'cur': None,
        'frontier': list(frontier),
        'reached': list(reached),
        'text': f"⚠ Đã duyệt {nodes_expanded} node, chưa tìm thấy đích.\n" +
                ("Frontier rỗng — không còn node để mở rộng." if not frontier else f"Đạt giới hạn {max_steps} bước.")
    })
    return steps

def solve_ucs(start_board, max_steps=2000):
    root = SearchNode(start_board)
    frontier = [root]
    reached = set()
    steps = []
    
    steps.append({
        'cur': None,
        'frontier': list(frontier),
        'reached': list(reached),
        'text': "Khởi tạo: Frontier chứa trạng thái ban đầu B0"
    })
    
    nodes_expanded = 0
    while frontier and len(steps) < max_steps:
        best_idx = 0
        for k in range(1, len(frontier)):
            if frontier[k].cost < frontier[best_idx].cost:
                best_idx = k
                
        curr = frontier.pop(best_idx)
        
        t = curr.state_tuple()
        if t in reached:
            continue
        reached.add(t)
        nodes_expanded += 1
        
        steps.append({
            'cur': curr,
            'frontier': list(frontier),
            'reached': list(reached),
            'text': f"Bước {nodes_expanded} (POP): Lấy node có đường đi thấp nhất g = {curr.cost} trong Frontier ra xét.\nHành động: Trượt ô {curr.tile_val or ''} {curr.action or ''}."
        })
        
        if curr.board == GOAL:
            path = []
            node = curr
            while node:
                path.append(node)
                node = node.parent
            path.reverse()
            path_desc = " → ".join([f"{n.tile_val or 'Start'}{n.action or ''}" for n in path])
            steps.append({
                'cur': curr,
                'frontier': list(frontier),
                'reached': list(reached),
                'text': f"🎉 ĐÃ TÌM THẤY ĐÍCH!\nTổng node duyệt: {nodes_expanded}\nĐộ dài lời giải: {len(path)-1} bước\nĐường đi: {path_desc}"
            })
            return steps
            
        children = curr.nbrs()
        new_children = []
        for child in children:
            if child.state_tuple() not in reached:
                frontier.append(child)
                new_children.append(child)
                
        nl = ", ".join([f"({c.tile_val}{c.action}, g={c.cost})" for c in new_children]) or "không có"
        steps.append({
            'cur': curr,
            'frontier': list(frontier),
            'reached': list(reached),
            'text': f"Sinh các node con: {nl}.\nThêm những node chưa duyệt vào Frontier."
        })
        
    steps.append({
        'cur': None,
        'frontier': list(frontier),
        'reached': list(reached),
        'text': f"⚠ Đã duyệt {nodes_expanded} node, chưa tìm thấy đích.\n" +
                ("Frontier rỗng — không còn node để mở rộng." if not frontier else f"Đạt giới hạn {max_steps} bước.")
    })
    return steps

=======
                tile_val = self.board[ni][nj]
                b[bi][bj], b[ni][nj] = b[ni][nj], b[bi][bj]
                res.append((State(b), nm, tile_val))
        return res

    def is_goal(self):
        return self.board == GOAL

    def h(self):
        c = 0
        for i in range(4):
            for j in range(4):
                if self.board[i][j] != 0 and self.board[i][j] != GOAL[i][j]:
                    c += 1
        return c

# ===== NODE CLASS =====
class Node:
    def __init__(self, state, parent=None, action=None, g=0, depth=0):
        self.state = state  # board (list of lists)
        self.parent = parent
        self.action = action
        self.g = g
        self.depth = depth

    def get_path(self):
        path = []
        curr = self
        while curr:
            path.append(curr.state)
            curr = curr.parent
        return path[::-1]

    def __lt__(self, other):
        return self.g < other.g

# ===== DRAWING HELPER =====
>>>>>>> Huy
def draw_board(canvas, board, cs, x0, y0, border_color=None):
    gap = 2
    total = 4 * cs + 3 * gap
    canvas.create_rectangle(x0 - 3, y0 - 3, x0 + total + 3, y0 + total + 3, fill=PANEL, outline=border_color or PANEL, width=3 if border_color else 0)
    for i in range(4):
        for j in range(4):
            x = x0 + j * (cs + gap)
            y = y0 + i * (cs + gap)
            v = board[i][j]
            if v == 0:
                canvas.create_rectangle(x, y, x + cs, y + cs, fill=CELL_E, outline=CELL_E)
            else:
<<<<<<< HEAD
                ok = v == GOAL[i][j]
                c = "#2d6a4f" if ok else CELL
=======
                ok = (v == GOAL[i][j])
                c = "#1e4620" if ok else "#78281f"
>>>>>>> Huy
                canvas.create_rectangle(x, y, x + cs, y + cs, fill=c, outline="#4a6d8c", width=1)
                fs = max(cs // 3, 8)
                canvas.create_text(x + cs // 2, y + cs // 2, text=str(v), fill=TEXT, font=("Segoe UI", fs, "bold"))
    return total

<<<<<<< HEAD
def input_dialog(parent, callback):
    dlg = tk.Toplevel(parent)
    dlg.title("Nhập trạng thái 15-Puzzle")
    dlg.configure(bg=BG)
    dlg.geometry("380x420")
    dlg.resizable(False, False)
    dlg.grab_set()
    
    tk.Label(dlg, text="Nhập số 0-15 (0 = ô trống)", font=("Segoe UI", 12, "bold"), bg=BG, fg=TEXT).pack(pady=(15, 5))
    tk.Label(dlg, text="Mỗi số chỉ xuất hiện 1 lần", font=("Segoe UI", 9), bg=BG, fg=SUB).pack(pady=(0, 10))
    
    gf = tk.Frame(dlg, bg=BG)
    gf.pack(pady=5)
    
    entries = []
    for i in range(4):
        row = []
        for j in range(4):
            e = tk.Entry(gf, width=4, font=("Segoe UI", 16, "bold"), justify="center", bg=PANEL, fg=TEXT, insertbackground=TEXT, relief="flat", highlightthickness=2, highlightbackground="#3d5a80", highlightcolor=ACCENT)
            e.grid(row=i, column=j, padx=4, pady=4, ipady=6)
            v = DEFAULT[i][j]
            if v != 0: e.insert(0, str(v))
            row.append(e)
        entries.append(row)
        
    def do_random():
        b = [r[:] for r in GOAL]
        bi, bj = 3, 3
        for _ in range(8):
            moves = []
            for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                ni, nj = bi + di, bj + dj
                if 0 <= ni < 4 and 0 <= nj < 4: moves.append((ni, nj))
            ni, nj = random.choice(moves)
            b[bi][bj], b[ni][nj] = b[ni][nj], b[bi][bj]
            bi, bj = ni, nj
        for i in range(4):
            for j in range(4):
                entries[i][j].delete(0, tk.END)
                if b[i][j] != 0: entries[i][j].insert(0, str(b[i][j]))
                
    def do_ok():
        try:
            board = []
            for i in range(4):
                row = []
                for j in range(4):
                    t = entries[i][j].get().strip()
                    row.append(0 if t == "" else int(t))
                board.append(row)
            vals = sorted([board[i][j] for i in range(4) for j in range(4)])
            if vals != list(range(16)):
                messagebox.showerror("Lỗi", "Phải chứa đúng các số 0-15, không trùng!", parent=dlg)
                return
            callback(board)
            dlg.destroy()
        except ValueError:
            messagebox.showerror("Lỗi", "Chỉ nhập số nguyên 0-15!", parent=dlg)
            
    bf = tk.Frame(dlg, bg=BG)
    bf.pack(pady=15)
    tk.Button(bf, text="🎲 Ngẫu nhiên", font=("Segoe UI", 11), bg="#6930c3", fg=TEXT, relief="flat", padx=15, pady=6, cursor="hand2", command=do_random).pack(side=tk.LEFT, padx=8)
    tk.Button(bf, text="✓ Xác nhận", font=("Segoe UI", 11), bg=GREEN, fg="#000", relief="flat", padx=15, pady=6, cursor="hand2", command=do_ok).pack(side=tk.LEFT, padx=8)
    tk.Button(bf, text="✕ Hủy", font=("Segoe UI", 11), bg=RED, fg=TEXT, relief="flat", padx=15, pady=6, cursor="hand2", command=dlg.destroy).pack(side=tk.LEFT, padx=8)

class PuzzleUI:
=======
# ===== ALGORITHMS =====
def run_bfs(start_board):
    start_state = State(start_board)
    start_node = Node(start_state.board, g=0, depth=0)
    
    queue = deque([start_node])
    visited = set()
    steps = []
    
    limit = 400
    expanded = 0
    
    while queue and expanded < limit:
        curr_node = queue.popleft()
        curr_board_tuple = tuple(tuple(r) for r in curr_node.state)
        
        if curr_board_tuple in visited:
            continue
        visited.add(curr_board_tuple)
        expanded += 1
        
        curr_state = State(curr_node.state)
        
        raw_neighbors = curr_state.get_neighbors()
        neighbors_data = []
        for nxt, act, tile_val in raw_neighbors:
            nxt_tuple = tuple(tuple(r) for r in nxt.board)
            if nxt_tuple in visited:
                status = "visited"
            else:
                status = "added"
            neighbors_data.append((nxt.board, act, status, tile_val))
            
        steps.append({
            'board': [r[:] for r in curr_node.state],
            'status': 'exploring',
            'depth': curr_node.depth,
            'g': curr_node.g,
            'path': curr_node.get_path(),
            'neighbors': neighbors_data,
            'chosen_idx': -1,
            'text': f"Xét trạng thái thứ {expanded} lấy ra từ hàng đợi (BFS).\nĐộ sâu hiện tại: {curr_node.depth}.\nSố ô sai vị trí (xung đột): {curr_state.h()}."
        })
        
        if curr_state.is_goal():
            steps[-1]['status'] = 'solved'
            steps[-1]['text'] = "🎉 Đã tìm thấy trạng thái Đích!"
            return steps
            
        for nxt_b, act, status, _ in neighbors_data:
            if status == "visited":
                continue
            child = Node(nxt_b, curr_node, act, curr_node.g + 1, curr_node.depth + 1)
            queue.append(child)
            
    return steps

def run_dfs(start_board, depth_limit=8):
    steps = []
    visited = {}  # board_tuple -> min_depth_visited
    limit = 400
    expanded = 0
    
    def dfs(curr_node):
        nonlocal expanded
        if expanded >= limit:
            return False
            
        curr_board_tuple = tuple(tuple(r) for r in curr_node.state)
        
        if curr_board_tuple in visited and visited[curr_board_tuple] <= curr_node.depth:
            return False
        visited[curr_board_tuple] = curr_node.depth
        expanded += 1
        
        curr_state = State(curr_node.state)
        raw_neighbors = curr_state.get_neighbors()
        
        neighbors_data = []
        for nxt, act, tile_val in raw_neighbors:
            nxt_tuple = tuple(tuple(r) for r in nxt.board)
            if nxt_tuple in visited and visited[nxt_tuple] <= curr_node.depth + 1:
                status = "visited"
            else:
                status = "added"
            neighbors_data.append((nxt.board, act, status, tile_val))
            
        steps.append({
            'board': [r[:] for r in curr_node.state],
            'status': 'exploring',
            'depth': curr_node.depth,
            'g': curr_node.g,
            'path': curr_node.get_path(),
            'neighbors': neighbors_data,
            'chosen_idx': -1,
            'text': f"Xét trạng thái thứ {expanded} lấy ra từ đỉnh ngăn xếp (DFS).\nĐộ sâu hiện tại: {curr_node.depth}.\nSố ô sai vị trí (xung đột): {curr_state.h()}."
        })
        
        if curr_state.is_goal():
            steps[-1]['status'] = 'solved'
            steps[-1]['text'] = "🎉 Đã tìm thấy trạng thái Đích!"
            return True
            
        if curr_node.depth < depth_limit:
            for idx, (nxt_b, act, status, tile_val) in enumerate(neighbors_data):
                if status == "visited":
                    continue
                    
                child = Node(nxt_b, curr_node, act, curr_node.g + 1, curr_node.depth + 1)
                steps[-1]['chosen_idx'] = idx
                
                if dfs(child):
                    return True
                    
                # Ghi nhận bước quay lui để tránh nhảy cóc trên giao diện
                steps.append({
                    'board': [r[:] for r in curr_node.state],
                    'status': 'backtracking',
                    'depth': curr_node.depth,
                    'g': curr_node.g,
                    'path': curr_node.get_path(),
                    'neighbors': neighbors_data,
                    'chosen_idx': -1,
                    'text': f"Quay lui về độ sâu {curr_node.depth} từ hướng đi {act}."
                })
                
        return False

    start_node = Node(start_board, g=0, depth=0)
    dfs(start_node)
    return steps

def run_ucs(start_board):
    start_state = State(start_board)
    start_node = Node(start_state.board, g=0, depth=0)
    
    count = 0
    queue = [(0, count, start_node)]
    visited = set()
    steps = []
    
    limit = 400
    expanded = 0
    
    while queue and expanded < limit:
        g_val, _, curr_node = heapq.heappop(queue)
        curr_board_tuple = tuple(tuple(r) for r in curr_node.state)
        
        if curr_board_tuple in visited:
            continue
        visited.add(curr_board_tuple)
        expanded += 1
        
        curr_state = State(curr_node.state)
        
        raw_neighbors = curr_state.get_neighbors()
        neighbors_data = []
        for nxt, act, tile_val in raw_neighbors:
            nxt_tuple = tuple(tuple(r) for r in nxt.board)
            if nxt_tuple in visited:
                status = "visited"
            else:
                status = "added"
            neighbors_data.append((nxt.board, act, status, tile_val))
            
        steps.append({
            'board': [r[:] for r in curr_node.state],
            'status': 'exploring',
            'depth': curr_node.depth,
            'g': curr_node.g,
            'path': curr_node.get_path(),
            'neighbors': neighbors_data,
            'chosen_idx': -1,
            'text': f"Xét trạng thái thứ {expanded} có chi phí g(n) = {curr_node.g} nhỏ nhất (UCS).\nĐộ sâu hiện tại: {curr_node.depth}.\nSố ô sai vị trí (xung đột): {curr_state.h()}."
        })
        
        if curr_state.is_goal():
            steps[-1]['status'] = 'solved'
            steps[-1]['text'] = "🎉 Đã tìm thấy trạng thái Đích!"
            return steps
            
        for nxt_b, act, status, _ in neighbors_data:
            if status == "visited":
                continue
            # Chi phí: Lên/Xuống = 1, Trái/Phải = 2 để phân biệt rõ với BFS
            move_cost = 2 if act in ["←", "→"] else 1
            child = Node(nxt_b, curr_node, act, curr_node.g + move_cost, curr_node.depth + 1)
            count += 1
            heapq.heappush(queue, (child.g, count, child))
            
    return steps

ALGOS = {
    "Breadth-First Search (BFS)": run_bfs,
    "Depth-First Search (DFS)": run_dfs,
    "Uniform Cost Search (UCS)": run_ucs
}

def get_move_relation(board1, board2):
    b1_i, b1_j = -1, -1
    b2_i, b2_j = -1, -1
    for i in range(4):
        for j in range(4):
            if board1[i][j] == 0:
                b1_i, b1_j = i, j
            if board2[i][j] == 0:
                b2_i, b2_j = i, j
    di, dj = b2_i - b1_i, b2_j - b1_j
    if di == -1 and dj == 0: return "↑"
    if di == 1 and dj == 0: return "↓"
    if di == 0 and dj == -1: return "←"
    if di == 0 and dj == 1: return "→"
    return ""

# ===== MAIN UI =====
class UninformedUI:
>>>>>>> Huy
    def __init__(self, parent, algo_name=None):
        self.parent = parent
        parent.withdraw()
        self.win = tk.Toplevel(parent)
        self.win.title("Nhóm 1: Tìm kiếm mù - 15 Puzzle")
        self.win.geometry("1350x780")
        self.win.configure(bg=BG)
        self.win.minsize(1200, 700)
        self.win.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.board = [r[:] for r in DEFAULT]
<<<<<<< HEAD
        self.algo = algo_name or "Breadth-First Search (BFS)"
        self.steps = []
        self.step_idx = -1
        self.algo_btns = {}
        
=======
        self.algo = algo_name
        self.steps = []
        self.step_idx = -1
        self.auto_playing = False
        
        self.algo_btns = {}
>>>>>>> Huy
        self._build_top()
        self._build_middle()
        self._build_bottom()
        
        if algo_name:
            self.select_algo(algo_name)
        self.draw_initial()
<<<<<<< HEAD
        
    def on_close(self):
        self.win.destroy()
        self.parent.deiconify()
        
    def _build_top(self):
        f = tk.Frame(self.win, bg=PANEL, pady=8)
        f.pack(fill=tk.X, padx=0)
        tk.Label(f, text="NHÓM 1: TÌM KIẾM MÙ", font=("Segoe UI", 14, "bold"), bg=PANEL, fg=ACCENT).pack(side=tk.LEFT, padx=20)
=======

    def on_close(self):
        self.win.destroy()
        self.parent.deiconify()

    def _build_top(self):
        f = tk.Frame(self.win, bg=PANEL, pady=8)
        f.pack(fill=tk.X, padx=0)
        tk.Label(f, text="NHÓM 1: TÌM KIẾM MÙ (UNINFORMED SEARCH)", font=("Segoe UI", 14, "bold"), bg=PANEL, fg=ACCENT).pack(side=tk.LEFT, padx=20)
>>>>>>> Huy
        
        bb = tk.Button(f, text="◀ Quay lại", font=("Segoe UI", 10, "bold"), bg=RED, fg=TEXT, relief="flat", padx=12, pady=4, cursor="hand2", command=self.on_close)
        bb.pack(side=tk.RIGHT, padx=15)
        
<<<<<<< HEAD
        algos = ["Uniform Cost Search (UCS)", "Depth-First Search (DFS)", "Breadth-First Search (BFS)"]
        for name in algos:
            b = tk.Button(f, text=name, font=("Segoe UI", 10), bg="#444455", fg=TEXT, relief="flat", padx=12, pady=4, cursor="hand2",
                          command=lambda n=name: self.select_algo(n))
            b.pack(side=tk.RIGHT, padx=4)
            self.algo_btns[name] = b
            
    def select_algo(self, name):
        self.algo = name
        for n, b in self.algo_btns.items():
            if n == name: b.config(bg=BTN_SEL)
            else: b.config(bg="#444455")
            
=======
        for name in reversed(list(ALGOS.keys())):
            b = tk.Button(f, text=name, font=("Segoe UI", 10), bg="#444455", fg=TEXT, relief="flat", padx=12, pady=4, cursor="hand2",
                        command=lambda n=name: self.select_algo(n))
            b.pack(side=tk.RIGHT, padx=4)
            self.algo_btns[name] = b

    def select_algo(self, name):
        self.algo = name
        for n, b in self.algo_btns.items():
            if n == name:
                b.config(bg=BTN_SEL)
            else:
                b.config(bg="#444455")
        self.steps = []
        self.step_idx = -1
        self.draw_initial()

>>>>>>> Huy
    def _build_middle(self):
        mf = tk.Frame(self.win, bg=BG)
        mf.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
<<<<<<< HEAD
=======
        # --- CỘT TRÁI: Node đang xét ---
>>>>>>> Huy
        lf = tk.Frame(mf, bg=CARD, highlightbackground="#2a3a5c", highlightthickness=1)
        lf.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        
        tk.Label(lf, text="NODE ĐANG XÉT", font=("Segoe UI", 11, "bold"), bg=CARD, fg=ACCENT).pack(pady=(10, 5))
<<<<<<< HEAD
        self.cv_cur = tk.Canvas(lf, width=260, height=260, bg=CARD, highlightthickness=0)
        self.cv_cur.pack(padx=15, pady=5)
        
        self.lbl_info = tk.Label(lf, text="g = 0\ndepth = 0\naction = Bắt đầu", font=("Segoe UI", 10, "bold"), bg=CARD, fg=YELLOW)
        self.lbl_info.pack(pady=(0, 5))
        
        sh_frame = tk.Frame(lf, bg=CARD, pady=5)
        sh_frame.pack(fill=tk.X, padx=15)
        
        tk.Label(sh_frame, text="Số nước Shuffle:", font=("Segoe UI", 9), bg=CARD, fg=TEXT).grid(row=0, column=0, sticky="w", pady=2)
        self.sp_shuffle = tk.Spinbox(sh_frame, from_=1, to=15, width=5, font=("Segoe UI", 9, "bold"), bg=PANEL, fg=TEXT, buttonbackground=PANEL)
        self.sp_shuffle.delete(0, tk.END)
        self.sp_shuffle.insert(0, "4")
        self.sp_shuffle.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        btn_sh = tk.Button(sh_frame, text="🎲 Shuffle", font=("Segoe UI", 9, "bold"), bg="#6930c3", fg=TEXT, relief="flat", cursor="hand2", padx=10, pady=4, command=self.do_shuffle)
        btn_sh.grid(row=1, column=0, sticky="nsew", padx=2, pady=4)
        
        btn_rs = tk.Button(sh_frame, text="🔄 Reset", font=("Segoe UI", 9, "bold"), bg=RED, fg=TEXT, relief="flat", cursor="hand2", padx=10, pady=4, command=self.do_reset)
        btn_rs.grid(row=1, column=1, sticky="nsew", padx=2, pady=4)
        
        tk.Label(lf, text="BÀN CỜ ĐÍCH", font=("Segoe UI", 10, "bold"), bg=CARD, fg=GREEN).pack(pady=(10, 2))
        self.cv_goal = tk.Canvas(lf, width=120, height=120, bg=CARD, highlightthickness=0)
        self.cv_goal.pack(pady=(0, 10))
        draw_board(self.cv_goal, GOAL, 26, 6, 6)
        
        cf = tk.Frame(mf, bg=CARD, highlightbackground="#2a3a5c", highlightthickness=1)
        cf.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        tk.Label(cf, text="📋 FRONTIER", font=("Segoe UI", 11, "bold"), bg=CARD, fg=ACCENT).pack(pady=(10, 5))
        
        cv_fr = tk.Canvas(cf, bg=CARD, highlightthickness=0)
        cv_fr.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        vs_fr = tk.Scrollbar(cf, orient=tk.VERTICAL, command=cv_fr.yview)
        vs_fr.pack(side=tk.RIGHT, fill=tk.Y)
        cv_fr.configure(yscrollcommand=vs_fr.set)
        
        self.fr_inner = tk.Frame(cv_fr, bg=CARD)
        cv_fr.create_window((0, 0), window=self.fr_inner, anchor="nw")
        self.fr_inner.bind("<Configure>", lambda e: cv_fr.configure(scrollregion=cv_fr.bbox("all")))
        self.fr_canvas = cv_fr
        
        rf = tk.Frame(mf, bg=BG)
        rf.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 0))
        rf.config(width=350)
        rf.pack_propagate(False)
        
        vf = tk.Frame(rf, bg=CARD, highlightbackground="#2a3a5c", highlightthickness=1)
        vf.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        tk.Label(vf, text="✅ REACHED (ĐÃ DUYỆT)", font=("Segoe UI", 10, "bold"), bg=CARD, fg=ACCENT).pack(pady=(8, 2))
        
        cv_re = tk.Canvas(vf, bg=CARD, highlightthickness=0)
        cv_re.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        vs_re = tk.Scrollbar(vf, orient=tk.VERTICAL, command=cv_re.yview)
        vs_re.pack(side=tk.RIGHT, fill=tk.Y)
        cv_re.configure(yscrollcommand=vs_re.set)
        
        self.re_inner = tk.Frame(cv_re, bg=CARD)
        cv_re.create_window((0, 0), window=self.re_inner, anchor="nw")
        self.re_inner.bind("<Configure>", lambda e: cv_re.configure(scrollregion=cv_re.bbox("all")))
        self.re_canvas = cv_re
        
        ef = tk.Frame(rf, bg=CARD, highlightbackground="#2a3a5c", highlightthickness=1, height=200)
        ef.pack(fill=tk.X, pady=(5, 0))
        ef.pack_propagate(False)
        tk.Label(ef, text="GIẢI THÍCH", font=("Segoe UI", 10, "bold"), bg=CARD, fg=ACCENT).pack(pady=(8, 2))
        self.txt_exp = tk.Text(ef, bg=CARD, fg=TEXT, font=("Segoe UI", 10), wrap=tk.WORD, relief="flat", padx=10, pady=5, state=tk.DISABLED)
        self.txt_exp.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        
=======
        self.cv_cur = tk.Canvas(lf, width=260, height=280, bg=CARD, highlightthickness=0)
        self.cv_cur.pack(padx=15, pady=5)
        
        self.lbl_h = tk.Label(lf, text="Xung đột: ?", font=("Segoe UI", 13, "bold"), bg=CARD, fg=YELLOW)
        self.lbl_h.pack(pady=(0, 5))
        
        # Bảng điều khiển Xáo trộn
        sf = tk.Frame(lf, bg=CARD)
        sf.pack(pady=5)
        tk.Label(sf, text="Bước Shuffle:", bg=CARD, fg=TEXT, font=("Segoe UI", 9)).grid(row=0, column=0, padx=5)
        self.sp_shuffle = tk.Spinbox(sf, from_=1, to=8, width=4, font=("Segoe UI", 9, "bold"))
        self.sp_shuffle.delete(0, "end")
        self.sp_shuffle.insert(0, "3")
        self.sp_shuffle.grid(row=0, column=1, padx=5)
        
        bf_shuffle = tk.Frame(lf, bg=CARD)
        bf_shuffle.pack(pady=5)
        tk.Button(bf_shuffle, text="🎲 Shuffle", font=("Segoe UI", 9, "bold"), bg="#6930c3", fg=TEXT, relief="flat", padx=10, pady=4, cursor="hand2", command=self.do_shuffle).pack(side=tk.LEFT, padx=5)
        tk.Button(bf_shuffle, text="🧹 Reset", font=("Segoe UI", 9, "bold"), bg="#444455", fg=TEXT, relief="flat", padx=10, pady=4, cursor="hand2", command=self.do_reset).pack(side=tk.LEFT, padx=5)

        # Chú thích màu sắc
        tk.Label(lf, text="CHÚ THÍCH", font=("Segoe UI", 11, "bold"), bg=CARD, fg=ACCENT).pack(pady=(10, 5))
        legend = [
            ("Không xung đột (đúng vị trí)", "#1e4620"),
            ("Đang xung đột (sai vị trí)", "#78281f"),
            ("Đã duyệt (Màu tối)", SUB),
            ("Được thêm vào biên (Biên vàng)", YELLOW)
        ]
        for name, col in legend:
            f_lg = tk.Frame(lf, bg=CARD)
            f_lg.pack(fill=tk.X, padx=25, pady=2)
            if col == YELLOW:
                tk.Frame(f_lg, width=15, height=15, bg="#3f3f2d", highlightbackground=YELLOW, highlightthickness=1).pack(side=tk.LEFT, padx=(0, 10))
            else:
                tk.Frame(f_lg, width=15, height=15, bg=col, highlightbackground=TEXT, highlightthickness=0.5).pack(side=tk.LEFT, padx=(0, 10))
            tk.Label(f_lg, text=name, bg=CARD, fg=TEXT, font=("Segoe UI", 9)).pack(side=tk.LEFT)

        # --- CỘT GIỮA: Các trạng thái con (Next States) ---
        cf = tk.Frame(mf, bg=CARD, highlightbackground="#2a3a5c", highlightthickness=1)
        cf.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        tk.Label(cf, text="CÁC BƯỚC THỬ TIẾP THEO (MIỀN GIÁ TRỊ)", font=("Segoe UI", 11, "bold"), bg=CARD, fg=ACCENT).pack(pady=(10, 5))
        self.children_frame = tk.Frame(cf, bg=CARD)
        self.children_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # --- CỘT PHẢI: Đường đi đã duyệt + Giải thích ---
        rf = tk.Frame(mf, bg=BG)
        rf.pack(side=tk.LEFT, fill=tk.BOTH, padx=(5, 0))
        rf.config(width=350)
        rf.pack_propagate(False)
        
        # Đường đi hiện tại (Path)
        vf = tk.Frame(rf, bg=CARD, highlightbackground="#2a3a5c", highlightthickness=1)
        vf.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        tk.Label(vf, text="ĐƯỜNG ĐI HIỆN TẠI (PATH)", font=("Segoe UI", 10, "bold"), bg=CARD, fg=ACCENT).pack(pady=(8, 2))
        
        vc = tk.Canvas(vf, bg=CARD, highlightthickness=0)
        vc.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        vs = tk.Scrollbar(vf, orient=tk.VERTICAL, command=vc.yview)
        vs.pack(side=tk.RIGHT, fill=tk.Y)
        vc.configure(yscrollcommand=vs.set)
        
        self.vis_inner = tk.Frame(vc, bg=CARD)
        vc.create_window((0, 0), window=self.vis_inner, anchor="nw")
        self.vis_inner.bind("<Configure>", lambda e: vc.configure(scrollregion=vc.bbox("all")))
        self.vis_canvas = vc
        
        # Giải thích
        ef = tk.Frame(rf, bg=CARD, highlightbackground="#2a3a5c", highlightthickness=1, height=200)
        ef.pack(fill=tk.X, pady=(5, 0))
        ef.pack_propagate(False)
        tk.Label(ef, text="GIẢI THÍCH CHI TIẾT", font=("Segoe UI", 10, "bold"), bg=CARD, fg=ACCENT).pack(pady=(8, 2))
        
        self.txt_exp = tk.Text(ef, bg=CARD, fg=TEXT, font=("Segoe UI", 10), wrap=tk.WORD, relief="flat", padx=10, pady=5, insertbackground=TEXT, state=tk.DISABLED)
        self.txt_exp.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))

>>>>>>> Huy
    def _build_bottom(self):
        f = tk.Frame(self.win, bg=PANEL, pady=10)
        f.pack(fill=tk.X)
        
        btns = [
<<<<<<< HEAD
            ("📝 Nhập tay", self.do_input, "#6930c3"),
=======
>>>>>>> Huy
            ("▶ Giải", self.do_solve, GREEN),
            ("◀◀ Bước trước", self.do_prev, BTN),
            ("Bước sau ▶▶", self.do_next, BTN),
        ]
        for txt, cmd, clr in btns:
<<<<<<< HEAD
            tk.Button(f, text=txt, font=("Segoe UI", 11, "bold"), bg=clr, fg=TEXT if clr != GREEN else "#000", relief="flat", padx=18, pady=8, cursor="hand2", command=cmd).pack(side=tk.LEFT, padx=10)
            
        self.btn_auto = tk.Button(f, text="Tự chạy ⏯", font=("Segoe UI", 11, "bold"), bg="#5a189a", fg=TEXT, relief="flat", padx=18, pady=8, cursor="hand2", command=self.toggle_auto_play)
        self.btn_auto.pack(side=tk.LEFT, padx=10)
        self.auto_playing = False
        
        self.lbl_step = tk.Label(f, text="", font=("Segoe UI", 12, "bold"), bg=PANEL, fg=YELLOW)
        self.lbl_step.pack(side=tk.RIGHT, padx=20)
        
    def draw_node_card(self, parent, node, idx):
        frame = tk.Frame(parent, bg=PANEL, padx=4, pady=3, highlightbackground="#3d5a80", highlightthickness=1)
        info = f"g={node.cost} | d={node.depth}"
        if node.action:
            info += f" | {node.tile_val}{node.action}"
        tk.Label(frame, text=info, font=("Segoe UI", 7), bg=PANEL, fg=TEXT).pack()
        cv = tk.Canvas(frame, width=94, height=94, bg=PANEL, highlightthickness=0)
        cv.pack()
        draw_board(cv, node.board, 21, 2, 2)
        tk.Label(frame, text=f"Idx: {idx}", font=("Segoe UI", 7), bg=PANEL, fg=SUB).pack()
        return frame
        
    def draw_reached_card(self, parent, board_tuple, idx):
        frame = tk.Frame(parent, bg=PANEL, padx=3, pady=2, highlightbackground="#2d6a4f", highlightthickness=1)
        cv = tk.Canvas(frame, width=64, height=64, bg=PANEL, highlightthickness=0)
        cv.pack()
        board = [list(r) for r in board_tuple]
        draw_board(cv, board, 14, 2, 2)
        tk.Label(frame, text=f"#{idx}", font=("Segoe UI", 7), bg=PANEL, fg=SUB).pack()
        return frame
        
    def draw_initial(self):
        self.elapsed = 0
        self.cv_cur.delete("all")
        draw_board(self.cv_cur, self.board, 58, 10, 10, border_color=ACCENT)
        self.lbl_info.config(text="g = 0\ndepth = 0\naction = Bắt đầu")
        
        for w in self.fr_inner.winfo_children(): w.destroy()
        tk.Label(self.fr_inner, text="Hộp rỗng", font=("Segoe UI", 11), bg=CARD, fg=SUB).pack(expand=True, pady=40)
        
        
        for w in self.re_inner.winfo_children(): w.destroy()
        tk.Label(self.re_inner, text="Hộp rỗng", font=("Segoe UI", 11), bg=CARD, fg=SUB).pack(expand=True, pady=40)
        
        self.set_exp("Chọn thuật toán ở thanh trên và nhấn Giải để quan sát mô phỏng.")
        self.lbl_step.config(text="")
        
    def show_step(self, idx):
        if idx < 0 or idx >= len(self.steps): return
        self.step_idx = idx
        st = self.steps[idx]
        time_str = f" | ⏱ {self.elapsed:.2f}s" if self.elapsed else ""
        self.lbl_step.config(text=f"Bước {idx+1}/{len(self.steps)}{time_str}")
        
        self.cv_cur.delete("all")
        cur_node = st['cur']
        if cur_node:
            draw_board(self.cv_cur, cur_node.board, 58, 10, 10, border_color=ACCENT)
            self.lbl_info.config(text=f"g = {cur_node.cost}\ndepth = {cur_node.depth}\naction = {cur_node.action or 'Bắt đầu'}")
        else:
            draw_board(self.cv_cur, self.board, 58, 10, 10, border_color=ACCENT)
            self.lbl_info.config(text="g = 0\ndepth = 0\naction = Bắt đầu")
            
        for w in self.fr_inner.winfo_children(): w.destroy()
        frontier_list = st['frontier']
        displayed_fr = min(len(frontier_list), 50)
        
        fr_cols = 3
        for i, node in enumerate(frontier_list[:displayed_fr]):
            r, c = divmod(i, fr_cols)
            card = self.draw_node_card(self.fr_inner, node, i + 1)
            card.grid(row=r, column=c, padx=6, pady=6)
            
        if len(frontier_list) > displayed_fr:
            r = (displayed_fr + fr_cols - 1) // fr_cols
            lbl = tk.Label(self.fr_inner, text=f"... và {len(frontier_list) - displayed_fr} node khác", font=("Segoe UI", 9, "italic"), bg=CARD, fg=SUB)
            lbl.grid(row=r, column=0, columnspan=fr_cols, pady=5)
            
        self.fr_canvas.update_idletasks()
        self.fr_canvas.configure(scrollregion=self.fr_canvas.bbox("all"))
        
        for w in self.re_inner.winfo_children(): w.destroy()
        reached_list = list(st['reached'])
        displayed_re = min(len(reached_list), 50)
        
        re_cols = 3
        for i, board_t in enumerate(reached_list[:displayed_re]):
            r, c = divmod(i, re_cols)
            card = self.draw_reached_card(self.re_inner, board_t, i + 1)
            card.grid(row=r, column=c, padx=4, pady=4)
            
        if len(reached_list) > displayed_re:
            r = (displayed_re + re_cols - 1) // re_cols
            lbl = tk.Label(self.re_inner, text=f"... và {len(reached_list) - displayed_re} trạng thái khác", font=("Segoe UI", 9, "italic"), bg=CARD, fg=SUB)
            lbl.grid(row=r, column=0, columnspan=re_cols, pady=5)
            
        self.re_canvas.update_idletasks()
        self.re_canvas.configure(scrollregion=self.re_canvas.bbox("all"))
        self.set_exp(st['text'])
        
=======
            tk.Button(f, text=txt, font=("Segoe UI", 11, "bold"), bg=clr, fg=TEXT if clr!=GREEN else "#000", relief="flat", padx=18, pady=8, cursor="hand2", command=cmd).pack(side=tk.LEFT, padx=10)
            
        self.btn_auto = tk.Button(f, text="Tự chạy ⏯", font=("Segoe UI", 11, "bold"), bg="#5a189a", fg=TEXT, relief="flat", padx=18, pady=8, cursor="hand2", command=self.toggle_auto_play)
        self.btn_auto.pack(side=tk.LEFT, padx=10)
        
        self.lbl_step = tk.Label(f, text="", font=("Segoe UI", 12, "bold"), bg=PANEL, fg=YELLOW)
        self.lbl_step.pack(side=tk.RIGHT, padx=20)

    def draw_initial(self):
        self.cv_cur.delete("all")
        draw_board(self.cv_cur, self.board, 58, 10, 10, border_color=ACCENT)
        self.lbl_h.config(text=f"Xung đột: {State(self.board).h()}")
        
        for w in self.children_frame.winfo_children(): w.destroy()
        tk.Label(self.children_frame, text="Nhấn '▶ Giải' để bắt đầu\nhoặc '🎲 Shuffle' để xáo trộn bàn cờ", font=("Segoe UI", 11), bg=CARD, fg=SUB, justify="center").pack(expand=True)
        
        self.set_exp("Chọn thuật toán ở thanh trên và nhấn Giải.")
        self.lbl_step.config(text="")
        for w in self.vis_inner.winfo_children(): w.destroy()

    def show_step(self, idx):
        if idx < 0 or idx >= len(self.steps):
            return
        self.step_idx = idx
        st = self.steps[idx]
        self.lbl_step.config(text=f"Bước {idx+1}/{len(self.steps)}")
        
        # 1. Vẽ trạng thái hiện tại ở cột trái
        self.cv_cur.delete("all")
        draw_board(self.cv_cur, st['board'], 58, 10, 10, border_color=ACCENT)
        
        g_desc = f" | Chi phí g(n): {st.get('g', 0)}" if self.algo == "Uniform Cost Search (UCS)" else ""
        self.lbl_h.config(text=f"Xung đột: {State(st['board']).h()}{g_desc}")
        
        # 2. Vẽ các trạng thái con tiếp theo ở cột giữa
        for w in self.children_frame.winfo_children(): w.destroy()
        
        neighbors = st.get('neighbors', [])
        chosen_idx = st.get('chosen_idx', -1)
        cols = 2
        n_cs = 24
        n_gap = 1
        grid_px = 4 * (n_cs + n_gap) + 6
        
        for i, item in enumerate(neighbors):
            r, c = divmod(i, cols)
            cf = tk.Frame(self.children_frame, bg=CARD)
            cf.grid(row=r, column=c, padx=10, pady=8, sticky="n")
            
            nxt_board, action, status, tile_val = item[:4]
            lbl_text = f"Trượt ô {tile_val} {action}"
            
            is_chosen = (i == chosen_idx)
            
            # Xác định thông số hiển thị dưới bàn cờ con (depth hoặc cost g)
            if self.algo == "Uniform Cost Search (UCS)":
                move_cost = 2 if action in ["←", "→"] else 1
                child_g = st.get('g', 0) + move_cost
                val_text = f"g = {child_g}"
            else:
                child_d = st.get('depth', 0) + 1
                val_text = f"d = {child_d}"
                
            if is_chosen:
                val_text += " ★"
            
            if status == "visited":
                status_text = "Đã duyệt (bị loại)"
                status_color = SUB
                bc = SUB
            elif status == "chosen":
                status_text = "Nước đi kế tiếp"
                status_color = GREEN
                bc = GREEN
            elif status == "other":
                status_text = "Hướng khác"
                status_color = SUB
                bc = None
            else:
                status_text = "Được thêm vào biên"
                status_color = YELLOW
                bc = None
                
            lbl_dir = tk.Label(cf, text=lbl_text, font=("Segoe UI", 10, "bold"), bg=CARD, fg=GREEN if is_chosen else TEXT)
            lbl_dir.pack(pady=(2, 2))
            
            cv = tk.Canvas(cf, width=grid_px + 10, height=grid_px + 10, bg=CARD, highlightthickness=0)
            cv.pack()
            
            draw_board(cv, nxt_board, n_cs, 5, 5, border_color=bc)
            
            # Hiển thị g hoặc d dưới bàn cờ con
            tk.Label(cf, text=val_text, font=("Segoe UI", 9, "bold"), bg=CARD, fg=GREEN if is_chosen else YELLOW).pack(pady=(2, 0))
            
            # Hiển thị trạng thái duyệt
            tk.Label(cf, text=status_text, font=("Segoe UI", 9), bg=CARD, fg=status_color).pack(pady=(0, 4))
            
        # 3. Vẽ đường đi ở cột phải
        for w in self.vis_inner.winfo_children(): w.destroy()
        
        path = st.get('path', [])
        vcs = 16
        vgap = 1
        vgrid = 4 * (vcs + vgap) + 6
        vcols = 2
        
        for vi in range(len(path)):
            vr, vc2 = divmod(vi, vcols)
            vf = tk.Frame(self.vis_inner, bg=CARD)
            vf.grid(row=vr, column=vc2, padx=4, pady=4)
            
            vcv = tk.Canvas(vf, width=vgrid + 6, height=vgrid + 6, bg=CARD, highlightthickness=0)
            vcv.pack()
            draw_board(vcv, path[vi], vcs, 3, 3)
            
            tk.Label(vf, text=f"#{vi}", font=("Segoe UI", 7), bg=CARD, fg=SUB).pack()
            
        self.vis_canvas.update_idletasks()
        self.vis_canvas.configure(scrollregion=self.vis_canvas.bbox("all"))
        
        # 4. Cập nhật giải thích
        self.set_exp(st['text'])

>>>>>>> Huy
    def set_exp(self, text):
        self.txt_exp.config(state=tk.NORMAL)
        self.txt_exp.delete("1.0", tk.END)
        self.txt_exp.insert(tk.END, text)
        self.txt_exp.config(state=tk.DISABLED)
<<<<<<< HEAD
        
    def do_input(self):
        def cb(board):
            self.auto_playing = False
            self.btn_auto.config(text="Tự chạy ⏯", bg="#5a189a")
            self.board = [r[:] for r in board]
            self.steps = []
            self.step_idx = -1
            self.draw_initial()
        input_dialog(self.win, cb)
        
    def do_shuffle(self):
        self.auto_playing = False
        self.btn_auto.config(text="Tự chạy ⏯", bg="#5a189a")
        try:
            steps_cnt = int(self.sp_shuffle.get())
        except ValueError:
            steps_cnt = 4
            
        b = [r[:] for r in GOAL]
        bi, bj = 3, 3
        for _ in range(steps_cnt):
            moves = []
            for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                ni, nj = bi + di, bj + dj
                if 0 <= ni < 4 and 0 <= nj < 4: moves.append((ni, nj))
            ni, nj = random.choice(moves)
            b[bi][bj], b[ni][nj] = b[ni][nj], b[bi][bj]
            bi, bj = ni, nj
=======

    def do_shuffle(self):
        self.auto_playing = False
        self.btn_auto.config(text="Tự chạy ⏯", bg="#5a189a")
        
        b = [r[:] for r in GOAL]
        bi, bj = 3, 3
        steps = int(self.sp_shuffle.get())
        
        last_move = None
        for _ in range(steps):
            moves = []
            for di, dj, m_name in [(-1, 0, "U"), (1, 0, "D"), (0, -1, "L"), (0, 1, "R")]:
                ni, nj = bi + di, bj + dj
                if 0 <= ni < 4 and 0 <= nj < 4:
                    if last_move == "U" and m_name == "D": continue
                    if last_move == "D" and m_name == "U": continue
                    if last_move == "L" and m_name == "R": continue
                    if last_move == "R" and m_name == "L": continue
                    moves.append((ni, nj, m_name))
            if not moves:
                break
            ni, nj, m_name = random.choice(moves)
            b[bi][bj], b[ni][nj] = b[ni][nj], b[bi][bj]
            bi, bj = ni, nj
            last_move = m_name
>>>>>>> Huy
            
        self.board = b
        self.steps = []
        self.step_idx = -1
        self.draw_initial()
<<<<<<< HEAD
        
=======

>>>>>>> Huy
    def do_reset(self):
        self.auto_playing = False
        self.btn_auto.config(text="Tự chạy ⏯", bg="#5a189a")
        self.board = [r[:] for r in DEFAULT]
        self.steps = []
        self.step_idx = -1
        self.draw_initial()
<<<<<<< HEAD
        
    def do_solve(self):
        self.auto_playing = False
        self.btn_auto.config(text="Tự chạy ⏯", bg="#5a189a")
        if not self.algo:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn thuật toán!", parent=self.win)
            return
            
        if not is_solvable(self.board):
            messagebox.showwarning("Không giải được",
                "Trạng thái này không thể đạt tới đích!\n(Số nghịch thế + vị trí ô trống không hợp lệ)",
                parent=self.win)
            return
        
        t0 = time.time()
        
        if self.algo == "Breadth-First Search (BFS)":
            self.steps = solve_bfs(self.board)
        elif self.algo == "Depth-First Search (DFS)":
            self.steps = solve_dfs(self.board)
        else:
            self.steps = solve_ucs(self.board)
        
        self.elapsed = time.time() - t0
            
        if self.steps:
            self.show_step(0)
        else:
            self.set_exp("Không tìm thấy lời giải.")
            
    def do_prev(self):
        if self.step_idx > 0: self.show_step(self.step_idx - 1)
        
    def do_next(self):
        if self.step_idx < len(self.steps) - 1: self.show_step(self.step_idx + 1)
        
    def toggle_auto_play(self):
        if not self.steps: return
=======

    def do_solve(self):
        self.auto_playing = False
        self.btn_auto.config(text="Tự chạy ⏯", bg="#5a189a")
        
        if not self.algo:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn thuật toán trước!", parent=self.win)
            return
            
        fn = ALGOS[self.algo]
        exploration_steps = fn(self.board)
        
        if exploration_steps and exploration_steps[-1]['status'] == 'solved':
            goal_path = exploration_steps[-1]['path']
            
            self.steps = []
            accumulated_g = 0
            for i in range(len(goal_path)):
                board = goal_path[i]
                curr_state = State(board)
                
                raw_neighbors = curr_state.get_neighbors()
                neighbors_data = []
                
                next_board = goal_path[i+1] if i < len(goal_path) - 1 else None
                chosen_idx = -1
                
                if next_board:
                    act_taken = get_move_relation(board, next_board)
                    # Chi phí: Lên/Xuống = 1, Trái/Phải = 2 (cho UCS)
                    move_cost = 1
                    if self.algo == "Uniform Cost Search (UCS)":
                        move_cost = 2 if act_taken in ["←", "→"] else 1
                
                for idx, (nxt, act, tile_val) in enumerate(raw_neighbors):
                    if next_board and nxt.board == next_board:
                        status = "chosen"
                        chosen_idx = idx
                    else:
                        status = "other"
                    neighbors_data.append((nxt.board, act, status, tile_val))
                
                g_desc = f" | Chi phí g(n): {accumulated_g}" if self.algo == "Uniform Cost Search (UCS)" else ""
                
                self.steps.append({
                    'board': board,
                    'status': 'solved' if i == len(goal_path) - 1 else 'solving',
                    'depth': i,
                    'g': accumulated_g,
                    'path': goal_path[:i+1],
                    'neighbors': neighbors_data,
                    'chosen_idx': chosen_idx,
                    'text': f"Bước {i} trong tiến trình giải câu đố.\nTrạng thái hiện tại có {curr_state.h()} ô sai vị trí.{g_desc}" if i < len(goal_path) - 1 else f"🎉 Đã đến trạng thái Đích!\nTổng chi phí: {accumulated_g}."
                })
                
                if next_board:
                    accumulated_g += move_cost
            
            self.show_step(0)
        else:
            self.steps = exploration_steps
            if self.steps:
                self.show_step(0)
            else:
                self.set_exp("Không tìm thấy lời giải trong giới hạn cho phép.")

    def do_prev(self):
        if self.step_idx > 0:
            self.show_step(self.step_idx - 1)

    def do_next(self):
        if self.step_idx < len(self.steps) - 1:
            self.show_step(self.step_idx + 1)

    def toggle_auto_play(self):
        if not self.steps:
            return
>>>>>>> Huy
        self.auto_playing = not self.auto_playing
        if self.auto_playing:
            self.btn_auto.config(text="Dừng ⏸", bg=RED)
            self.run_auto_step()
        else:
            self.btn_auto.config(text="Tự chạy ⏯", bg="#5a189a")
<<<<<<< HEAD
            
    def run_auto_step(self):
        if self.auto_playing and self.step_idx < len(self.steps) - 1:
            self.do_next()
            self.win.after(800, self.run_auto_step)
        elif self.step_idx >= len(self.steps) - 1:
            self.auto_playing = False
            self.btn_auto.config(text="Tự chạy ⏯", bg="#5a189a")

def open_ui(parent, algo_name):
    PuzzleUI(parent, algo_name)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Nhóm 1 Simulator Standalone")
    root.withdraw()
    def custom_close(ui):
        ui.win.destroy()
        root.destroy()
    ui = PuzzleUI(root, "Breadth-First Search (BFS)")
    ui.on_close = lambda: custom_close(ui)
    root.mainloop()
=======

    def run_auto_step(self):
        if self.auto_playing and self.step_idx < len(self.steps) - 1:
            self.do_next()
            self.win.after(500, self.run_auto_step)

def open_ui(parent, algo_name):
    UninformedUI(parent, algo_name)
>>>>>>> Huy
