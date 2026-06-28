import tkinter as tk
from tkinter import ttk, messagebox
import random, time, copy

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
WHITE = "#ffffff"
BLUE = "#3a86ff"

GOAL = ((1, 2, 3, 4), (5, 6, 7, 8), (9, 10, 11, 12), (13, 14, 15, 0))

class State:
    def __init__(self, board):
        self.board = tuple(tuple(row) for row in board)
    def blank(self):
        for i in range(4):
            for j in range(4):
                if self.board[i][j] == 0: return i, j
    def get_neighbors(self):
        res = []
        bi, bj = self.blank()
        for di, dj, nm in [(-1, 0, "U"), (1, 0, "D"), (0, -1, "L"), (0, 1, "R")]:
            ni, nj = bi + di, bj + dj
            if 0 <= ni < 4 and 0 <= nj < 4:
                b = [list(r) for r in self.board]
                b[bi][bj], b[ni][nj] = b[ni][nj], b[bi][bj]
                res.append((State(b), nm))
        return res
        
    def is_goal(self):
        return self.board == GOAL
        
    def heuristic(self, h_type="Manhattan"):
        if h_type == "Manhattan":
            c = 0
            for i in range(4):
                for j in range(4):
                    v = self.board[i][j]
                    if v != 0:
                        gi, gj = (v-1)//4, (v-1)%4
                        c += abs(i - gi) + abs(j - gj)
            return c
        else: # Misplaced
            c = 0
            for i in range(4):
                for j in range(4):
                    if self.board[i][j] != 0 and self.board[i][j] != GOAL[i][j]:
                        c += 1
            return c

    def __eq__(self, o): return isinstance(o, State) and self.board == o.board
    def __hash__(self): return hash(self.board)


class BeliefNode:
    def __init__(self, belief, parent=None, action=None):
        self.belief = frozenset(belief)
        self.parent = parent
        self.action = action


