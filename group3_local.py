import tkinter as tk
from tkinter import messagebox
import copy, random

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

GOAL = [[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,0]]
DEFAULT = [[1,2,3,4],[5,6,0,8],[9,10,7,11],[13,14,15,12]]

# ===== PUZZLE STATE =====
class S:
    def __init__(s, b): s.board = [r[:] for r in b]
    def blank(s):
        for i in range(4):
            for j in range(4):
                if s.board[i][j]==0: return i,j
    def nbrs(s):
        res=[]; bi,bj=s.blank()
        for di,dj,nm in [(-1,0,"↑"),(1,0,"↓"),(0,-1,"←"),(0,1,"→")]:
            ni,nj=bi+di,bj+dj
            if 0<=ni<4 and 0<=nj<4:
                b=[r[:] for r in s.board]; b[bi][bj],b[ni][nj]=b[ni][nj],b[bi][bj]
                res.append((S(b),nm,s.board[ni][nj]))
        return res
    def h(s):
        c=0
        for i in range(4):
            for j in range(4):
                if s.board[i][j]!=0 and s.board[i][j]!=GOAL[i][j]: c+=1
        return c
    def __eq__(s,o): return s.board==o.board

# ===== ALGORITHMS =====
def simple_hc(state):
    steps=[]; cur=state; vis=[S(cur.board)]
    for _ in range(500):
        ch=cur.h(); children=[(n,d,t,n.h()) for n,d,t in cur.nbrs()]
        step={'cur':cur,'children':children,'h':ch,'text':'','chosen':-1}
        if ch==0:
            step['text']="🎉 Đã đạt trạng thái đích! h = 0"; steps.append(step); break
        found=False
        for i,(n,d,t,nh) in enumerate(children):
            if nh<ch:
                step['text']=f"Simple Hill Climbing: Duyệt lần lượt các trạng thái con.\nTrạng thái con '{d}' (trượt ô {t}) có h={nh} < h hiện tại={ch}.\n→ Chọn ngay trạng thái đầu tiên tốt hơn."
                step['chosen']=i; steps.append(step); cur=n; vis.append(S(cur.board)); found=True; break
        if not found:
            step['text']=f"Không có trạng thái con nào có h < {ch}.\n→ Dừng lại tại cực trị địa phương (h={ch})."; steps.append(step); break
    return steps,vis

def steepest_hc(state):
    steps=[]; cur=state; vis=[S(cur.board)]
    for _ in range(500):
        ch=cur.h(); children=[(n,d,t,n.h()) for n,d,t in cur.nbrs()]
        step={'cur':cur,'children':children,'h':ch,'text':'','chosen':-1}
        if ch==0:
            step['text']="🎉 Đã đạt trạng thái đích! h = 0"; steps.append(step); break
        bi=min(range(len(children)),key=lambda i:children[i][3]); bh=children[bi][3]
        hl=", ".join([f"h({c[1]})={c[3]}" for c in children])
        if bh<ch:
            n,d,t,nh=children[bi]
            step['text']=f"Steepest-Ascent: Đánh giá TẤT CẢ trạng thái con:\n{hl}\nTrạng thái '{d}' (trượt ô {t}) có h={nh} nhỏ nhất và < h hiện tại={ch}.\n→ Chọn trạng thái tốt nhất."
            step['chosen']=bi; steps.append(step); cur=n; vis.append(S(cur.board))
        else:
            step['text']=f"Đánh giá tất cả: {hl}.\nKhông có trạng thái nào tốt hơn h hiện tại={ch}.\n→ Dừng lại (cực trị địa phương)."; steps.append(step); break
    return steps,vis

