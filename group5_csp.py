import tkinter as tk
from tkinter import messagebox
<<<<<<< HEAD
import random, itertools, time

# ===== THEME =====
BG    = "#1a1a2e"
PANEL = "#16213e"
CARD  = "#0f3460"
TEXT  = "#e6e6e6"
SUB   = "#8d99ae"
ACCENT= "#00d4ff"
BTN   = "#3a86ff"
BTN_SEL="#e63946"
CELL  = "#3d5a80"
CELL_E= "#0e0e1a"
GREEN = "#06d6a0"
RED   = "#ef476f"
YELLOW= "#ffd166"
PURPLE= "#6930c3"

# =============================================================
# CSP PROBLEM STRUCTURE ANALYSIS
# =============================================================
# Variables: V_r_c  (r,c in 0..3), domain = {0..15}
# Constraints:
#   C1. AllDifferent — all 16 values distinct
#   C2. V_3_3 = 0   — blank at bottom-right corner
#   C3. Symmetry     — For every pair (V_r_c, V_(3-r)_(3-c))
#       that does NOT involve V_3_3: their sum = 16
#   C4. Solvability  — even inversion count
#
# KEY INSIGHT:
#   V_3_3 = 0  →  its symmetric partner is V_0_0 (excluded from C3)
#   The 7 remaining symmetric pairs must each sum to 16.
#   Value-pairs that sum to 16: (1,15)(2,14)(3,13)(4,12)(5,11)(6,10)(7,9)
#   That covers values {1..15} \ {8}.  Value 8 has no partner ⟹ V_0_0 = 8.
#   So we only need to:
#     1. Assign the 7 value-pairs to the 7 position-pairs  (7! orderings)
#     2. Within each pair, choose which position gets which value (2^7 choices)
#     3. Check C4 (even inversions)
# =============================================================

VARS = [(r, c) for r in range(4) for c in range(4)]

# The 7 symmetric position-pairs (ordered, excluding the V_0_0/V_3_3 pair)
SYM_POS_PAIRS = [
    ((0,1),(3,2)), ((0,2),(3,1)), ((0,3),(3,0)),
    ((1,0),(2,3)), ((1,1),(2,2)), ((1,2),(2,1)), ((1,3),(2,0)),
]
# The 7 value-pairs that sum to 16
VALUE_PAIRS = [(1,15),(2,14),(3,13),(4,12),(5,11),(6,10),(7,9)]

def count_inversions(flat):
    nums = [x for x in flat if x != 0]
    inv = sum(1 for i in range(len(nums)) for j in range(i+1, len(nums)) if nums[i] > nums[j])
    return inv

def is_solvable(board_2d):
    flat = [board_2d[r][c] for r in range(4) for c in range(4)]
    return count_inversions(flat) % 2 == 0

def assignment_to_board(assignment):
    return [[assignment[(r,c)] for c in range(4)] for r in range(4)]

def board_str(board):
    lines = []
    for row in board:
        parts = ["[ ]" if v == 0 else f"{v:2}" for v in row]
        lines.append("  ".join(parts))
    return "\n".join(lines)

# =============================================================
# ALGORITHM 1 — BACKTRACKING
# Assigns value-pairs to position-pairs one by one.
# At each step checks symmetry (auto-satisfied by construction)
# and AllDifferent (also auto-satisfied).
# Only real decision: which orientation of the value in the pair?
# Backtracks when no valid orientation satisfies solvability.
# Records every assignment attempt as a step.
# =============================================================
def solve_backtracking():
    steps = []
    assignment = {(0,0): 8, (3,3): 0}   # V_0_0=8, V_3_3=0 are fixed

    steps.append({
        'phase': 'init',
        'assignment': dict(assignment),
        'text': (
            "BACKTRACKING – Phân tích ràng buộc:\n\n"
            "• V_3_3 = 0  (ô trống cố định)\n"
            "• V_0_0 = 8  (giá trị duy nhất không có cặp đối xứng)\n"
            "• 7 cặp vị trí đối xứng nhận 7 cặp giá trị (tổng = 16):\n"
            "  (1,15) (2,14) (3,13) (4,12) (5,11) (6,10) (7,9)\n\n"
            "Bắt đầu gán lần lượt từng cặp..."
        ),
        'pair_idx': -1, 'val_pair': None, 'pos_pair': None, 'orient': None, 'ok': None,
    })

    # Deterministic order of value-pairs (shuffled for variety)
    vp_order = VALUE_PAIRS[:]

    def backtrack(depth, vp_remaining):
        if depth == 7:
            board = assignment_to_board(assignment)
            if is_solvable(board):
                return True
            # Solvability failed — note it and backtrack
            steps.append({
                'phase': 'solvability_fail',
                'assignment': dict(assignment),
                'text': (
                    f"Hoàn thành gán ({len(assignment)}/16 biến).\n"
                    "✗ Ràng buộc nghịch thế: số nghịch thế LẺ!\n"
                    "← Quay lui để thử phân bổ khác."
                ),
                'pair_idx': depth, 'val_pair': None, 'pos_pair': None, 'orient': None, 'ok': False,
            })
            return False

        pos_pair = SYM_POS_PAIRS[depth]
        p1, p2 = pos_pair

        for val_pair in vp_remaining:
            a, b = val_pair
            for orient in [(a, b), (b, a)]:
                v1, v2 = orient
                assignment[p1] = v1
                assignment[p2] = v2

                steps.append({
                    'phase': 'assign',
                    'assignment': dict(assignment),
                    'text': (
                        f"Gán cặp {depth+1}/7:\n"
                        f"  Cặp vị trí: V_{p1[0]}_{p1[1]} & V_{p2[0]}_{p2[1]}\n"
                        f"  Cặp giá trị: ({a},{b})  →  thử ({v1}, {v2})\n"
                        f"  Kiểm tra: {v1}+{v2} = {v1+v2} {'= 16 ✓' if v1+v2==16 else '≠ 16 ✗'}\n"
                        f"  Đã gán: {len(assignment)}/16 biến"
                    ),
                    'pair_idx': depth, 'val_pair': val_pair, 'pos_pair': pos_pair,
                    'orient': orient, 'ok': True,
                    'highlight': [p1, p2],
                })

                new_remaining = [vp for vp in vp_remaining if vp != val_pair]
                if backtrack(depth + 1, new_remaining):
                    return True

                del assignment[p1]
                del assignment[p2]

                steps.append({
                    'phase': 'backtrack',
                    'assignment': dict(assignment),
                    'text': (
                        f"← Backtrack: V_{p1[0]}_{p1[1]}={v1}, V_{p2[0]}_{p2[1]}={v2}\n"
                        f"   không dẫn đến lời giải. Thử hướng ngược lại..."
                    ),
                    'pair_idx': depth, 'val_pair': val_pair, 'pos_pair': pos_pair,
                    'orient': orient, 'ok': False,
                    'highlight': [p1, p2],
                })

        return False

    backtrack(0, vp_order)
    sol = assignment if len(assignment) == 16 else {}
    return sol, steps


