import tkinter as tk
import heapq
import random

# ==========================================
# 1. CÁC THÀNH PHẦN CƠ BẢN CHO 15-PUZZLE
# ==========================================

# Trạng thái đích của 15-Puzzle: 1 đến 15 và 0 ở cuối
GOAL_STATE = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 0)

class State:
    def __init__(self, frontier, explored_size, current_path, hud_metrics, action_description):
        self.frontier = frontier
        self.explored_size = explored_size
        self.current_path = current_path
        self.hud_metrics = hud_metrics
        self.action_description = action_description

class BaseAlgorithm:
    def run(self, environment, start, target):
        raise NotImplementedError("Phải override phương thức run()")

def heuristic(state, target=GOAL_STATE):
    """Tính tổng khoảng cách Manhattan của 15 viên gạch tới vị trí đích"""
    dist = 0
    for i, val in enumerate(state):
        if val == 0: continue
        # Vị trí hiện tại của val
        curr_r, curr_c = divmod(i, 4)
        # Vị trí đích của val
        tar_r, tar_c = divmod(val - 1, 4)
        dist += abs(curr_r - tar_r) + abs(curr_c - tar_c)
    return dist

class PuzzleEnvironment:
    def get_neighbors(self, state):
        neighbors = []
        idx = state.index(0) # Tìm vị trí ô trống (0)
        r, c = divmod(idx, 4)
        
        # Các hướng trượt ô trống: Lên, Xuống, Trái, Phải
        moves = []
        if r > 0: moves.append(-4) # Trượt lên
        if r < 3: moves.append(4)  # Trượt xuống
        if c > 0: moves.append(-1) # Trượt trái
        if c < 3: moves.append(1)  # Trượt phải
        
        for m in moves:
            new_idx = idx + m
            new_state = list(state)
            # Hoán đổi ô trống với ô bên cạnh
            new_state[idx], new_state[new_idx] = new_state[new_idx], new_state[idx]
            neighbors.append(tuple(new_state))
            
        return neighbors

    def get_cost(self):
        return 1 # Mỗi lần trượt tốn 1 bước

# ==========================================
# 2. CÁC THUẬT TOÁN TÌM KIẾM 
# ==========================================

class GreedySearch(BaseAlgorithm):
    def run(self, environment, start, target=GOAL_STATE):
        history = []
        count = 0 # Tie-breaker cho heapq nếu Heuristic bằng nhau
        pq = [(heuristic(start), count, [start])]
        explored = set()

        while pq:
            h_cost, _, path = heapq.heappop(pq)
            node = path[-1]
            explored.add(node)

            history.append(State(
                frontier=[p[-1] for _, _, p in pq], explored_size=len(explored), current_path=path,
                hud_metrics={"Thuật toán": "Greedy Search", "Frontier Size": str(len(pq)), "h(n)": str(h_cost), "Nodes Explored": str(len(explored))},
                action_description=f"Duyệt trạng thái với h(n) = {h_cost}."
            ))

            if node == target:
                history.append(State(
                    frontier=[p[-1] for _, _, p in pq], explored_size=len(explored), current_path=path,
                    hud_metrics={"Thuật toán": "Greedy Search", "Frontier Size": str(len(pq)), "h(n)": "0", "Nodes Explored": str(len(explored))},
                    action_description="Đã đạt tới Goal!"
                ))
                break

            for neighbor in environment.get_neighbors(node):
                if neighbor not in explored and neighbor not in [p[-1] for _, _, p in pq]:
                    count += 1
                    new_path = list(path)
                    new_path.append(neighbor)
                    heapq.heappush(pq, (heuristic(neighbor), count, new_path))
        return history

