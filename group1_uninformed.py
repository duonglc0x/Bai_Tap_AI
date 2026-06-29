import tkinter as tk
from tkinter import messagebox
from collections import deque
import copy
import random

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

class SearchNode:
    def __init__(self, board, action=None, tile_val=None, depth=0, parent=None, cost=0):
        self.board = [r[:] for r in board]
        self.action = action
        self.tile_val = tile_val
        self.depth = depth
        self.parent = parent
        self.cost = cost
        
    def blank(self):
        for i in range(4):
            for j in range(4):
                if self.board[i][j] == 0:
                    return i, j
                    
    def nbrs(self):
        res = []
        bi, bj = self.blank()
        for di, dj, nm in [(-1, 0, "↑"), (1, 0, "↓"), (0, -1, "←"), (0, 1, "→")]:
            ni, nj = bi + di, bj + dj
            if 0 <= ni < 4 and 0 <= nj < 4:
                b = [r[:] for r in self.board]
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
            steps.append({
                'cur': curr,
                'frontier': list(frontier),
                'reached': list(reached),
                'text': f"🎉 ĐÃ TÌM THẤY ĐÍCH! Tổng số node đã duyệt: {nodes_expanded}."
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
            steps.append({
                'cur': curr,
                'frontier': list(frontier),
                'reached': list(reached),
                'text': f"🎉 ĐÃ TÌM THẤY ĐÍCH! Tổng số node đã duyệt: {nodes_expanded}."
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
            steps.append({
                'cur': curr,
                'frontier': list(frontier),
                'reached': list(reached),
                'text': f"🎉 ĐÃ TÌM THẤY ĐÍCH! Tổng số node đã duyệt: {nodes_expanded}."
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
        
    return steps

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
                ok = v == GOAL[i][j]
                c = "#2d6a4f" if ok else CELL
                canvas.create_rectangle(x, y, x + cs, y + cs, fill=c, outline="#4a6d8c", width=1)
                fs = max(cs // 3, 8)
                canvas.create_text(x + cs // 2, y + cs // 2, text=str(v), fill=TEXT, font=("Segoe UI", fs, "bold"))
    return total

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
        self.algo = algo_name or "Breadth-First Search (BFS)"
        self.steps = []
        self.step_idx = -1
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
        tk.Label(f, text="NHÓM 1: TÌM KIẾM MÙ", font=("Segoe UI", 14, "bold"), bg=PANEL, fg=ACCENT).pack(side=tk.LEFT, padx=20)
        
        bb = tk.Button(f, text="◀ Quay lại", font=("Segoe UI", 10, "bold"), bg=RED, fg=TEXT, relief="flat", padx=12, pady=4, cursor="hand2", command=self.on_close)
        bb.pack(side=tk.RIGHT, padx=15)
        
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
            
    def _build_middle(self):
        mf = tk.Frame(self.win, bg=BG)
        mf.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        lf = tk.Frame(mf, bg=CARD, highlightbackground="#2a3a5c", highlightthickness=1)
        lf.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        
        tk.Label(lf, text="NODE ĐANG XÉT", font=("Segoe UI", 11, "bold"), bg=CARD, fg=ACCENT).pack(pady=(10, 5))
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
        
    def _build_bottom(self):
        f = tk.Frame(self.win, bg=PANEL, pady=10)
        f.pack(fill=tk.X)
        
        btns = [
            ("📝 Nhập tay", self.do_input, "#6930c3"),
            ("▶ Giải", self.do_solve, GREEN),
            ("◀◀ Bước trước", self.do_prev, BTN),
            ("Bước sau ▶▶", self.do_next, BTN),
        ]
        for txt, cmd, clr in btns:
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
        self.cv_cur.delete("all")
        draw_board(self.cv_cur, self.board, 58, 10, 10, border_color=ACCENT)
        self.lbl_info.config(text="g = 0\ndepth = 0\naction = Bắt đầu")
        
        for w in self.fr_inner.winfo_children(): w.destroy()
        
        
        for w in self.re_inner.winfo_children(): w.destroy()
        tk.Label(self.re_inner, text="Hộp rỗng", font=("Segoe UI", 11), bg=CARD, fg=SUB).pack(expand=True, pady=40)
        
        self.set_exp("Chọn thuật toán ở thanh trên và nhấn Giải để quan sát mô phỏng.")
        self.lbl_step.config(text="")
        
    def show_step(self, idx):
        if idx < 0 or idx >= len(self.steps): return
        self.step_idx = idx
        st = self.steps[idx]
        self.lbl_step.config(text=f"Bước {idx+1}/{len(self.steps)}")
        
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
        
    def set_exp(self, text):
        self.txt_exp.config(state=tk.NORMAL)
        self.txt_exp.delete("1.0", tk.END)
        self.txt_exp.insert(tk.END, text)
        self.txt_exp.config(state=tk.DISABLED)
        
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
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn thuật toán!", parent=self.win)
            return
            
        if self.algo == "Breadth-First Search (BFS)":
            self.steps = solve_bfs(self.board)
        elif self.algo == "Depth-First Search (DFS)":
            self.steps = solve_dfs(self.board)
        else:
            self.steps = solve_ucs(self.board)
            
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
        self.auto_playing = not self.auto_playing
        if self.auto_playing:
            self.btn_auto.config(text="Dừng ⏸", bg=RED)
            self.run_auto_step()
        else:
            self.btn_auto.config(text="Tự chạy ⏯", bg="#5a189a")
            
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