# =============================================================
# ALGORITHM 2 — FORWARD CHECKING
# Same pair-based approach, but after each assignment pruning
# the remaining available value-pairs by checking:
#   • Whether any future position-pair would have its domain wiped
#   • Records explicit domain sizes before/after pruning
# =============================================================
def solve_forward_checking():
    steps = []
    assignment = {(0,0): 8, (3,3): 0}

    steps.append({
        'phase': 'init',
        'assignment': dict(assignment),
        'domains': {i: list(VALUE_PAIRS) for i in range(7)},
        'text': (
            "FORWARD CHECKING – Khởi tạo:\n\n"
            "• Mỗi trong 7 cặp vị trí có miền = 7 cặp giá trị\n"
            "• Sau mỗi lần gán: cắt tỉa miền của các cặp chưa gán\n"
            "• Nếu miền nào rỗng (domain wipe-out) → Backtrack sớm\n\n"
            "Miền ban đầu:\n"
            "  Cặp 1..7: [(1,15),(2,14),(3,13),(4,12),(5,11),(6,10),(7,9)]"
        ),
        'pair_idx': -1, 'val_pair': None, 'pos_pair': None, 'orient': None, 'ok': None,
    })

    def fc_backtrack(depth, remaining_vp_list):
        """remaining_vp_list[i] = list of available value-pairs for position-pair i (i >= depth)."""
        if depth == 7:
            board = assignment_to_board(assignment)
            if is_solvable(board):
                return True
            steps.append({
                'phase': 'solvability_fail',
                'assignment': dict(assignment),
                'domains': {},
                'text': (
                    "Hoàn thành gán. ✗ Nghịch thế LẺ!\n← Quay lui."
                ),
                'pair_idx': depth, 'val_pair': None, 'pos_pair': None, 'orient': None, 'ok': False,
            })
            return False

        pos_pair = SYM_POS_PAIRS[depth]
        p1, p2 = pos_pair
        available = remaining_vp_list[depth]

        for val_pair in available:
            a, b = val_pair
            for orient in [(a, b), (b, a)]:
                v1, v2 = orient
                assignment[p1] = v1
                assignment[p2] = v2

                # Forward checking: build pruned domains for future pairs
                new_vp_list = dict(remaining_vp_list)
                wipeout = False
                pruned_count = 0
                for future_depth in range(depth + 1, 7):
                    new_vp_list[future_depth] = [
                        vp for vp in remaining_vp_list[future_depth]
                        if vp != val_pair
                    ]
                    pruned_count += (len(remaining_vp_list[future_depth]) - len(new_vp_list[future_depth]))
                    if not new_vp_list[future_depth]:
                        wipeout = True
                        break

                ok = not wipeout
                steps.append({
                    'phase': 'assign',
                    'assignment': dict(assignment),
                    'domains': {i: new_vp_list.get(i, []) for i in range(7)},
                    'text': (
                        f"FC Gán cặp {depth+1}/7:\n"
                        f"  V_{p1[0]}_{p1[1]}={v1}, V_{p2[0]}_{p2[1]}={v2}  (tổng={v1+v2})\n"
                        + (
                            f"  ✓ Forward Check OK: cắt {pruned_count} giá trị\n"
                            f"  Tiếp tục gán cặp {depth+2}/7..."
                            if ok else
                            f"  ✗ Domain Wipe-out ở cặp {depth+2}!\n"
                            f"  ← Backtrack sớm (không cần thử thêm)."
                        )
                    ),
                    'pair_idx': depth, 'val_pair': val_pair, 'pos_pair': pos_pair,
                    'orient': orient, 'ok': ok,
                    'highlight': [p1, p2],
                    'pruned': pruned_count,
                })

                if ok and fc_backtrack(depth + 1, new_vp_list):
                    return True

                del assignment[p1]
                del assignment[p2]

                if not ok:
                    continue  # Already noted above

                steps.append({
                    'phase': 'backtrack',
                    'assignment': dict(assignment),
                    'domains': {i: remaining_vp_list.get(i, []) for i in range(7)},
                    'text': (
                        f"← FC Backtrack: cặp giá trị {val_pair} hướng {orient}\n"
                        f"   không dẫn đến lời giải. Thử hướng ngược..."
                    ),
                    'pair_idx': depth, 'val_pair': val_pair, 'pos_pair': pos_pair,
                    'orient': orient, 'ok': False,
                    'highlight': [p1, p2],
                })

        return False

    init_domains = {i: list(VALUE_PAIRS) for i in range(7)}
    fc_backtrack(0, init_domains)
    sol = assignment if len(assignment) == 16 else {}
    return sol, steps


