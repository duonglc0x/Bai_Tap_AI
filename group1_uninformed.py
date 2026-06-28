import tkinter as tk
from tkinter import messagebox, simpledialog
from collections import deque
import heapq
import copy
import threading

# ============================================================
#  BẢNG MÀU (Dark Theme - phong cách giống hình mẫu)
# ============================================================
BG_MAIN = "#1a1a2e"          # Nền chính (xanh đen đậm)
BG_PANEL = "#16213e"         # Nền panel
BG_CELL = "#0f3460"          # Ô puzzle
BG_EMPTY = "#1a1a2e"         # Ô trống
BG_HEADER = "#0f0f23"        # Nền header
BORDER_COLOR = "#2a2a4a"     # Viền

COLOR_TAB_ACTIVE = "#e94560"      # Tab đang chọn (đỏ hồng)
COLOR_TAB_INACTIVE = "#16213e"    # Tab chưa chọn
COLOR_TAB_HOVER = "#1a3a5c"      # Tab hover

COLOR_HIGHLIGHT = "#00e676"       # Viền highlight node con được chọn (xanh lá)
COLOR_HIGHLIGHT_BG = "#0a2e1a"    # Nền node con được highlight

COLOR_BTN_GREEN = "#00c853"       # Nút Giải
COLOR_BTN_BLUE = "#2979ff"        # Nút Bước
COLOR_BTN_TEAL = "#00bcd4"        # Nút Nhập tay
COLOR_BTN_RED = "#e94560"         # Nút Quay lại
COLOR_BTN_ORANGE = "#ff9800"      # Nút Auto Play
COLOR_BTN_HOVER_GREEN = "#00a844"
COLOR_BTN_HOVER_BLUE = "#2162cc"
COLOR_BTN_HOVER_TEAL = "#0097a7"
COLOR_BTN_HOVER_RED = "#c73550"

TEXT_WHITE = "#ffffff"
TEXT_CYAN = "#00e5ff"
TEXT_PINK = "#ff4081"
TEXT_GRAY = "#8899aa"
TEXT_YELLOW = "#ffd740"

FONT_TITLE = ("Segoe UI", 14, "bold")
FONT_SECTION = ("Segoe UI", 11, "bold")
FONT_CELL = ("Segoe UI", 13, "bold")
FONT_CELL_SM = ("Segoe UI", 8, "bold")
FONT_CELL_XS = ("Segoe UI", 6)
FONT_BTN = ("Segoe UI", 10, "bold")
FONT_INFO = ("Segoe UI", 9)
FONT_EXPLAIN = ("Segoe UI", 9)

# ============================================================
#  TRẠNG THÁI GOAL & MẶC ĐỊNH
# ============================================================
GOAL_STATE = [
    [1,  2,  3,  4],
    [5,  6,  7,  8],
    [9,  10, 11, 12],
    [13, 14, 15, 0]
]

DEFAULT_STATE = [
    [1,  2,  3,  4],
    [5,  6,  0,  8],
    [9,  10, 7,  11],
    [13, 14, 15, 12]
]

# ============================================================
#  TIỆN ÍCH PUZZLE
# ============================================================
def find_blank(state):
    """Tìm vị trí ô trống (0)."""
    for i in range(4):
        for j in range(4):
            if state[i][j] == 0:
                return i, j
    return -1, -1

def get_neighbors(state):
    """Trả về danh sách (direction_label, new_state) cho các bước di chuyển hợp lệ."""
    bi, bj = find_blank(state)
    moves = []
    # Mũi tên chỉ hướng di chuyển của ô (ngược với hướng di chuyển ô trống)
    # (-1,0) = blank đi lên → ô ở trên đi XUỐNG (↓)
    # (1,0) = blank đi xuống → ô ở dưới đi LÊN (↑)
    # (0,-1) = blank đi trái → ô ở trái đi PHẢI (→)
    # (0,1) = blank đi phải → ô ở phải đi TRÁI (←)
    directions = [(-1, 0, "↓"), (1, 0, "↑"), (0, -1, "→"), (0, 1, "←")]

    for di, dj, arrow in directions:
        ni, nj = bi + di, bj + dj
        if 0 <= ni < 4 and 0 <= nj < 4:
            new_state = copy.deepcopy(state)
            new_state[bi][bj], new_state[ni][nj] = new_state[ni][nj], new_state[bi][bj]
            moved_val = state[ni][nj]
            label = f"Trượt ô {moved_val} {arrow}"
            moves.append((label, new_state))
    return moves

