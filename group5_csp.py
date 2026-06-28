import tkinter as tk
from tkinter import messagebox
import copy
import random
import threading

# ============================================================
#  BẢNG MÀU (Dark Theme - Đồng nhất 100% với Group 1)
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
COLOR_BTN_HOVER_GREEN = "#00a844"
COLOR_BTN_HOVER_BLUE = "#2162cc"
COLOR_BTN_HOVER_TEAL = "#0097a7"
COLOR_BTN_HOVER_RED = "#c73550"
COLOR_BTN_ORANGE = "#ff9800"      # Nút Auto Play

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

def tuple_to_state(t):
    """Chuyển tuple trạng thái về dạng list 2D."""
    return [list(t[i*4:(i+1)*4]) for i in range(4)]

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

def manhattan_distance(state):
    """Tính tổng khoảng cách Manhattan cho tất cả các ô."""
    dist = 0
    for i in range(4):
        for j in range(4):
            val = state[i][j]
            if val == 0:
                continue
            goal_i = (val - 1) // 4
            goal_j = (val - 1) % 4
            dist += abs(i - goal_i) + abs(j - goal_j)
    return dist

def count_misplaced(state):
    """Đếm số ô sai vị trí."""
    count = 0
    for i in range(4):
        for j in range(4):
            val = state[i][j]
            if val == 0:
                continue
            goal_i = (val - 1) // 4
            goal_j = (val - 1) % 4
            if i != goal_i or j != goal_j:
                count += 1
    return count

def reconstruct_path(parent, start_tuple, goal_tuple):
    """Truy vết đường đi bằng parent pointers."""
    path_tuples = [goal_tuple]
    current = goal_tuple
    while current != start_tuple:
        parent_tuple, _ = parent[current]
        path_tuples.append(parent_tuple)
        current = parent_tuple
    path_tuples.reverse()
    return [tuple_to_state(t) for t in path_tuples]

def create_csp_path_steps(path, algo_name, steps_explored, total_visited, domain_pruning_info=None):
    """Tạo danh sách SolveStep từ đường đi lời giải dạng CSP."""
    steps = []
    total_moves = len(path) - 1
    domain_pruning_info = domain_pruning_info or {}

    for i, state in enumerate(path):
        children = get_neighbors(state)
        chosen_idx = -1

        if i < total_moves:
            next_tuple = state_to_tuple(path[i + 1])
            for j, (_, child) in enumerate(children):
                if state_to_tuple(child) == next_tuple:
                    chosen_idx = j
                    break

        move_label = ""
        if i > 0:
            prev_neighbors = get_neighbors(path[i - 1])
            current_tuple = state_to_tuple(state)
            for label, child in prev_neighbors:
                if state_to_tuple(child) == current_tuple:
                    move_label = label
                    break

        # Thông tin miền giá trị (Domain) & Cắt nhánh của CSP
        state_tuple = state_to_tuple(state)
        pruning_msg = domain_pruning_info.get(state_tuple, "")

        if i == 0:
            expl = (f"{algo_name} (CSP):\n"
                    f"• Trạng thái ban đầu.\n"
                    f"• Biến (Variables): Các bước đi X1, X2,...\n"
                    f"• Miền (Domains): { {l for l, _ in children} }\n"
                    f"• Ràng buộc (Constraints): Trạng thái sau di chuyển không được lặp lại.\n"
                    f"• Đã duyệt: {total_visited} trạng thái.")
        elif i == total_moves:
            expl = (f"🎉 ĐÃ TÌM THẤY ĐÍCH!\n"
                    f"• Bước cuối: {move_label}\n"
                    f"• Tổng số bước di chuyển: {total_moves}\n"
                    f"• Số trạng thái đã duyệt: {total_visited}")
        else:
            expl = (f"{algo_name} (CSP): Bước {i}/{total_moves}.\n"
                    f"• Thực hiện gán biến: {move_label}\n"
                    f"• Ràng buộc: Thỏa mãn (Trạng thái mới).\n"
                    f"• {pruning_msg}\n"
                    f"• Số trạng thái đã duyệt: {total_visited}")

        steps.append(SolveStep(state, children, chosen_idx, 0, total_visited, expl, depth=i, cost=i))

    return steps

