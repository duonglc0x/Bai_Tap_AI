import tkinter as tk
from tkinter import messagebox
import random

# --- LOGIC MÔI TRƯỜNG ---
class PuzzleEnv:
    GOAL1 = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 0)
    GOAL2 = (0, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1)

    @staticmethod
    def get_neighbors(state, last_state):
        neighbors = []
        idx = state.index(0)
        r, c = divmod(idx, 4)
        for move in [-4, 4, -1, 1]:
            n_idx = idx + move
            if 0 <= n_idx < 16 and not (move == 1 and c == 3) and not (move == -1 and c == 0):
                new_s = list(state)
                new_s[idx], new_s[n_idx] = new_s[n_idx], new_s[idx]
                t_s = tuple(new_s)
                if t_s != last_state: neighbors.append(t_s)
        return neighbors

    @staticmethod
    def heuristic(state, goal):
        dist = 0
        for i, val in enumerate(state):
            if val == 0: continue
            tar_idx = goal.index(val)
            dist += abs(i // 4 - tar_idx // 4) + abs(i % 4 - tar_idx % 4)
        return dist

    @staticmethod
    def count_misplaced(state, goal):
        return sum(1 for i in range(16) if state[i] != goal[i] and state[i] != 0)

# --- THUẬT TOÁN ---
class Minimax:
    def get_move(self, s, l, g, d=2):
        def m(s, d, is_max, l):
            if d == 0: return -PuzzleEnv.heuristic(s, g), None
            moves = PuzzleEnv.get_neighbors(s, l)
            if not moves: return -PuzzleEnv.heuristic(s, g), None
            best = -float('inf') if is_max else float('inf')
            best_move = moves[0]
            for m_next in moves:
                val, _ = m(m_next, d-1, not is_max, s)
                if (is_max and val > best) or (not is_max and val < best):
                    best, best_move = val, m_next
            return best, best_move
        
        moves = PuzzleEnv.get_neighbors(s, l)
        if not moves: return s, []
        _, best = m(s, d, True, l)
        return best, moves

class AlphaBeta(Minimax):
    def get_move(self, s, l, g, d=2):
        def ab(s, d, a, b, is_max, l):
            if d == 0: return -PuzzleEnv.heuristic(s, g), None
            moves = PuzzleEnv.get_neighbors(s, l)
            best_move = moves[0]
            if is_max:
                v = -float('inf')
                for m in moves:
                    val, _ = ab(m, d-1, a, b, False, s)
                    if val > v: v, best_move = val, m
                    a = max(a, val)
                    if b <= a: break
                return v, best_move
            else:
                v = float('inf')
                for m in moves:
                    val, _ = ab(m, d-1, a, b, True, s)
                    if val < v: v, best_move = val, m
                    b = min(b, val)
                    if b <= a: break
                return v, best_move
        
        moves = PuzzleEnv.get_neighbors(s, l)
        if not moves: return s, []
        _, best = ab(s, d, -float('inf'), float('inf'), True, l)
        return best, moves

class Expectimax(Minimax):
    def get_move(self, s, l, g, d=2):
        def exp(s, d, is_max, l):
            if d == 0: return -PuzzleEnv.heuristic(s, g), None
            moves = PuzzleEnv.get_neighbors(s, l)
            if is_max:
                v = -float('inf'); best_m = moves[0]
                for m in moves:
                    val, _ = exp(m, d-1, False, s)
                    if val > v: v, best_m = val, m
                return v, best_m
            else: return sum(exp(m, d-1, True, s)[0] for m in moves)/len(moves), None
        
        moves = PuzzleEnv.get_neighbors(s, l)
        if not moves: return s, []
        _, best = exp(s, d, True, l)
        return best, moves

# --- GIAO DIỆN UI ---
class AdversarialUI:
    def __init__(self, parent, algo_name):
        self.win = tk.Toplevel(parent) # Tạo cửa sổ mới đè lên parent
        self.win.title(f"Human vs {algo_name}")
        self.win.geometry("1000x700")
        self.win.configure(bg="#1e1e24")

        # Khởi tạo thuật toán
        solvers = {"Minimax": Minimax(), "Alpha-Beta Pruning": AlphaBeta(), "Expectimax": Expectimax()}
        self.ai = solvers.get(algo_name, Minimax())
        self.MAX_MOVES = 50
        
        # Gọi reset_game SAU KHI UI đã sẵn sàng
        self.setup_ui()
        self.reset_game()

    def setup_ui(self):
        # Layout chính
        main = tk.Frame(self.win, bg="#1e1e24")
        main.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

        # Cột P1
        self.f1 = self.create_side_panel(main, "GOAL CỦA BẠN", PuzzleEnv.GOAL1, "#3a86ff")
        self.f1.pack(side=tk.LEFT, fill=tk.Y, padx=10)

        # Cột giữa
        center = tk.Frame(main, bg="#1e1e24")
        center.pack(side=tk.LEFT, expand=True)
        self.cv = tk.Canvas(center, width=400, height=400, bg="#2b2b36", highlightthickness=0)
        self.cv.pack()
        self.cv.bind("<Button-1>", self.on_click)
        
        self.lbl_status = tk.Label(center, text="Bước: 0/50", fg="white", bg="#1e1e24", font=("Arial", 14))
        self.lbl_status.pack(pady=10)
        tk.Button(center, text="Reset Ván Mới", command=self.reset_game, bg="#444455", fg="white").pack()

        # Cột P2
        self.f2 = self.create_side_panel(main, "GOAL CỦA MÁY", PuzzleEnv.GOAL2, "#ef476f")
        self.f2.pack(side=tk.LEFT, fill=tk.Y, padx=10)

    def create_side_panel(self, parent, title, goal, color):
        f = tk.Frame(parent, bg="#2b2b36", padx=10, pady=10)
        tk.Label(f, text=title, fg=color, bg="#2b2b36", font=("Arial", 10, "bold")).pack()
        cv = tk.Canvas(f, width=120, height=120, bg="black", highlightthickness=0)
        cv.pack(pady=5)
        for i, val in enumerate(goal):
            if val == 0: continue
            r, c = divmod(i, 4)
            cv.create_rectangle(c*30+2, r*30+2, c*30+28, r*30+28, fill=color, outline="")
            cv.create_text(c*30+15, r*30+15, text=str(val), fill="white", font=("Arial", 8))
        
        tk.Label(f, text="AI Frontier:", fg="white", bg="#2b2b36").pack(anchor="w")
        lb = tk.Listbox(f, width=25, height=10, bg="#1e1e24", fg="white")
        lb.pack(fill=tk.BOTH, expand=True)
        setattr(f, 'listbox', lb)
        return f

    def on_click(self, event):
        if self.move_count >= self.MAX_MOVES: return
        c, r = event.x // 100, event.y // 100
        if not (0 <= c < 4 and 0 <= r < 4): return
        
        idx = r * 4 + c
        zero_idx = self.state.index(0)
        if abs(idx//4 - zero_idx//4) + abs(idx%4 - zero_idx%4) == 1:
            s_list = list(self.state)
            s_list[idx], s_list[zero_idx] = s_list[zero_idx], s_list[idx]
            new_state = tuple(s_list)
            if new_state == self.last_state: return 
            
            self.last_state = self.state
            self.state = new_state
            self.move_count += 1
            self.update_status()
            self.draw_all()
            if self.move_count >= self.MAX_MOVES: self.game_over()
            else: self.win.after(300, self.ai_turn)

    def ai_turn(self):
        new_state, frontier = self.ai.get_move(self.state, self.last_state, PuzzleEnv.GOAL2)
        if new_state:
            self.last_state = self.state
            self.state = new_state
            self.move_count += 1
            self.update_status()
        self.update_frontier(frontier)
        self.draw_all()
        if self.move_count >= self.MAX_MOVES: self.game_over()

    def update_frontier(self, frontier):
        self.f2.listbox.delete(0, tk.END)
        for move in frontier: self.f2.listbox.insert(tk.END, str(move)[:15] + "...")

    def update_status(self):
        self.lbl_status.config(text=f"Bước: {self.move_count}/{self.MAX_MOVES}")

    def game_over(self):
        mis1 = PuzzleEnv.count_misplaced(self.state, PuzzleEnv.GOAL1)
        mis2 = PuzzleEnv.count_misplaced(self.state, PuzzleEnv.GOAL2)
        messagebox.showinfo("Kết quả", f"Hết 50 bước!\n\nSố ô sai của bạn: {mis1}\nSố ô sai của máy: {mis2}")

    def draw_all(self):
        self.cv.delete("all")
        for i, val in enumerate(self.state):
            if val == 0: continue
            r, c = divmod(i, 4)
            self.cv.create_rectangle(c*100+5, r*100+5, c*100+95, r*100+95, fill="#4a4e69", outline="")
            self.cv.create_text(c*100+50, r*100+50, text=str(val), fill="white", font=("Arial", 20, "bold"))
        self.cv.update()

    def reset_game(self):
        arr = list(range(16)); random.shuffle(arr); self.state = tuple(arr)
        self.last_state = None; self.move_count = 0
        self.update_status()
        if hasattr(self, 'cv'): self.draw_all()

def open_ui(root, algo_name):
    AdversarialUI(root, algo_name)