def state_to_tuple(state):
    """Chuyển state thành tuple để hash."""
    return tuple(state[i][j] for i in range(4) for j in range(4))

def is_solvable(state):
    """Kiểm tra puzzle có giải được không (dựa trên số inversions)."""
    flat = [state[i][j] for i in range(4) for j in range(4)]
    inversions = 0
    for i in range(16):
        for j in range(i + 1, 16):
            if flat[i] != 0 and flat[j] != 0 and flat[i] > flat[j]:
                inversions += 1
    blank_row = find_blank(state)[0]
    blank_from_bottom = 4 - blank_row
    if blank_from_bottom % 2 == 0:
        return inversions % 2 == 1
    else:
        return inversions % 2 == 0

# ============================================================
#  TIỆN ÍCH ĐƯỜNG ĐI LỜI GIẢI
# ============================================================
def tuple_to_state(t):
    """Chuyển tuple trạng thái về dạng list 2D."""
    return [list(t[i*4:(i+1)*4]) for i in range(4)]

def reconstruct_path(parent, start_tuple, goal_tuple):
    """Truy vết đường đi từ trạng thái đầu đến đích bằng parent pointers."""
    path_tuples = [goal_tuple]
    current = goal_tuple
    while current != start_tuple:
        parent_tuple, _ = parent[current]
        path_tuples.append(parent_tuple)
        current = parent_tuple
    path_tuples.reverse()
    return [tuple_to_state(t) for t in path_tuples]

def create_path_steps(path, algo_name, nodes_explored, visited_count):
    """Tạo danh sách SolveStep từ đường đi lời giải (mỗi bước = 1 di chuyển)."""
    steps = []
    total_moves = len(path) - 1

    for i, state in enumerate(path):
        children = get_neighbors(state)
        chosen_idx = -1

        # Tìm node con ứng với bước tiếp theo trong đường đi
        if i < total_moves:
            next_tuple = state_to_tuple(path[i + 1])
            for j, (_, child) in enumerate(children):
                if state_to_tuple(child) == next_tuple:
                    chosen_idx = j
                    break

        # Tìm nhãn bước di chuyển đã thực hiện
        move_label = ""
        if i > 0:
            prev_neighbors = get_neighbors(path[i - 1])
            current_tuple = state_to_tuple(state)
            for label, child in prev_neighbors:
                if state_to_tuple(child) == current_tuple:
                    move_label = label
                    break

        if i == 0:
            expl = (f"{algo_name}: Trạng thái ban đầu.\n"
                    f"Tìm đường đi đến trạng thái đích.\n"
                    f"Số node đã duyệt: {nodes_explored}\n"
                    f"Tổng bước đi: {total_moves}")
        elif i == total_moves:
            expl = (f"ĐÃ TÌM THẤY ĐÍCH!\n"
                    f"Bước cuối: {move_label}\n"
                    f"Tổng bước đi: {total_moves}\n"
                    f"Số node đã duyệt: {nodes_explored}")
        else:
            expl = (f"{algo_name}: Bước {i}/{total_moves}.\n"
                    f"Thực hiện: {move_label}\n"
                    f"Số node đã duyệt: {nodes_explored}\n"
                    f"Còn {total_moves - i} bước nữa.")

        steps.append(SolveStep(state, children, chosen_idx,
                               0, visited_count, expl, depth=i, cost=i))

    return steps

# ============================================================
#  CẤU TRÚC BƯỚC GIẢI (cho visualization)
# ============================================================
class SolveStep:
    """Mỗi bước trong quá trình giải."""
    def __init__(self, current_state, children, chosen_idx, frontier_size, visited_count, explanation, depth=0, cost=0):
        self.current_state = current_state      # Trạng thái đang xét
        self.children = children                # Danh sách (label, state)
        self.chosen_idx = chosen_idx            # Index của node con được chọn (-1 nếu không chọn)
        self.frontier_size = frontier_size      # Kích thước frontier
        self.visited_count = visited_count      # Số node đã thăm
        self.explanation = explanation           # Giải thích bước này
        self.depth = depth                      # Độ sâu
        self.cost = cost                        # Chi phí (cho UCS)

