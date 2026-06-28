import tkinter as tk
from tkinter import messagebox
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
        # Số ô sai vị trí (xung đột)
        c = 0
        for i in range(4):
            for j in range(4):
                if self.board[i][j] != 0 and self.board[i][j] != GOAL[i][j]:
                    c += 1
        return c

    def manhattan(self):
        c = 0
        for i in range(4):
            for j in range(4):
                v = self.board[i][j]
                if v != 0:
                    gi, gj = (v-1)//4, (v-1)%4
                    c += abs(i - gi) + abs(j - gj)
        return c

    def __eq__(self, o):
        return self.board == o.board

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
def run_backtracking(start_board, depth_limit=8):
    steps = []
    visited_path = [State(start_board)]
    
    def backtrack(depth):
        curr_state = visited_path[-1]
        
        # Sắp xếp các trạng thái con theo khoảng cách Manhattan tăng dần (Heuristic LCV)
        raw_neighbors = curr_state.get_neighbors()
        raw_neighbors = sorted(raw_neighbors, key=lambda x: x[0].manhattan())
        
        neighbors_data = []
        for nxt, act, tile_val in raw_neighbors:
            if nxt in visited_path:
                status = "visited"
            else:
                status = "valid"
            neighbors_data.append((nxt.board, act, status, tile_val))
            
        steps.append({
            'board': [r[:] for r in curr_state.board],
            'status': 'exploring',
            'depth': depth,
            'path': [s.board for s in visited_path],
            'neighbors': neighbors_data,
            'chosen_idx': -1,
            'text': f"Xét trạng thái tại độ sâu {depth}. Số ô sai vị trí (xung đột): {curr_state.h()}."
        })
        
        if curr_state.is_goal():
            steps[-1]['status'] = 'solved'
            steps[-1]['text'] = "🎉 Đã tìm thấy trạng thái Đích!"
            return True
            
        if depth >= depth_limit:
            steps[-1]['status'] = 'cutoff'
            steps[-1]['text'] = f"Đạt giới hạn độ sâu ({depth_limit}). Quay lui!"
            return False
            
        for idx, (nxt, act, status, _) in enumerate(neighbors_data):
            if status == "visited":
                continue
                
            nxt_state = State(nxt)
            visited_path.append(nxt_state)
            
            steps[-1]['chosen_idx'] = idx
            steps[-1]['text'] += f"\n→ Chọn đi hướng {act}."
            
            if backtrack(depth + 1):
                return True
                
            visited_path.pop()
            
            steps.append({
                'board': [r[:] for r in curr_state.board],
                'status': 'backtracking',
                'depth': depth,
                'path': [s.board for s in visited_path],
                'neighbors': neighbors_data,
                'chosen_idx': -1,
                'text': f"Quay lui về độ sâu {depth} từ hướng đi {act}."
            })
            
        return False
        
    backtrack(0)
    return steps

def run_forward_checking(start_board, depth_limit=8):
    steps = []
    visited_path = [State(start_board)]
    
    def fc(depth):
        curr_state = visited_path[-1]
        
        # Sắp xếp các trạng thái con theo khoảng cách Manhattan tăng dần (Heuristic LCV)
        raw_neighbors = curr_state.get_neighbors()
        raw_neighbors = sorted(raw_neighbors, key=lambda x: x[0].manhattan())
        
        neighbors_data = []
        for nxt, act, tile_val in raw_neighbors:
            reasons = []
            if nxt in visited_path:
                reasons.append("Chu kỳ")
            h_val = nxt.manhattan()
            remaining_steps = depth_limit - (depth + 1)
            if h_val > remaining_steps:
                reasons.append(f"Manhattan {h_val} > {remaining_steps}")
                
            if reasons:
                status = "pruned"
                reason_str = ", ".join(reasons)
            else:
                status = "valid"
                reason_str = ""
            neighbors_data.append((nxt.board, act, status, reason_str, tile_val))
            
        domain_desc = ", ".join([act for _, act, _ in raw_neighbors])
        pruned_list = [f"{act} ({r})" for _, act, st, r, _ in neighbors_data if st == "pruned"]
        pruned_desc = ", ".join(pruned_list)
        valid_list = [act for _, act, st, _, _ in neighbors_data if st == "valid"]
        valid_desc = ", ".join(valid_list)
        
        text = (f"Xét trạng thái ở độ sâu {depth}.\n"
                f"Các hướng có thể: {domain_desc}.\n"
                f"→ FC cắt tỉa miền giá trị: {pruned_desc if pruned_desc else 'Không có'}.\n"
                f"→ Miền giá trị còn lại: {valid_desc if valid_desc else 'Trống (phải quay lui!)'}.")
                
        steps.append({
            'board': [r[:] for r in curr_state.board],
            'status': 'exploring',
            'depth': depth,
            'path': [s.board for s in visited_path],
            'neighbors': neighbors_data,
            'chosen_idx': -1,
            'text': text
        })
        
        if curr_state.is_goal():
            steps[-1]['status'] = 'solved'
            steps[-1]['text'] = "🎉 Đã tìm thấy trạng thái Đích!"
            return True
            
        if depth >= depth_limit:
            steps[-1]['status'] = 'cutoff'
            steps[-1]['text'] = f"Đạt giới hạn độ sâu ({depth_limit}). Quay lui!"
            return False
            
        for idx, (nxt, act, status, reason, _) in enumerate(neighbors_data):
            if status == "pruned":
                continue
                
            nxt_state = State(nxt)
            visited_path.append(nxt_state)
            
            steps[-1]['chosen_idx'] = idx
            steps[-1]['text'] += f"\n→ Chọn đi hướng {act}."
            
            if fc(depth + 1):
                return True
                
            visited_path.pop()
            
            steps.append({
                'board': [r[:] for r in curr_state.board],
                'status': 'backtracking',
                'depth': depth,
                'path': [s.board for s in visited_path],
                'neighbors': neighbors_data,
                'chosen_idx': -1,
                'text': f"Quay lui về độ sâu {depth}."
            })
            
        return False
        
    fc(0)
    return steps