# =============================================================
# ALGORITHM 3 — MIN-CONFLICTS
# Start from a random complete valid-structure assignment,
# then iteratively fix constraint violations (orientation of pairs).
# Conflict = wrong inversion parity (solvability constraint).
# Since symmetry is always satisfied by construction,
# the only conflict is solvability. So Min-Conflicts swaps
# orientations of pairs to minimize parity conflicts.
# =============================================================
def solve_min_conflicts(max_steps=200):
    steps = []

    # Build a random complete assignment respecting C1-C3
    vp_shuffled = VALUE_PAIRS[:]
    random.shuffle(vp_shuffled)
    assignment = {(0,0): 8, (3,3): 0}
    orientations = []  # list of (pos_pair, val_pair, chosen_orient)
    for i, (pos_pair, val_pair) in enumerate(zip(SYM_POS_PAIRS, vp_shuffled)):
        p1, p2 = pos_pair
        a, b = val_pair
        orient = random.choice([(a,b),(b,a)])
        assignment[p1] = orient[0]
        assignment[p2] = orient[1]
        orientations.append([pos_pair, val_pair, orient])

    board = assignment_to_board(assignment)
    inv = count_inversions([board[r][c] for r in range(4) for c in range(4)])
    conflict = 0 if inv % 2 == 0 else 1

    steps.append({
        'phase': 'init',
        'assignment': dict(assignment),
        'inv': inv,
        'conflicts': conflict,
        'text': (
            "MIN-CONFLICTS – Khởi tạo ngẫu nhiên:\n\n"
            "Gán ngẫu nhiên 7 cặp giá trị vào 7 cặp vị trí.\n"
            "Ràng buộc C1,C2,C3 đã được đảm bảo theo cấu trúc.\n"
            f"Chỉ cần kiểm tra C4 (nghịch thế chẵn).\n\n"
            f"Số nghịch thế ban đầu: {inv} → "
            f"{'CHẴN ✓' if inv%2==0 else 'LẺ ✗ (cần sửa)'}\n"
            f"Xung đột ban đầu: {conflict}"
        ),
        'step_num': 0, 'orient_info': None,
    })

    if conflict == 0:
        steps[-1]['text'] += "\n\n🎉 Ngẫu nhiên trúng lời giải ngay!"
        return assignment, steps

    # Min-Conflicts: try flipping each pair orientation to reduce conflicts
    for step_num in range(1, max_steps + 1):
        board = assignment_to_board(assignment)
        inv = count_inversions([board[r][c] for r in range(4) for c in range(4)])
        if inv % 2 == 0:
            steps.append({
                'phase': 'solution',
                'assignment': dict(assignment),
                'inv': inv,
                'conflicts': 0,
                'text': (
                    f"🎉 Tìm thấy lời giải sau {step_num-1} bước!\n\n"
                    f"Số nghịch thế: {inv} (CHẴN ✓)\n"
                    "Tất cả ràng buộc đã thỏa mãn."
                ),
                'step_num': step_num, 'orient_info': None,
            })
            return assignment, steps

        # Find all conflicted pairs: flipping any one might fix parity
        # (flipping a pair changes inversions by an odd/even amount depending on values)
        # Try each pair, pick the one that gives min conflicts (0 preferred)
        best_idx = -1
        best_inv = inv
        for i, (pos_pair, val_pair, orient) in enumerate(orientations):
            p1, p2 = pos_pair
            a, b = val_pair
            alt_orient = (b, a) if orient == (a, b) else (a, b)
            # Simulate flip
            assignment[p1] = alt_orient[0]
            assignment[p2] = alt_orient[1]
            test_board = assignment_to_board(assignment)
            test_inv = count_inversions([test_board[r][c] for r in range(4) for c in range(4)])
            if test_inv % 2 == 0:
                best_idx = i
                best_inv = test_inv
                assignment[p1] = orient[0]
                assignment[p2] = orient[1]
                break
            if abs(test_inv - inv) < abs(best_inv - inv) or best_idx == -1:
                best_idx = i
                best_inv = test_inv
            # Restore
            assignment[p1] = orient[0]
            assignment[p2] = orient[1]

        # Apply best flip
        pos_pair, val_pair, old_orient = orientations[best_idx]
        p1, p2 = pos_pair
        a, b = val_pair
        new_orient = (b, a) if old_orient == (a, b) else (a, b)
        orientations[best_idx][2] = new_orient
        assignment[p1] = new_orient[0]
        assignment[p2] = new_orient[1]

        new_conflict = 1 if best_inv % 2 != 0 else 0
        steps.append({
            'phase': 'step',
            'assignment': dict(assignment),
            'inv': best_inv,
            'conflicts': new_conflict,
            'text': (
                f"Bước {step_num}: Lật hướng cặp {best_idx+1}\n"
                f"  V_{p1[0]}_{p1[1]} & V_{p2[0]}_{p2[1]}:\n"
                f"  {old_orient} → {new_orient}\n"
                f"  Nghịch thế: {inv} → {best_inv} "
                f"({'CHẴN ✓' if best_inv%2==0 else 'LẺ ✗'})\n"
                f"  Xung đột: {1 if inv%2!=0 else 0} → {new_conflict}"
            ),
            'step_num': step_num,
            'orient_info': (best_idx, old_orient, new_orient, p1, p2),
            'highlight': [p1, p2],
        })

    # Fallback: if still not solved, try exhaustive over 2^7
    for bits in range(128):
        assignment = {(0,0): 8, (3,3): 0}
        for i, (pos_pair, val_pair) in enumerate(zip(SYM_POS_PAIRS, VALUE_PAIRS)):
            p1, p2 = pos_pair
            a, b = val_pair
            if (bits >> i) & 1:
                assignment[p1], assignment[p2] = b, a
            else:
                assignment[p1], assignment[p2] = a, b
        board = assignment_to_board(assignment)
        if is_solvable(board):
            steps.append({
                'phase': 'solution',
                'assignment': dict(assignment),
                'inv': count_inversions([board[r][c] for r in range(4) for c in range(4)]),
                'conflicts': 0,
                'text': "🎉 Tìm thấy lời giải qua brute-force fallback!",
                'step_num': max_steps + 1, 'orient_info': None,
            })
            return assignment, steps

    return {}, steps


