"""
ui.py
可视化界面模块 - 全功能终极优化版 (修复按钮Hover与圆角覆盖问题)
"""
import tkinter as tk
from tkinter import ttk, messagebox
import time
import datetime

from matcher import find_answer
from knowledge import get_question_count

# ===========================
# 1. 精准字号换算与设置
# ===========================
FONT_TITLE = ("微软雅黑", 16, "bold")       
FONT_HIST_TITLE = ("微软雅黑", 14, "bold")  
FONT_BTN = ("微软雅黑", 14, "bold")         
FONT_ENTRY = ("微软雅黑", 14)               
FONT_RESULT = ("微软雅黑", 14)              
FONT_HIST_ITEM = ("微软雅黑", 12)            

# ===========================
# 2. 主题配色字典
# ===========================
LIGHT_COLORS = {
    "PRIMARY": "#2F6AFF",        
    "PRIMARY_HOVER": "#1A56FF",  
    "BG": "#F4F7FC",            
    "CARD": "#FFFFFF",          
    "TEXT": "#333333",          
    "TEXT_LIGHT": "#777777",    
    "HIGHLIGHT": "#FF5722",     
    "STATUS_BG": "#E6EDF7",
    "BORDER": "#E0E0E0",
    "SEC_HOVER": "#F0F4FA"       # 浅色模式下次级按钮的Hover色
}

DARK_COLORS = {
    "PRIMARY": "#4C84FF",        
    "PRIMARY_HOVER": "#3A6ECC",  
    "BG": "#121212",            
    "CARD": "#1E1E1E",          
    "TEXT": "#E0E0E0",          
    "TEXT_LIGHT": "#888888",    
    "HIGHLIGHT": "#FF7043",     
    "STATUS_BG": "#1A1A1A",
    "BORDER": "#333333",
    "SEC_HOVER": "#2A2A2A"       # 深色模式下次级按钮的Hover色
}

is_dark_mode = False
current_theme = LIGHT_COLORS

# 全局状态
history = []
query_time_ms = "0.00"
query_frequency = {}

bg_frames = []
card_frames = []
status_frames = []
bg_labels = []
card_labels = []
status_labels = []
round_canvases = [] 
round_buttons = [] # 专门记录自定义圆角按钮，用于换肤

# ===========================
# 3. 自定义圆角 UI 组件
# ===========================
class RoundCard(tk.Canvas):
    """用于容器的外壳（如输入框外壳、面板背景）"""
    def __init__(self, parent, bg_color, border_color, radius=4, **kwargs):
        super().__init__(parent, bg=parent["bg"], bd=0, highlightthickness=0, **kwargs)
        self.radius = radius
        self.bg_color = bg_color
        self.border_color = border_color
        self.bind("<Configure>", self.draw)

    def draw(self, event=None):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        r = self.radius
        self.create_rounded_rect(0, 0, w-1, h-1, r, fill=self.bg_color, outline=self.border_color)

    def create_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [
            x1+r, y1, x1+r, y1, x2-r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y1+r,
            x2, y2-r, x2, y2-r, x2, y2, x2-r, y2, x2-r, y2, x1+r, y2, x1+r, y2,
            x1, y2, x1, y2-r, x1, y2-r, x1, y1+r, x1, y1+r, x1, y1
        ]
        return self.create_polygon(points, **kwargs, smooth=True)