# ============================================================
#  THUẬT TOÁN BFS - Trả về đường đi lời giải
# ============================================================
def solve_bfs(initial_state, max_nodes=50000):
    """BFS: Tìm kiếm theo chiều rộng - trả về đường đi từng bước."""
    goal_tuple = state_to_tuple(GOAL_STATE)
    init_tuple = state_to_tuple(initial_state)

    if init_tuple == goal_tuple:
        return [SolveStep(initial_state, [], -1, 0, 1, "Trạng thái ban đầu đã là trạng thái đích!")]

    queue = deque()
    visited = set()
    parent = {}  # child_tuple -> (parent_tuple, move_label)

    visited.add(init_tuple)
    queue.append((initial_state, 0))
    nodes_explored = 0

    while queue and len(visited) < max_nodes:
        current, depth = queue.popleft()
        nodes_explored += 1
        ct = state_to_tuple(current)

        for label, child_state in get_neighbors(current):
            child_tuple = state_to_tuple(child_state)
            if child_tuple not in visited:
                visited.add(child_tuple)
                parent[child_tuple] = (ct, label)

                if child_tuple == goal_tuple:
                    # Tìm thấy đích -> truy vết đường đi
                    path = reconstruct_path(parent, init_tuple, goal_tuple)
                    return create_path_steps(path, "BFS", nodes_explored, len(visited))

                queue.append((child_state, depth + 1))

    return [SolveStep(initial_state, [], -1, 0, len(visited),
                      f"Không tìm thấy lời giải trong giới hạn {max_nodes} node.\n"
                      f"Đã duyệt: {len(visited)} node.")]

# ============================================================
#  THUẬT TOÁN DFS - Trả về đường đi lời giải (Iterative Deepening)
# ============================================================
def solve_dfs(initial_state, max_nodes=200000):
    """DFS: Tìm kiếm theo chiều sâu (Iterative Deepening) - trả về đường đi từng bước."""
    goal_tuple = state_to_tuple(GOAL_STATE)
    init_tuple = state_to_tuple(initial_state)

    if init_tuple == goal_tuple:
        return [SolveStep(initial_state, [], -1, 0, 1, "Trạng thái ban đầu đã là trạng thái đích!")]

    total_explored = 0

    # Iterative Deepening: tăng dần giới hạn depth
    for max_depth in range(1, 81):
        stack = [(initial_state, 0)]
        visited = {init_tuple}
        parent = {}
        nodes_explored = 0

        while stack and total_explored + nodes_explored < max_nodes:
            current, depth = stack.pop()
            nodes_explored += 1
            ct = state_to_tuple(current)

            if depth >= max_depth:
                continue

            for label, child_state in get_neighbors(current):
                child_tuple = state_to_tuple(child_state)
                if child_tuple not in visited:
                    visited.add(child_tuple)
                    parent[child_tuple] = (ct, label)

                    if child_tuple == goal_tuple:
                        # Tìm thấy đích -> truy vết đường đi
                        total_explored += nodes_explored
                        path = reconstruct_path(parent, init_tuple, goal_tuple)
                        return create_path_steps(path, "DFS (IDDFS)", total_explored, len(visited))

                    stack.append((child_state, depth + 1))

        total_explored += nodes_explored

        if total_explored >= max_nodes:
            break

    return [SolveStep(initial_state, [], -1, 0, total_explored,
                      f"Không tìm thấy lời giải trong giới hạn {max_nodes} node.\n"
                      f"Đã duyệt: {total_explored} node.")]


# ============================================================
#  THUẬT TOÁN UCS - Trả về đường đi lời giải
# ============================================================
def solve_ucs(initial_state, max_nodes=50000):
    """UCS: Tìm kiếm chi phí đều (mỗi bước cost=1) - trả về đường đi từng bước."""
    goal_tuple = state_to_tuple(GOAL_STATE)
    init_tuple = state_to_tuple(initial_state)

    if init_tuple == goal_tuple:
        return [SolveStep(initial_state, [], -1, 0, 1, "Trạng thái ban đầu đã là trạng thái đích!", cost=0)]

    counter = 0
    heap = [(0, counter, initial_state)]
    counter += 1
    visited = set()
    parent = {}  # child_tuple -> (parent_tuple, move_label)
    cost_map = {init_tuple: 0}
    nodes_explored = 0

    while heap and len(visited) < max_nodes:
        cost, _, current = heapq.heappop(heap)
        ct = state_to_tuple(current)

        if ct in visited:
            continue
        visited.add(ct)
        nodes_explored += 1

        if ct == goal_tuple:
            # Tìm thấy đích -> truy vết đường đi
            path = reconstruct_path(parent, init_tuple, goal_tuple)
            return create_path_steps(path, "UCS", nodes_explored, len(visited))

        for label, child_state in get_neighbors(current):
            child_tuple = state_to_tuple(child_state)
            new_cost = cost + 1

            if child_tuple not in visited:
                if child_tuple not in cost_map or new_cost < cost_map[child_tuple]:
                    cost_map[child_tuple] = new_cost
                    parent[child_tuple] = (ct, label)
                    heapq.heappush(heap, (new_cost, counter, child_state))
                    counter += 1

    return [SolveStep(initial_state, [], -1, 0, len(visited),
                      f"Không tìm thấy lời giải trong giới hạn {max_nodes} node.\n"
                      f"Đã duyệt: {len(visited)} node.",
                      cost=0)]


