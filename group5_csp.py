import tkinter as tk
from tkinter import ttk

def open_ui(parent, algo_name):
    parent.withdraw()
    
    window = tk.Toplevel(parent)
    window.title(f"Thỏa mãn ràng buộc (CSP) - {algo_name}")
    window.geometry("600x400")
    
    lbl = ttk.Label(window, text=f"Thuật toán: {algo_name}", font=("Helvetica", 16, "bold"))
    lbl.pack(pady=20)
    
    info_lbl = ttk.Label(window, text="Đây là giao diện của Nhóm 5: Thỏa mãn ràng buộc (CSP).\nBạn có thể thêm các control (VD: bài toán N-Queens, tô màu bản đồ) ở đây.", justify="center")
    info_lbl.pack(pady=10)
    
    def on_close():
        window.destroy()
        parent.deiconify()
        
    window.protocol("WM_DELETE_WINDOW", on_close)
    
    btn_back = ttk.Button(window, text="Quay lại Menu", command=on_close)
    btn_back.pack(pady=20)