def run_min_conflicts(start_board, max_steps=30):
    steps = []
    curr_state = State(start_board)
    
    for step_num in range(max_steps):
        conflicts = curr_state.h()
        
        if conflicts == 0:
            steps.append({
                'board': [r[:] for r in curr_state.board],
                'status': 'solved',
                'conflicts': 0,
                'path': [],
                'neighbors': [],
                'chosen_idx': -1,
                'text': f"🎉 Thành công! Giải được câu đố sau {step_num} bước lặp. Số ô sai vị trí = 0."
            })
            return steps
            
        raw_neighbors = curr_state.get_neighbors()
        neighbors_data = []
        
        for nxt, act, tile_val in raw_neighbors:
            nxt_h = nxt.h()
            neighbors_data.append((nxt.board, act, tile_val, nxt_h))
            
        # Tìm các nước đi tối thiểu hoá số ô sai
        min_h = min([item[3] for item in neighbors_data])
        best_indices = [i for i, item in enumerate(neighbors_data) if item[3] == min_h]
        
        final_neighbors_data = []
        for i, (nxt_b, act, tile, nxt_h) in enumerate(neighbors_data):
            status = "min_conflict" if i in best_indices else "valid"
            final_neighbors_data.append((nxt_b, act, status, tile, nxt_h))
            
        moves_desc = ", ".join([f"Trượt {item[3]} ({item[1]}): h={item[4]}" for item in final_neighbors_data])
        
        text = (f"Vòng lặp {step_num+1}:\nSố ô sai vị trí hiện tại (xung đột): {conflicts}.\n"
                f"Các nước đi có thể:\n{moves_desc}.\n"
                f"→ Chọn nước đi tối thiểu hoá số ô sai (h = {min_h}).")
                
        steps.append({
            'board': [r[:] for r in curr_state.board],
            'status': 'evaluating',
            'conflicts': conflicts,
            'path': [],
            'neighbors': final_neighbors_data,
            'chosen_idx': -1,
            'text': text
        })
        
        chosen_idx = random.choice(best_indices)
        nxt_b, act, status, tile, nxt_h = final_neighbors_data[chosen_idx]
        
        steps[-1]['chosen_idx'] = chosen_idx
        steps[-1]['text'] += f"\n→ Chọn trượt ô {tile} ({act})."
        
        curr_state = State(nxt_b)
        
    steps.append({
        'board': [r[:] for r in curr_state.board],
        'status': 'unsolved',
        'conflicts': curr_state.h(),
        'path': [],
        'neighbors': [],
        'chosen_idx': -1,
        'text': f"Không tìm thấy lời giải sau {max_steps} bước lặp (đạt giới hạn tối đa)."
    })
    return steps

ALGOS = {
    "Backtracking": run_backtracking,
    "Forward Checking": run_forward_checking,
    "Min-Conflicts": run_min_conflicts
}

