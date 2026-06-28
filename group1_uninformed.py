import tkinter as tk
from tkinter import messagebox
import random
from collections import deque
import heapq

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

# ===== STATE CLASS =====
class State:
    def __init__(self, board):
        self.board = [r[:] for r in board]

    def blank(self):
        for i in range(4):
            for j in range(4):
                if self.board[i][j] == 0:
                    return i, j

    def get_neighbors(self):
        res = []
        bi, bj = self.blank()
        for di, dj, nm in [(-1, 0, "↑"), (1, 0, "↓"), (0, -1, "←"), (0, 1, "→")]:
            ni, nj = bi + di, bj + dj
            if 0 <= ni < 4 and 0 <= nj < 4:
                b = [r[:] for r in self.board]
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
                ok = (v == GOAL[i][j])
                c = "#1e4620" if ok else "#78281f"
                canvas.create_rectangle(x, y, x + cs, y + cs, fill=c, outline="#4a6d8c", width=1)
                fs = max(cs // 3, 8)
                canvas.create_text(x + cs // 2, y + cs // 2, text=str(v), fill=TEXT, font=("Segoe UI", fs, "bold"))
    return total

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
        self.algo = algo_name
        self.steps = []
        self.step_idx = -1
        self.auto_playing = False
        
        self.algo_btns = {}
        self._build_top()
        self._build_middle()
        self._build_bottom()
        
        if algo_name:
            self.select_algo(algo_name)
        self.draw_initial()

    def on_close(self):
        self.win.destroy()
        self.parent.deiconify()

    def _build_top(self):
        f = tk.Frame(self.win, bg=PANEL, pady=8)
        f.pack(fill=tk.X, padx=0)
        tk.Label(f, text="NHÓM 1: TÌM KIẾM MÙ (UNINFORMED SEARCH)", font=("Segoe UI", 14, "bold"), bg=PANEL, fg=ACCENT).pack(side=tk.LEFT, padx=20)
        
        bb = tk.Button(f, text="◀ Quay lại", font=("Segoe UI", 10, "bold"), bg=RED, fg=TEXT, relief="flat", padx=12, pady=4, cursor="hand2", command=self.on_close)
        bb.pack(side=tk.RIGHT, padx=15)
        
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

    def _build_middle(self):
        mf = tk.Frame(self.win, bg=BG)
        mf.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # --- CỘT TRÁI: Node đang xét ---
        lf = tk.Frame(mf, bg=CARD, highlightbackground="#2a3a5c", highlightthickness=1)
        lf.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        
        tk.Label(lf, text="NODE ĐANG XÉT", font=("Segoe UI", 11, "bold"), bg=CARD, fg=ACCENT).pack(pady=(10, 5))
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

    def _build_bottom(self):
        f = tk.Frame(self.win, bg=PANEL, pady=10)
        f.pack(fill=tk.X)
        
        btns = [
            ("▶ Giải", self.do_solve, GREEN),
            ("◀◀ Bước trước", self.do_prev, BTN),
            ("Bước sau ▶▶", self.do_next, BTN),
        ]
        for txt, cmd, clr in btns:
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

    def set_exp(self, text):
        self.txt_exp.config(state=tk.NORMAL)
        self.txt_exp.delete("1.0", tk.END)
        self.txt_exp.insert(tk.END, text)
        self.txt_exp.config(state=tk.DISABLED)

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
            
        self.board = b
        self.steps = []
        self.step_idx = -1
        self.draw_initial()

    def do_reset(self):
        self.auto_playing = False
        self.btn_auto.config(text="Tự chạy ⏯", bg="#5a189a")
        self.board = [r[:] for r in DEFAULT]
        self.steps = []
        self.step_idx = -1
        self.draw_initial()

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
        self.auto_playing = not self.auto_playing
        if self.auto_playing:
            self.btn_auto.config(text="Dừng ⏸", bg=RED)
            self.run_auto_step()
        else:
            self.btn_auto.config(text="Tự chạy ⏯", bg="#5a189a")

    def run_auto_step(self):
        if self.auto_playing and self.step_idx < len(self.steps) - 1:
            self.do_next()
            self.win.after(500, self.run_auto_step)

def open_ui(parent, algo_name):
    UninformedUI(parent, algo_name)