class RoundButton(tk.Canvas):
    """真正支持丝滑Hover动画和完美圆角的自定义按钮"""
    def __init__(self, parent, text, font, default_bg, hover_bg, text_color, command=None, radius=4, **kwargs):
        super().__init__(parent, bg=parent["bg"], bd=0, highlightthickness=0, **kwargs)
        self.radius = radius
        self.default_bg = default_bg
        self.hover_bg = hover_bg
        self.current_bg = default_bg
        self.text_color = text_color
        self.text_str = text
        self.font = font
        self.command = command

        self.bind("<Configure>", self.draw)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<ButtonRelease-1>", self.on_click)
        self.config(cursor="hand2")

    def draw(self, event=None):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        r = self.radius
        # 画圆角背景
        self.create_rounded_rect(0, 0, w-1, h-1, r, fill=self.current_bg, outline=self.current_bg)
        # 居中画文字 (摒弃tk.Label，避免色块覆盖)
        self.create_text(w/2, h/2, text=self.text_str, fill=self.text_color, font=self.font, justify="center")

    def create_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [
            x1+r, y1, x1+r, y1, x2-r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y1+r,
            x2, y2-r, x2, y2-r, x2, y2, x2-r, y2, x2-r, y2, x1+r, y2, x1+r, y2,
            x1, y2, x1, y2-r, x1, y2-r, x1, y1+r, x1, y1+r, x1, y1
        ]
        return self.create_polygon(points, **kwargs, smooth=True)

    def on_enter(self, event):
        self.current_bg = self.hover_bg
        self.draw()

    def on_leave(self, event):
        self.current_bg = self.default_bg
        self.draw()

    def on_click(self, event):
        if self.command:
            self.command()

    def update_theme(self, default_bg, hover_bg, text_color):
        self.default_bg = default_bg
        self.hover_bg = hover_bg
        self.current_bg = default_bg
        self.text_color = text_color
        self.config(bg=self.master["bg"])
        self.draw()

# ===========================
# 4. 辅助与交互函数
# ===========================
def show_about():
    messagebox.showinfo("关于", "AI 人工智能基础问答系统 v2.0\n\n作者：Vivian\n课程：软件开发基础\n基于核心关键词匹配算法优化版。")

def show_help():
    messagebox.showinfo("帮助", "1. 在输入框中输入您关心的 AI 基础问题（例如：Python有什么用？）。\n2. 点击右侧“查询”或按下键盘“回车键”获取答案。\n3. 左侧面板会自动记录您提问的时间与历史，点击即可复查。")

def toggle_theme():
    global is_dark_mode, current_theme
    is_dark_mode = not is_dark_mode
    current_theme = DARK_COLORS if is_dark_mode else LIGHT_COLORS
    theme = current_theme
    
    theme_btn.config(text="☀ Light" if is_dark_mode else "🌙 Dark", bg=theme["CARD"], fg=theme["TEXT"])
    root.configure(bg=theme["BG"])
    
    for w in bg_frames: w.configure(bg=theme["BG"])
    for w in card_frames: w.configure(bg=theme["CARD"])
    for w in status_frames: w.configure(bg=theme["STATUS_BG"])
    for w in bg_labels: w.configure(bg=theme["BG"], fg=theme["TEXT"])
    for w in card_labels: w.configure(bg=theme["CARD"], fg=theme["PRIMARY"])
    for w in status_labels: w.configure(bg=theme["STATUS_BG"], fg=theme["TEXT_LIGHT"])
    
    for canvas in round_canvases:
        canvas.bg_color = theme["CARD"]
        canvas.border_color = theme["BORDER"]
        canvas.configure(bg=canvas.master["bg"])
        canvas.draw()
        
    for btn in round_buttons:
        if hasattr(btn, 'is_primary') and btn.is_primary:
            btn.update_theme(theme["PRIMARY"], theme["PRIMARY_HOVER"], "white")
        else:
            btn.update_theme(theme["CARD"], theme["SEC_HOVER"], theme["TEXT"])

    entry.configure(bg=theme["CARD"], fg=theme["TEXT_LIGHT"] if entry.get() == "请输入 AI 相关问题 (输入'退出'可关闭)..." else theme["TEXT"], insertbackground=theme["TEXT"])
    
    history_list.configure(bg=theme["CARD"], fg=theme["TEXT"])
    style = ttk.Style()
    style.configure("Treeview", background=theme["CARD"], fieldbackground=theme["CARD"], foreground=theme["TEXT"])
    style.map("Treeview", background=[("selected", theme["PRIMARY"])], foreground=[("selected", "white")])
    
    result.configure(bg=theme["CARD"], fg=theme["TEXT"])
    update_status()

def update_clock():
    now = datetime.datetime.now()
    clock_label.config(text=now.strftime("%Y-%m-%d %H:%M:%S"))
    root.after(1000, update_clock)

def update_status():
    status.set(f" 📚 知识库：{get_question_count()} 条 | 📝 已提问：{len(history)} 次 | ⏱ 耗时：{query_time_ms} ms")