# =============================================================
# DRAWING
# =============================================================
def draw_board(canvas, assignment, cs, x0, y0, highlight=None, border=None):
    gap = 2
    total = 4 * cs + 3 * gap
    if border:
        canvas.create_rectangle(x0-3, y0-3, x0+total+3, y0+total+3,
                                 fill=PANEL, outline=border, width=3)
    for r in range(4):
        for c in range(4):
            x = x0 + c*(cs+gap); y = y0 + r*(cs+gap)
            var = (r, c)
            val = assignment.get(var, None)
            hl = highlight and var in highlight
            if val is None:
                canvas.create_rectangle(x,y,x+cs,y+cs, fill="#252535", outline="#3a3a4a")
                canvas.create_text(x+cs//2,y+cs//2, text="?", fill=SUB, font=("Segoe UI", max(cs//3,8)))
            elif val == 0:
                canvas.create_rectangle(x,y,x+cs,y+cs, fill=CELL_E, outline=CELL_E)
                canvas.create_text(x+cs//2,y+cs//2, text="[ ]", fill=SUB, font=("Segoe UI", max(cs//4,7)))
            else:
                fill = YELLOW if hl else CELL
                fg   = "#000" if hl else TEXT
                canvas.create_rectangle(x,y,x+cs,y+cs, fill=fill, outline="#4a6d8c")
                canvas.create_text(x+cs//2,y+cs//2, text=str(val), fill=fg,
                                   font=("Segoe UI", max(cs//3,8), "bold"))


# =============================================================
# ALGORITHM DESCRIPTIONS
# =============================================================
ALGO_DESCS = {
    "Backtracking": (
        "BACKTRACKING CSP\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Khai thác cấu trúc CSP:\n"
        "  • V_3_3 = 0   (cố định)\n"
        "  • V_0_0 = 8   (giá trị duy nhất không có\n"
        "                 cặp đối xứng)\n"
        "  • 7 cặp vị trí đối xứng ↔ 7 cặp giá trị\n"
        "    (1,15)(2,14)(3,13)(4,12)(5,11)(6,10)(7,9)\n\n"
        "Chiến lược:\n"
        "  Gán lần lượt từng cặp giá trị vào cặp vị trí.\n"
        "  Với mỗi cặp: thử 2 hướng (a→p1,b→p2 hoặc ngược).\n"
        "  Kiểm tra ràng buộc nghịch thế ở cuối.\n"
        "  Quay lui nếu không thỏa mãn."
    ),
    "Forward Checking": (
        "FORWARD CHECKING CSP\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Mở rộng Backtracking với cắt tỉa sớm:\n\n"
        "  Sau mỗi lần gán cặp giá trị (a,b) vào cặp\n"
        "  vị trí thứ i, xóa (a,b) khỏi miền của tất cả\n"
        "  các cặp vị trí chưa gán (i+1 đến 6).\n\n"
        "  Nếu miền của cặp nào bị rỗng (Domain Wipe-out)\n"
        "  → Backtrack ngay, không cần gán thêm.\n\n"
        "Hiệu quả hơn Backtracking thuần vì phát hiện\n"
        "xung đột sớm hơn."
    ),
    "Min-Conflicts": (
        "MIN-CONFLICTS CSP\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Tìm kiếm cục bộ trên không gian hoàn chỉnh:\n\n"
        "  1. Khởi tạo: gán ngẫu nhiên 7 cặp giá trị\n"
        "     vào 7 cặp vị trí (C1,C2,C3 luôn thỏa).\n"
        "  2. Chỉ cần giải quyết C4: nghịch thế chẵn.\n"
        "  3. Thử lật hướng từng cặp, chọn cặp giảm\n"
        "     xung đột nhiều nhất.\n"
        "  4. Lặp cho đến khi không còn xung đột.\n\n"
        "Ưu điểm: Rất nhanh, hội tụ trong vài bước."
    ),
}

ALGOS = {
    "Backtracking": solve_backtracking,
    "Forward Checking": solve_forward_checking,
    "Min-Conflicts": solve_min_conflicts,
}


# =============================================================
# MAIN UI
# =============================================================
class CSPUI:
=======
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
>>>>>>> Huy
    def __init__(self, parent, algo_name=None):
        self.parent = parent
        parent.withdraw()
        self.win = tk.Toplevel(parent)
<<<<<<< HEAD
        self.win.title("Nhóm 5: Thỏa mãn ràng buộc (CSP) – 15 Puzzle")
        self.win.geometry("1350x800")
        self.win.configure(bg=BG)
        self.win.minsize(1100, 680)
        self.win.protocol("WM_DELETE_WINDOW", self.on_close)

        self.algo_name = algo_name
        self.steps = []
        self.step_idx = -1
        self.solution = {}
        self.auto_playing = False
        self.algo_btns = {}

        self._build_top()
        self._build_middle()
        self._build_bottom()
        if algo_name:
            self.select_algo(algo_name)
        self._show_idle()
=======
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
>>>>>>> Huy

    def on_close(self):
        self.win.destroy()
        self.parent.deiconify()

<<<<<<< HEAD
    # ---------- BUILD ----------
    def _build_top(self):
        f = tk.Frame(self.win, bg=PANEL, pady=8)
        f.pack(fill=tk.X)
        tk.Label(f, text="NHÓM 5: THỎA MÃN RÀNG BUỘC (CSP)",
                 font=("Segoe UI", 14, "bold"), bg=PANEL, fg=ACCENT).pack(side=tk.LEFT, padx=20)
        tk.Button(f, text="◀ Quay lại", font=("Segoe UI", 10, "bold"),
                  bg=BTN_SEL, fg=TEXT, relief="flat", padx=12, pady=4,
                  cursor="hand2", command=self.on_close).pack(side=tk.RIGHT, padx=15)
        for name in reversed(list(ALGOS.keys())):
            b = tk.Button(f, text=name, font=("Segoe UI", 10), bg="#444455", fg=TEXT,
                          relief="flat", padx=12, pady=4, cursor="hand2",
                          command=lambda n=name: self.select_algo(n))
            b.pack(side=tk.RIGHT, padx=4)
            self.algo_btns[name] = b

    def _build_middle(self):
        mf = tk.Frame(self.win, bg=BG)
        mf.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # LEFT — current assignment board
        lf = tk.Frame(mf, bg=CARD, highlightbackground="#2a3a5c", highlightthickness=1)
        lf.pack(side=tk.LEFT, fill=tk.Y, padx=(0,5))
        lf.config(width=290); lf.pack_propagate(False)

        tk.Label(lf, text="TRẠNG THÁI HIỆN TẠI",
                 font=("Segoe UI", 11, "bold"), bg=CARD, fg=ACCENT).pack(pady=(10,5))
        self.cv_main = tk.Canvas(lf, width=260, height=260, bg=CARD, highlightthickness=0)
        self.cv_main.pack(padx=10, pady=5)
        self.lbl_assigned = tk.Label(lf, text="Đã gán: 2/16 (V_0_0=8, V_3_3=0)",
                                     font=("Segoe UI", 9, "bold"), bg=CARD, fg=YELLOW)
        self.lbl_assigned.pack(pady=(2,0))

        # Constraint status
        cst_f = tk.Frame(lf, bg=CARD); cst_f.pack(fill=tk.X, padx=12, pady=8)
        tk.Label(cst_f, text="RÀNG BUỘC:", font=("Segoe UI", 9, "bold"), bg=CARD, fg=ACCENT).pack(anchor="w")
        self.lbl_c = [tk.Label(cst_f, text=t, font=("Segoe UI", 9), bg=CARD, fg=SUB)
                      for t in ["● C1: AllDifferent", "● C2: V_3_3 = 0",
                                "● C3: Đối xứng (= 16)", "● C4: Nghịch thế chẵn"]]
        for l in self.lbl_c: l.pack(anchor="w")

        # CENTER — step detail
        cf = tk.Frame(mf, bg=CARD, highlightbackground="#2a3a5c", highlightthickness=1)
        cf.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        tk.Label(cf, text="CHI TIẾT BƯỚC",
                 font=("Segoe UI", 11, "bold"), bg=CARD, fg=ACCENT).pack(pady=(10,5))
        self.lbl_step_hdr = tk.Label(cf, text="", font=("Segoe UI", 12, "bold"), bg=CARD, fg=YELLOW)
        self.lbl_step_hdr.pack()

        self.cv_center = tk.Canvas(cf, width=420, height=300, bg=CARD, highlightthickness=0)
        self.cv_center.pack(padx=10, pady=5)

        self.lbl_pair_info = tk.Label(cf, text="", font=("Segoe UI", 10), bg=CARD, fg=TEXT,
                                      wraplength=400, justify="left")
        self.lbl_pair_info.pack(padx=10, pady=4)

        self.lbl_result = tk.Label(cf, text="", font=("Segoe UI", 11, "bold"), bg=CARD, fg=GREEN)
        self.lbl_result.pack(pady=4)

        # RIGHT — solution + explanation
        rf = tk.Frame(mf, bg=BG); rf.pack(side=tk.LEFT, fill=tk.BOTH, padx=(5,0))
        rf.config(width=360); rf.pack_propagate(False)

        sf = tk.Frame(rf, bg=CARD, highlightbackground="#2a3a5c", highlightthickness=1)
        sf.pack(fill=tk.X, pady=(0,5))
        tk.Label(sf, text="LỜI GIẢI TÌM ĐƯỢC",
                 font=("Segoe UI", 11, "bold"), bg=CARD, fg=ACCENT).pack(pady=(8,4))
        self.cv_sol = tk.Canvas(sf, width=230, height=230, bg=CARD, highlightthickness=0)
        self.cv_sol.pack(padx=10, pady=4)
        self.lbl_sol_info = tk.Label(sf, text="Chưa có lời giải",
                                     font=("Segoe UI", 9), bg=CARD, fg=SUB)
        self.lbl_sol_info.pack(pady=(0,8))

        ef = tk.Frame(rf, bg=CARD, highlightbackground="#2a3a5c", highlightthickness=1)
        ef.pack(fill=tk.BOTH, expand=True, pady=(5,0))
        tk.Label(ef, text="GIẢI THÍCH",
                 font=("Segoe UI", 10, "bold"), bg=CARD, fg=ACCENT).pack(pady=(8,2))
        self.txt_exp = tk.Text(ef, bg=CARD, fg=TEXT, font=("Segoe UI", 10), wrap=tk.WORD,
                               relief="flat", padx=10, pady=5, state=tk.DISABLED)
        self.txt_exp.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0,5))

    def _build_bottom(self):
        f = tk.Frame(self.win, bg=PANEL, pady=10); f.pack(fill=tk.X)
        for txt, cmd, bg, fg in [
            ("▶ Giải", self.do_solve, GREEN, "#000"),
            ("◀◀ Trước", self.do_prev, BTN, TEXT),
            ("Sau ▶▶", self.do_next, BTN, TEXT),
        ]:
            tk.Button(f, text=txt, font=("Segoe UI", 11, "bold"), bg=bg, fg=fg,
                      relief="flat", padx=18, pady=8, cursor="hand2", command=cmd).pack(side=tk.LEFT, padx=10)
        self.btn_auto = tk.Button(f, text="Tự chạy ⏯", font=("Segoe UI", 11, "bold"),
                                  bg=PURPLE, fg=TEXT, relief="flat", padx=18, pady=8,
                                  cursor="hand2", command=self.toggle_auto)
        self.btn_auto.pack(side=tk.LEFT, padx=10)
        self.lbl_stepnum = tk.Label(f, text="", font=("Segoe UI", 12, "bold"), bg=PANEL, fg=YELLOW)
        self.lbl_stepnum.pack(side=tk.RIGHT, padx=20)
        self.lbl_stats = tk.Label(f, text="", font=("Segoe UI", 10), bg=PANEL, fg=ACCENT)
        self.lbl_stats.pack(side=tk.RIGHT, padx=10)

    # ---------- HELPERS ----------
    def select_algo(self, name):
        self.algo_name = name
        for n, b in self.algo_btns.items():
            b.config(bg=BTN_SEL if n == name else "#444455")
        self.set_exp(ALGO_DESCS.get(name, ""))
=======
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
>>>>>>> Huy

    def set_exp(self, text):
        self.txt_exp.config(state=tk.NORMAL)
        self.txt_exp.delete("1.0", tk.END)
        self.txt_exp.insert(tk.END, text)
        self.txt_exp.config(state=tk.DISABLED)

<<<<<<< HEAD
    def _show_idle(self):
        self.cv_main.delete("all")
        draw_board(self.cv_main, {(0,0):8,(3,3):0}, 58, 10, 10)
        self.cv_center.delete("all")
        self.cv_center.create_text(210, 150, text='Nhấn "▶ Giải" để bắt đầu',
                                   fill=SUB, font=("Segoe UI", 13))
        self.cv_sol.delete("all")
        self.cv_sol.create_text(115, 115, text="Chưa có\nlời giải",
                                fill=SUB, font=("Segoe UI", 12), justify="center")
        self.lbl_sol_info.config(text="Chưa có lời giải", fg=SUB)
        self.lbl_stepnum.config(text="")
        self.lbl_step_hdr.config(text="")
        self.lbl_pair_info.config(text="")
        self.lbl_result.config(text="")
        self.lbl_stats.config(text="")
        for l in self.lbl_c: l.config(fg=SUB)

    # ---------- SHOW STEP ----------
    def show_step(self, idx):
        if idx < 0 or idx >= len(self.steps): return
        self.step_idx = idx
        st = self.steps[idx]
        self.lbl_stepnum.config(text=f"Bước {idx+1}/{len(self.steps)}")

        asgn = st.get('assignment', {})
        hl   = set(st.get('highlight', []))
        phase = st.get('phase', '')

        # Main board
        self.cv_main.delete("all")
        draw_board(self.cv_main, asgn, 58, 10, 10, highlight=hl, border=ACCENT)
        n = len(asgn)
        self.lbl_assigned.config(text=f"Đã gán: {n}/16 biến  ({n*100//16}%)")

        # Center canvas: show current pair assignment
        self.cv_center.delete("all")
        self._draw_pairs_center(asgn, hl, st)

        # Step header
        pair_idx = st.get('pair_idx', -1)
        if pair_idx >= 0:
            self.lbl_step_hdr.config(text=f"Cặp {pair_idx+1}/7 — {phase.upper()}")
        else:
            self.lbl_step_hdr.config(text=phase.upper())

        # Pair info
        vp = st.get('val_pair')
        pp = st.get('pos_pair')
        orient = st.get('orient')
        if vp and pp:
            p1, p2 = pp
            info = (f"Cặp giá trị: {vp}   Hướng: {orient}\n"
                    f"V_{p1[0]}_{p1[1]} = {orient[0]}   V_{p2[0]}_{p2[1]} = {orient[1]}")
        elif st.get('orient_info'):
            bi, old_o, new_o, p1, p2 = st['orient_info']
            info = f"Lật cặp {bi+1}: V_{p1[0]}_{p1[1]}&V_{p2[0]}_{p2[1]}  {old_o}→{new_o}"
        else:
            info = ""
        self.lbl_pair_info.config(text=info)

        # Result label
        ok = st.get('ok')
        inv = st.get('inv')
        conflicts = st.get('conflicts')
        if phase == 'solution':
            self.lbl_result.config(text=f"🎉 Lời giải! Nghịch thế={inv} (CHẴN ✓)", fg=GREEN)
        elif phase == 'backtrack':
            self.lbl_result.config(text="← Backtrack", fg=YELLOW)
        elif phase == 'solvability_fail':
            self.lbl_result.config(text="✗ Nghịch thế LẺ — Backtrack", fg=RED)
        elif ok is True:
            self.lbl_result.config(text="✓ Gán hợp lệ — tiếp tục", fg=GREEN)
        elif ok is False:
            self.lbl_result.config(text="✗ Domain Wipe-out / Vi phạm", fg=RED)
        elif conflicts is not None:
            self.lbl_result.config(
                text=f"Xung đột: {conflicts} | Nghịch thế: {inv}",
                fg=GREEN if conflicts == 0 else RED)
        else:
            self.lbl_result.config(text="")

        # Constraint indicators
        vals = list(asgn.values())
        c1 = len(vals) == len(set(vals))
        c2 = asgn.get((3,3), 0) == 0
        c3 = all(asgn.get(p1,0) + asgn.get(p2,0) == 16
                 for p1,p2 in SYM_POS_PAIRS if p1 in asgn and p2 in asgn)
        c4 = None
        if len(asgn) == 16:
            flat = [asgn[(r,c)] for r in range(4) for c in range(4)]
            c4 = count_inversions(flat) % 2 == 0
        for i, (lbl, ok2) in enumerate(zip(self.lbl_c, [c1, c2, c3, c4])):
            if ok2 is None: lbl.config(fg=SUB)
            else: lbl.config(fg=GREEN if ok2 else RED)

        # Solution
        if self.solution and len(self.solution) == 16:
            self.cv_sol.delete("all")
            draw_board(self.cv_sol, self.solution, 48, 8, 8, border=GREEN)
            flat = [self.solution[(r,c)] for r in range(4) for c in range(4)]
            inv2 = count_inversions(flat)
            self.lbl_sol_info.config(
                text=f"Nghịch thế: {inv2} ({'CHẴN ✓' if inv2%2==0 else 'LẺ ✗'})", fg=GREEN)
        elif phase == 'failed':
            self.cv_sol.delete("all")
            self.cv_sol.create_text(115,115, text="Không tìm\nthấy",
                                    fill=RED, font=("Segoe UI",12,"bold"), justify="center")

        # Explanation
        self.set_exp(st.get('text', ''))

    def _draw_pairs_center(self, asgn, hl, st):
        """Draw the 7 position-pairs and their assigned values in center canvas."""
        cv = self.cv_center
        cv.delete("all")
        # Title
        cv.create_text(210, 14, text="7 CẶP VỊ TRÍ ĐỐI XỨNG QUA TÂM",
                       fill=ACCENT, font=("Segoe UI", 10, "bold"))
        # Draw each pair as two boxes with a "+" between
        box_w, box_h = 50, 30; gap_x = 10; rows = 4; cols = 2
        x_starts = [20, 240]
        pair_idx_hl = st.get('pair_idx', -1)
        for i, ((p1, p2)) in enumerate(SYM_POS_PAIRS):
            col = i % cols; row = i // cols
            xbase = x_starts[col]; y = 35 + row * 50
            # Is this pair currently being highlighted?
            is_hl = (i == pair_idx_hl) or (p1 in hl) or (p2 in hl)
            border_col = YELLOW if is_hl else "#3a3a5a"
            lw = 2 if is_hl else 1

            for pi, pos in enumerate([p1, p2]):
                xb = xbase + pi * (box_w + gap_x + 20)
                val = asgn.get(pos)
                fill = YELLOW if pos in hl else (CELL if val is not None else "#252535")
                fg = "#000" if pos in hl else TEXT
                cv.create_rectangle(xb, y, xb+box_w, y+box_h, fill=fill,
                                    outline=border_col, width=lw)
                if val is None:
                    cv.create_text(xb+box_w//2, y+box_h//2, text="?", fill=SUB,
                                   font=("Segoe UI", 11))
                elif val == 0:
                    cv.create_text(xb+box_w//2, y+box_h//2, text="[ ]", fill=SUB,
                                   font=("Segoe UI", 9))
                else:
                    cv.create_text(xb+box_w//2, y+box_h//2, text=str(val), fill=fg,
                                   font=("Segoe UI", 12, "bold"))
                # Position label
                cv.create_text(xb+box_w//2, y+box_h+6,
                                text=f"({pos[0]},{pos[1]})", fill=SUB,
                                font=("Segoe UI", 7))

            # "+" sign and sum display
            mid_x = xbase + box_w + gap_x//2 + 10
            cv.create_text(mid_x, y+box_h//2, text="+", fill=ACCENT,
                           font=("Segoe UI", 11, "bold"))
            v1 = asgn.get(p1); v2 = asgn.get(p2)
            if v1 is not None and v2 is not None:
                s = v1 + v2
                col2 = GREEN if s == 16 else RED
                cv.create_text(mid_x, y+box_h+6, text=f"={s}",
                               fill=col2, font=("Segoe UI", 8, "bold"))

            # Pair label
            cv.create_text(xbase - 8, y+box_h//2, text=f"{i+1}.", fill=SUB,
                           font=("Segoe UI", 9))

        # Fixed cells: V_0_0=8 and V_3_3=0
        cv.create_text(210, 250, fill=TEXT, font=("Segoe UI", 9),
                       text="V_0_0 = 8 (cố định)   |   V_3_3 = 0 (ô trống)")

    # ---------- ACTIONS ----------
    def do_solve(self):
        if not self.algo_name:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn thuật toán!", parent=self.win)
            return
        self.auto_playing = False
        self.btn_auto.config(text="Tự chạy ⏯", bg=PURPLE)
        self.solution = {}
        self._show_idle()
        self.set_exp(f"Đang chạy {self.algo_name}...")
        self.win.update()

        random.seed(int(time.time()))
        t0 = time.time()
        sol, steps = ALGOS[self.algo_name]()
        elapsed = time.time() - t0

        self.steps = steps
        self.solution = sol
        self.lbl_stats.config(text=f"{len(steps)} bước | {elapsed:.3f}s")

        if steps:
            self.show_step(0)
        if sol and len(sol) == 16:
            self._print_solution(sol)
            # Show solution on board
            self.cv_sol.delete("all")
            draw_board(self.cv_sol, sol, 48, 8, 8, border=GREEN)
            flat = [sol[(r,c)] for r in range(4) for c in range(4)]
            inv2 = count_inversions(flat)
            self.lbl_sol_info.config(
                text=f"Nghịch thế: {inv2} ({'CHẴN ✓' if inv2%2==0 else 'LẺ ✗'})", fg=GREEN)

    def _print_solution(self, sol):
        print("\n" + "="*45)
        print("  CẤU HÌNH BÀN CỜ 4x4 HỢP LỆ (CSP):")
        print("="*45)
        for r in range(4):
            row_str = "  "
            for c in range(4):
                v = sol.get((r,c), 0)
                row_str += "[ ]  " if v == 0 else f"{v:2}   "
            print(row_str)
        flat = [sol.get((r,c),0) for r in range(4) for c in range(4)]
        inv = count_inversions(flat)
        print(f"\n  Nghịch thế: {inv}  ({'CHẴN → Có thể giải' if inv%2==0 else 'LẺ → Không giải được'})")
        print("="*45 + "\n")

    def do_next(self):
        if self.step_idx < len(self.steps) - 1:
            self.show_step(self.step_idx + 1)
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
>>>>>>> Huy

    def do_prev(self):
        if self.step_idx > 0:
            self.show_step(self.step_idx - 1)

<<<<<<< HEAD
    def toggle_auto(self):
        if not self.steps: return
        self.auto_playing = not self.auto_playing
        if self.auto_playing:
            self.btn_auto.config(text="Dừng ⏸", bg=BTN_SEL)
            self._run_auto()
        else:
            self.btn_auto.config(text="Tự chạy ⏯", bg=PURPLE)

    def _run_auto(self):
        if self.auto_playing and self.step_idx < len(self.steps) - 1:
            self.do_next()
            self.win.after(500, self._run_auto)
        else:
            self.auto_playing = False
            self.btn_auto.config(text="Tự chạy ⏯", bg=PURPLE)


def open_ui(parent, algo_name):
    CSPUI(parent, algo_name)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Nhóm 5 CSP Standalone")
    root.withdraw()
    def custom_close(ui):
        ui.win.destroy()
        root.destroy()
    ui = CSPUI(root, "Backtracking")
    ui.on_close = lambda: custom_close(ui)
    root.mainloop()
=======
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
>>>>>>> Huy