# ============================================================
#  CẤU TRÚC BƯỚC GIẢI (Đồng nhất với Group 1)
# ============================================================
class SolveStep:
    def __init__(self, current_state, children, chosen_idx, frontier_size, visited_count, explanation, depth=0, cost=0):
        self.current_state = current_state      # Trạng thái đang xét
        self.children = children                # Danh sách (label, state)
        self.chosen_idx = chosen_idx            # Index của node con được chọn
        self.frontier_size = frontier_size      # Kích thước biên
        self.visited_count = visited_count      # Số trạng thái đã thăm
        self.explanation = explanation          # Giải thích chuẩn AI
        self.depth = depth                      # Độ sâu g
        self.cost = cost                        # Chi phí
# ============================================================
#  THUẬT TOÁN 1: CSP BACKTRACKING SEARCH
# ============================================================
def solve_backtracking(initial_state, max_nodes=50000):
    """Backtracking Search dưới góc nhìn CSP (lọc trùng lặp trạng thái)."""
    goal_tuple = state_to_tuple(GOAL_STATE)
    init_tuple = state_to_tuple(initial_state)

    if init_tuple == goal_tuple:
        return [SolveStep(initial_state, [], -1, 0, 1, "Trạng thái ban đầu đã là đích!")]

    parent = {}
    nodes_explored = [0]
    found = [False]
    pruning_info = {}

    def backtrack(state, visited_path, depth, max_depth):
        if found[0] or nodes_explored[0] >= max_nodes:
            return

        curr_tuple = state_to_tuple(state)
        if curr_tuple == goal_tuple:
            found[0] = True
            return

        if depth >= max_depth:
            return

        neighbors = get_neighbors(state)
        neighbors.sort(key=lambda x: manhattan_distance(x[1]))

        for label, next_state in neighbors:
            next_tuple = state_to_tuple(next_state)
            if next_tuple not in visited_path:
                nodes_explored[0] += 1
                visited_path.add(next_tuple)
                parent[next_tuple] = (curr_tuple, label)
                pruning_info[next_tuple] = f"Miền giá trị khả thi tiếp theo: {len(get_neighbors(next_state))} hướng."

                backtrack(next_state, visited_path, depth + 1, max_depth)
                if found[0]:
                    return
                visited_path.remove(next_tuple)

    for d in range(1, 40):
        if found[0] or nodes_explored[0] >= max_nodes:
            break
        visited_path = {init_tuple}
        backtrack(initial_state, visited_path, 0, d)

    if found[0]:
        path = reconstruct_path(parent, init_tuple, goal_tuple)
        return create_csp_path_steps(path, "CSP Backtracking", nodes_explored[0], nodes_explored[0], pruning_info)
    
    return [SolveStep(initial_state, [], -1, 0, nodes_explored[0], f"Không tìm thấy lời giải CSP trong giới hạn {max_nodes} node.")]