# ===== MAIN UI =====
class CSP_UI:
    def __init__(self, parent, algo_name=None):
        self.parent = parent
        parent.withdraw()
        self.win = tk.Toplevel(parent)
        self.win.title("Nhóm 5: Thoả mãn ràng buộc - 15 Puzzle")
        self.win.geometry("1350x780")
        self.win.configure(bg=BG)
        self.win.minsize(1200, 700)
        self.win.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.board = [r[:] for r in DEFAULT]
        self.algo = algo_name
        self.steps = []
        self.step_idx = -1
        self.auto_playing = False
        self.depth_limit = 8
        
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
        tk.Label(f, text="NHÓM 5: THOẢ MÃN RÀNG BUỘC (CSP)", font=("Segoe UI", 14, "bold"), bg=PANEL, fg=ACCENT).pack(side=tk.LEFT, padx=20)
        
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
            ("Nước đi được chọn (★)", GREEN)
        ]
        for name, col in legend:
            f_lg = tk.Frame(lf, bg=CARD)
            f_lg.pack(fill=tk.X, padx=25, pady=2)
            if col == GREEN:
                tk.Label(f_lg, text=" ★ ", bg=CARD, fg=GREEN, font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 10))
            else:
                tk.Frame(f_lg, width=15, height=15, bg=col, highlightbackground=TEXT, highlightthickness=0.5).pack(side=tk.LEFT, padx=(0, 10))
            tk.Label(f_lg, text=name, bg=CARD, fg=TEXT, font=("Segoe UI", 9)).pack(side=tk.LEFT)

        # --- CỘT GIỮA: Các trạng thái con (Next States) ---
        cf = tk.Frame(mf, bg=CARD, highlightbackground="#2a3a5c", highlightthickness=1)
        cf.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        tk.Label(cf, text="CÁC BƯỚC THỬ TIẾP THEO (MIỀN GIÁ TRỊ)", font=("Segoe UI", 11, "bold"), bg=CARD, fg=ACCENT).pack(pady=(10, 5))
        self.children_frame = tk.Frame(cf, bg=CARD)
        self.children_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # --- CỘT PHẢI: Đường đi / Lịch sử đã duyệt + Giải thích ---
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
        self.lbl_h.config(text=f"Xung đột: {State(st['board']).h()}")
        
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
            
            is_chosen = (i == chosen_idx)
            
            if self.algo == "Backtracking":
                nxt_board, action, status, tile_val = item[:4]
                lbl_text = f"Trượt ô {tile_val} {action}"
                status_text = "Đã duyệt (bị loại)" if status == "visited" else "Hợp lệ"
                status_color = SUB if status == "visited" else YELLOW
                
                h_val = State(nxt_board).manhattan()
                val_text = f"h = {h_val}"
            elif self.algo == "Forward Checking":
                nxt_board, action, status, reason, tile_val = item[:5]
                lbl_text = f"Trượt ô {tile_val} {action}"
                status_text = f"Cắt tỉa: {reason}" if status == "pruned" else "Hợp lệ"
                status_color = RED if status == "pruned" else YELLOW
                
                h_val = State(nxt_board).manhattan()
                val_text = f"h = {h_val}"
            else: # Min-Conflicts
                nxt_board, action, status, tile, nxt_h = item[:5]
                lbl_text = f"Trượt ô {tile} {action}"
                status_text = f"Min-Conflict" if status == "min_conflict" else f"Hợp lệ"
                status_color = GREEN if status == "min_conflict" else TEXT
                
                val_text = f"h = {nxt_h}"
                
            if is_chosen:
                val_text += " ★"
                
            lbl_dir = tk.Label(cf, text=lbl_text, font=("Segoe UI", 10, "bold"), bg=CARD, fg=GREEN if is_chosen else TEXT)
            lbl_dir.pack(pady=(2, 2))
            
            cv = tk.Canvas(cf, width=grid_px + 10, height=grid_px + 10, bg=CARD, highlightthickness=0)
            cv.pack()
            
            bc = GREEN if is_chosen else (RED if (self.algo == "Forward Checking" and status == "pruned") else None)
            draw_board(cv, nxt_board, n_cs, 5, 5, border_color=bc)
            
            # Hiển thị chỉ số h dưới bàn cờ con
            tk.Label(cf, text=val_text, font=("Segoe UI", 9, "bold"), bg=CARD, fg=GREEN if is_chosen else YELLOW).pack(pady=(2, 0))
            
            # Hiển thị trạng thái duyệt
            tk.Label(cf, text=status_text, font=("Segoe UI", 9), bg=CARD, fg=GREEN if is_chosen else status_color).pack(pady=(0, 4))
            
        # 3. Vẽ đường đi ở cột phải
        for w in self.vis_inner.winfo_children(): w.destroy()
        
        path = st.get('path', [])
        if self.algo == "Min-Conflicts":
            path = [self.steps[k]['board'] for k in range(idx + 1)]
            
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
        self.steps = fn(self.board)
        
        if self.steps:
            self.show_step(0)
        else:
            self.set_exp("Không tìm thấy lời giải.")

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
    CSP_UI(parent, algo_name)