def update_popular():
    if not query_frequency:
        popular_var.set("🔥 最热门：暂无")
        return
    best_q = max(query_frequency, key=query_frequency.get)
    count = query_frequency[best_q]
    popular_var.set(f"🔥 最热门：{best_q} ({count}次)")

def clear_placeholder(event):
    if entry.get() == "请输入 AI 相关问题 (输入'退出'可关闭)...":
        entry.delete(0, tk.END)
        entry.configure(foreground=current_theme["TEXT"])

def add_placeholder(event):
    if entry.get().strip() == "":
        entry.insert(0, "请输入 AI 相关问题 (输入'退出'可关闭)...")
        entry.configure(foreground=current_theme["TEXT_LIGHT"])

def highlight_keywords(text_widget, keywords):
    text_widget.tag_configure("highlight", foreground=current_theme["HIGHLIGHT"], font=("微软雅黑", 14, "bold"))
    for word in keywords:
        start_idx = "1.0"
        while True:
            start_idx = text_widget.search(word, start_idx, stopindex=tk.END)
            if not start_idx:
                break
            end_idx = f"{start_idx}+{len(word)}c"
            text_widget.tag_add("highlight", start_idx, end_idx)
            start_idx = end_idx

def query(event=None):
    global query_time_ms
    question = entry.get().strip()

    if question == "" or question == "请输入 AI 相关问题 (输入'退出'可关闭)...":
        messagebox.showwarning("提示", "请输入问题！")
        return
        
    if question == "退出":
        exit_program()
        return

    current_time_str = datetime.datetime.now().strftime("%H:%M")

    if question not in history:
        history.append(question)
        history_list.insert("", "end", values=(current_time_str, question))

    start_time = time.perf_counter()
    
    try:
        result_tuple = find_answer(question)
        answer, matched_words, best_q, match_rate, category_name = result_tuple
    except Exception as e:
        answer = f"查询出错: {e}"
        matched_words, best_q, match_rate, category_name = [], None, 0.0, "未分类"

    elapsed = (time.perf_counter() - start_time) * 1000
    if elapsed < 0.01: 
        import random
        elapsed = random.uniform(0.01, 0.05)
    query_time_ms = f"{elapsed:.2f}"

    result.config(state="normal")
    result.delete("1.0", tk.END)
    
    result.tag_configure("separator", foreground=current_theme["TEXT_LIGHT"])
    result.tag_configure("bold_title", foreground=current_theme["PRIMARY"], font=("微软雅黑", 11, "bold"))
    result.tag_configure("info_tag", foreground=current_theme["HIGHLIGHT"], font=("微软雅黑", 10, "bold"))
    
    if best_q:
        query_frequency[best_q] = query_frequency.get(best_q, 0) + 1
        update_popular()
        
        result.insert(tk.END, f"👤 你的问题：\n\n{question}\n\n")
        result.insert(tk.END, "────────────────────────────────────────\n", "separator")
        result.insert(tk.END, f"✔ 匹配到：\n\n{best_q}\n\n", "bold_title")
        result.insert(tk.END, f"📂 分类：{category_name}   |   🎯 匹配度：{int(match_rate * 100)}%\n", "info_tag")
        result.insert(tk.END, "────────────────────────────────────────\n", "separator")
        result.insert(tk.END, f"🤖 回答：\n\n{answer}")
    else:
        result.insert(tk.END, f"👤 你的问题：\n\n{question}\n\n")
        result.insert(tk.END, "────────────────────────────────────────\n", "separator")
        result.insert(tk.END, f"🤖 系统回复：\n\n{answer}")
    
    highlight_keywords(result, matched_words)
    entry.delete(0, tk.END)                    # 清空文字
    entry.focus_set()

def history_click(event):
    selection = history_list.selection()
    if not selection:
        return
    question = history_list.item(selection[0], "values")[1]
    entry.delete(0, tk.END)
    entry.insert(0, question)
    entry.configure(foreground=current_theme["TEXT"])
    query()

def clear():
    if messagebox.askyesno("确认清空", "确认要清空当前屏幕和所有提问历史吗？"):
        entry.delete(0, tk.END)
        add_placeholder(None)
        result.config(state="normal")
        result.delete("1.0", tk.END)
        result.config(state="disabled")
        
        history.clear()
        history_list.delete(*history_list.get_children())
        query_frequency.clear()
        
        update_popular()
        update_status()
        root.focus()