class AStar(BaseAlgorithm):
    def run(self, environment, start, target=GOAL_STATE):
        history = []
        count = 0
        pq = [(heuristic(start), count, 0, [start])]
        g_costs = {start: 0}
        explored = set()

        while pq:
            f_cost, _, g_cost, path = heapq.heappop(pq)
            node = path[-1]

            if node in explored and g_cost > g_costs.get(node, float('inf')):
                continue

            explored.add(node)
            h_cost = f_cost - g_cost

            history.append(State(
                frontier=[p[-1] for _, _, _, p in pq], explored_size=len(explored), current_path=path,
                hud_metrics={
                    "Thuật toán": "A* Search", "Frontier Size": str(len(pq)),
                    "f(n)": str(f_cost), "g(n)": str(g_cost), "h(n)": str(h_cost), 
                    "Nodes Explored": str(len(explored))
                },
                action_description=f"Duyệt trạng thái (f={f_cost}, g={g_cost}, h={h_cost})."
            ))

            if node == target:
                history.append(State(
                    frontier=[p[-1] for _, _, _, p in pq], explored_size=len(explored), current_path=path,
                    hud_metrics={"Thuật toán": "A* Search", "Frontier Size": str(len(pq)), "f(n)": str(f_cost), "Nodes Explored": str(len(explored))},
                    action_description="Đã đạt tới Goal bằng đường đi tối ưu!"
                ))
                break

            for neighbor in environment.get_neighbors(node):
                new_g_cost = g_cost + environment.get_cost()
                if new_g_cost < g_costs.get(neighbor, float('inf')):
                    g_costs[neighbor] = new_g_cost
                    new_f_cost = new_g_cost + heuristic(neighbor)
                    count += 1
                    new_path = list(path)
                    new_path.append(neighbor)
                    heapq.heappush(pq, (new_f_cost, count, new_g_cost, new_path))
        return history

class IDAStar(BaseAlgorithm):
    def run(self, environment, start, target=GOAL_STATE):
        history = []
        threshold = heuristic(start)
        explored_total_count = 0

        while True:
            stack = [([start], 0)]
            min_exceeded_f = float('inf')
            found = False
            visited_g = {}

            while stack:
                path, g_cost = stack.pop()
                node = path[-1]
                f_cost = g_cost + heuristic(node)

                if f_cost > threshold:
                    min_exceeded_f = min(min_exceeded_f, f_cost)
                    continue

                if node in visited_g and visited_g[node] <= g_cost:
                    continue
                visited_g[node] = g_cost
                explored_total_count += 1

                history.append(State(
                    frontier=[p[-1] for p, _ in stack], explored_size=explored_total_count, current_path=path,
                    hud_metrics={
                        "Thuật toán": "IDA* Search", "Stack Size": str(len(stack)),
                        "Threshold f(n)": str(threshold), "Current f(n)": str(f_cost), 
                        "Total Nodes Explored": str(explored_total_count)
                    },
                    action_description=f"Duyệt trạng thái (f={f_cost}, Ngưỡng={threshold})."
                ))

                if node == target:
                    history.append(State(
                        frontier=[p[-1] for p, _ in stack], explored_size=explored_total_count, current_path=path,
                        hud_metrics={"Thuật toán": "IDA* Search", "Frontier Size": str(len(stack)), "Threshold": str(threshold), "Nodes Explored": str(explored_total_count)},
                        action_description=f"Đã đạt tới Goal (ngưỡng f={threshold})!"
                    ))
                    found = True
                    break

                for neighbor in environment.get_neighbors(node):
                    if neighbor not in path:
                        new_path = list(path)
                        new_path.append(neighbor)
                        stack.append((new_path, g_cost + environment.get_cost()))

            if found or min_exceeded_f == float('inf'):
                break
            threshold = min_exceeded_f
        return history

ALGOS_PATHFINDING = {
    "Greedy Search": GreedySearch,
    "A* Search": AStar,
    "IDA* Search": IDAStar
}

# ==========================================
# 3. GIAO DIỆN UI 
# ==========================================
BG, PANEL, CARD, TEXT, SUB, ACCENT, BTN, BTN_H, BTN_SEL = "#1a1a2e", "#16213e", "#0f3460", "#e6e6e6", "#8d99ae", "#00d4ff", "#3a86ff", "#2a75e6", "#e63946"
CELL, CELL_E, GREEN, RED, YELLOW, WALL = "#3d5a80", "#0e0e1a", "#06d6a0", "#ef476f", "#ffd166", "#4a4e69"