# ============================================================
#  THUẬT TOÁN 2: CSP FORWARD CHECKING (FC)
# ============================================================
def solve_forward_checking(initial_state, max_nodes=50000):
    """
    Forward Checking (FC) cho 15-Puzzle dưới dạng CSP.
    Tại mỗi bước gán, FC nhìn trước (look-ahead) các bước đi tiếp theo.
    Nếu một bước đi kế tiếp dẫn tới miền giá trị rỗng (tất cả các di chuyển kế tiếp đều đụng trạng thái đã duyệt),
    nhánh đó sẽ bị tỉa (pruned) ngay lập tức mà không cần đi vào.
    """
    goal_tuple = state_to_tuple(GOAL_STATE)
    init_tuple = state_to_tuple(initial_state)

    if init_tuple == goal_tuple:
        return [SolveStep(initial_state, [], -1, 0, 1, "Trạng thái ban đầu đã là đích!")]

    parent = {}
    nodes_explored = [0]
    found = [False]
    pruning_info = {}

    def fc_search(state, visited_path, depth, max_depth):
        if found[0] or nodes_explored[0] >= max_nodes:
            return

        curr_tuple = state_to_tuple(state)
        if curr_tuple == goal_tuple:
            found[0] = True
            return

        if depth >= max_depth:
            return

        neighbors = get_neighbors(state)
        neighbors.sort(key=lambda x: manhattan_distance(x[1]))

        for label, next_state in neighbors:
            next_tuple = state_to_tuple(next_state)
            if next_tuple not in visited_path:
                # --- FORWARD CHECKING (LOOK-AHEAD) ---
                future_neighbors = get_neighbors(next_state)
                valid_future_count = 0
                pruned_actions = []
                
                for f_label, f_state in future_neighbors:
                    f_tuple = state_to_tuple(f_state)
                    if f_tuple not in visited_path:
                        valid_future_count += 1
                    else:
                        pruned_actions.append(f_label)

                # Nếu miền của biến tiếp theo bị rỗng (tất cả các hướng đi tiếp theo đều đã nằm trên đường đi hiện tại)
                if valid_future_count == 0 and next_tuple != goal_tuple:
                    continue

                nodes_explored[0] += 1
                visited_path.add(next_tuple)
                parent[next_tuple] = (curr_tuple, label)
                
                pruning_info[next_tuple] = (
                    f"Forward Checking: Nhìn trước bước tiếp theo.\n"
                    f"• Đã tỉa trước {len(pruned_actions)} hướng đi bị lặp.\n"
                    f"• Miền khả thi của bước tiếp theo còn: {valid_future_count} hướng."
                )

                fc_search(next_state, visited_path, depth + 1, max_depth)
                if found[0]:
                    return
                visited_path.remove(next_tuple)

    for d in range(1, 40):
        if found[0] or nodes_explored[0] >= max_nodes:
            break
        visited_path = {init_tuple}
        fc_search(initial_state, visited_path, 0, d)

    if found[0]:
        path = reconstruct_path(parent, init_tuple, goal_tuple)
        return create_csp_path_steps(path, "CSP Forward Checking", nodes_explored[0], nodes_explored[0], pruning_info)
    
    return [SolveStep(initial_state, [], -1, 0, nodes_explored[0], f"Không tìm thấy lời giải CSP Forward Checking.")]
# ============================================================
#  THUẬT TOÁN 3: CSP MIN-CONFLICTS (Local Search CSP)
# ============================================================
def solve_min_conflicts(initial_state, max_steps=300):
    """
    Min-Conflicts cho 15-Puzzle.
    • Xung đột (Conflicts) được định nghĩa là số ô sai vị trí (Misplaced tiles).
    • Tại mỗi bước, ta chọn bước di chuyển có số lượng xung đột nhỏ nhất.
    """
    goal_tuple = state_to_tuple(GOAL_STATE)
    current = copy.deepcopy(initial_state)
    
    path = [current]
    visited = {state_to_tuple(current)}
    pruning_info = {}

    for step in range(max_steps):
        curr_tuple = state_to_tuple(current)
        if curr_tuple == goal_tuple:
            break

        neighbors = get_neighbors(current)
        # Tính số conflict (ô sai vị trí) của từng node con
        scored_neighbors = []
        for label, nxt in neighbors:
            nxt_tuple = state_to_tuple(nxt)
            conflicts = count_misplaced(nxt)
            # Phạt nặng các trạng thái đã đi qua để tránh lặp vòng vô chậm
            penalty = 100 if nxt_tuple in visited else 0
            scored_neighbors.append((label, nxt, conflicts, conflicts + penalty))

        # Chọn di chuyển có conflict + penalty nhỏ nhất
        scored_neighbors.sort(key=lambda x: x[3])
        best_label, best_state, best_conf, _ = scored_neighbors[0]

        best_tuple = state_to_tuple(best_state)
        visited.add(best_tuple)
        
        pruning_info[best_tuple] = (
            f"Min-Conflicts: Chọn nước đi giảm xung đột tốt nhất.\n"
            f"• Xung đột hiện tại (Ô sai vị trí): {best_conf}/15."
        )
        
        path.append(best_state)
        current = best_state

    if state_to_tuple(current) == goal_tuple:
        return create_csp_path_steps(path, "CSP Min-Conflicts", len(path), len(visited), pruning_info)
    
    return [SolveStep(initial_state, [], -1, 0, len(visited), f"Min-Conflicts không hội tụ sau {max_steps} bước.")]