# ============================================================
#  VẼ PUZZLE TRÊN CANVAS
# ============================================================
def draw_puzzle(canvas, state, x, y, cell_size, highlight=False, highlight_color=None):
    """Vẽ bảng puzzle 4x4 lên canvas tại vị trí (x, y)."""
    padding = 2
    total = cell_size * 4 + padding * 5

    if highlight and highlight_color:
        canvas.create_rectangle(x - 3, y - 3, x + total + 3, y + total + 3,
                                outline=highlight_color, width=3)

    for i in range(4):
        for j in range(4):
            cx = x + padding + j * (cell_size + padding)
            cy = y + padding + i * (cell_size + padding)
            val = state[i][j]

            if val == 0:
                fill = BG_EMPTY
                canvas.create_rectangle(cx, cy, cx + cell_size, cy + cell_size,
                                        fill=fill, outline=fill)
            else:
                fill = BG_CELL
                canvas.create_rectangle(cx, cy, cx + cell_size, cy + cell_size,
                                        fill=fill, outline="#1a3a6a", width=1)
                # Chọn font theo cell_size
                if cell_size >= 35:
                    font = FONT_CELL
                elif cell_size >= 22:
                    font = FONT_CELL_SM
                else:
                    font = FONT_CELL_XS

                canvas.create_text(cx + cell_size // 2, cy + cell_size // 2,
                                   text=str(val), fill=TEXT_WHITE, font=font)

# ============================================================
#  DIALOG NHẬP TAY
# ============================================================
class PuzzleInputDialog(tk.Toplevel):
    """Dialog để nhập puzzle thủ công."""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Nhập trạng thái Puzzle")
        self.configure(bg=BG_MAIN)
        self.resizable(False, False)
        self.result = None

        # Center dialog
        self.geometry("400x480")
        self.transient(parent)
        self.grab_set()

        tk.Label(self, text="NHẬP TRẠNG THÁI 15-PUZZLE", font=FONT_TITLE,
                 bg=BG_MAIN, fg=TEXT_CYAN).pack(pady=(15, 5))
        tk.Label(self, text="Nhập số từ 0-15 (0 = ô trống)", font=FONT_INFO,
                 bg=BG_MAIN, fg=TEXT_GRAY).pack(pady=(0, 10))

        grid_frame = tk.Frame(self, bg=BG_PANEL, padx=15, pady=15)
        grid_frame.pack(padx=20, pady=5)

        self.entries = []
        for i in range(4):
            row_entries = []
            for j in range(4):
                e = tk.Entry(grid_frame, width=4, font=FONT_CELL, justify="center",
                             bg=BG_CELL, fg=TEXT_WHITE, insertbackground=TEXT_WHITE,
                             relief="flat", bd=2)
                e.grid(row=i, column=j, padx=4, pady=4, ipady=6)
                row_entries.append(e)
            self.entries.append(row_entries)

        # Pre-fill default
        for i in range(4):
            for j in range(4):
                self.entries[i][j].insert(0, str(DEFAULT_STATE[i][j]))

        btn_frame = tk.Frame(self, bg=BG_MAIN)
        btn_frame.pack(pady=15)

        tk.Button(btn_frame, text="✓ Xác nhận", font=FONT_BTN,
                  bg=COLOR_BTN_GREEN, fg=TEXT_WHITE, relief="flat",
                  cursor="hand2", padx=20, pady=8,
                  command=self._on_ok).pack(side=tk.LEFT, padx=10)

        tk.Button(btn_frame, text="✗ Hủy", font=FONT_BTN,
                  bg=COLOR_BTN_RED, fg=TEXT_WHITE, relief="flat",
                  cursor="hand2", padx=20, pady=8,
                  command=self._on_cancel).pack(side=tk.LEFT, padx=10)

        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.wait_window()

    def _on_ok(self):
        try:
            state = []
            all_vals = []
            for i in range(4):
                row = []
                for j in range(4):
                    val = int(self.entries[i][j].get().strip())
                    if val < 0 or val > 15:
                        raise ValueError(f"Giá trị {val} không hợp lệ")
                    row.append(val)
                    all_vals.append(val)
                state.append(row)

            if sorted(all_vals) != list(range(16)):
                messagebox.showerror("Lỗi", "Phải nhập đủ các số từ 0 đến 15, mỗi số xuất hiện đúng 1 lần!",
                                     parent=self)
                return

            if not is_solvable(state):
                messagebox.showwarning("Cảnh báo", "Trạng thái này KHÔNG thể giải được!\nVui lòng nhập lại.",
                                       parent=self)
                return

            self.result = state
            self.destroy()

        except ValueError as e:
            messagebox.showerror("Lỗi", f"Dữ liệu không hợp lệ!\nChỉ nhập số nguyên từ 0-15.\n{e}",
                                 parent=self)

    def _on_cancel(self):
        self.result = None
        self.destroy()