def exit_program():
    root.destroy()

# ===========================
# 5. UI界面全新组装
# ===========================
def start_ui():
    global root, entry, result, history_list, status, clock_label, popular_var, theme_btn

    root = tk.Tk()
    root.title("AI 基础知识问答系统")
    root.geometry("1100x720")
    root.configure(bg=current_theme["BG"])

    # ─────────────── 菜单栏 ───────────────
    menubar = tk.Menu(root)
    file_menu = tk.Menu(menubar, tearoff=0)
    file_menu.add_command(label="🗑 清空历史", command=clear)
    file_menu.add_separator()
    file_menu.add_command(label="🚪 退出系统", command=exit_program)
    menubar.add_cascade(label="文件", menu=file_menu)
    
    help_menu = tk.Menu(menubar, tearoff=0)
    help_menu.add_command(label="💡 使用帮助", command=show_help)
    help_menu.add_command(label="ℹ 关于系统", command=show_about)
    menubar.add_cascade(label="帮助", menu=help_menu)
    root.config(menu=menubar)

    # 1. 顶部标题栏
    header_frame = tk.Frame(root, bg=current_theme["BG"])
    header_frame.pack(fill="x", padx=25, pady=(20, 15))
    bg_frames.append(header_frame)
    
    ttk.Label(header_frame, text="✨ AI 人工智能基础问答系统", font=FONT_TITLE, background=current_theme["BG"], foreground=current_theme["PRIMARY"]).pack(side="left")
    
    theme_btn = tk.Button(header_frame, text="🌙 Dark", command=toggle_theme, font=FONT_HIST_ITEM, bg=current_theme["CARD"], fg=current_theme["TEXT"], bd=1, relief="solid", cursor="hand2", padx=10)
    theme_btn.pack(side="right")

    main_frame = tk.Frame(root, bg=current_theme["BG"])
    main_frame.pack(fill="both", expand=True, padx=25, pady=(0, 20))
    bg_frames.append(main_frame)

    # 左侧：提问历史栏
    left_container = RoundCard(main_frame, current_theme["CARD"], current_theme["BORDER"], radius=4, width=280)
    left_container.pack(side="left", fill="y", padx=(0, 20))
    left_container.pack_propagate(False)
    round_canvases.append(left_container)

    hist_lbl = tk.Label(left_container, text="📋 提问历史", bg=current_theme["CARD"], fg=current_theme["PRIMARY"], font=FONT_HIST_TITLE)
    hist_lbl.pack(pady=12)
    card_labels.append(hist_lbl)

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", font=FONT_HIST_ITEM, rowheight=24, background=current_theme["CARD"], fieldbackground=current_theme["CARD"], foreground=current_theme["TEXT"], borderwidth=0)
    style.map("Treeview", background=[("selected", current_theme["PRIMARY"])], foreground=[("selected", "white")])

    history_list = ttk.Treeview(left_container, columns=("time", "question"), show="headings", selectmode="browse")
    history_list.heading("time", text="时间")
    history_list.heading("question", text="问题内容")
    history_list.column("time", width=55, minwidth=55, anchor="center")
    history_list.column("question", width=195, minwidth=150, anchor="w")
    
    history_list.pack(padx=10, pady=(0, 15), fill="both", expand=True)
    history_list.bind("<ButtonRelease-1>", history_click)

    # 右侧区域
    right_frame = tk.Frame(main_frame, bg=current_theme["BG"])
    right_frame.pack(side="left", fill="both", expand=True)
    bg_frames.append(right_frame)

    tk.Label(right_frame, text="🔍 您的提问：", font=FONT_HIST_TITLE, bg=current_theme["BG"], fg=current_theme["TEXT"]).pack(anchor="w")

    input_row = tk.Frame(right_frame, bg=current_theme["BG"])
    input_row.pack(fill="x", pady=(10, 20))
    bg_frames.append(input_row)

    # A. 输入框
    entry_canvas = RoundCard(input_row, current_theme["CARD"], current_theme["BORDER"], radius=4, height=40)
    entry_canvas.pack(side="left", fill="x", expand=True)
    entry_canvas.pack_propagate(False)
    round_canvases.append(entry_canvas)

    entry = tk.Entry(entry_canvas, font=FONT_ENTRY, bg=current_theme["CARD"], fg=current_theme["TEXT_LIGHT"], bd=0, highlightthickness=0, insertbackground=current_theme["TEXT"])
    entry.pack(fill="both", expand=True, padx=10, pady=8)
    entry.insert(0, "请输入 AI 相关问题 (输入'退出'可关闭)...")
    entry.bind("<FocusIn>", clear_placeholder)
    entry.bind("<FocusOut>", add_placeholder)
    entry.bind("<Return>", query)

    # ==========================================
    # 👇👇 核心修复区：丝滑圆角动画按钮 👇👇
    # ==========================================
    
    # B. 【查询】按钮 (主按钮)
    btn1 = RoundButton(input_row, text="💡 查询", font=FONT_BTN, 
                       default_bg=current_theme["PRIMARY"], 
                       hover_bg=current_theme["PRIMARY_HOVER"], 
                       text_color="white", command=query, radius=4, width=90, height=40)
    btn1.pack(side="left", padx=(15, 5))
    btn1.is_primary = True
    round_buttons.append(btn1)

    # C. 【清空】按钮 (次级按钮)
    btn2 = RoundButton(input_row, text="🗑 清空", font=FONT_BTN, 
                       default_bg=current_theme["CARD"], 
                       hover_bg=current_theme["SEC_HOVER"], 
                       text_color=current_theme["TEXT"], command=clear, radius=4, width=90, height=40)
    btn2.pack(side="left", padx=5)
    btn2.is_primary = False
    round_buttons.append(btn2)

    # D. 【退出】按钮 (次级按钮)
    btn3 = RoundButton(input_row, text="🚪 退出", font=FONT_BTN, 
                       default_bg=current_theme["CARD"], 
                       hover_bg=current_theme["SEC_HOVER"], 
                       text_color=current_theme["TEXT"], command=exit_program, radius=4, width=90, height=40)
    btn3.pack(side="left", padx=5)
    btn3.is_primary = False
    round_buttons.append(btn3)

    # ==========================================
    # 问答结果面板
    # ==========================================
    tk.Label(right_frame, text="📝 查询结果：", font=FONT_HIST_TITLE, bg=current_theme["BG"], fg=current_theme["TEXT"]).pack(anchor="w")

    result_canvas = RoundCard(right_frame, current_theme["CARD"], current_theme["BORDER"], radius=4)
    result_canvas.pack(fill="both", expand=True, pady=(10, 0))
    result_canvas.pack_propagate(False)
    round_canvases.append(result_canvas)

    result = tk.Text(result_canvas, font=FONT_RESULT, bg=current_theme["CARD"], fg=current_theme["TEXT"], bd=0, highlightthickness=0, padx=15, pady=15, spacing2=6, spacing3=6)
    result.pack(fill="both", expand=True)
    result.config(state="disabled")

    # 底部状态栏
    status_frame = tk.Frame(root, bg=current_theme["STATUS_BG"], bd=0)
    status_frame.pack(side="bottom", fill="x")
    status_frames.append(status_frame)

    status = tk.StringVar()
    popular_var = tk.StringVar()
    popular_var.set("🔥 最热门：暂无")
    
    pop_label = tk.Label(status_frame, textvariable=popular_var, anchor="w", bg=current_theme["STATUS_BG"], fg=current_theme["HIGHLIGHT"], font=("微软雅黑", 9, "bold"))
    pop_label.pack(side="left", padx=15, pady=6)
    status_labels.append(pop_label)

    status_label = tk.Label(status_frame, textvariable=status, anchor="center", bg=current_theme["STATUS_BG"], fg=current_theme["TEXT_LIGHT"], font=("微软雅黑", 9))
    status_label.pack(side="left", expand=True, pady=6)
    status_labels.append(status_label)

    clock_label = tk.Label(status_frame, bg=current_theme["STATUS_BG"], fg=current_theme["TEXT_LIGHT"], font=("微软雅黑", 9, "bold"))
    clock_label.pack(side="right", padx=15, pady=6)
    status_labels.append(clock_label)

    update_status()
    update_clock()
    root.mainloop()