class PuzzleUI:
    def __init__(self, parent, environment, start_pos, algo_name="A* Search"):
        self.parent = parent
        if parent: parent.withdraw()
        
        self.win = tk.Toplevel(parent) if parent else tk.Tk()
        self.win.title("Nhóm 3: 15-Puzzle Solver (Heuristic)")
        self.win.geometry("1400x780")
        self.win.configure(bg=BG)
        self.win.minsize(1200, 700)
        self.win.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.env = environment
        self.start = start_pos
        self.target = GOAL_STATE
        
        self.algo_name = algo_name
        self.history = []
        self.step_idx = -1
        self.algo_btns = {}
        self.auto_playing = False
        
        self._build_top()
        self._build_middle()
        self._build_bottom()
        
        if algo_name: self.select_algo(algo_name)
        self.draw_initial()

    def on_close(self):
        self.win.destroy()
        if self.parent: self.parent.deiconify()

    def _build_top(self):
        f = tk.Frame(self.win, bg=PANEL, pady=8); f.pack(fill=tk.X, padx=0)
        tk.Label(f, text="NHÓM 3: 15-PUZZLE SOLVER", font=("Segoe UI", 14, "bold"), bg=PANEL, fg=ACCENT).pack(side=tk.LEFT, padx=20)
        
        for name in reversed(list(ALGOS_PATHFINDING.keys())):
            b = tk.Button(f, text=name, font=("Segoe UI", 10), bg="#444455", fg=TEXT, relief="flat", padx=12, pady=4, cursor="hand2", command=lambda n=name: self.select_algo(n))
            b.pack(side=tk.RIGHT, padx=4)
            self.algo_btns[name] = b

    def select_algo(self, name):
        self.algo_name = name
        for n, b in self.algo_btns.items():
            b.config(bg=BTN_SEL if n == name else "#444455")
        self.draw_initial()

    def _build_middle(self):
        mf = tk.Frame(self.win, bg=BG)
        mf.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # --- KHUNG BÊN TRÁI: MÔ PHỎNG MÔI TRƯỜNG ---
        cf = tk.Frame(mf, bg=CARD, highlightbackground="#2a3a5c", highlightthickness=1)
        cf.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        tk.Label(cf, text="TRẠNG THÁI PUZZLE", font=("Segoe UI", 11, "bold"), bg=CARD, fg=ACCENT).pack(pady=(10, 5))
        
        self.cv_grid = tk.Canvas(cf, bg=CELL_E, highlightthickness=0)
        self.cv_grid.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # --- KHUNG BÊN PHẢI: METRICS & LOG ---
        rf = tk.Frame(mf, bg=BG)
        rf.pack(side=tk.LEFT, fill=tk.BOTH, padx=(5, 0))
        rf.config(width=400)
        rf.pack_propagate(False)
        
        # 1. HUD Metrics
        vf = tk.Frame(rf, bg=CARD, highlightbackground="#2a3a5c", highlightthickness=1)
        vf.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        tk.Label(vf, text="HUD METRICS", font=("Segoe UI", 10, "bold"), bg=CARD, fg=ACCENT).pack(pady=(8, 5))
        
        self.metrics_frame = tk.Frame(vf, bg=CARD)
        self.metrics_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        
        # 2. Khung Log
        ef = tk.Frame(rf, bg=CARD, highlightbackground="#2a3a5c", highlightthickness=1, height=280)
        ef.pack(fill=tk.X, pady=(5, 0))
        ef.pack_propagate(False)
        tk.Label(ef, text="LỊCH SỬ LOG & FRONTIER", font=("Segoe UI", 10, "bold"), bg=CARD, fg=ACCENT).pack(pady=(8, 2))
        
        scroll = tk.Scrollbar(ef)
        scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=(0, 5))
        
        self.txt_exp = tk.Text(ef, bg=CARD, fg=YELLOW, font=("Consolas", 10), wrap=tk.WORD, 
                               relief="flat", padx=10, pady=5, insertbackground=TEXT, state=tk.DISABLED,
                               yscrollcommand=scroll.set)
        self.txt_exp.pack(fill=tk.BOTH, expand=True, padx=(5, 0), pady=(0, 5))
        scroll.config(command=self.txt_exp.yview)

    def _build_bottom(self):
        f = tk.Frame(self.win, bg=PANEL, pady=10); f.pack(fill=tk.X)
        tk.Button(f, text="🎲 Xáo trộn (Shuffle)", font=("Segoe UI", 11, "bold"), bg="#ff9f1c", fg="#000", 
                  relief="flat", padx=15, pady=8, cursor="hand2", command=self.shuffle_map).pack(side=tk.LEFT, padx=10)
        
        btns = [
            ("▶ Giải ngay", self.do_solve, GREEN), 
            ("◀◀ Bước trước", self.do_prev, BTN), 
            ("Bước sau ▶▶", self.do_next, BTN),
            ("⏭ Kết quả", self.do_skip_to_end, RED)
        ]
        
        for txt, cmd, clr in btns:
            tk.Button(f, text=txt, font=("Segoe UI", 11, "bold"), bg=clr, fg=TEXT if clr not in [GREEN, YELLOW] else "#000", relief="flat", padx=18, pady=8, cursor="hand2", command=cmd).pack(side=tk.LEFT, padx=5)
        
        self.btn_auto = tk.Button(f, text="Tự chạy ⏯", font=("Segoe UI", 11, "bold"), bg="#5a189a", fg=TEXT, relief="flat", padx=18, pady=8, cursor="hand2", command=self.toggle_auto_play)
        self.btn_auto.pack(side=tk.LEFT, padx=10)
        self.lbl_step = tk.Label(f, text="Chưa bắt đầu", font=("Segoe UI", 12, "bold"), bg=PANEL, fg=YELLOW)
        self.lbl_step.pack(side=tk.RIGHT, padx=20)

    def _draw_grid_state(self, state=None):
        self.cv_grid.delete("all")
        cv_w, cv_h = self.cv_grid.winfo_width(), self.cv_grid.winfo_height()
        if cv_w <= 1 or cv_h <= 1:
            self.win.after(100, lambda: self._draw_grid_state(state))
            return

        # Vẽ lưới 4x4 ở giữa
        cs = min(cv_w // 4, cv_h // 4) - 5
        ox = (cv_w - cs * 4) // 2
        oy = (cv_h - cs * 4) // 2

        current_puzzle = state.current_path[-1] if state else self.start

        for i, val in enumerate(current_puzzle):
            r, c = divmod(i, 4)
            x1, y1 = ox + c * cs, oy + r * cs
            x2, y2 = x1 + cs - 2, y1 + cs - 2 # Trừ 2 để tạo khe hở (gap) giữa các gạch
            
            if val == 0:
                self.cv_grid.create_rectangle(x1, y1, x2, y2, fill=CELL_E, outline=CELL_E)
            else:
                # Gạch nằm đúng vị trí đích thì tô viền xanh lá mạ
                tar_r, tar_c = divmod(val - 1, 4)
                border_col = GREEN if (r == tar_r and c == tar_c) else "#1a1a2e"
                
                self.cv_grid.create_rectangle(x1, y1, x2, y2, fill=CELL, outline=border_col, width=3)
                self.cv_grid.create_text(x1+cs/2, y1+cs/2, text=str(val), fill=TEXT, font=("Segoe UI", cs//3, "bold"))

    def draw_initial(self):
        self.history = []
        self.step_idx = -1
        self._draw_grid_state(None)
        self._update_metrics({})
        self.print_system_msg(f"Hệ thống sẵn sàng.\nThuật toán: {self.algo_name}\nNhấn 'Giải ngay' để tìm đường.")
        self.lbl_step.config(text="Chưa bắt đầu")

    def show_step(self, idx):
        if idx < 0 or idx >= len(self.history): return
        self.step_idx = idx
        state = self.history[idx]
        self.lbl_step.config(text=f"Bước {idx+1}/{len(self.history)}")
        self._draw_grid_state(state)
        self._update_metrics(state.hud_metrics)
        self.print_logs_up_to_step(idx)

    def print_logs_up_to_step(self, current_idx):
        self.txt_exp.config(state=tk.NORMAL)
        self.txt_exp.delete("1.0", tk.END)
        
        log_text = ""
        # Rút gọn log chỉ in 10 bước gần nhất để tránh giật lag khi đường đi quá dài
        start_print_idx = max(0, current_idx - 10)
        if start_print_idx > 0:
            log_text += f"... (Đã ẩn {start_print_idx} bước trước đó) ...\n\n"
            
        for i in range(start_print_idx, current_idx + 1):
            state = self.history[i]
            log_text += f"[B.{i+1}] {state.action_description}\n"
            
            if state.frontier:
                # Chỉ in 3 trạng thái đầu tiên trong frontier cho đỡ rối rắm
                frontier_str = "\n      ".join([str(p) for p in state.frontier[:3]])
                if len(state.frontier) > 3:
                    frontier_str += f"\n      ... (+{len(state.frontier) - 3} node khác)"
                log_text += f"   >> Frontier:\n      {frontier_str}\n"
            else:
                log_text += f"   >> Frontier: Trống\n"
            log_text += "-" * 40 + "\n"

        self.txt_exp.insert(tk.END, log_text)
        self.txt_exp.see(tk.END)
        self.txt_exp.config(state=tk.DISABLED)

    def print_system_msg(self, text):
        self.txt_exp.config(state=tk.NORMAL)
        self.txt_exp.delete("1.0", tk.END)
        self.txt_exp.insert(tk.END, text)
        self.txt_exp.config(state=tk.DISABLED)

    def _update_metrics(self, metrics_dict):
        for w in self.metrics_frame.winfo_children(): w.destroy()
        for k, v in metrics_dict.items():
            row = tk.Frame(self.metrics_frame, bg=CARD); row.pack(fill=tk.X, pady=4)
            tk.Label(row, text=k + ":", font=("Segoe UI", 10), bg=CARD, fg=SUB).pack(side=tk.LEFT)
            tk.Label(row, text=v, font=("Segoe UI", 11, "bold"), bg=CARD, fg=TEXT).pack(side=tk.RIGHT)

    def do_solve(self):
        self.auto_playing = False
        self.btn_auto.config(text="Tự chạy ⏯", bg="#5a189a")
        algo_instance = ALGOS_PATHFINDING[self.algo_name]()
        self.history = algo_instance.run(self.env, self.start, self.target)
        if self.history: self.show_step(0)

    def do_skip_to_end(self):
        if not self.history:
            algo_instance = ALGOS_PATHFINDING[self.algo_name]()
            self.history = algo_instance.run(self.env, self.start, self.target)
        
        if self.history:
            self.auto_playing = False
            self.btn_auto.config(text="Tự chạy ⏯", bg="#5a189a")
            self.show_step(len(self.history) - 1)

    def shuffle_map(self):
        # Đi ngược ngẫu nhiên 25 bước từ trạng thái đích để tạo puzzle (Đảm bảo có thể giải ra nhanh)
        curr = GOAL_STATE
        prev = None
        for _ in range(25):
            neighbors = self.env.get_neighbors(curr)
            if prev in neighbors and len(neighbors) > 1:
                neighbors.remove(prev) # Hạn chế đi ngược lại ngay bước trước đó
            prev = curr
            curr = random.choice(neighbors)
            
        self.start = curr
        self.draw_initial()
        self.print_system_msg("Đã xáo trộn ngẫu nhiên thành công!")

    def do_prev(self):
        if self.step_idx > 0: self.show_step(self.step_idx - 1)

    def do_next(self):
        if self.step_idx < len(self.history) - 1: self.show_step(self.step_idx + 1)

    def toggle_auto_play(self):
        if not self.history: return
        self.auto_playing = not self.auto_playing
        if self.auto_playing:
            self.btn_auto.config(text="Dừng ⏸", bg=RED)
            self.run_auto_step()
        else: self.btn_auto.config(text="Tự chạy ⏯", bg="#5a189a")

    def run_auto_step(self):
        if self.auto_playing and self.step_idx < len(self.history) - 1:
            self.do_next()
            self.win.after(100, self.run_auto_step) # 100ms chạy một bước
        elif self.step_idx >= len(self.history) - 1:
            self.auto_playing = False
            self.btn_auto.config(text="Tự chạy ⏯", bg="#5a189a")

def open_ui(parent, algo_name):
    # Khởi tạo trạng thái ngẫu nhiên hợp lệ (Đi lùi từ Goal 25 bước)
    env = PuzzleEnvironment()
    curr = GOAL_STATE
    prev = None
    for _ in range(25):
        neighbors = env.get_neighbors(curr)
        if prev in neighbors and len(neighbors) > 1:
            neighbors.remove(prev)
        prev = curr
        curr = random.choice(neighbors)
        
    start_pos = curr
    app = PuzzleUI(parent, env, start_pos, algo_name)

if __name__ == "__main__":
    open_ui(None, "A* Search")
    tk.mainloop()
