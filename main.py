import tkinter as tk
from tkinter import messagebox

import group1_uninformed
import group2_informed
# import group3_local
# import group4_complex
# import group5_csp
import group6_adversarial



# --- Bảng màu (Modern Dark Theme) ---
BG_COLOR = "#1e1e24"
FRAME_COLOR = "#2b2b36"
TEXT_COLOR = "#ffffff"
SUBTEXT_COLOR = "#a0a0b0"

BTN_BG = "#3a86ff"               # Xanh dương cho nút thuật toán
BTN_HOVER = "#2a75e6"

GROUP_BTN_BG = "#444455"         # Xám đậm cho nút nhóm chưa chọn
GROUP_BTN_HOVER = "#555566"
GROUP_BTN_ACTIVE = "#e63946"     # Đỏ hồng nổi bật cho nhóm đang chọn

BTN_TEXT = "#ffffff"
BORDER_COLOR = "#444455"

class HoverButton(tk.Button):
    """Nút bấm có khả năng tuỳ chỉnh màu hover linh hoạt."""
    def __init__(self, master, default_bg, hover_bg, **kw):
        tk.Button.__init__(self, master=master, bg=default_bg, **kw)
        self.defaultBackground = default_bg
        self.hoverBackground = hover_bg
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, e):
        if self["state"] != "disabled":
            self["background"] = self.hoverBackground

    def on_leave(self, e):
        if self["state"] != "disabled":
            self["background"] = self.defaultBackground

def run_algorithm(root, group_name, algo_name):
    if "Nhóm 1" in group_name:
        group1_uninformed.open_ui(root, algo_name)
    elif "Nhóm 2" in group_name:
        group2_informed.open_ui(root, algo_name)
    elif "Nhóm 3" in group_name:
        group3_local.open_ui(root, algo_name)
    elif "Nhóm 4" in group_name:
        group4_complex.open_ui(root, algo_name)
    elif "Nhóm 5" in group_name:
        group5_csp.open_ui(root, algo_name)
    elif "Nhóm 6" in group_name:
        group6_adversarial.open_ui(root, algo_name)
    else:
        messagebox.showerror("Lỗi", "Không tìm thấy nhóm thuật toán tương ứng.")

def main():
    root = tk.Tk()
    root.title("Hệ Thống Mô Phỏng Thuật Toán AI")
    root.geometry("1000x750")
    root.configure(bg=BG_COLOR)
    root.eval('tk::PlaceWindow . center')

    # --- Header ---
    header_frame = tk.Frame(root, bg=BG_COLOR)
    header_frame.pack(fill=tk.X, pady=(30, 10))

    lbl_title = tk.Label(header_frame, text="BÀI TẬP CUỐI KỲ MÔN TRÍ TUỆ NHÂN TẠO", font=("Segoe UI", 24, "bold"), bg=BG_COLOR, fg=TEXT_COLOR)
    lbl_title.pack()

    lbl_subtitle = tk.Label(header_frame, text="Vui lòng chọn một nhóm thuật toán ở trên", font=("Segoe UI", 12), bg=BG_COLOR, fg=SUBTEXT_COLOR)
    lbl_subtitle.pack(pady=(5, 0))

    algorithm_groups = {
        "Nhóm 1: Tìm kiếm mù": ["Breadth-First Search (BFS)", "Depth-First Search (DFS)", "Uniform Cost Search (UCS)"],
        "Nhóm 2: Tìm kiếm có thông tin": ["Greedy Search", "A* Search", "IDA*"],
        "Nhóm 3: Tìm kiếm cục bộ": ["Simple Hill Climbing", "Steepest-Ascent Hill Climbing", "Stochastic Hill Climbing"],
        "Nhóm 4: Môi trường phức tạp": ["AND-OR Search", "No Observation", "Partially Observable"],
        "Nhóm 5: Thoả mãn ràng buộc": ["Backtracking", "Forward Checking", "Min-Conflicts"],
        "Nhóm 6: Tìm kiếm đối kháng": ["Minimax", "Alpha-Beta Pruning", "Expectimax"]
    }

    # --- Khu vực chứa danh sách nhóm (Nửa trên) ---
    groups_frame = tk.Frame(root, bg=BG_COLOR)
    groups_frame.pack(fill=tk.X, padx=40, pady=10)
    
    # Cấu hình grid 3 cột đều nhau
    for i in range(3):
        groups_frame.columnconfigure(i, weight=1)

    # --- Khu vực chứa danh sách thuật toán (Nửa dưới) ---
    algos_frame = tk.Frame(root, bg=FRAME_COLOR, highlightbackground=BORDER_COLOR, highlightthickness=1, padx=20, pady=20)
    
    lbl_algo_title = tk.Label(algos_frame, text="", font=("Segoe UI", 16, "bold"), bg=FRAME_COLOR, fg=TEXT_COLOR)
    lbl_algo_title.pack(pady=(0, 15))

    btn_container = tk.Frame(algos_frame, bg=FRAME_COLOR)
    btn_container.pack(fill=tk.BOTH, expand=True)

    group_buttons = []

    def show_algorithms(group_name):
        # Đổi màu highlight cho nút nhóm đang chọn, reset các nút khác
        for btn, name in group_buttons:
            if name == group_name:
                btn.config(bg=GROUP_BTN_ACTIVE)
                btn.defaultBackground = GROUP_BTN_ACTIVE
                btn.hoverBackground = GROUP_BTN_ACTIVE # Không đổi màu khi hover vào mục đang chọn
            else:
                btn.config(bg=GROUP_BTN_BG)
                btn.defaultBackground = GROUP_BTN_BG
                btn.hoverBackground = GROUP_BTN_HOVER

        # Cập nhật tiêu đề thuật toán
        lbl_algo_title.config(text=f"Các thuật toán trong {group_name}")
        lbl_subtitle.config(text="Chọn thuật toán để xem mô phỏng")

        # Xóa các nút thuật toán cũ
        for widget in btn_container.winfo_children():
            widget.destroy()

        # Tạo danh sách các nút thuật toán mới
        algos = algorithm_groups[group_name]
        for algo in algos:
            btn = HoverButton(
                btn_container,
                default_bg=BTN_BG,
                hover_bg=BTN_HOVER,
                text=algo,
                font=("Segoe UI", 13),
                fg=BTN_TEXT,
                relief="flat",
                cursor="hand2",
                pady=12,
                command=lambda g=group_name, a=algo: run_algorithm(root, g, a)
            )
            btn.pack(fill=tk.X, pady=8, padx=40)

        # Hiển thị algos_frame nếu chưa hiển thị
        algos_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=(10, 40))

    # --- Render các nút nhóm ---
    row_idx = 0
    col_idx = 0
    for group_name in algorithm_groups.keys():
        btn = HoverButton(
            groups_frame,
            default_bg=GROUP_BTN_BG,
            hover_bg=GROUP_BTN_HOVER,
            text=group_name,
            font=("Segoe UI", 11, "bold"),
            fg=BTN_TEXT,
            relief="flat",
            cursor="hand2",
            pady=15
        )
        # Gắn sự kiện show_algorithms
        btn.config(command=lambda g=group_name: show_algorithms(g))
        btn.grid(row=row_idx, column=col_idx, padx=10, pady=10, sticky="nsew")
        group_buttons.append((btn, group_name))

        col_idx += 1
        if col_idx > 2:
            col_idx = 0
            row_idx += 1

    root.mainloop()

if __name__ == "__main__":
    main()