def stochastic_hc(state):
    steps=[]; cur=state; vis=[S(cur.board)]
    for _ in range(500):
        ch=cur.h(); children=[(n,d,t,n.h()) for n,d,t in cur.nbrs()]
        step={'cur':cur,'children':children,'h':ch,'text':'','chosen':-1}
        if ch==0:
            step['text']="🎉 Đã đạt trạng thái đích! h = 0"; steps.append(step); break
        imp=[(i,n,d,t,nh) for i,(n,d,t,nh) in enumerate(children) if nh<ch]
        if imp:
            ci,n,d,t,nh=random.choice(imp)
            step['text']=f"Stochastic: Tìm thấy {len(imp)} trạng thái cải thiện.\nChọn ngẫu nhiên: '{d}' (trượt ô {t}), h={nh} < h hiện tại={ch}.\n→ Di chuyển đến trạng thái được chọn ngẫu nhiên."
            step['chosen']=ci; steps.append(step); cur=n; vis.append(S(cur.board))
        else:
            step['text']=f"Không có trạng thái cải thiện (tất cả h ≥ {ch}).\n→ Dừng lại (cực trị địa phương)."; steps.append(step); break
    return steps,vis

ALGOS={"Simple Hill Climbing":simple_hc,"Steepest-Ascent Hill Climbing":steepest_hc,"Stochastic Hill Climbing":stochastic_hc}

