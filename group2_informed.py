import tkinter as tk
from tkinter import messagebox

# ===== THEME CHUẨN CỦA NHÓM =====
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

# Danh sách thuật toán để map với UI
# Giả sử bạn đã import các class thuật toán: GreedySearch, AStar, IDAStar
ALGOS_PATHFINDING = {
    "Greedy Search": GreedySearch,
    "A* Search": AStar,
    "IDA* Search": IDAStar
}

class PathfindingUI:
    def __init__(self, parent, environment, start_pos, target_pos, algo_name="A* Search"):
        """
        Giao diện mô phỏng thuật toán tìm kiếm đường đi.
        :param environment: Đối tượng môi trường (bản đồ, vật cản...)
        :param start_pos: Tuple tọa độ ban đầu (Police)
        :param target_pos: Tuple tọa độ đích (Thief)
        """
        self.parent = parent
        if parent: parent.withdraw()
        
        self.win = tk.Toplevel(parent) if parent else tk.Tk()
        self.win.title("Nhóm 3: Tìm kiếm có thông tin - Truy bắt Thief")
        self.win.geometry("1350x780")
        self.win.configure(bg=BG)
        self.win.minsize(1200, 700)
        self.win.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Dữ liệu bài toán
        self.env = environment
        self.start = start_pos
        self.target = target_pos
        
        # State quản lý UI
        self.algo_name = algo_name
        self.history = []
        self.step_idx = -1
        self.algo_btns = {}
        self.auto_playing = False
        
        # Tọa độ grid logic (Giả sử bản đồ kích thước 20x20 để vẽ grid)
        self.grid_rows = 20
        self.grid_cols = 20
        
        # Xây dựng giao diện
        self._build_top()
        self._build_middle()
        self._build_bottom()
        
        if algo_name:
            self.select_algo(algo_name)
            
        self.draw_initial()

    def on_close(self):
        self.win.destroy()
        if self.parent: self.parent.deiconify()

    def _build_top(self):
        f = tk.Frame(self.win, bg=PANEL, pady=8)
        f.pack(fill=tk.X, padx=0)
        tk.Label(f, text="NHÓM 3: TÌM KIẾM CÓ THÔNG TIN (HEURISTIC)", font=("Segoe UI", 14, "bold"), bg=PANEL, fg=ACCENT).pack(side=tk.LEFT, padx=20)
        
        bb = tk.Button(f, text="◀ Quay lại", font=("Segoe UI", 10, "bold"), bg=RED, fg=TEXT, relief="flat", padx=12, pady=4, cursor="hand2", command=self.on_close)
        bb.pack(side=tk.RIGHT, padx=15)
        
        for name in reversed(list(ALGOS_PATHFINDING.keys())):
            b = tk.Button(f, text=name, font=("Segoe UI", 10), bg="#444455", fg=TEXT, relief="flat", padx=12, pady=4, cursor="hand2",
                          command=lambda n=name: self.select_algo(n))
            b.pack(side=tk.RIGHT, padx=4)
            self.algo_btns[name] = b

    def select_algo(self, name):
        self.algo_name = name
        for n, b in self.algo_btns.items():
            if n == name: b.config(bg=BTN_SEL)
            else: b.config(bg="#444455")

    def _build_middle(self):
        mf = tk.Frame(self.win, bg=BG)
        mf.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Cột Trái: Lưới (Grid) mô phỏng môi trường
        cf = tk.Frame(mf, bg=CARD, highlightbackground="#2a3a5c", highlightthickness=1)
        cf.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        tk.Label(cf, text="MÔ PHỎNG MÔI TRƯỜNG", font=("Segoe UI", 11, "bold"), bg=CARD, fg=ACCENT).pack(pady=(10, 5))
        
        self.cv_grid = tk.Canvas(cf, bg=CELL_E, highlightthickness=0)
        self.cv_grid.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Cột Phải: HUD Metrics & Action Description
        rf = tk.Frame(mf, bg=BG)
        rf.pack(side=tk.LEFT, fill=tk.BOTH, padx=(5, 0))
        rf.config(width=350)
        rf.pack_propagate(False)
        
        # Bảng HUD Metrics
        vf = tk.Frame(rf, bg=CARD, highlightbackground="#2a3a5c", highlightthickness=1)
        vf.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        tk.Label(vf, text="HUD METRICS", font=("Segoe UI", 10, "bold"), bg=CARD, fg=ACCENT).pack(pady=(8, 5))
        
        self.metrics_frame = tk.Frame(vf, bg=CARD)
        self.metrics_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        self.lbl_metrics = []
        
        # Giải thích thao tác
        ef = tk.Frame(rf, bg=CARD, highlightbackground="#2a3a5c", highlightthickness=1, height=150)
        ef.pack(fill=tk.X, pady=(5, 0))
        ef.pack_propagate(False)
        tk.Label(ef, text="HÀNH ĐỘNG CỦA POLICE", font=("Segoe UI", 10, "bold"), bg=CARD, fg=ACCENT).pack(pady=(8, 2))
        self.txt_exp = tk.Text(ef, bg=CARD, fg=YELLOW, font=("Segoe UI", 11, "bold"), wrap=tk.WORD, relief="flat", padx=10, pady=5, insertbackground=TEXT, state=tk.DISABLED)
        self.txt_exp.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))

    def _build_bottom(self):
        f = tk.Frame(self.win, bg=PANEL, pady=10)
        f.pack(fill=tk.X)
        
        btns = [
            ("▶ Giải ngay", self.do_solve, GREEN),
            ("◀◀ Bước trước", self.do_prev, BTN),
            ("Bước sau ▶▶", self.do_next, BTN),
        ]
        
        for txt, cmd, clr in btns:
            tk.Button(f, text=txt, font=("Segoe UI", 11, "bold"), bg=clr, fg=TEXT if clr != GREEN else "#000", relief="flat", padx=18, pady=8, cursor="hand2", command=cmd).pack(side=tk.LEFT, padx=10)
            
        self.btn_auto = tk.Button(f, text="Tự chạy ⏯", font=("Segoe UI", 11, "bold"), bg="#5a189a", fg=TEXT, relief="flat", padx=18, pady=8, cursor="hand2", command=self.toggle_auto_play)
        self.btn_auto.pack(side=tk.LEFT, padx=10)
        
        self.lbl_step = tk.Label(f, text="Chưa bắt đầu", font=("Segoe UI", 12, "bold"), bg=PANEL, fg=YELLOW)
        self.lbl_step.pack(side=tk.RIGHT, padx=20)

    # ===== HIỂN THỊ TRẠNG THÁI (DRAWING) =====
    def _draw_grid_state(self, state=None):
        self.cv_grid.delete("all")
        cv_w = self.cv_grid.winfo_width()
        cv_h = self.cv_grid.winfo_height()
        
        # Chỉ vẽ khi Canvas đã load (tránh size = 1)
        if cv_w <= 1 or cv_h <= 1:
            self.win.after(100, lambda: self._draw_grid_state(state))
            return

        cs = min(cv_w // self.grid_cols, cv_h // self.grid_rows)
        ox = (cv_w - cs * self.grid_cols) // 2
        oy = (cv_h - cs * self.grid_rows) // 2

        # Lấy data từ state (nếu có)
        explored = state.explored if state else set()
        frontier = state.frontier if state else []
        path = state.current_path if state else []

        # Vẽ lưới
        for r in range(self.grid_rows):
            for c in range(self.grid_cols):
                x1, y1 = ox + c * cs, oy + r * cs
                x2, y2 = x1 + cs, y1 + cs
                
                node = (r, c)
                color = CELL_E
                
                if node in explored:
                    color = CELL       # Đã duyệt
                elif node in frontier:
                    color = "#2a9d8f"  # Đang chờ duyệt (Màu teal nhạt)
                
                # Vẽ ô
                self.cv_grid.create_rectangle(x1, y1, x2, y2, fill=color, outline="#16213e")

        # Vẽ đường đi hiện tại (Path)
        if len(path) > 1:
            points = [(ox + p[1] * cs + cs/2, oy + p[0] * cs + cs/2) for p in path]
            self.cv_grid.create_line(*points, fill=GREEN, width=3, dash=(4, 2))

        # Vẽ Start (Police) và Target (Thief)
        for t_pos, t_color, t_text in [(self.start, BTN_SEL, "P"), (self.target, "#ffb703", "T")]:
            if t_pos:
                r, c = t_pos
                x1, y1 = ox + c * cs, oy + r * cs
                self.cv_grid.create_oval(x1+4, y1+4, x1+cs-4, y1+cs-4, fill=t_color, outline=TEXT)
                self.cv_grid.create_text(x1+cs/2, y1+cs/2, text=t_text, fill=TEXT, font=("Segoe UI", max(8, cs//2), "bold"))

    def draw_initial(self):
        self.history = []
        self.step_idx = -1
        self._draw_grid_state(None)
        self._update_metrics({})
        self.set_exp(f"Hệ thống sẵn sàng.\nThuật toán: {self.algo_name}\nNhấn 'Giải ngay' để Police bắt đầu truy tìm Thief.")
        self.lbl_step.config(text="Chưa bắt đầu")

    def show_step(self, idx):
        if idx < 0 or idx >= len(self.history): return
        self.step_idx = idx
        state = self.history[idx]
        
        self.lbl_step.config(text=f"Bước {idx+1}/{len(self.history)}")
        
        # Cập nhật lưới
        self._draw_grid_state(state)
        
        # Cập nhật HUD Metrics
        self._update_metrics(state.hud_metrics)
        
        # Cập nhật hành động
        self.set_exp(state.action_description)

    def _update_metrics(self, metrics_dict):
        # Clear bảng HUD cũ
        for w in self.metrics_frame.winfo_children(): w.destroy()
        
        for k, v in metrics_dict.items():
            row = tk.Frame(self.metrics_frame, bg=CARD)
            row.pack(fill=tk.X, pady=4)
            tk.Label(row, text=k + ":", font=("Segoe UI", 10), bg=CARD, fg=SUB).pack(side=tk.LEFT)
            tk.Label(row, text=v, font=("Segoe UI", 11, "bold"), bg=CARD, fg=TEXT).pack(side=tk.RIGHT)

    def set_exp(self, text):
        self.txt_exp.config(state=tk.NORMAL)
        self.txt_exp.delete("1.0", tk.END)
        self.txt_exp.insert(tk.END, text)
        self.txt_exp.config(state=tk.DISABLED)

    # ===== THAO TÁC NÚT BẤM (ACTIONS) =====
    def do_solve(self):
        self.auto_playing = False
        self.btn_auto.config(text="Tự chạy ⏯", bg="#5a189a")
        
        if not self.algo_name:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn thuật toán!", parent=self.win)
            return
            
        AlgoClass = ALGOS_PATHFINDING[self.algo_name]
        algo_instance = AlgoClass()
        
        # Chạy thuật toán và lấy history
        self.history = algo_instance.run(self.env, self.start, self.target)
        
        if self.history:
            self.show_step(0)
        else:
            self.set_exp("Không tìm thấy đường đi nào!")

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
        else:
            self.btn_auto.config(text="Tự chạy ⏯", bg="#5a189a")

    def run_auto_step(self):
        if self.auto_playing and self.step_idx < len(self.history) - 1:
            self.do_next()
            self.win.after(200, self.run_auto_step) # Chỉnh tốc độ mô phỏng ở đây (200ms)
        elif self.step_idx >= len(self.history) - 1:
            self.auto_playing = False
            self.btn_auto.config(text="Tự chạy ⏯", bg="#5a189a")

# Để gọi giao diện này từ app chính của bạn:
def open_pathfinding_ui(parent, environment, start_pos, target_pos, algo_name):
    PathfindingUI(parent, environment, start_pos, target_pos, algo_name)