# ============================================================
#  GIAO DIỆN CHÍNH - GROUP 1
# ============================================================
def open_ui(parent, algo_name):
    """Mở giao diện Nhóm 1: Tìm kiếm không có thông tin."""
    parent.withdraw()

    window = tk.Toplevel(parent)
    window.title(f"Nhóm 1: Tìm kiếm không có thông tin - 15 Puzzle")
    window.geometry("1024x620")
    window.configure(bg=BG_MAIN)
    window.minsize(1024, 620)

    # --- State variables ---
    current_algo = tk.StringVar(value="BFS")
    current_state = [row[:] for row in DEFAULT_STATE]
    solve_steps = []
    current_step_idx = tk.IntVar(value=0)
    is_solving = tk.BooleanVar(value=False)

    # Xác định thuật toán ban đầu từ algo_name
    if "DFS" in algo_name.upper():
        current_algo.set("DFS")
    elif "UCS" in algo_name.upper():
        current_algo.set("UCS")
    else:
        current_algo.set("BFS")

    # ─── HEADER ───
    header_frame = tk.Frame(window, bg=BG_HEADER, height=50)
    header_frame.pack(fill=tk.X)
    header_frame.pack_propagate(False)

    tk.Label(header_frame, text="NHÓM 1: TÌM KIẾM KHÔNG CÓ THÔNG TIN",
             font=FONT_TITLE, bg=BG_HEADER, fg=TEXT_CYAN).pack(side=tk.LEFT, padx=15)

    # Nút Quay lại
    def on_close():
        window.destroy()
        parent.deiconify()

    window.protocol("WM_DELETE_WINDOW", on_close)

    btn_back = tk.Button(header_frame, text="✕ Quay lại", font=FONT_BTN,
                         bg=COLOR_BTN_RED, fg=TEXT_WHITE, relief="flat",
                         cursor="hand2", padx=12, pady=2, command=on_close)
    btn_back.pack(side=tk.RIGHT, padx=10, pady=8)

    # Tab thuật toán
    tab_frame = tk.Frame(header_frame, bg=BG_HEADER)
    tab_frame.pack(side=tk.RIGHT, padx=5)

    tab_buttons = {}

    def switch_algo(name):
        current_algo.set(name)
        solve_steps.clear()
        current_step_idx.set(0)
        update_tabs()
        update_display()

    def update_tabs():
        for name, btn in tab_buttons.items():
            if name == current_algo.get():
                btn.config(bg=COLOR_TAB_ACTIVE)
            else:
                btn.config(bg=COLOR_TAB_INACTIVE)

    for algo in ["BFS", "DFS", "UCS"]:
        btn = tk.Button(tab_frame, text=algo, font=FONT_BTN,
                        bg=COLOR_TAB_INACTIVE, fg=TEXT_WHITE,
                        relief="flat", cursor="hand2", padx=14, pady=2,
                        command=lambda a=algo: switch_algo(a))
        btn.pack(side=tk.LEFT, padx=3, pady=8)
        tab_buttons[algo] = btn

        # Hover effects
        def on_enter(e, b=btn, a=algo):
            if current_algo.get() != a:
                b.config(bg=COLOR_TAB_HOVER)

        def on_leave(e, b=btn, a=algo):
            if current_algo.get() != a:
                b.config(bg=COLOR_TAB_INACTIVE)

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

    update_tabs()

    # ─── MAIN CONTENT ───
    content_frame = tk.Frame(window, bg=BG_MAIN)
    content_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=5)

    # --- Panel trái: NODE ĐANG XÉT ---
    left_panel = tk.Frame(content_frame, bg=BG_PANEL, bd=1, relief="solid",
                          highlightbackground=BORDER_COLOR, highlightthickness=1)
    left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5), pady=0)
    left_panel.config(width=200)
    left_panel.pack_propagate(False)

    tk.Label(left_panel, text="NODE ĐANG XÉT", font=FONT_SECTION,
             bg=BG_PANEL, fg=TEXT_WHITE).pack(pady=(8, 5))

    left_canvas = tk.Canvas(left_panel, bg=BG_PANEL, highlightthickness=0,
                            width=185, height=185)
    left_canvas.pack(pady=5)

    left_info_label = tk.Label(left_panel, text="", font=FONT_INFO,
                               bg=BG_PANEL, fg=TEXT_PINK, justify="center")
    left_info_label.pack(pady=5)

    # --- Panel giữa: CÁC NODE CON ---
    center_panel = tk.Frame(content_frame, bg=BG_PANEL, bd=1, relief="solid",
                            highlightbackground=BORDER_COLOR, highlightthickness=1)
    center_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=0)

    tk.Label(center_panel, text="CÁC NODE CON", font=FONT_SECTION,
             bg=BG_PANEL, fg=TEXT_WHITE).pack(pady=(8, 5))

    center_canvas = tk.Canvas(center_panel, bg=BG_PANEL, highlightthickness=0)
    center_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # --- Panel phải: ĐÃ XÉT + GIẢI THÍCH ---
    right_panel = tk.Frame(content_frame, bg=BG_PANEL, bd=1, relief="solid",
                           highlightbackground=BORDER_COLOR, highlightthickness=1)
    right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0), pady=0)
    right_panel.config(width=230)
    right_panel.pack_propagate(False)

    tk.Label(right_panel, text="ĐÃ XÉT", font=FONT_SECTION,
             bg=BG_PANEL, fg=TEXT_WHITE).pack(pady=(8, 3))

    # Canvas cho thumbnails đã xét
    visited_canvas = tk.Canvas(right_panel, bg=BG_PANEL, highlightthickness=0,
                               width=210, height=180)
    visited_canvas.pack(pady=2, padx=5)

    # Scrollbar cho visited
    visited_scroll_frame = tk.Frame(right_panel, bg=BG_PANEL)
    visited_scroll_frame.pack(fill=tk.X, padx=5)

    visited_info_label = tk.Label(visited_scroll_frame, text="", font=("Segoe UI", 8),
                                  bg=BG_PANEL, fg=TEXT_GRAY)
    visited_info_label.pack()

    # Giải thích
    explain_frame = tk.Frame(right_panel, bg="#0d1b2a", bd=1, relief="solid",
                             highlightbackground=BORDER_COLOR, highlightthickness=1)
    explain_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(5, 8))

    tk.Label(explain_frame, text="GIẢI THÍCH", font=FONT_SECTION,
             bg="#0d1b2a", fg=TEXT_YELLOW).pack(pady=(5, 3))

    explain_text = tk.Text(explain_frame, bg="#0d1b2a", fg=TEXT_WHITE,
                           font=FONT_EXPLAIN, wrap=tk.WORD, relief="flat",
                           height=8, padx=8, pady=5)
    explain_text.pack(fill=tk.BOTH, expand=True, padx=3, pady=(0, 5))
    explain_text.config(state=tk.DISABLED)

    # ─── FOOTER ───
    footer_frame = tk.Frame(window, bg=BG_HEADER, height=50)
    footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
    footer_frame.pack_propagate(False)

    # Nút Nhập tay
    def on_input():
        dialog = PuzzleInputDialog(window)
        if dialog.result:
            nonlocal current_state
            current_state = dialog.result
            solve_steps.clear()
            current_step_idx.set(0)
            update_display()

    btn_input = tk.Button(footer_frame, text="📝 Nhập tay", font=FONT_BTN,
                          bg=COLOR_BTN_TEAL, fg=TEXT_WHITE, relief="flat",
                          cursor="hand2", padx=14, pady=4, command=on_input)
    btn_input.pack(side=tk.LEFT, padx=(15, 5), pady=8)

    # Nút Giải
    def on_solve():
        if is_solving.get():
            return

        algo = current_algo.get()
        if not is_solvable(current_state):
            messagebox.showwarning("Cảnh báo",
                                   "Trạng thái hiện tại KHÔNG thể giải được!\nVui lòng nhập trạng thái khác.",
                                   parent=window)
            return

        is_solving.set(True)
        btn_solve.config(state=tk.DISABLED, text="⏳ Đang giải...")
        solve_steps.clear()
        current_step_idx.set(0)

        def do_solve():
            try:
                if algo == "BFS":
                    result = solve_bfs(current_state)
                elif algo == "DFS":
                    result = solve_dfs(current_state)
                else:
                    result = solve_ucs(current_state)

                solve_steps.extend(result)
            except Exception as e:
                solve_steps.append(SolveStep(current_state, [], -1, 0, 0, f"Lỗi: {str(e)}"))
            finally:
                window.after(0, on_solve_done)

        def on_solve_done():
            is_solving.set(False)
            btn_solve.config(state=tk.NORMAL, text="▶ Giải")
            if solve_steps:
                current_step_idx.set(0)
            update_display()

        thread = threading.Thread(target=do_solve, daemon=True)
        thread.start()

    btn_solve = tk.Button(footer_frame, text="▶ Giải", font=FONT_BTN,
                          bg=COLOR_BTN_GREEN, fg=TEXT_WHITE, relief="flat",
                          cursor="hand2", padx=14, pady=4, command=on_solve)
    btn_solve.pack(side=tk.LEFT, padx=5, pady=8)

    # Nút Bước trước
    def on_prev():
        if solve_steps and current_step_idx.get() > 0:
            current_step_idx.set(current_step_idx.get() - 1)
            update_display()

    btn_prev = tk.Button(footer_frame, text="◀◀ Bước trước", font=FONT_BTN,
                         bg=COLOR_BTN_BLUE, fg=TEXT_WHITE, relief="flat",
                         cursor="hand2", padx=14, pady=4, command=on_prev)
    btn_prev.pack(side=tk.LEFT, padx=5, pady=8)

    # Nút Bước sau
    def on_next():
        if solve_steps and current_step_idx.get() < len(solve_steps) - 1:
            current_step_idx.set(current_step_idx.get() + 1)
            update_display()

    btn_next = tk.Button(footer_frame, text="Bước sau ▶▶", font=FONT_BTN,
                         bg=COLOR_BTN_BLUE, fg=TEXT_WHITE, relief="flat",
                         cursor="hand2", padx=14, pady=4, command=on_next)
    btn_next.pack(side=tk.LEFT, padx=5, pady=8)

    # Nút Auto Play / Dừng
    auto_playing = tk.BooleanVar(value=False)

    def on_auto_play():
        if auto_playing.get():
            auto_playing.set(False)
            btn_auto.config(text="▶ Tự chạy", bg=COLOR_BTN_ORANGE)
            return

        if not solve_steps:
            return

        auto_playing.set(True)
        btn_auto.config(text="⏸ Dừng", bg=COLOR_BTN_RED)

        def auto_step():
            if not auto_playing.get():
                btn_auto.config(text="▶ Tự chạy", bg=COLOR_BTN_ORANGE)
                return
            if current_step_idx.get() < len(solve_steps) - 1:
                current_step_idx.set(current_step_idx.get() + 1)
                update_display()
                window.after(300, auto_step)
            else:
                auto_playing.set(False)
                btn_auto.config(text="▶ Tự chạy", bg=COLOR_BTN_ORANGE)

        auto_step()

    btn_auto = tk.Button(footer_frame, text="▶ Tự chạy", font=FONT_BTN,
                         bg=COLOR_BTN_ORANGE, fg=TEXT_WHITE, relief="flat",
                         cursor="hand2", padx=14, pady=4, command=on_auto_play)
    btn_auto.pack(side=tk.LEFT, padx=5, pady=8)

    # Label bước
    step_label = tk.Label(footer_frame, text="", font=FONT_BTN,
                          bg=BG_HEADER, fg=TEXT_CYAN)
    step_label.pack(side=tk.RIGHT, padx=15, pady=8)

    # ─── CẬP NHẬT HIỂN THỊ ───
    def update_display():
        left_canvas.delete("all")
        center_canvas.delete("all")
        visited_canvas.delete("all")

        explain_text.config(state=tk.NORMAL)
        explain_text.delete("1.0", tk.END)

        if not solve_steps:
            # Chưa giải - hiển thị trạng thái ban đầu
            draw_puzzle(left_canvas, current_state, 10, 10, 40)
            left_info_label.config(text="Trạng thái ban đầu")
            center_canvas.create_text(
                center_canvas.winfo_width() // 2 if center_canvas.winfo_width() > 1 else 250,
                center_canvas.winfo_height() // 2 if center_canvas.winfo_height() > 1 else 200,
                text="Nhấn \"Giải\" để bắt đầu\ntìm kiếm lời giải",
                fill=TEXT_GRAY, font=FONT_SECTION, justify="center"
            )
            explain_text.insert("1.0", f"Thuật toán: {current_algo.get()}\n\n"
                                       f"Nhấn \"Giải\" để chạy thuật toán.\n"
                                       f"Hoặc \"Nhập tay\" để thay đổi trạng thái.")
            explain_text.config(state=tk.DISABLED)
            step_label.config(text="")
            visited_info_label.config(text="")
            return

        idx = current_step_idx.get()
        step = solve_steps[idx]

        # --- Vẽ node đang xét (panel trái) ---
        draw_puzzle(left_canvas, step.current_state, 10, 10, 40)

        algo = current_algo.get()
        if algo == "UCS":
            left_info_label.config(text=f"g = {step.cost}")
        else:
            left_info_label.config(text=f"depth = {step.depth}")

        # --- Vẽ các node con (panel giữa) ---
        center_canvas.update_idletasks()
        cw = center_canvas.winfo_width()
        ch = center_canvas.winfo_height()

        children = step.children
        n = len(children)

        if n == 0:
            center_canvas.create_text(cw // 2, ch // 2,
                                      text="Không có node con\n(Đích hoặc kết thúc)",
                                      fill=TEXT_GRAY, font=FONT_SECTION, justify="center")
        else:
            # Layout: tối đa 2 cột
            cols = min(n, 2)
            rows = (n + 1) // 2
            cell_sz = 28
            puzzle_w = cell_sz * 4 + 2 * 5 + 6
            puzzle_h = cell_sz * 4 + 2 * 5 + 6

            gap_x = 30
            gap_y = 35
            total_w = cols * puzzle_w + (cols - 1) * gap_x
            total_h = rows * (puzzle_h + 30) + (rows - 1) * gap_y

            start_x = (cw - total_w) // 2
            start_y = max(10, (ch - total_h) // 2 - 10)

            for ci, (label, child_state) in enumerate(children):
                col = ci % 2
                row = ci // 2

                px = start_x + col * (puzzle_w + gap_x)
                py = start_y + row * (puzzle_h + 30 + gap_y)

                # Label phía trên
                is_chosen = (ci == step.chosen_idx)

                label_color = COLOR_HIGHLIGHT if is_chosen else TEXT_GRAY
                center_canvas.create_text(px + puzzle_w // 2, py,
                                          text=label + (" ★" if is_chosen else ""),
                                          fill=label_color, font=("Segoe UI", 8, "bold"),
                                          anchor="s")

                draw_puzzle(center_canvas, child_state, px, py + 3, cell_sz,
                            highlight=is_chosen, highlight_color=COLOR_HIGHLIGHT)

        # --- Vẽ thumbnails đã xét (panel phải) ---
        thumb_size = 12
        thumb_total = thumb_size * 4 + 5
        cols_t = 3
        gap_t = 8

        # Hiển thị tối đa các bước trước đó
        max_thumbs = min(idx + 1, 12)  # Giới hạn 12 thumbnails
        start_from = max(0, idx + 1 - max_thumbs)

        for ti in range(max_thumbs):
            si = start_from + ti
            col_t = ti % cols_t
            row_t = ti // cols_t

            tx = 5 + col_t * (thumb_total + gap_t)
            ty = 5 + row_t * (thumb_total + gap_t + 15)

            s = solve_steps[si]
            draw_puzzle(visited_canvas, s.current_state, tx, ty, thumb_size)

            # Số thứ tự
            visited_canvas.create_text(tx + thumb_total // 2, ty + thumb_total + 3,
                                       text=f"#{si + 1}", fill=TEXT_GRAY,
                                       font=("Segoe UI", 7))

        visited_info_label.config(text=f"Hiển thị {max_thumbs}/{idx + 1} node")

        # --- Giải thích ---
        explain_text.insert("1.0", step.explanation)
        explain_text.config(state=tk.DISABLED)

        # --- Cập nhật step label ---
        step_label.config(text=f"Bước {idx + 1}/{len(solve_steps)}")

    # Hiển thị ban đầu
    window.after(100, update_display)