# ===== DRAWING HELPERS =====
def draw_board(canvas, board, cs, x0, y0, border_color=None):
    gap=2; total=4*cs+3*gap
    canvas.create_rectangle(x0-3,y0-3,x0+total+3,y0+total+3, fill=PANEL, outline=border_color or PANEL, width=3 if border_color else 0)
    for i in range(4):
        for j in range(4):
            x=x0+j*(cs+gap); y=y0+i*(cs+gap); v=board[i][j]
            if v==0:
                canvas.create_rectangle(x,y,x+cs,y+cs,fill=CELL_E,outline=CELL_E)
            else:
                ok = v==GOAL[i][j]
                c = "#2d6a4f" if ok else CELL
                canvas.create_rectangle(x,y,x+cs,y+cs,fill=c,outline="#4a6d8c",width=1)
                fs=max(cs//3,8)
                canvas.create_text(x+cs//2,y+cs//2,text=str(v),fill=TEXT,font=("Segoe UI",fs,"bold"))
    return total

# ===== INPUT DIALOG =====
def input_dialog(parent, callback):
    dlg=tk.Toplevel(parent); dlg.title("Nhập trạng thái 15-Puzzle"); dlg.configure(bg=BG)
    dlg.geometry("380x420"); dlg.resizable(False,False); dlg.grab_set()
    tk.Label(dlg,text="Nhập số 0-15 (0 = ô trống)",font=("Segoe UI",12,"bold"),bg=BG,fg=TEXT).pack(pady=(15,5))
    tk.Label(dlg,text="Mỗi số chỉ xuất hiện 1 lần",font=("Segoe UI",9),bg=BG,fg=SUB).pack(pady=(0,10))
    gf=tk.Frame(dlg,bg=BG); gf.pack(pady=5)
    entries=[]
    for i in range(4):
        row=[]
        for j in range(4):
            e=tk.Entry(gf,width=4,font=("Segoe UI",16,"bold"),justify="center",bg=PANEL,fg=TEXT,insertbackground=TEXT,relief="flat",highlightthickness=2,highlightbackground="#3d5a80",highlightcolor=ACCENT)
            e.grid(row=i,column=j,padx=4,pady=4,ipady=6)
            v=DEFAULT[i][j]
            if v!=0: e.insert(0,str(v))
            row.append(e)
        entries.append(row)
    def do_random():
        b=[r[:] for r in GOAL]
        bi,bj=3,3
        for _ in range(80):
            moves=[]
            for di,dj in [(-1,0),(1,0),(0,-1),(0,1)]:
                ni,nj=bi+di,bj+dj
                if 0<=ni<4 and 0<=nj<4: moves.append((ni,nj))
            ni,nj=random.choice(moves); b[bi][bj],b[ni][nj]=b[ni][nj],b[bi][bj]; bi,bj=ni,nj
        for i in range(4):
            for j in range(4):
                entries[i][j].delete(0,tk.END)
                if b[i][j]!=0: entries[i][j].insert(0,str(b[i][j]))
    def do_ok():
        try:
            board=[]
            for i in range(4):
                row=[]
                for j in range(4):
                    t=entries[i][j].get().strip()
                    row.append(0 if t=="" else int(t))
                board.append(row)
            vals=sorted([board[i][j] for i in range(4) for j in range(4)])
            if vals!=list(range(16)):
                messagebox.showerror("Lỗi","Phải chứa đúng các số 0-15, không trùng!",parent=dlg); return
            callback(board); dlg.destroy()
        except ValueError:
            messagebox.showerror("Lỗi","Chỉ nhập số nguyên 0-15!",parent=dlg)
    bf=tk.Frame(dlg,bg=BG); bf.pack(pady=15)
    tk.Button(bf,text="🎲 Ngẫu nhiên",font=("Segoe UI",11),bg="#6930c3",fg=TEXT,relief="flat",padx=15,pady=6,cursor="hand2",command=do_random).pack(side=tk.LEFT,padx=8)
    tk.Button(bf,text="✓ Xác nhận",font=("Segoe UI",11),bg=GREEN,fg="#000",relief="flat",padx=15,pady=6,cursor="hand2",command=do_ok).pack(side=tk.LEFT,padx=8)
    tk.Button(bf,text="✕ Hủy",font=("Segoe UI",11),bg=RED,fg=TEXT,relief="flat",padx=15,pady=6,cursor="hand2",command=dlg.destroy).pack(side=tk.LEFT,padx=8)

# ===== MAIN UI =====
class PuzzleUI:
    def __init__(self, parent, algo_name=None):
        self.parent=parent; parent.withdraw()
        self.win=tk.Toplevel(parent); self.win.title("Nhóm 3: Tìm kiếm cục bộ - 15 Puzzle")
        self.win.geometry("1350x780"); self.win.configure(bg=BG); self.win.minsize(1200,700)
        self.win.protocol("WM_DELETE_WINDOW",self.on_close)
        self.board=[r[:] for r in DEFAULT]; self.algo=algo_name; self.steps=[]; self.visited=[]; self.step_idx=-1
        self.algo_btns={}
        self._build_top(); self._build_middle(); self._build_bottom()
        if algo_name: self.select_algo(algo_name)
        self.draw_initial()

    def on_close(self):
        self.win.destroy(); self.parent.deiconify()

    def _build_top(self):
        f=tk.Frame(self.win,bg=PANEL,pady=8); f.pack(fill=tk.X,padx=0)
        tk.Label(f,text="NHÓM 3: TÌM KIẾM CỤC BỘ",font=("Segoe UI",14,"bold"),bg=PANEL,fg=ACCENT).pack(side=tk.LEFT,padx=20)
        # Back button
        bb=tk.Button(f,text="◀ Quay lại",font=("Segoe UI",10,"bold"),bg=RED,fg=TEXT,relief="flat",padx=12,pady=4,cursor="hand2",command=self.on_close)
        bb.pack(side=tk.RIGHT,padx=15)
        # Algo buttons
        for name in reversed(list(ALGOS.keys())):
            b=tk.Button(f,text=name,font=("Segoe UI",10),bg="#444455",fg=TEXT,relief="flat",padx=12,pady=4,cursor="hand2",
                        command=lambda n=name:self.select_algo(n))
            b.pack(side=tk.RIGHT,padx=4)
            self.algo_btns[name]=b

    def select_algo(self, name):
        self.algo=name
        for n,b in self.algo_btns.items():
            if n==name: b.config(bg=BTN_SEL)
            else: b.config(bg="#444455")

    def _build_middle(self):
        mf=tk.Frame(self.win,bg=BG); mf.pack(fill=tk.BOTH,expand=True,padx=10,pady=5)
        # Left: current node
        lf=tk.Frame(mf,bg=CARD,highlightbackground="#2a3a5c",highlightthickness=1); lf.pack(side=tk.LEFT,fill=tk.Y,padx=(0,5))
        tk.Label(lf,text="NODE ĐANG XÉT",font=("Segoe UI",11,"bold"),bg=CARD,fg=ACCENT).pack(pady=(10,5))
        self.cv_cur=tk.Canvas(lf,width=260,height=280,bg=CARD,highlightthickness=0); self.cv_cur.pack(padx=15,pady=5)
        self.lbl_h=tk.Label(lf,text="h = ?",font=("Segoe UI",14,"bold"),bg=CARD,fg=YELLOW); self.lbl_h.pack(pady=(0,10))
        # Center: children
        cf=tk.Frame(mf,bg=CARD,highlightbackground="#2a3a5c",highlightthickness=1); cf.pack(side=tk.LEFT,fill=tk.BOTH,expand=True,padx=5)
        tk.Label(cf,text="CÁC NODE CON",font=("Segoe UI",11,"bold"),bg=CARD,fg=ACCENT).pack(pady=(10,5))
        self.children_frame=tk.Frame(cf,bg=CARD); self.children_frame.pack(fill=tk.BOTH,expand=True,padx=10,pady=5)
        # Right: visited + explanation
        rf=tk.Frame(mf,bg=BG); rf.pack(side=tk.LEFT,fill=tk.BOTH,padx=(5,0))
        rf.config(width=350); rf.pack_propagate(False)
        # Visited
        vf=tk.Frame(rf,bg=CARD,highlightbackground="#2a3a5c",highlightthickness=1); vf.pack(fill=tk.BOTH,expand=True,pady=(0,5))
        tk.Label(vf,text="ĐÃ XÉT",font=("Segoe UI",10,"bold"),bg=CARD,fg=ACCENT).pack(pady=(8,2))
        vc=tk.Canvas(vf,bg=CARD,highlightthickness=0); vc.pack(fill=tk.BOTH,expand=True,side=tk.LEFT)
        vs=tk.Scrollbar(vf,orient=tk.VERTICAL,command=vc.yview); vs.pack(side=tk.RIGHT,fill=tk.Y)
        vc.configure(yscrollcommand=vs.set)
        self.vis_inner=tk.Frame(vc,bg=CARD); vc.create_window((0,0),window=self.vis_inner,anchor="nw")
        self.vis_inner.bind("<Configure>",lambda e:vc.configure(scrollregion=vc.bbox("all")))
        self.vis_canvas=vc
        # Explanation
        ef=tk.Frame(rf,bg=CARD,highlightbackground="#2a3a5c",highlightthickness=1,height=200); ef.pack(fill=tk.X,pady=(5,0)); ef.pack_propagate(False)
        tk.Label(ef,text="GIẢI THÍCH",font=("Segoe UI",10,"bold"),bg=CARD,fg=ACCENT).pack(pady=(8,2))
        self.txt_exp=tk.Text(ef,bg=CARD,fg=TEXT,font=("Segoe UI",10),wrap=tk.WORD,relief="flat",padx=10,pady=5,insertbackground=TEXT,state=tk.DISABLED)
        self.txt_exp.pack(fill=tk.BOTH,expand=True,padx=5,pady=(0,5))

    def _build_bottom(self):
        f=tk.Frame(self.win,bg=PANEL,pady=10); f.pack(fill=tk.X)
        btns=[
            ("📝 Nhập tay",self.do_input,"#6930c3"),
            ("▶ Giải",self.do_solve,GREEN),
            ("◀◀ Bước trước",self.do_prev,BTN),
            ("Bước sau ▶▶",self.do_next,BTN),
        ]
        for txt,cmd,clr in btns:
            tk.Button(f,text=txt,font=("Segoe UI",11,"bold"),bg=clr,fg=TEXT if clr!=GREEN else "#000",relief="flat",padx=18,pady=8,cursor="hand2",command=cmd).pack(side=tk.LEFT,padx=10)
        self.lbl_step=tk.Label(f,text="",font=("Segoe UI",12,"bold"),bg=PANEL,fg=YELLOW); self.lbl_step.pack(side=tk.RIGHT,padx=20)

    # ===== DISPLAY =====
    def draw_initial(self):
        self.cv_cur.delete("all")
        draw_board(self.cv_cur,self.board,58,10,10,border_color=ACCENT)
        self.lbl_h.config(text=f"h = {S(self.board).h()}")
        for w in self.children_frame.winfo_children(): w.destroy()
        tk.Label(self.children_frame,text='Nhấn "▶ Giải" để bắt đầu\nhoặc "📝 Nhập tay" để đổi trạng thái',font=("Segoe UI",11),bg=CARD,fg=SUB,justify="center").pack(expand=True)
        self.set_exp("Chọn thuật toán ở thanh trên và nhấn Giải.")
        self.lbl_step.config(text="")
        for w in self.vis_inner.winfo_children(): w.destroy()

    def show_step(self, idx):
        if idx<0 or idx>=len(self.steps): return
        self.step_idx=idx; st=self.steps[idx]
        self.lbl_step.config(text=f"Bước {idx+1}/{len(self.steps)}")
        # Current node
        self.cv_cur.delete("all")
        draw_board(self.cv_cur,st['cur'].board,58,10,10,border_color=ACCENT)
        self.lbl_h.config(text=f"h = {st['h']}")
        # Children
        for w in self.children_frame.winfo_children(): w.destroy()
        children=st['children']; chosen=st['chosen']
        cols=2; cs=42; gap=2; grid_px=4*(cs+gap)+6
        for i,(n,d,t,nh) in enumerate(children):
            r,c=divmod(i,cols)
            cf=tk.Frame(self.children_frame,bg=CARD); cf.grid(row=r,column=c,padx=8,pady=6,sticky="n")
            is_chosen=i==chosen
            lbl_dir=tk.Label(cf,text=f"Trượt ô {t} {d}",font=("Segoe UI",9,"bold"),bg=CARD,fg=GREEN if is_chosen else TEXT)
            lbl_dir.pack(pady=(2,2))
            cv=tk.Canvas(cf,width=grid_px+10,height=grid_px+10,bg=CARD,highlightthickness=0); cv.pack()
            bc=GREEN if is_chosen else None
            draw_board(cv,n.board,cs,5,5,border_color=bc)
            hc=GREEN if is_chosen else (RED if nh>st['h'] else YELLOW)
            tag=" ★" if is_chosen else ""
            tk.Label(cf,text=f"h = {nh}{tag}",font=("Segoe UI",10,"bold"),bg=CARD,fg=hc).pack(pady=(2,4))
        # Visited
        for w in self.vis_inner.winfo_children(): w.destroy()
        vcs=22; vgap=1; vgrid=4*(vcs+vgap)+6
        vcols=max(1,(330)//(vgrid+10))
        for vi in range(min(idx+1,len(self.visited))):
            vr,vc2=divmod(vi,vcols)
            vf=tk.Frame(self.vis_inner,bg=CARD)
            vf.grid(row=vr,column=vc2,padx=4,pady=4)
            vcv=tk.Canvas(vf,width=vgrid+6,height=vgrid+6,bg=CARD,highlightthickness=0); vcv.pack()
            draw_board(vcv,self.visited[vi].board,vcs,3,3)
            tk.Label(vf,text=f"#{vi+1}",font=("Segoe UI",7),bg=CARD,fg=SUB).pack()
        self.vis_canvas.update_idletasks()
        self.vis_canvas.configure(scrollregion=self.vis_canvas.bbox("all"))
        # Explanation
        self.set_exp(st['text'])

    def set_exp(self, text):
        self.txt_exp.config(state=tk.NORMAL); self.txt_exp.delete("1.0",tk.END); self.txt_exp.insert(tk.END,text); self.txt_exp.config(state=tk.DISABLED)

    # ===== ACTIONS =====
    def do_input(self):
        def cb(board):
            self.board=[r[:] for r in board]; self.steps=[]; self.visited=[]; self.step_idx=-1; self.draw_initial()
        input_dialog(self.win,cb)

    def do_solve(self):
        if not self.algo:
            messagebox.showwarning("Chưa chọn","Vui lòng chọn thuật toán trước!",parent=self.win); return
        fn=ALGOS[self.algo]; state=S(self.board)
        self.steps,self.visited=fn(state)
        if self.steps:
            self.show_step(0)
        else:
            self.set_exp("Không có bước nào.")

    def do_prev(self):
        if self.step_idx>0: self.show_step(self.step_idx-1)

    def do_next(self):
        if self.step_idx<len(self.steps)-1: self.show_step(self.step_idx+1)

def open_ui(parent, algo_name):
    PuzzleUI(parent, algo_name)