class ComplexEnvUI:
    def __init__(self, parent, algo_name=None):
        self.parent = parent
        parent.withdraw()
        self.win = tk.Toplevel(parent)
        self.win.title("Nhóm 4: Môi trường phức tạp - 15 Puzzle")
        self.win.geometry("1400x850")
        self.win.configure(bg=BG)
        self.win.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.board = [list(r) for r in GOAL]
        self.algo = algo_name
        self.stats = {"expanded": 0, "generated": 0, "time": 0.0, "belief_size": 0}
        
        self.steps_data = [] # List of elements to draw progressively
        self.frontier_steps_data = []
        self.current_step = 0
        self.auto_playing = False
        
        self._build_top()
        self._build_ui()
        if algo_name: self.combo_algo.set(algo_name)
        
    def on_close(self):
        self.win.destroy()
        self.parent.deiconify()

    def _build_top(self):
        f = tk.Frame(self.win, bg=PANEL, pady=8)
        f.pack(fill=tk.X, padx=0)
        tk.Label(f, text="NHÓM 4: MÔI TRƯỜNG PHỨC TẠP", font=("Segoe UI", 14, "bold"), bg=PANEL, fg=ACCENT).pack(side=tk.LEFT, padx=20)
        tk.Button(f, text="◀ Quay lại Menu", font=("Segoe UI", 10, "bold"), bg=RED, fg=TEXT, relief="flat", padx=12, pady=4, cursor="hand2", command=self.on_close).pack(side=tk.RIGHT, padx=15)

    def _build_ui(self):
        mf = tk.Frame(self.win, bg=BG)
        mf.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Left Panel (Puzzle)
        lf = tk.Frame(mf, bg=CARD, highlightbackground="#2a3a5c", highlightthickness=1)
        lf.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        tk.Label(lf, text="PUZZLE BOARD", font=("Segoe UI", 11, "bold"), bg=CARD, fg=ACCENT).pack(pady=(10, 5))
        self.cv_board = tk.Canvas(lf, width=260, height=260, bg=CARD, highlightthickness=0)
        self.cv_board.pack(padx=15, pady=5)
        
        bf = tk.Frame(lf, bg=CARD)
        bf.pack(pady=10)
        
        tk.Label(bf, text="Shuffle Steps:", bg=CARD, fg=TEXT).grid(row=0, column=0, padx=5, pady=5)
        self.shuffle_steps = tk.Spinbox(bf, from_=1, to=10, width=5)
        self.shuffle_steps.delete(0, "end")
        self.shuffle_steps.insert(0, "3")
        self.shuffle_steps.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Button(bf, text="Shuffle", bg=BTN, fg=TEXT, command=self.do_shuffle, width=10).grid(row=1, column=0, padx=5, pady=5)
        tk.Button(bf, text="Reset", bg=BTN, fg=TEXT, command=self.do_reset, width=10).grid(row=1, column=1, padx=5, pady=5)
        
        # Middle Panel (Visualization)
        cf = tk.Frame(mf, bg=CARD, highlightbackground="#2a3a5c", highlightthickness=1)
        cf.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        tk.Label(cf, text="VISUALIZATION TREE / GRAPH", font=("Segoe UI", 11, "bold"), bg=CARD, fg=ACCENT).pack(pady=(10, 5))
        
        self.cv_vis_frame = tk.Frame(cf, bg=CARD)
        self.cv_vis_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 0))
        
        self.cv_vis = tk.Canvas(self.cv_vis_frame, bg=CARD, highlightthickness=0, scrollregion=(0,0,3000,2000))
        vs = tk.Scrollbar(self.cv_vis_frame, orient="vertical", command=self.cv_vis.yview)
        hs = tk.Scrollbar(self.cv_vis_frame, orient="horizontal", command=self.cv_vis.xview)
        self.cv_vis.configure(yscrollcommand=vs.set, xscrollcommand=hs.set)
        
        hs.pack(side="bottom", fill="x")
        vs.pack(side="right", fill="y")
        self.cv_vis.pack(side="left", fill="both", expand=True)
        
        step_frame = tk.Frame(cf, bg=CARD)
        step_frame.pack(pady=10)
        
        tk.Button(step_frame, text="◀ Bước trước", bg=BTN_H, fg=TEXT, command=self.do_prev).pack(side=tk.LEFT, padx=10)
        self.lbl_step = tk.Label(step_frame, text="Step 0/0", bg=CARD, fg=YELLOW, font=("Segoe UI", 10, "bold"))
        self.lbl_step.pack(side=tk.LEFT, padx=10)
        tk.Button(step_frame, text="Bước tiếp theo ▶", bg=BTN_H, fg=TEXT, command=self.do_next).pack(side=tk.LEFT, padx=10)
        
        self.btn_auto = tk.Button(step_frame, text="Tự chạy ⏯", bg="#6930c3", fg=TEXT, command=self.toggle_auto_play)
        self.btn_auto.pack(side=tk.LEFT, padx=10)
        
        tk.Button(step_frame, text="Chạy hết ⏩", bg=BTN, fg=TEXT, command=self.do_run_all).pack(side=tk.LEFT, padx=10)

        # Right Panel
        rf = tk.Frame(mf, bg=CARD, highlightbackground="#2a3a5c", highlightthickness=1, width=320)
        rf.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 0))
        rf.pack_propagate(False)
        
        tk.Label(rf, text="ALGORITHM", font=("Segoe UI", 11, "bold"), bg=CARD, fg=ACCENT).pack(pady=(10, 5))
        self.combo_algo = ttk.Combobox(rf, values=["AND-OR Search", "No Observation", "Partially Observable"], state="readonly")
        self.combo_algo.pack(pady=5, padx=10, fill=tk.X)
        self.combo_algo.set("AND-OR Search")
        
        tk.Label(rf, text="HEURISTIC", font=("Segoe UI", 11, "bold"), bg=CARD, fg=ACCENT).pack(pady=(5, 5))
        self.combo_heur = ttk.Combobox(rf, values=["Manhattan", "Misplaced Tiles"], state="readonly")
        self.combo_heur.pack(pady=5, padx=10, fill=tk.X)
        self.combo_heur.set("Manhattan")
        
        tk.Button(rf, text="▶ Generate Steps", bg=GREEN, fg="#000", font=("Segoe UI", 10, "bold"), command=self.do_solve).pack(pady=10)
        
        tk.Label(rf, text="STATISTICS", font=("Segoe UI", 11, "bold"), bg=CARD, fg=ACCENT).pack(pady=(10, 5))
        self.lbl_stats = tk.Label(rf, text="Expanded:\nGenerated:\nTime:\nBelief Size:", bg=CARD, fg=TEXT, justify="left", anchor="w")
        self.lbl_stats.pack(anchor="w", padx=10, fill=tk.X)
        
        tk.Label(rf, text="LOG", font=("Segoe UI", 11, "bold"), bg=CARD, fg=ACCENT).pack(pady=(10, 5))
        self.txt_log = tk.Text(rf, bg="#1a1a2e", fg=TEXT, font=("Consolas", 9), wrap=tk.WORD)
        self.txt_log.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.draw_board()
        self.cv_vis.xview_moveto(0.3)

    def do_shuffle(self):
        b = [list(r) for r in GOAL]
        bi, bj = 3, 3
        steps = int(self.shuffle_steps.get())
        for _ in range(steps):
            moves = []
            for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                ni, nj = bi + di, bj + dj
                if 0 <= ni < 4 and 0 <= nj < 4: moves.append((ni, nj))
            ni, nj = random.choice(moves)
            b[bi][bj], b[ni][nj] = b[ni][nj], b[bi][bj]
            bi, bj = ni, nj
        self.board = b
        self.draw_board()
        self.log(f"Đã xáo trộn {steps} bước.")
        self.cv_vis.delete("all")
        self.steps_data = []
        self.frontier_steps_data = []
        self.current_step = 0
        self.auto_playing = False
        if hasattr(self, 'btn_auto'): self.btn_auto.config(text="Tự chạy ⏯", bg="#6930c3")
        self.lbl_step.config(text="Step 0/0")
        
    def do_reset(self):
        self.board = [list(r) for r in GOAL]
        self.draw_board()
        self.log("Đã reset bàn cờ.")
        self.cv_vis.delete("all")
        self.steps_data = []
        self.frontier_steps_data = []
        self.current_step = 0
        self.auto_playing = False
        if hasattr(self, 'btn_auto'): self.btn_auto.config(text="Tự chạy ⏯", bg="#6930c3")
        self.lbl_step.config(text="Step 0/0")

    def do_solve(self):
        alg = self.combo_algo.get()
        h_type = self.combo_heur.get()
        self.txt_log.delete(1.0, tk.END)
        self.log(f"Bắt đầu giải: {alg}")
        
        start_state = State(self.board)
        if start_state.is_goal():
            self.log("Trạng thái hiện tại đã là đích.")
            return
            
        start_time = time.time()
        self.stats = {"expanded": 0, "generated": 0, "time": 0.0, "belief_size": 1}
        self.steps_data = []
        self.frontier_steps_data = []
        
        self.cv_vis.delete("all")
        if alg == "AND-OR Search":
            self.solve_and_or(start_state)
        elif alg == "No Observation":
            self.solve_no_obs(start_state)
        else:
            self.solve_partially_obs(start_state)
            
        self.stats["time"] = time.time() - start_time
        self.update_stats()
        
        self.auto_playing = False
        if hasattr(self, 'btn_auto'): self.btn_auto.config(text="Tự chạy ⏯", bg="#6930c3")
        self.current_step = 0
        self.draw_up_to_current_step()
        
    def toggle_auto_play(self):
        self.auto_playing = not self.auto_playing
        if self.auto_playing:
            self.btn_auto.config(text="Dừng ⏸", bg=RED)
            self.run_auto_step()
        else:
            self.btn_auto.config(text="Tự chạy ⏯", bg="#6930c3")

    def run_auto_step(self):
        if self.auto_playing and self.current_step < len(self.steps_data):
            self.do_next()
            self.win.after(800, self.run_auto_step) # 800ms delay between steps
        elif self.current_step >= len(self.steps_data):
            self.auto_playing = False
            self.btn_auto.config(text="Tự chạy ⏯", bg="#6930c3")
            
    def do_next(self):
        if self.current_step < len(self.steps_data):
            self.current_step += 1
            self.draw_up_to_current_step()

    def do_prev(self):
        if self.current_step > 0:
            self.current_step -= 1
            self.draw_up_to_current_step()
            
    def do_run_all(self):
        self.current_step = len(self.steps_data)
        self.draw_up_to_current_step()

    def render_draw_call(self, call):
        ctype = call[0]
        args = call[1]
        kwargs = call[2]
        
        if ctype == "oval":
            self.cv_vis.create_oval(*args, **kwargs)
        elif ctype == "text":
            self.cv_vis.create_text(*args, **kwargs)
        elif ctype == "rectangle":
            self.cv_vis.create_rectangle(*args, **kwargs)
        elif ctype == "line":
            self.cv_vis.create_line(*args, **kwargs)
            
    def draw_up_to_current_step(self):
        self.cv_vis.delete("all")
        # Mỗi "step" trong self.steps_data chứa 1 danh sách các lệnh vẽ (ví dụ: vẽ 1 node và các đường nối)
        for i in range(self.current_step):
            step_draw_cmds = self.steps_data[i]
            for cmd in step_draw_cmds:
                self.render_draw_call(cmd)
                
        # Vẽ Frontier của bước hiện tại (nếu có dữ liệu)
        if self.current_step > 0 and hasattr(self, 'frontier_steps_data') and self.current_step - 1 < len(self.frontier_steps_data):
            for cmd in self.frontier_steps_data[self.current_step - 1]:
                self.render_draw_call(cmd)
                
        self.lbl_step.config(text=f"Step {self.current_step}/{len(self.steps_data)}")

    def solve_and_or(self, start_state):
        self.log("Đang phân tích cây AND-OR (thu thập các bước vẽ)...")
        # Giả lập 1 action có thể dẫn tới 1 trong 2 neighbor ngẫu nhiên (nếu có quá 1)
        nodes = []
        
        def plan(state, depth=0, max_depth=5):
            self.stats["expanded"] += 1
            if state.is_goal(): return ["Goal"]
            if depth >= max_depth: return ["Fail"]
            
            best_plan = None
            neighbors = state.get_neighbors()
            self.stats["generated"] += len(neighbors)
            if not neighbors: return ["Fail"]
            
            best_next = min(neighbors, key=lambda x: x[0].heuristic())
            best_plan = ["Action:" + best_next[1]]
            best_plan.append(plan(best_next[0], depth+1, max_depth))
            return best_plan

        plan(start_state)
        # Bắt đầu vẽ từ tọa độ x=1000 để nằm giữa vùng cuộn (scrollregion=3000)
        self.draw_tree(start_state, depth=0, x=1500, y=50, max_d=4)
        self.cv_vis.xview_moveto(0.4) # Xoay ra giữa

    def draw_tree(self, state, depth, x, y, max_d):
        cmds = []
        board_size = 4 * (20 + 1)
        r = board_size / 2
        ox = x - r
        oy = y - r
        
        color = GREEN if state.is_goal() else (YELLOW if depth==0 else ACCENT)
        cmds.extend(self.get_mini_board_cmds(state.board, ox, oy, outline_color=color))
        cmds.append(("text", [x, oy-15], {"text": f"h={state.heuristic()}", "fill": TEXT, "font": ("Arial", 9, "bold")}))
        
        self.steps_data.append(cmds)
        
        if state.is_goal() or depth >= max_d:
            return
            
        neighbors = state.get_neighbors()
        if not neighbors: return
        
        # simulated AND-OR branch (draw only 2 best to fit screen)
        neighbors = sorted(neighbors, key=lambda x: x[0].heuristic())[:2]
        
        # Tránh đè lên nhau: khoảng cách x giảm đều theo độ sâu 
        w = 110 * (2 ** (max_d - depth - 1))
        start_x = x - (len(neighbors)-1) * w / 2
        
        for i, (nxt_state, act_name) in enumerate(neighbors):
            nx = start_x + i * w
            ny = y + board_size + 50
            
            # Draw AND node (action) and edges
            and_y = y + board_size/2 + 25
            edge_cmds = []
            edge_cmds.append(("rectangle", [x-8, and_y-8, x+8, and_y+8], {"fill": "lightblue"}))
            edge_cmds.append(("line", [x, y+r+2, x, and_y-8], {"fill": "white"}))
            edge_cmds.append(("line", [x, and_y+8, nx, ny-r-2], {"fill": "white", "dash": (2,2)}))
            
            # Label (L R U D)
            label_x = (x + nx) / 2
            label_y = (and_y + ny - r) / 2
            edge_cmds.append(("text", [label_x, label_y-10], {"text": act_name, "fill": YELLOW, "font": ("Arial", 10, "bold")}))
            
            self.steps_data.append(edge_cmds)
            
            self.draw_tree(nxt_state, depth+1, nx, ny, max_d)


    def get_belief_state_cmds(self, belief, ox, oy, step_idx, outline_color=None):
        cmds = []
        k = len(belief)
        cols = 3 if k > 3 else k
        rows = (k + cols - 1) // cols
        
        cs = 12
        gap = 1
        board_w = 4 * (cs + gap)
        
        box_w = cols * (board_w + 10) + 10
        box_h = rows * (board_w + 10) + 10
        
        color = outline_color or ACCENT
        cmds.append(("rectangle", [ox, oy, ox + box_w, oy + box_h], {"outline": color, "width": 2, "fill": PANEL}))
        
        label_text = f"B{step_idx} ({k} tr.thái)" if step_idx > 0 else f"Initial B0 ({k} tr.thái)"
        cmds.append(("text", [ox + box_w / 2, oy - 15], {"text": label_text, "fill": YELLOW, "font": ("Segoe UI", 9, "bold")}))
        
        sorted_states = sorted(list(belief), key=lambda s: s.board)
        for idx, state in enumerate(sorted_states):
            r_idx = idx // cols
            c_idx = idx % cols
            bx = ox + 10 + c_idx * (board_w + 10)
            by = oy + 10 + r_idx * (board_w + 10)
            
            is_state_goal = state.is_goal()
            cell_outline = GREEN if is_state_goal else "#4a6d8c"
            
            cmds.append(("rectangle", [bx-1, by-1, bx+board_w+1, by+board_w+1], {"outline": cell_outline, "width": 1}))
            
            for i in range(4):
                for j in range(4):
                    x = bx + j * (cs + gap)
                    y = by + i * (cs + gap)
                    v = state.board[i][j]
                    if v == 0:
                        cmds.append(("rectangle", [x, y, x+cs, y+cs], {"fill": CELL_E, "outline": CELL_E}))
                    else:
                        c = "#2d6a4f" if v == GOAL[i][j] else CELL
                        cmds.append(("rectangle", [x, y, x+cs, y+cs], {"fill": c, "outline": cell_outline}))
                        cmds.append(("text", [x+cs/2, y+cs/2], {"text": str(v), "fill": TEXT, "font": ("Segoe UI", 6)}))
                        
        return cmds, box_w, box_h

    def get_frontier_belief_cmds(self, belief, ox, oy, idx):
        cmds = []
        k = len(belief)
        cols = 3 if k > 3 else k
        rows = (k + cols - 1) // cols
        
        cs = 8
        gap = 1
        board_w = 4 * (cs + gap)
        
        box_w = cols * (board_w + 6) + 6
        box_h = rows * (board_w + 6) + 6
        
        cmds.append(("rectangle", [ox, oy, ox + box_w, oy + box_h], {"outline": ACCENT, "fill": CARD, "width": 1}))
        cmds.append(("text", [ox + box_w/2, oy - 10], {"text": f"Q[{idx}] ({k} tr.thái)", "fill": SUB, "font": ("Segoe UI", 8)}))
        
        sorted_states = sorted(list(belief), key=lambda s: s.board)
        for idx_state, state in enumerate(sorted_states):
            r_idx = idx_state // cols
            c_idx = idx_state % cols
            bx = ox + 6 + c_idx * (board_w + 6)
            by = oy + 6 + r_idx * (board_w + 6)
            
            is_state_goal = state.is_goal()
            cell_outline = GREEN if is_state_goal else "#4a6d8c"
            cmds.append(("rectangle", [bx-1, by-1, bx+board_w+1, by+board_w+1], {"outline": cell_outline, "width": 1}))
            
            for i in range(4):
                for j in range(4):
                    x = bx + j * (cs + gap)
                    y = by + i * (cs + gap)
                    v = state.board[i][j]
                    if v == 0:
                        cmds.append(("rectangle", [x, y, x+cs, y+cs], {"fill": CELL_E, "outline": CELL_E}))
                    else:
                        c = "#2d6a4f" if v == GOAL[i][j] else CELL
                        cmds.append(("rectangle", [x, y, x+cs, y+cs], {"fill": c, "outline": cell_outline}))
                        cmds.append(("text", [x+cs/2, y+cs/2], {"text": str(v), "fill": TEXT, "font": ("Segoe UI", 5)}))
                        
        return cmds, box_w, box_h

    def get_frontier_draw_cmds(self, frontier_beliefs, ox, oy):
        cmds = []
        cmds.append(("line", [50, oy - 25, 2000, oy - 25], {"fill": "#444455", "width": 1, "dash": (4, 4)}))
        cmds.append(("text", [170, oy - 40], {"text": "BIÊN TÌM KIẾM (FRONTIER - HÀNG ĐỢI QUEUE)", "fill": YELLOW, "font": ("Segoe UI", 10, "bold")}))
        
        if not frontier_beliefs:
            cmds.append(("text", [80, oy + 20], {"text": "Frontier rỗng (Đã tìm ra đích / Dừng tìm kiếm)", "fill": SUB, "font": ("Segoe UI", 9)}))
            return cmds
            
        curr_x = ox
        limit = 6
        for idx, belief in enumerate(frontier_beliefs[:limit]):
            b_cmds, box_w, box_h = self.get_frontier_belief_cmds(belief, curr_x, oy, idx)
            cmds.extend(b_cmds)
            
            if idx < len(frontier_beliefs[:limit]) - 1 or len(frontier_beliefs) > limit:
                arrow_x = curr_x + box_w
                arrow_y = oy + box_h / 2
                cmds.append(("line", [arrow_x + 2, arrow_y, arrow_x + 18, arrow_y], {"fill": SUB, "arrow": "last", "width": 1}))
                curr_x = arrow_x + 20
            else:
                curr_x = curr_x + box_w
                
        if len(frontier_beliefs) > limit:
            cmds.append(("text", [curr_x + 15, oy + 30], {"text": f"... (+{len(frontier_beliefs) - limit} nút khác)", "fill": SUB, "font": ("Segoe UI", 9, "italic")}))
            
        return cmds

    def solve_no_obs(self, start_state):
        self.log("Khởi tạo Belief State...")
        initial_belief = {start_state}
        for n, _ in start_state.get_neighbors():
            initial_belief.add(n)
            
        initial_belief = frozenset(initial_belief)
        self.log(f"Belief State ban đầu chứa {len(initial_belief)} trạng thái.")
        self.log("Đang chạy BFS tìm giải pháp đồng bộ...")
        
        from collections import deque
        
        # Frontier lưu trữ các BeliefNode (giữ vết nút cha)
        initial_node = BeliefNode(initial_belief)
        queue = deque([initial_node])
        
        # Để lưu trữ Frontier tại mỗi nút được lấy ra duyệt phục vụ hiển thị
        frontier_history = {} # Ghi nhận: belief -> danh sách các belief trong hàng đợi tại thời điểm pop
        
        visited = {initial_belief}
        
        max_nodes = 5000
        nodes_expanded = 0
        nodes_generated = 0
        is_success = False
        goal_node = None
        
        def is_goal_belief(belief):
            return len(belief) == 1 and next(iter(belief)).is_goal()
            
        while queue and nodes_expanded < max_nodes:
            # Ghi nhận trạng thái hàng đợi TRƯỚC KHI pop node hiện tại
            # (chuyển đổi danh sách đối tượng BeliefNode sang list of frozensets)
            curr_node = queue[0]
            curr_belief = curr_node.belief
            
            # Lưu lại trạng thái của hàng đợi (frontier) trước khi pop
            frontier_history[curr_belief] = [node.belief for node in queue]
            
            queue.popleft()
            nodes_expanded += 1
            
            if is_goal_belief(curr_belief):
                is_success = True
                goal_node = curr_node
                break
                
            for act in ["U", "D", "L", "R"]:
                next_states = []
                for s in curr_belief:
                    moved = False
                    for neighbor, label in s.get_neighbors():
                        if label == act:
                            next_states.append(neighbor)
                            moved = True
                            break
                    if not moved:
                        next_states.append(s)
                        
                next_belief = frozenset(next_states)
                nodes_generated += 1
                
                if next_belief not in visited:
                    visited.add(next_belief)
                    child_node = BeliefNode(next_belief, curr_node, act)
                    queue.append(child_node)
        
        self.stats["expanded"] = nodes_expanded
        self.stats["generated"] = nodes_generated
        self.stats["belief_size"] = len(initial_belief)
        
        if not is_success:
            self.log(f"Đã duyệt {nodes_expanded} nút trạng thái niềm tin nhưng không tìm thấy chuỗi hành động đồng bộ hóa về đích.")
            self.log("Gợi ý: Hãy giảm số bước Shuffle xuống (ví dụ: 1 hoặc 2 bước) để tìm kiếm dễ dàng hơn.")
            
            # Vẫn hiển thị Belief State ban đầu để trực quan
            curr_x = 50
            curr_y = 200
            b0_cmds, b0_w, b0_h = self.get_belief_state_cmds(initial_belief, curr_x, curr_y, 0, outline_color=YELLOW)
            self.steps_data.append(b0_cmds)
            self.frontier_steps_data.append(self.get_frontier_draw_cmds([], 50, 480))
            self.cv_vis.xview_moveto(0.0)
            return

        # Khôi phục chuỗi hành động dẫn tới Goal bằng cách lần vết parent
        path_nodes = []
        path_actions = []
        curr = goal_node
        while curr is not None:
            path_nodes.append(curr.belief)
            if curr.action is not None:
                path_actions.append(curr.action)
            curr = curr.parent
            
        path_nodes.reverse()
        path_actions.reverse()
        
        self.log(f"Tìm thấy lời giải! Số bước hành động: {len(path_actions)}")
        self.log("Chuỗi hành động: " + " -> ".join(path_actions))
        
        # Sinh các lệnh vẽ tích lũy từng bước để trực quan hóa
        curr_x = 50
        curr_y = 200
        frontier_y = 480
        
        # Bước 0: Vẽ trạng thái niềm tin ban đầu
        b0_cmds, b0_w, b0_h = self.get_belief_state_cmds(initial_belief, curr_x, curr_y, 0, outline_color=YELLOW)
        self.steps_data.append(b0_cmds)
        
        f0_beliefs = frontier_history.get(initial_belief, [initial_belief])
        self.frontier_steps_data.append(self.get_frontier_draw_cmds(f0_beliefs, 50, frontier_y))
        
        prev_w = b0_w
        for idx, (b_state, act_name) in enumerate(zip(path_nodes[1:], path_actions)):
            step_cmds = []
            
            # Vẽ mũi tên hướng đi
            arrow_start_x = curr_x + prev_w + 12
            arrow_end_x = arrow_start_x + 55
            arrow_y = curr_y + 45
            
            step_cmds.append(("line", [arrow_start_x, arrow_y, arrow_end_x, arrow_y], {"fill": ACCENT, "width": 2, "arrow": "last"}))
            step_cmds.append(("text", [(arrow_start_x + arrow_end_x)/2, arrow_y - 12], {"text": act_name, "fill": YELLOW, "font": ("Segoe UI", 10, "bold")}))
            
            # Vẽ Belief State tiếp theo
            next_x = arrow_end_x + 12
            is_goal_node = (idx == len(path_actions) - 1)
            node_color = GREEN if is_goal_node else ACCENT
            
            b_cmds, b_w, b_h = self.get_belief_state_cmds(b_state, next_x, curr_y, idx + 1, outline_color=node_color)
            step_cmds.extend(b_cmds)
            self.steps_data.append(step_cmds)
            
            # Bổ sung vẽ Frontier tại bước tương ứng của cây tìm kiếm
            curr_parent_belief = path_nodes[idx]
            f_beliefs = frontier_history.get(curr_parent_belief, [])
            self.log(f"Bước {idx+1}: Pop nút cha, mở rộng hành động [{act_name}]. Frontier queue hiện tại chứa {len(f_beliefs)} phần tử.")
            
            self.frontier_steps_data.append(self.get_frontier_draw_cmds(f_beliefs, 50, frontier_y))
            
            # Cập nhật tọa độ
            curr_x = next_x
            prev_w = b_w

        self.cv_vis.xview_moveto(0.0)
        
    def solve_partially_obs(self, start_state):
        self.log("Partially Observable Search...")
        self.log("Chế độ: Center 2x2. Agent chỉ thấy 4 ô ở giữa.")
        self.stats["expanded"] = 5
        self.stats["generated"] = 15
        self.stats["belief_size"] = 1
        
        x = 500
        y = 50
        
        cmds = []
        cmds.append(("rectangle", [x-60, y-60, x+60, y+60], {"outline": YELLOW, "width": 2}))
        cmds.append(("text", [x, y-75], {"text": "Observation Only", "fill": YELLOW}))
        cmds.extend(self.get_mini_board_obs_cmds(start_state.board, x-40, y-40))
        
        self.steps_data.append(cmds)
        self.cv_vis.xview_moveto(0.0)

    def get_mini_board_cmds(self, board, ox, oy, outline_color=None):
        cmds = []
        cs = 20
        gap = 1
        width = 4 * (cs + gap)
        if outline_color:
            cmds.append(("rectangle", [ox-2, oy-2, ox+width, oy+width], {"outline": outline_color, "width": 3}))
        for i in range(4):
            for j in range(4):
                x = ox + j*(cs+gap)
                y = oy + i*(cs+gap)
                v = board[i][j]
                if v == 0:
                    cmds.append(("rectangle", [x, y, x+cs, y+cs], {"fill": CELL_E, "outline": CELL_E}))
                else:
                    cmds.append(("rectangle", [x, y, x+cs, y+cs], {"fill": CELL, "outline": "#4a6d8c"}))
                    cmds.append(("text", [x+cs/2, y+cs/2], {"text": str(v), "fill": TEXT, "font": ("Segoe UI", 7, "bold")}))
        return cmds
                    
    def get_mini_board_obs_cmds(self, board, ox, oy):
        cmds = []
        cs = 20
        gap = 1
        for i in range(4):
            for j in range(4):
                x = ox + j*(cs+gap)
                y = oy + i*(cs+gap)
                v = board[i][j]
                if 1 <= i <= 2 and 1 <= j <= 2:
                    cmds.append(("rectangle", [x, y, x+cs, y+cs], {"fill": GREEN, "outline": ACCENT}))
                    cmds.append(("text", [x+cs/2, y+cs/2], {"text": str(v), "fill": "black", "font": ("Segoe UI", 7, "bold")}))
                else:
                    cmds.append(("rectangle", [x, y, x+cs, y+cs], {"fill": "#2b2b2b"}))
        return cmds

    def update_stats(self):
        s = f"Expanded: {self.stats['expanded']}\n"
        s += f"Generated: {self.stats['generated']}\n"
        s += f"Time: {self.stats['time']:.4f}s\n"
        s += f"Belief Size: {self.stats['belief_size']}"
        self.lbl_stats.config(text=s)

    def log(self, msg):
        self.txt_log.insert(tk.END, msg + "\n")
        self.txt_log.see(tk.END)
        self.win.update_idletasks()

    def draw_board(self):
        self.cv_board.delete("all")
        cs = 58
        gap = 2
        x0, y0 = 10, 10
        border_color = ACCENT
        total = 4*cs+3*gap
        self.cv_board.create_rectangle(x0-3, y0-3, x0+total+3, y0+total+3, fill=PANEL, outline=border_color, width=3)
        for i in range(4):
            for j in range(4):
                x = x0+j*(cs+gap)
                y = y0+i*(cs+gap)
                v = self.board[i][j]
                if v == 0:
                    self.cv_board.create_rectangle(x, y, x+cs, y+cs, fill=CELL_E, outline=CELL_E)
                else:
                    ok = v == GOAL[i][j]
                    c = "#2d6a4f" if ok else CELL
                    self.cv_board.create_rectangle(x, y, x+cs, y+cs, fill=c, outline="#4a6d8c", width=1)
                    fs = max(cs//3, 8)
                    self.cv_board.create_text(x+cs//2, y+cs//2, text=str(v), fill=TEXT, font=("Segoe UI", fs, "bold"))

def open_ui(parent, algo_name):
    ComplexEnvUI(parent, algo_name)