# ============================================================
#  VẼ PUZZLE TRÊN CANVAS (Đồng nhất với Group 1)
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
                if cell_size >= 35:
                    font = FONT_CELL
                elif cell_size >= 22:
                    font = FONT_CELL_SM
                else:
                    font = FONT_CELL_XS

                canvas.create_text(cx + cell_size // 2, cy + cell_size // 2,
                                   text=str(val), fill=TEXT_WHITE, font=font)

# ============================================================
#  GIAO DIỆN CHÍNH - GROUP 5 (Đồng nhất 100% với Group 1)
# ============================================================
def open_ui(parent, algo_name):
    """Mở giao diện Nhóm 5: Thỏa mãn ràng buộc (CSP) - 15 Puzzle."""
    parent.withdraw()

    window = tk.Toplevel(parent)
    window.title(f"Nhóm 5: Thỏa mãn ràng buộc (CSP) - 15 Puzzle")
    window.geometry("1024x620")
    window.configure(bg=BG_MAIN)
    window.minsize(1024, 620)

    # --- State variables ---
    current_algo = tk.StringVar(value="Backtracking")
    state_holder = {'state': [row[:] for row in DEFAULT_STATE]}
    solve_steps = []
    current_step_idx = tk.IntVar(value=0)
    is_solving = tk.BooleanVar(value=False)

    # Xác định thuật toán ban đầu
    algo_upper = algo_name.upper()
    if "FORWARD" in algo_upper or "FC" in algo_upper:
        current_algo.set("Forward Checking")
    elif "MIN" in algo_upper or "CONFLICT" in algo_upper:
        current_algo.set("Min-Conflicts")
    else:
        current_algo.set("Backtracking")

    # ─── HEADER ───
    header_frame = tk.Frame(window, bg=BG_HEADER, height=50)
    header_frame.pack(fill=tk.X)
    header_frame.pack_propagate(False)

    tk.Label(header_frame, text="NHÓM 5: THỎA MÃN RÀNG BUỘC (CSP)",
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

    for algo in ["Backtracking", "Forward Checking", "Min-Conflicts"]:
        btn = tk.Button(tab_frame, text=algo, font=FONT_BTN,
                        bg=COLOR_TAB_INACTIVE, fg=TEXT_WHITE,
                        relief="flat", cursor="hand2", padx=10, pady=2,
                        command=lambda a=algo: switch_algo(a))
        btn.pack(side=tk.LEFT, padx=3, pady=8)
        tab_buttons[algo] = btn

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

    # Scrollbar info
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
        dialog = PuzzleInputDialog(window, state_holder['state'])
        if dialog.result:
            state_holder['state'] = dialog.result
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

        if not is_solvable(state_holder['state']):
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
                algo = current_algo.get()
                if algo == "Backtracking":
                    result = solve_backtracking(state_holder['state'])
                elif algo == "Forward Checking":
                    result = solve_forward_checking(state_holder['state'])
                else:
                    result = solve_min_conflicts(state_holder['state'])

                solve_steps.extend(result)
            except Exception as e:
                solve_steps.append(SolveStep(
                    state_holder['state'], [], -1, 0, 0,
                    f"Lỗi: {str(e)}"
                ))
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

    # Nút Tự chạy / Dừng
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

    # ─── CẬP NHẬT HIỂN THỊ (Đồng nhất hoàn toàn với Group 1) ───
    def update_display():
        left_canvas.delete("all")
        center_canvas.delete("all")
        visited_canvas.delete("all")

        explain_text.config(state=tk.NORMAL)
        explain_text.delete("1.0", tk.END)

        if not solve_steps:
            # Chưa giải - hiển thị trạng thái ban đầu
            draw_puzzle(left_canvas, state_holder['state'], 10, 10, 40)
            left_info_label.config(text="Trạng thái ban đầu")
            center_canvas.create_text(
                center_canvas.winfo_width() // 2 if center_canvas.winfo_width() > 1 else 250,
                center_canvas.winfo_height() // 2 if center_canvas.winfo_height() > 1 else 200,
                text="Nhấn \"Giải\" để bắt đầu\ntìm kiếm lời giải CSP",
                fill=TEXT_GRAY, font=FONT_SECTION, justify="center"
            )
            explain_text.insert("1.0", f"Thuật toán CSP: {current_algo.get()}\n\n"
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
        left_info_label.config(text=f"depth = {step.depth}")

        # --- Vẽ các node con (panel giữa) ---
        center_canvas.update_idletasks()
        cw = center_canvas.winfo_width()
        ch = center_canvas.winfo_height()

        children = step.children
        n = len(children)

        if n == 0:
            center_canvas.create_text(cw // 2, ch // 2,
                                      text="Không có lựa chọn tiếp theo\n(Trạng thái Đích)",
                                      fill=TEXT_GRAY, font=FONT_SECTION, justify="center")
        else:
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

        max_thumbs = min(idx + 1, 12)
        start_from = max(0, idx + 1 - max_thumbs)

        for ti in range(max_thumbs):
            si = start_from + ti
            col_t = ti % cols_t
            row_t = ti // cols_t

            tx = 5 + col_t * (thumb_total + gap_t)
            ty = 5 + row_t * (thumb_total + gap_t + 15)

            s = solve_steps[si]
            draw_puzzle(visited_canvas, s.current_state, tx, ty, thumb_size)

            visited_canvas.create_text(tx + thumb_total // 2, ty + thumb_total + 3,
                                       text=f"#{si + 1}", fill=TEXT_GRAY,
                                       font=("Segoe UI", 7))

        visited_info_label.config(text=f"Hiển thị {max_thumbs}/{idx + 1} bước")

        # --- Giải thích ---
        explain_text.insert("1.0", step.explanation)
        explain_text.config(state=tk.DISABLED)

        # --- Cập nhật step label ---
        step_label.config(text=f"Bước {idx + 1}/{len(solve_steps)}")

    window.after(100, update_display)


# ============================================================
#  DIALOG NHẬP TAY (Đồng nhất với Group 1)
# ============================================================
class PuzzleInputDialog(tk.Toplevel):
    def __init__(self, parent, current_state=None):
        super().__init__(parent)
        self.title("Nhập trạng thái Puzzle")
        self.configure(bg=BG_MAIN)
        self.resizable(False, False)
        self.result = None

        self.geometry("400x480")
        self.transient(parent)
        self.grab_set()

        tk.Label(self, text="NHẬP TRẠNG THÁI 15-PUZZLE", font=FONT_TITLE,
                 bg=BG_MAIN, fg=TEXT_CYAN).pack(pady=(15, 5))
        tk.Label(self, text="Nhập số từ 0-15 (0 = ô trống)", font=FONT_INFO,
                 bg=BG_MAIN, fg=TEXT_GRAY).pack(pady=(0, 10))

        grid_frame = tk.Frame(self, bg=BG_PANEL, padx=15, pady=15)
        grid_frame.pack(padx=20, pady=5)

        init_state = current_state if current_state else DEFAULT_STATE

        self.entries = []
        for i in range(4):
            row_entries = []
            for j in range(4):
                e = tk.Entry(grid_frame, width=4, font=FONT_CELL, justify="center",
                             bg=BG_CELL, fg=TEXT_WHITE, insertbackground=TEXT_WHITE,
                             relief="flat", bd=2)
                e.grid(row=i, column=j, padx=4, pady=4, ipady=6)
                e.insert(0, str(init_state[i][j]))
                row_entries.append(e)
            self.entries.append(row_entries)

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
